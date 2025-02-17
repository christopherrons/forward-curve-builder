import os
from collections import defaultdict
from datetime import date, datetime
from typing import List, Dict

import matplotlib.pyplot as plt
import numpy as np

from forward_curve import ForwardCurve, DayCountConvention, InterpolationStrategy, CurveKey
from models import InstrumentDetails, PriceSeries, ForwardCurvePrice
from utils import read_csv_and_map_to_objects

import seaborn as sns

sns.set_theme(style="whitegrid")


def main():
    directory: str = "/Users/christopherherron/cme/output"
    instrument_details: List[InstrumentDetails] = []
    for input_directory in sorted(os.listdir(directory)):
        if ".DS_Store" in input_directory:
            continue
        for file in sorted(os.listdir(f"{directory}/{input_directory}")):
            print(f"Parsing: {file}")
            instrument_details.extend(read_csv_and_map_to_objects(f"{directory}/{input_directory}/{file}"))

    curves_by_key: Dict[CurveKey, ForwardCurve] = build_curves(instrument_details)
    for curve in curves_by_key.values():
        print(f"Store curve: {curve.curve_key}")
        store_curve_plots(curve)

    for detail in read_csv_and_map_to_objects("/Users/christopherherron/cme/output/2024/instrument_20241230.csv"):
        price_series: PriceSeries = calculate_price_series(curves_by_key, detail)
        print(f"Store Prices: {price_series.instrument_id}")
        store_price_plots(price_series)
        print(f"Store Returns: {price_series.instrument_id}")
        store_return_plots(price_series)


def build_curves(instrument_details: List[InstrumentDetails]) -> Dict[CurveKey, ForwardCurve]:
    details_by_curve_key: Dict[CurveKey, List[InstrumentDetails]] = group_instruments_by_key(instrument_details, key_func=lambda x: x.forward_curve_key)
    curve_by_key: Dict[CurveKey, ForwardCurve] = defaultdict()
    for curve_key, details in details_by_curve_key.items():
        curve: ForwardCurve = ForwardCurve.create_from(curve_key, DayCountConvention.ACT_365, InterpolationStrategy.CUBIC_SPLINE, details)
        curve_by_key[curve_key] = curve
    sorted_by_values: Dict[CurveKey, ForwardCurve] = dict(
        sorted(curve_by_key.items(), key=lambda item: item[0].settlement_date)
    )

    return sorted_by_values


def group_instruments_by_key(instrument_details: List[InstrumentDetails], key_func) -> Dict[CurveKey, List[InstrumentDetails]]:
    grouped_dict: Dict[CurveKey, List[InstrumentDetails]] = defaultdict(list)
    for details in instrument_details:
        grouped_dict[key_func(details)].append(details)
    return grouped_dict


def calculate_price_series(curves_by_key: Dict[CurveKey, ForwardCurve], details: InstrumentDetails) -> PriceSeries:
    prices: List[ForwardCurvePrice] = []
    maturity_date: date = details.maturity_date
    for curve_key, curve in curves_by_key.items():
        if curve_key.exchange != details.exchange or curve_key.product != details.product:
            continue
        time_to_maturity: float = curve.get_time_to_maturity(maturity_date, datetime.now().date())
        price: float = curve.get_price(time_to_maturity)
        prices.append(ForwardCurvePrice(details.instrument_id, curve_key, maturity_date, time_to_maturity, price))

    return PriceSeries(details.instrument_id, prices)


def store_curve_plots(curve: ForwardCurve):
    maturities: np.ndarray = np.linspace(curve.time_to_maturity[0], curve.time_to_maturity[-1], 100)

    plt.figure(figsize=(10, 6))

    prices: [float] = [curve.get_price(maturity) for maturity in maturities]
    plt.plot(maturities, prices, label=str(curve.curve_key))
    plt.scatter(curve.time_to_maturity, curve.prices, label="Observed: " + str(curve.curve_key))

    plt.xlabel('Maturity')
    plt.ylabel('Price')
    plt.title(f'Price vs Maturity for {curve.curve_key.exchange} {curve.curve_key.product}')
    plt.legend()
    plt.grid(True)

    save_path = f"plots/curves/{curve.curve_key.exchange}/{curve.curve_key.product}/curve_{curve.curve_key}.png"
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    plt.savefig(save_path)

    plt.close()


def store_price_plots(price_series: PriceSeries):
    plt.figure(figsize=(10, 6))

    dates: List[date] = []
    prices: List[ForwardCurvePrice] = []
    for price in price_series.prices:
        dates.append(price.curve_key.settlement_date)
        prices.append(price.price)

    plt.plot(dates, prices, label=str(price_series.instrument_id))

    plt.xlabel('Date')
    plt.ylabel('Return %')
    plt.title(f'Price vs Date for Instrument {price_series.instrument_id}')
    plt.legend()
    plt.grid(True)

    save_path = f"plots/prices/{price_series.prices[0].curve_key.exchange}/{price_series.prices[0].curve_key.product}/prices_{price_series.instrument_id.__str__()}.png"
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    plt.savefig(save_path)

    plt.close()


def store_return_plots(price_series: PriceSeries):
    plt.figure(figsize=(10, 6))

    dates: List[date] = []
    daily_returns: List[date] = []
    for daily_return in price_series.get_returns():
        dates.append(daily_return.date_of_return)
        daily_returns.append(daily_return.daily_return * 100)

    plt.plot(dates, daily_returns, label=str(price_series.instrument_id))

    plt.xlabel('Date')
    plt.ylabel('Return %')
    plt.title(f'Returns vs Date for Instrument {price_series.instrument_id}')
    plt.legend()
    plt.grid(True)

    save_path = f"plots/returns/{price_series.prices[0].curve_key.exchange}/{price_series.prices[0].curve_key.product}/returns_{price_series.instrument_id.__str__()}.png"
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    plt.savefig(save_path)

    plt.close()


if __name__ == "__main__":
    main()
