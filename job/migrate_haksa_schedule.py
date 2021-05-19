import csv

from job.base_khu_job import BaseKhuJob
import yaml

class MigrateHaksaSchedule(BaseKhuJob):
    def process(self, data):
        f = open("haksa-2021.csv", "r", encoding='utf8')
        data = csv.reader(f)
        for row in data:
            print(row)