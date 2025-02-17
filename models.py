import csv
from datetime import datetime, date

from enum import Enum, auto
from typing import List


class CurveKey:
    def __init__(self, settlement_date: date, exchange: str, product: str):
        self.settlement_date = settlement_date
        self.product = product
        self.exchange = exchange

    def __hash__(self):
        return hash((self.settlement_date, self.exchange, self.product))

    def __eq__(self, other):
        if isinstance(other, CurveKey):
            return self.settlement_date == other.settlement_date and self.exchange == other.exchange and self.product == other.product
        return False

    def __str__(self):
        return f"{self.settlement_date}_{self.exchange}_{self.product}"


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
    OTHER = "other"


class InstrumentDetails:
    def __init__(self, date, exchange, name, product, product_type, underlying, currency, settlement_price, maturity_date):
        self.settlement_date = self.parse_valid_date(date)
        self.exchange = exchange
        self.name = name.replace(" ", "-")
        self.product = product
        self.product_type = product_type
        self.underlying = underlying
        self.currency = currency
        self.settlement_price = settlement_price
        self.maturity_date = self.parse_valid_date(maturity_date)
        self.forward_curve_key = CurveKey(self.settlement_date, self.exchange, self.product)
        self.instrument_id = f"{self.name}_{self.product}_{self.product_type.value}_{self.maturity_date}".lower()

    @staticmethod
    def parse_valid_date(date_str):
        """Ensures 'YYYYMM00' dates are corrected to 'YYYYMM01' before parsing."""
        if date_str[-2:] == "00":
            date_str = date_str[:-2] + "01"
        return datetime.strptime(date_str, "%Y%m%d").date()
