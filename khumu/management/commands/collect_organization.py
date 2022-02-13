import logging
import os

from django.core.management.base import BaseCommand

from board.models import Board
from job.khu_organization_collector import KhuOrganizationCollectorJob
from khu_domain.models import LectureSuite

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = '대학(Organization)을 정보를 데이터베이스에 저장합니다. data_20XX.py 파일이 필요합니다.'

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        collector = KhuOrganizationCollectorJob()
        collector.process()

