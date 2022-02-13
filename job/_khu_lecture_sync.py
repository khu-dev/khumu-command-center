# Deprecated
# 뭐하던 코드인지는 기억 안나지만 어쨌든 강의 크롤링 로직이 변경되면서 필요 없어진 코드인듯

from board.models import Board, FollowBoard
from job.khu_auth_job import *
from khu_domain.models import Lecture, LectureSuite, Campus, Organization, Department
from user.models import KhumuUser

logger = logging.getLogger(__name__)

class KhuLectureSyncJob(KhuAuthJob):
    lectures = []
    def __init__(self, data: dict):
        super().__init__(data)
    def process(self):
        user_info_html = self.login(self.data)
        user = KhumuUser.objects.get(username=self.data['id'])
        lecture_codes = self.get_lecture_codes_registered()
        # lecture_codes = ['CSE301-02', 'CSE327-00', 'CSE406-00', 'CSE335-00', 'APHY1002-16', 'GEB1102-G00', 'GEE1670-G00']
        lecture_suites = LectureSuite.objects.filter(lecture__id__in=lecture_codes)
        print(LectureSuite.objects.filter(lecture__id__in=lecture_codes))
        print(lecture_suites)
        boardsToFollow = Board.objects.filter(category='lecture_suite', related_lecture_suite__in=lecture_suites)
        follows = []
        for board in boardsToFollow:
            follow, is_created = FollowBoard.objects.get_or_create(user=user, board=board)
            logger.info(f'{board.name} 보드에 대한 팔로우를 생성하거나 조회했습니다. is_create={is_created}')
            follows.append(follow)

        # Verify 잘 동작했는지.
        for lecture_suite in lecture_suites:
            if lecture_suite.id not in map(lambda b: b.related_lecture_suite.id, boardsToFollow):
                logger.warning(f'{lecture_suite.id} LectureSuite에 대한 Board가 존재하지 않습니다. Board 목록을 점검해주세요.')

        for board in boardsToFollow:
            if board.name not in map(lambda f: f.board.name, follows):
                logger.warning(f'{board.name} Board에 대한 Follow가 생성되지 않았습니다. 버그를 픽스해주세요.')


    def get_lecture_codes_registered(self):
        r = self.sess.get('https://portal.khu.ac.kr/haksa/clss/clss/atnlReqsDtls/index.do')
        # print(r.text)
        body_soup = BeautifulSoup(r.text, 'html.parser')

        lecture_codes = []
        for row in body_soup.select("table.table.t_list tbody tr"):
            lecture_code_dom = row.select_one('td[data-mb^="학수번호-분반"]')
            # lecture_code_dom이 None이라는 것은 "데이터없음" 을 나타내는 row만 있는 경우임.
            # 예를 들어 나는 재수강표에서는 재수강 수강 내역이 없어서 데이터 없음 행만 나옴.
            if lecture_code_dom:
                lecture_code = lecture_code_dom.text.strip() \
                    .replace('-', '') # 분반코드 없앰. 예를 들어 우리 DB에는 CSE33500로 저장되어있는데 수강 목록에선 CSE335-00으로 조회되기 때문
                lecture_codes.append(lecture_code)
            else:
                pass
        return lecture_codes
