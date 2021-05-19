import logging
from django.core.management.base import BaseCommand, CommandError
import yaml
from django.db import transaction

from board.models import Board
from job.migrate_haksa_schedule_job import MigrateHaksaScheduleJob

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = '쿠뮤의 전체적인 초기화 데이터를 구축합니다. DB와 연결되어있는지 확인해주세요~!'

    @transaction.atomic()
    def handle(self, *args, **options):
        f = open('job/data.yaml', "r", encoding='utf8')
        data = yaml.load(f, yaml.SafeLoader)
        for campus in data['campuses']:
            for university in campus['universities']:
                for organization in university['organizations']:
                    for department in organization['departments']:

                        if len(Board.objects.filter(name=department['name'])) > 0:
                            print(department['name'] + "에 대한 게시판이 존재합니다.")
                        else:
                            print(department['name'] + "에 대한 게시판을 생성합니다.")
                            board = Board(
                                name=department['name'],
                                display_name=department['name'],
                                description=f'{organization["name"]}의 {department["name"]}에 대한 게시판입니다.',
                                category='department',
                                related_department_id=department['code']
                            )
                            board.save()

