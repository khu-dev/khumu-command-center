# 데이터베이스의 NewDepartment row들을 참고해
# Subject와 NewLecture을 만들고, 그에 대한 Board(게시판)도 만든다.
from job.khu_auth_job import *
from khu_domain.models import NewDepartment, Subject, NewLecture
from board.models import Board

logger = logging.getLogger(__name__)

class KhuLectureCollectorNewJob():
    '''
    http://sugang.khu.ac.kr/core?attribute=lectListJson&lang=ko&loginYn=N&menu=1&search_div=T&p_major=A10627&p_year=2022&p_term=10&initYn=Y&page=1
    '''
    # 전공 코드
    majors = []
    # 학년도
    year = 2022
    # 학기
    term = 10
    # 페이지
    page = 1
    
    def __init__(self, majors:list):
        self.logger = logger
        self.majors = majors
        if not majors:
            self.majors = NewDepartment.objects.all()

    def process(self):
        for major in self.majors:
            url = f'http://sugang.khu.ac.kr/core?attribute=lectListJson&lang=ko&loginYn=N&menu=1&search_div=T&p_major={major.code}&p_year={self.year}&p_term={self.term}&initYn=Y&page={self.page}'
            r = requests.get(url)
            data = json.loads(r.text)
            for row in data['rows']:
                subjects = Subject.objects.filter(code=row['subjt_cd'], name=row['subjt_name'])
                if not subjects.exists():
                    subject = Subject(name=row['subjt_name'], code=row['subjt_cd'])
                    subject.save()
                    print(f'{subject.code} {subject.name} Subject를 생성했습니다.')
                subject = Subject.objects.filter(code=row['subjt_cd']).first()
                lectures = NewLecture.objects.filter(code=row['lecture_cd'], year=self.year, term=self.term)
                if lectures.exists():
                    print(f'{row["lecture_cd"]} {self.year}-{self.term} Lecture가 이미 존재합니다.')
                else:
                    lecture = NewLecture(code=row['lecture_cd'], subject=subject, name=subject.name, year=self.year, term=self.term, professor=row['teach_na'])
                    lecture.save()
                    print(f'{lecture}을 생성했습니다.')
                boards = Board.objects.filter(display_name=subject.name)
                if boards.exists():
                    print(f'{subject.name} 게시판이 이미 존재합니다.')
                else:
                    board = Board(name=subject.name, display_name=subject.name, description=f'{subject.name} 강의에 대한 게시판입니다.', category='subject', related_subject=subject)
                    board.save()
                    print(f'{board}를 생성했습니다.')


