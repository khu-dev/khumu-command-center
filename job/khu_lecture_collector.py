import abc
import logging
import os
from unittest import TestCase
import yaml
import requests
from bs4 import BeautifulSoup

from job.base_khu_job import BaseKhuJob, BaseKhuException
from job.khu_auth_job import *
from khu_domain.models import Lecture, LectureSuite, Campus, Organization, Department

logger = logging.getLogger(__name__)

class KhuLectureCollectorJob(KhuAuthJob):

    max_page_for_current_query = None # 매 학과를 쿼리할 때 마다 max_page 설정
    current_page = None
    organizations = None # 제한하고자하는 organization. None이면 다.
    def __init__(self, data: dict, organizations:list):
        super().__init__(data)
        self.logger = logger
        self.organizations = organizations

    def process(self):
        user_info_html = self.login(self.data)
        # manage.py의 command로서 실행할 것이기떄문에 
        # 프로젝트 루트를 기준 위치로 이용한다.
        with open('khu_domain/data.yaml') as f:
            y = yaml.load(f, Loader=yaml.FullLoader)
            for campus in y['campuses']:
                campus_instance, created = Campus.objects.get_or_create(name=campus['name'])
                self.logger.info(f'Campus 생성 or 조회 {campus_instance}')
                for university in campus['universities']:
                    for organization in university['organizations']:
                        # 모든 organization에 대해 쿼리하는 경우와
                        # 인자로 받은 특정 organizations만 쿼리하는 경우
                        if self.organizations == None or \
                                (self.organizations != None and organization['name'] in self.organizations):
                            organization_instance, created = Organization.objects.get_or_create(id=organization['code'], name=organization['name'], campus=campus_instance)
                            self.logger.info(f'Organization 생성 or 조회 {organization_instance}')
                            for dept in organization['departments']:
                                department_instance, created = Department.objects.get_or_create(id=dept['code'], name=dept['name'], organization=organization_instance)
                                self.max_page_for_current_query = 300 # 무한 루프 방지용 겸 초기 맥스값
                                self.current_page = 1
                                while self.current_page <= self.max_page_for_current_query:
                                    # 국제캠, 2021학년도, 1학기, 단과대, 학과
                                    self.logger.info(f'쿼리 시작 2, 2021, 10, {organization["name"] + organization["code"]}, { dept["name"] + dept["code"]}')
                                    self.query(2, 2021, 10, organization['code'], dept['code'])
                                    self.current_page += 1



    def query(self, campus_id:int, year:int, semester_code:int, org_code:str, dept_code:str):
        r = self.sess.post('https://portal.khu.ac.kr/haksa/clss/clss/totTmTbl/index.do', data={
            "currentPageNo": self.current_page,
            # "corseCode": None, # 컴퓨터공학과, 컴퓨터공학과(소프트웨어) 와 같이 불필요한 정보이므로 생략
            "searchSyy": year,
            "searchSemstCode": semester_code,
            "searchCampsSeCode": campus_id,
            "searchUnivGdhlSeCode": "A10081", # 학부 과정 ( 대학원 X)
            "searchOrgnzCode": org_code,
            "searchDeprtCode": dept_code,
            # 전공부서 내의 전공은 불필요..
            # "searchMajorCode": "A07308",
            "searchSupdcSeCode": "2",
            # "searchEnglCorseSeCode": None,
            # "searchDaywCode": None,
            # "searchBeginHm": "0600",
            # "searchEndHm": "2330",
            # "searchAtnlcHy": "",
            # "searchPersNm": "",
        })
        body_soup = BeautifulSoup(r.text, 'html.parser')

        # 예시
        # 총 게시물 113 페이지 1 / 15
        page_raw_text = body_soup.select_one('ul.tab_bottom').text.strip()
        max_page = int(page_raw_text[page_raw_text.find('/') + 1:])
        self.max_page_for_current_query = max_page
        self.logger.info(f'max_page update:  {self.max_page_for_current_query}')

        for elem in body_soup.select('tbody>tr'):
            td_list = elem.select('td')
            try:
                school_year = int(td_list[1].text.strip() if td_list[1].text.strip() else 0)
                lecture_code = td_list[2].text.strip()
                lecture_kind = td_list[3].text.strip()
                name = td_list[4].text.strip()
                # is_english_lecture = td_list[5]
                remark = td_list[6].text.strip() # 특이사항
                # is_abeek = td_list[7].text.strip()
                course_credit = int(td_list[8].text.strip() if td_list[8].text.strip() else 0)
                professor = td_list[9].text.strip()

                if lecture_code == "":
                    print("수업이 2일 이상 있는 경우. 우선 현재의 기능에서는 패스...")
                else:
                    lecture_suite,created = LectureSuite.objects.get_or_create(name=name, department_id=dept_code, school_year=school_year, course_credit=course_credit)
                    self.logger.info(f'LectureSuite 생성 or 조회 {lecture_suite}')
                    lecture, created = Lecture.objects.get_or_create(id=lecture_code, name=name, lecture_suite_id=lecture_suite.id, professor=professor)
                    self.logger.info(f'Lecture 생성 or 조회 {lecture}')
            except Exception as e:
                self.logger.warning(e)
                self.logger.warning('자료가 존재하지 않는 경우이거나 알 수 없는 오류가 발생했습니다.')
                self.logger.warning(td_list)
