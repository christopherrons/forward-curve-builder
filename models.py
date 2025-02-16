import csv
from datetime import datetime, date

from enum import Enum, auto


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


class DayCountConvention(Enum):
    ACT_365 = 365
    ACT_360 = 360


class InterpolationStrategy(Enum):
    LINEAR = auto()
    CUBIC_SPLINE = auto()
    BLUE = auto()


class ProductType(Enum):
    FUTURE = auto()
    OPTION = auto()


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
