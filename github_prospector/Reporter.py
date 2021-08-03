import csv
import json
import optparse
import os
from datetime import datetime
from enum import Enum
from pprint import pprint


class ReporterTypes(Enum):
    """Enumerate of report types."""
    JSON = 'json'
    PRINT = 'print'

    # CSV = 'csv'

    @staticmethod
    def get_all_reporters_types():
        """Returns all report types."""
        return list(map(
            lambda x: x.value,
            ReporterTypes))


class Reporter:
    """Creating reports class."""

    def __init__(self, data: dict, config: optparse.Values):
        reporter_type = getattr(config, 'reporter_type', ReporterTypes.PRINT)
        try:
            self.reporter_type = ReporterTypes(reporter_type)
        except ValueError:
            print(f'{reporter_type} - reporter not found. Setting default: {ReporterTypes.PRINT}')
            self.reporter_type = ReporterTypes.PRINT
        self.data = data
        self.config = config

    def run(self):

        if not self.data:
            return
        if self.reporter_type == ReporterTypes.PRINT:
            pprint(self.data, width=120)
        elif self.reporter_type == ReporterTypes.JSON:
            self.create_json_reports()
        elif self.reporter_type == ReporterTypes.CSV:
            self.create_csv_reports()
        else:
            print(f'Error! Reporter not found!!!')
            print(self.data)

    def create_json_reports(self):
        """Creating json reports (multi, one files)."""
        output_dir = getattr(self.config, 'output_dir')
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        if getattr(self.config, 'one_file'):
            path = os.path.join(output_dir, f'{datetime.now().strftime("%m-%d-%Y")}.json')
            self._create_json_report(self.data, path)
        else:
            for name, data in self.data.items():
                path = os.path.join(output_dir, f'{name}-{datetime.now().strftime("%m-%d-%Y")}.json')
                self._create_json_report(data, path)

    def _create_json_report(self, data: dict, file_path: str):
        """Creating json report."""
        f = open(file_path, 'w')
        f.write(json.dumps(data, indent=4, sort_keys=True))
        f.close()

    def create_csv_reports(self):
        """Creating csv reports."""
        output_dir = getattr(self.config, 'output_dir')
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        if getattr(self.config, 'one_file'):
            path = os.path.join(output_dir, f'{datetime.now().strftime("%m-%d-%Y")}.csv')
            self._create_csv_one_file_report(self.data, path)
        else:
            for name, data in self.data.items():
                path = os.path.join(output_dir, f'{name}-{datetime.now().strftime("%m-%d-%Y")}.csv')
                self._create_csv_report(data, path)

    def _create_csv_report(self, data: dict, file_path: str):
        """Creating csv report."""
        f = open(file_path, 'w')
        writer = csv.writer(f)
        for k, v in data.items():
            writer.writerow((k, v))
        f.close()

    def _create_csv_one_file_report(self, data: dict, file_path: str):
        """Creating one-file csv report."""
        metrics = ['Repository Name', *[i for i in data.values()][0].keys()]
        f = open(file_path, 'w')
        writer = csv.writer(f)
        writer.writerow(metrics)
        for name, _data in data.items():
            writer.writerow((name, *_data.values()))
        f.close()
