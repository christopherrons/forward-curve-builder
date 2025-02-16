from datetime import datetime, date
from typing import List

import numpy as np
from scipy.interpolate import CubicSpline, interp1d

from models import InstrumentDetails, CurveKey, InterpolationStrategy, DayCountConvention


class ForwardCurve:
    def __init__(self,
                 curve_key: CurveKey,
                 time_to_maturities: np.ndarray,
                 prices: np.ndarray,
                 interpolation_strategy: InterpolationStrategy,
                 day_count_convention: DayCountConvention):
        self.curve_key = curve_key
        self.time_to_maturity = time_to_maturities
        self.prices = prices
        if interpolation_strategy == InterpolationStrategy.CUBIC_SPLINE:
            self.curve = CubicSpline(time_to_maturities, prices)
        else:
            self.curve = interp1d(time_to_maturities, prices, kind='linear')
        self.day_count_convention = day_count_convention

    @staticmethod
    def create_from(curve_key: CurveKey,
                    day_count_convention: DayCountConvention,
                    interpolation_strategy: InterpolationStrategy,
                    future_in_same_product: List[InstrumentDetails]):
        sorted_details: List[InstrumentDetails] = list(
            sorted(future_in_same_product, key=lambda item: item.maturity_date)
        )
        time_to_maturity: [float] = []
        prices: [float] = []
        for detail in sorted_details:
            time_to_maturity.append((detail.maturity_date - detail.settlement_date).days / day_count_convention.value)
            prices.append(detail.settlement_price)

        return ForwardCurve(curve_key, np.array(time_to_maturity), np.array(prices), interpolation_strategy, day_count_convention)


    def get_time_to_maturity(self, maturity_date: date, calculation_date: date):
        return (maturity_date - calculation_date).days / self.day_count_convention.value

    def get_price(self, time_to_maturity: float) -> float:
        return self.curve(time_to_maturity)
