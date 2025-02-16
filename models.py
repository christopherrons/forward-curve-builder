import csv
from datetime import datetime, date

from enum import Enum, auto
from typing import List


class CurveKey:
    def __init__(self, settlement_date: date, product: str):
        self.settlement_date = settlement_date
        self.product = product

    def __hash__(self):
        return hash((self.settlement_date, self.product))

    def __eq__(self, other):
        if isinstance(other, CurveKey):
            return self.settlement_date == other.settlement_date and self.product == other.product
        return False

    def __str__(self):
        return f"{self.settlement_date}_{self.product}"


class ForwardCurvePrice:
    def __init__(self, instrument_id, curve_key: CurveKey, maturity_date: date, time_to_maturity, price: float):
        self.instrument_id = instrument_id
        self.curve_key = curve_key
        self.maturity_date = maturity_date
        self.time_to_maturity = time_to_maturity
        self.price = price


class PriceSeries:
    def __init__(self, instrument_id: str, prices: [ForwardCurvePrice]):
        self.instrument_id = instrument_id
        self.prices = list(
            sorted(prices, key=lambda item: item.curve_key.settlement_date)
        )

    def get_returns(self):
        daily_returns: List[DailyReturn] = []
        previous_price: ForwardCurvePrice = None
        for price in self.prices:
            if previous_price is None:
                previous_price: ForwardCurvePrice = price
                continue
            daily_return: float = (price.price - previous_price.price) / previous_price.price
            daily_returns.append(DailyReturn(price.curve_key.settlement_date, daily_return))
        return daily_returns


class DailyReturn:
    def __init__(self, date_of_return: date, daily_return: float):
        self.date_of_return = date_of_return
        self.daily_return = daily_return


class DayCountConvention(Enum):
    ACT_365 = 365
    ACT_360 = 360


class InterpolationStrategy(Enum):
    LINEAR = auto()
    CUBIC_SPLINE = auto()
    BLUE = auto()


class ProductType(Enum):
    FUTURE = "future"
    OPTION = "option"


class InstrumentDetails:
    def __init__(self,
                 date: str,
                 exchange: str,
                 product: str,
                 product_type: ProductType,
                 currency: str,
                 settlement_price: float,
                 maturity_date: str):
        self.settlement_date = datetime.strptime(date, "%Y%m%d").date()
        self.exchange = exchange
        self.product = product
        self.product_type = product_type
        self.currency = currency
        self.settlement_price = settlement_price
        self.maturity_date = datetime.strptime(maturity_date, "%Y%m%d").date()
        self.forward_curve_key = CurveKey(self.settlement_date, self.product)
        self.instrument_id = f"{product}_{product_type.value}_{maturity_date}"
