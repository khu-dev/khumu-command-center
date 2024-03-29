import logging
import os

from django.core.management.base import BaseCommand

from board.models import Board
from job.khu_lecture_collector_new import KhuLectureCollectorNewJob

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = '강의(Lecture 및 Subject)를 정보를 데이터베이스에 저장합니다.'

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        collector = KhuLectureCollectorNewJob(majors=[])
        collector.process()

