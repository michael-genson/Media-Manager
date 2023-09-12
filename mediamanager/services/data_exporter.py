import csv
from tempfile import NamedTemporaryFile

from ..models.app.data_exporter import Exportable


class DataExporter:
    def create_csv(self, data: list[Exportable], headers: list[str] | None = None) -> str:
        """
        Convert a list of dictionaries into a CSV file

        Optionally supply a list of headers, otherwise all fields in the first dictionary will be used
        """
        if not data:
            raise ValueError("data cannot be empty")

        csv_filepath = NamedTemporaryFile(delete=False, suffix="csv").name
        with open(csv_filepath, "w", newline="") as f:
            fieldnames = headers or data[0].to_csv().keys()
            writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
            writer.writeheader()
            for row in data:
                writer.writerow(row.to_csv())

        return csv_filepath
