import csv

from models import InstrumentDetails, ProductType


def read_csv_and_map_to_objects(csv_file_path) -> [InstrumentDetails]:
    instrument_details = []
    with open(csv_file_path, mode='r', newline='') as file:
        reader = csv.DictReader(file)
        for row in reader:
            instrument = InstrumentDetails(
                date=row["date"],
                exchange=row["exchange"],
                product=row["product"],
                product_type=map_product_type(row["product_type"]),
                currency=row["currency"],
                settlement_price=float(row["settlement_price"]),
                maturity_date=row["maturity_date"]
            )
            instrument_details.append(instrument)
    return instrument_details


def map_product_type(product_type_str) -> ProductType:
    if product_type_str.upper() == "FUTURES":
        return ProductType.FUTURE
    elif product_type_str.upper() == "OPTIONS":
        return ProductType.OPTION
    else:
        raise ValueError(f"Unknown product type: {product_type_str}")
