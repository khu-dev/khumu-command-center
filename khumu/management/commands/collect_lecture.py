import os

from django.core.management.base import BaseCommand

from job.khu_lecture_collector import KhuLectureCollectorJob


class Command(BaseCommand):
    help = '쿠뮤의 전체적인 초기화 데이터를 구축합니다. DB와 연결되어있는지 확인해주세요~!'

    # def add_arguments(self, parser):
    #     parser.add_argument('poll_ids', nargs='+', type=int)

    def handle(self, *args, **options):

        collector = KhuLectureCollectorJob({
            'id': os.getenv('KHUMU_INFO21_TEST_ID'),
            'password': os.getenv('KHUMU_INFO21_TEST_PASSWORD'),
        }, options['organizations'])
        collector.process()

    def add_arguments(self, parser):
        parser.add_argument('-o', '--organizations', nargs='+', help='<Optional> 전체 단과대가 아닌 특정 단과대만 이용. 단과대 이름을 통해 설정한다. (e.g. 공과대학)', required=False)