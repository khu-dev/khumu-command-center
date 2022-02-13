# haksa-XXXX.csv 파일을 DB에 반영합니다.
# 멱등성이 보장됩니다.

import csv

from job.base_khu_job import BaseKhuJob
import yaml

from khu_domain.models import HaksaSchedule
import datetime
from django.db import transaction

class MigrateHaksaScheduleJob(BaseKhuJob):
    def __init__(self, data_file_path:str):
        self.data_file_path = data_file_path

    # 성공안되면 롤백.
    @transaction.atomic
    def process(self):
        f = open(self.data_file_path, "r", encoding='utf8')
        data = csv.DictReader(f, delimiter=',')
        for i, row in enumerate(data):
            starts_at = f'{row["start"][:4]}-{row["start"][4:6]}-{row["start"][6:8]}T00:00:00.000+09:00'
            ends_at = f'{row["end"][:4]}-{row["end"][4:6]}-{row["end"][6:8]}T23:59:59.999+09:00'
            haksa_schedule = HaksaSchedule(
                title=row['title'],
                starts_at=starts_at,
                ends_at=ends_at
            )
            haksa_schedule.save()
            print(haksa_schedule)