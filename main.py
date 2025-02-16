import os
from collections import defaultdict
from datetime import date
import matplotlib.pyplot as plt
import numpy as np

from forward_curve import ForwardCurve, DayCountConvention, InterpolationStrategy, CurveKey
from models import InstrumentDetails, ProductType
from utils import read_csv_and_map_to_objects


class HistoricalReturns:
    def __init__(self, settlement_date: date, daily_return: float):
        self.settlement_date = settlement_date
        self.daily_return = daily_return


def main():
    instrument_details = []
    for file in os.listdir("examples/"):
        instrument_details: [InstrumentDetails] = instrument_details + read_csv_and_map_to_objects(file)
    curves_by_key: {CurveKey, ForwardCurve} = build_curves(instrument_details)
    test_historical_returns: [HistoricalReturns] = calculate_historical_returns(curves_by_key, create_test_details())
    plot_curves(curves_by_key)


def build_curves(instrument_details: [InstrumentDetails]) -> {CurveKey, ForwardCurve}:
    details_by_curve_key = group_instruments_by_key(instrument_details, key_func=lambda x: x.curve_key)
    curve_by_key = defaultdict(list)
    for curve_key, details in details_by_curve_key.items():
        curve: ForwardCurve = ForwardCurve.create_from(curve_key, DayCountConvention.ACT_365, InterpolationStrategy.CUBIC_SPLINE, details)
        curve_by_key[curve_key].append(curve)


def group_instruments_by_key(instrument_details: [InstrumentDetails], key_func) -> {CurveKey, [InstrumentDetails]}:
    grouped_dict = defaultdict(list)
    for details in instrument_details:
        grouped_dict[key_func(details)].append(details)
    return grouped_dict


def calculate_historical_returns(curves_by_key: {CurveKey, ForwardCurve}, details: InstrumentDetails) -> [HistoricalReturns]:
    historical_returns: [HistoricalReturns] = []
    previous_curve: ForwardCurve = None
    maturity_date: date = details.maturity_date

    sorted_by_values: {CurveKey, ForwardCurve} = dict(
        sorted(curves_by_key.items(), key=lambda item: item[0].settlement_date)
    )

    for curve_key, curve in sorted_by_values.items():
        if previous_curve is None:
            previous_curve = curve
            continue

        previous_price: float = previous_curve.get_price_for_date(maturity_date)
        current_price: float = curve.get_price_for_date(maturity_date)

        if previous_price == 0:
            daily_returns = 0.0
        else:
            daily_returns: float = (current_price - previous_price) / previous_price

        historical_returns.append(HistoricalReturns(curve_key.settlement_date, daily_returns))
        previous_curve: ForwardCurve = curve

    return historical_returns


def plot_curves(curves_by_key: {CurveKey, ForwardCurve}):
    maturities: np.ndarray = np.linspace(0, 1, 100)

    plt.figure(figsize=(10, 6))

    for curve_key, curve in curves_by_key.items():
        prices: [float] = [curve.get_price(maturity) for maturity in maturities]

        plt.plot(maturities, prices, label=str(curve_key))

    plt.xlabel('Maturity')
    plt.ylabel('Price')
    plt.title('Price vs Maturity for Different Curves')
    plt.legend()
    plt.grid(True)

    plt.show()


def create_test_details() -> InstrumentDetails:
    return InstrumentDetails(
        "20250201",
        "TEST",
        "TEST",
        ProductType.FUTURE,
        "USD",
        0,
        "20250701"
    )


if __name__ == "__main__":
    main()
