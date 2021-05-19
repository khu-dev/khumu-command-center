import logging
import os

from django.core.management.base import BaseCommand

from board.models import Board
from job.khu_lecture_collector import KhuLectureCollectorJob
from khu_domain.models import LectureSuite

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = '쿠뮤의 전체적인 초기화 데이터를 구축합니다. DB와 연결되어있는지 확인해주세요~!'

    # def add_arguments(self, parser):
    #     parser.add_argument('poll_ids', nargs='+', type=int)

    def add_arguments(self, parser):
        parser.add_argument('-o', '--organizations', nargs='+', help='<Optional> 전체 단과대가 아닌 특정 단과대만 이용. 단과대 이름을 통해 설정한다. (e.g. 공과대학)', required=False)

    def handle(self, *args, **options):
        collector = KhuLectureCollectorJob({
            'id': os.getenv('KHUMU_INFO21_TEST_ID'),
            'password': os.getenv('KHUMU_INFO21_TEST_PASSWORD'),
        }, options['organizations'])
        collector.process()

        self.create_lecture_boards()

    def create_lecture_boards(self):
        lecture_suites = LectureSuite.objects.all()
        for lecture_suite in lecture_suites:
            if len(Board.objects.filter(display_name__exact=lecture_suite.name)) > 0:
                logger.info(f'{lecture_suite.name}에 대한 게시판이 존재합니다.')
            else:
                board = Board(
                    name=lecture_suite.name,
                    display_name=lecture_suite.name,
                    description =f'{lecture_suite.name}에 대한 게시판입니다.',
                    category='lecture_suite',
                    related_lecture_suite=lecture_suite,
                )
                board.save()
                logger.info(f'{lecture_suite.name} LectureSuite에 대한 Board를 생성했습니다.')
