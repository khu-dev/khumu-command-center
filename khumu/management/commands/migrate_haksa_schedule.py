import logging
from django.core.management.base import BaseCommand, CommandError



from job.migrate_haksa_schedule_job import MigrateHaksaScheduleJob

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = '쿠뮤의 전체적인 초기화 데이터를 구축합니다. DB와 연결되어있는지 확인해주세요~!'

    # def add_arguments(self, parser):
    #     parser.add_argument('poll_ids', nargs='+', type=int)

    def add_arguments(self, parser):
        parser.add_argument('-f', '--haksa-file', help='학사 일정을 담은 csv 파일의 경로', required=True)


    def handle(self, *args, **options):
        job = MigrateHaksaScheduleJob(options['haksa_file'])
        job.process()