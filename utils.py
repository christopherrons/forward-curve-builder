import csv

from models import InstrumentDetails, ProductType


def read_csv_and_map_to_objects(csv_file_path) -> [InstrumentDetails]:
    instrument_details = []
    with open(csv_file_path, mode='r', newline='') as file:
        reader = csv.DictReader(file)
        for row in reader:
            instrument = InstrumentDetails(
                date=row["Date"],
                exchange=row["Exchange"],
                name=row["Name"],
                product=row["Product"],
                product_type=map_product_type(row["ProductType"]),
                underlying=row["Underlying"],
                currency=row["Currency"],
                settlement_price=float(row["SettlementPrice"]),
                maturity_date=row["MaturityDate"]
            )
            if instrument.product_type == ProductType.FUTURE:
                instrument_details.append(instrument)
    return instrument_details


def map_product_type(product_type_str) -> ProductType:
    if product_type_str.upper() == "FUT":
        return ProductType.FUTURE
    return ProductType.OTHER
