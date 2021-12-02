import logging
import traceback
import json
import requests
from bs4 import BeautifulSoup

from job.base_khu_job import BaseKhuJob, BaseKhuException

logger = logging.getLogger(__name__)

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

class KhuAuthJob(BaseKhuJob):
    # 인증 리다이렉트 되면서 쿠키를 유지할 세션
    sess = None
    logger = logger
    data = {}
    # 인증 작업 도중 오류가 발생할 경우 retry할 횟수
    max_retry = 6
    # 인증 작업 도중 각 step들의 요청 timeout
    each_step_timeout = 2

    def __init__(self, data: dict):
        self.sess = requests.session()
        self.data = data

    def __del__(self):
        self.sess.close()

    def get_logger_prefix(self):
        log_data = {}
        if self.data.get("id", ""):
            log_data['id'] = self.data.get("id", "")
        return str(log_data) + " "

    # Authenticate 작업을 하는 Job을 수행한다.
    def process(self) -> UserInfo:
        user_info = None
        for trial in range(self.max_retry):
            try:
                logger.info(f'{trial} 번째 로그인 시도')
                user_info_html = self.login(self.data)
                user_info = self.parse_user_info(user_info_html)
                logger.info(f'인증 작업 완료. {user_info}')
                # 성공했으면 break
                break
            except (Info21WrongCredential) as e:
                logger.warning(f'올바르지 않은 인포21 계정입니다. id: {self.data.get("id")}')
                raise e
            except Exception as e:
                logger.error(f'ID: {self.data.get("id")}의 유저에 대한 인증 도중 에러 발생')
                traceback.print_exc()
                self.sess.close()
                self.sess = requests.session()
        self.sess.close()
        if user_info is None:
            raise Info21AuthenticationUnknownException("")
        return user_info

    # body_data는 id와 password 필요.
    def login(self, body_data):
        logger.info("인포21 로그인 작업 시작")
        try:
            info21_login_response = self.sess.post("https://info21.khu.ac.kr/com/KsignCtr/loginProc.do", timeout=self.each_step_timeout,
               headers={
                   'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36'
               },
               data={
                'userId': body_data.get('id'),
                'userPw': body_data.get('password'),
                'returnurl': None,
                'portalType': None,
                'retUrl': None,
                'socpsId': "",
                'loginRequest': "",
            }, verify=False)

            soup1 = BeautifulSoup(info21_login_response.text, 'html.parser')
            if info21_login_response.status_code != 200 or soup1.find('title') is not None:
                # 인증이 성공한 경우 title은 None
                # 인증이 실패한 경우 title은 "에러"
                # - 2021.08.20
                logger.error(self.get_logger_prefix() + "인포21 로그인 응답이 200이 아니거나 title이 None이 아닙니다. " + info21_login_response.text)
                raise Info21WrongCredential()


            info21_redirected_encode_response = self.sess.get("https://portal.khu.ac.kr/ksign/index.jsp", verify=False)
            logger.info(self.get_logger_prefix() + "인포21 로그인 리다이렉트 응답 코드" + str(info21_redirected_encode_response.status_code))

            # 옛날엔 여기 redirect 되는 곳에서 올바르지 않은 credential인지 확인할 수 있었는데
            # 이제는 위에서처럼 바로 info21에 로그인 요청 보낼 때 올바르지 않은 credential을 확인함.
            # - 2021.08.20
            if info21_redirected_encode_response.status_code != 200 :
                logger.error(self.get_logger_prefix() + "인포21 로그인 리다이렉트 응답이 200이 아님. " + str(info21_redirected_encode_response.text))
                raise Info21AuthenticationUnknownException()
            soup2 = BeautifulSoup(info21_redirected_encode_response.text, 'html.parser')
            encoded_user_id_elem = soup2.select_one('[name="userId"]')
            if not encoded_user_id_elem:
                logger.error("ID: " + body_data.get('id') + "에 대한 올바르지 않은 ID 혹은 PW 에러")
                raise Info21AuthenticationUnknownException()
            encoded_user_id = encoded_user_id_elem.get('value', "").strip()
            logger.info(self.get_logger_prefix() + "Encoded Username: " + encoded_user_id)

            info21_after_login_response = self.sess.post("https://portal.khu.ac.kr/common/user/loginProc.do", data={
                'userId': encoded_user_id,
                'rtnUrl': '',
                'lang': 'kor'
                }, timeout=self.each_step_timeout, verify=False)
            logger.info(self.get_logger_prefix() + "인포21 로그인 후 응답 코드" + str(info21_after_login_response.status_code))

            if info21_after_login_response.status_code != 200:
                logger.info(info21_after_login_response.text)

            user_info_response = self.sess.get('https://portal.khu.ac.kr/haksa/main/dialog/comInfo.do',
                                               timeout=self.each_step_timeout,
                                               verify=False)
            logger.info(self.get_logger_prefix() + "인포21 user info 응답 코드" + str(user_info_response.status_code))

            if info21_after_login_response.status_code != 200:
                logger.error(self.get_logger_prefix() + "인포21 user info 응답이 200이 아님. " + user_info_response.text)
        except Info21WrongCredential as e:
            raise Info21WrongCredential()
        except Exception as e:
            logger.error(e)
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
            logger.error(e)
            raise Info21LoginParsingException(message="", exception=e)

        return user_info



class Info21WrongCredential(BaseKhuException):
    def __init__(self, exception=None):
        self.message = "잘못된 인포 21 계정 정보이거나 인포21이 올바르게 동작하지 않습니다."
        self.exception = exception

# timeout 과 같이 알 수 없는 이유로 인증이 실패했을 때
class Info21AuthenticationUnknownException(BaseKhuException):
    def __init__(self, message, exception=None):
        self.message = "인포 21 인증이 알 수 없는 이유로 실패했습니다." + message
        self.exception = exception

class Info21LoginWrongHtmlException(Info21AuthenticationUnknownException):
    def __init__(self, message, exception=None):
        self.message = "인포 21 로그인 도중 예상치 못한 HTML 형태로 문제가 발생했습니다." + message
        self.exception = exception

class Info21LoginParsingException(Info21AuthenticationUnknownException):
    def __init__(self, message, exception=None):
        self.message = "인포 21 로그인 도중 올바른 값을 추출해내지 못했습니다." + message
        self.exception = exception

