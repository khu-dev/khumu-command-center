import logging
import os

from django.core.management.base import BaseCommand

from board.models import Board
from job.khu_department_collector import KhuDepartmentCollectorJob
from khu_domain.models import LectureSuite

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = '전공부서(Department)을 정보를 데이터베이스에 저장합니다. data_20XX.py 파일이 필요합니다.'

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        collector = KhuDepartmentCollectorJob()
        collector.process()

