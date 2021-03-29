import abc
import logging

import requests
from bs4 import BeautifulSoup

from job.base_khu_job import BaseKhuJob, BaseKhuException

logger = logging.getLogger(__name__)

class KhuAuthJob(BaseKhuJob):
    sess = None
    logger = logger
    data = {}

    def __init__(self, data: dict):
        self.sess = requests.session()
        self.data = data

    def get_logger_prefix(self):
        log_data = {}
        if self.data.get("id", ""):
            log_data['id'] = self.data.get("id", "")
        return str(log_data) + " "

    def process(self):
        user_info_html = self.login(self.data)
        user_info = self.parse_user_info(user_info_html)
        return user_info

    # body_data는 id와 password 필요.
    def login(self, body_data):
        try:
            logger.info(self.get_logger_prefix() + '인포21 로그인 시도 ')
            info21_login_response = self.sess.post("https://info21.khu.ac.kr/com/KsignCtr/loginProc.do", data={
                'userId': body_data.get('id'),
                'userPw': body_data.get('password'),
                'returnurl': None,
                'portalType': None,
                'retUrl': None,
                'socpsId': "",
                'loginRequest': "",
            })
            if info21_login_response.status_code != 200:
                logger.error(self.get_logger_prefix() + "인포21 로그인 응답이 200이 아님. " + info21_login_response.text)

            info21_redirected_encode_response = self.sess.get("https://portal.khu.ac.kr/ksign/index.jsp")
            logger.info(self.get_logger_prefix() + "인포21 로그인 리다이렉트 응답 코드" + str(info21_redirected_encode_response.status_code))

            if info21_redirected_encode_response.status_code != 200 :
                logger.error(self.get_logger_prefix() + "인포21 로그인 리다이렉트 응답이 200이 아님. " + str(info21_redirected_encode_response.text))
                raise Info21WrongCredential(" ID: " + body_data.get('id') + " PW: ***")
            soup2 = BeautifulSoup(info21_redirected_encode_response.text, 'html.parser')
            encoded_user_id_elem = soup2.select_one('[name="userId"]')
            if not encoded_user_id_elem:
                raise Info21WrongCredential(" ID: " + body_data.get('id') + " PW: ***")
            encoded_user_id = encoded_user_id_elem.get('value', "").strip()
            logger.info(self.get_logger_prefix() + "Encoded Username: " + encoded_user_id)

            info21_after_login_response = self.sess.post("https://portal.khu.ac.kr/common/user/loginProc.do", data={
                'userId': encoded_user_id,
                'rtnUrl': '',
                'lang': 'kor'
            })
            logger.info(self.get_logger_prefix() + "인포21 로그인 후 응답 코드" + str(info21_after_login_response.status_code))

            if info21_after_login_response.status_code != 200:
                logger.info(info21_after_login_response.text)

            user_info_response = self.sess.get('https://portal.khu.ac.kr/haksa/main/dialog/comInfo.do')
            logger.info(self.get_logger_prefix() + "인포21 user info 응답 코드" + str(user_info_response.status_code))

            if info21_after_login_response.status_code != 200:
                logger.error(self.get_logger_prefix() + "인포21 user info 응답이 200이 아님. " + user_info_response.text)
        except Info21WrongCredential as e:
            raise Info21WrongCredential(" ID: " + body_data.get('id') + " PW: ***")
        except Exception as e:
            raise Info21LoginWrongHtmlException(message="", exception=e)

        return user_info_response.text

    def parse_user_info(self, body_html):
        try:
            body_soup = BeautifulSoup(body_html, 'html.parser')
            user_box = body_soup.select_one('.user_box01')
            name_raw = user_box.select_one('.user_text01').text.strip()
            student_num_raw = user_box.select_one('.user_text02').text.strip()
            dept_raw = user_box.select_one('.user_text03').text.strip()
            name = name_raw

            # 사이 공백이 &nbsp; 로 표시되어이쏙, 이는 파이썬에서 "\xa0"으로 이용된다.

            student_num = student_num_raw.split("\xa0")[0]
            dept = dept_raw.split("\xa0")[-1]

            user_info = UserInfo(name, student_num, dept, True)
            logger.info(user_info)

        except Exception as e:
            raise Info21LoginParsingException(message="", exception=e)

        return user_info

class UserInfo:
    name = ""
    student_num = ""
    dept = ""

    def __init__(self, name, student_num, dept, verified):
        self.name = name
        self.student_num = student_num
        self.dept = dept
        self.verified = verified

    def __str__(self) -> str:
        return f'name: {self.name}, student_num: {self.student_num}, deptartment: {self.dept}, verified: {self.verified}'''
        return super().__str__()

class Info21WrongCredential(BaseKhuException):
    def __init__(self, message, exception=None):
        self.message = "잘못된 인포 21 계정 정보입니다." + message
        self.exception = exception

class Info21LoginWrongHtmlException(BaseKhuException):
    def __init__(self, message, exception=None):
        self.message = "인포 21 로그인 도중 예상치 못한 HTML 형태로 문제가 발생했습니다." + message
        self.exception = exception

class Info21LoginParsingException(BaseKhuException):
    def __init__(self, message, exception=None):
        self.message = "인포 21 로그인 도중 올바른 값을 추출해내지 못했습니다." + message
        self.exception = exception
