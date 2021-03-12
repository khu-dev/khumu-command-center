import abc
import requests
from bs4 import BeautifulSoup
from khu.job.job import BaseKhuJob


class KhuAuthJob(BaseKhuJob):
    sess = None

    def __init__(self):
        self.sess = requests.session()

    # body_data는 id와 password 필요.
    def login(self, body_data):
        info21_login_response = self.sess.post("https://info21.khu.ac.kr/com/KsignCtr/loginProc.do", data={
            'userId': body_data.get('id'),
            'userPw': body_data.get('password'),
            'returnurl': None,
            'portalType': None,
            'retUrl': None,
            'socpsId': "",
            'loginRequest': "",
        })
        print(info21_login_response.text)
        if info21_login_response.status_code != 200:
            print(info21_login_response.text)

        info21_redirected_encode_response = self.sess.get("https://portal.khu.ac.kr/ksign/index.jsp")
        print(info21_redirected_encode_response.status_code)
        if info21_redirected_encode_response.status_code != 200:
            print(info21_redirected_encode_response.text)
        soup2 = BeautifulSoup(info21_redirected_encode_response.text, 'html.parser')
        encoded_user_id = soup2.select_one('[name="userId"]').get('value', "").strip()
        print("Encoded Username: ", encoded_user_id)

        info21_after_login_response = self.sess.post("https://portal.khu.ac.kr/common/user/loginProc.do", data={
            'userId': encoded_user_id,
            'rtnUrl': '',
            'lang': 'kor'
        })
        print(info21_after_login_response.status_code)

        if info21_after_login_response.status_code != 200:
            print(info21_after_login_response.text)

        user_info_response = self.sess.get('https://portal.khu.ac.kr/haksa/main/dialog/comInfo.do')
        print(user_info_response.text)
        print(user_info_response.status_code)

        return user_info_response.text

    def process(self, body_html):
        body_soup = BeautifulSoup(body_html, 'html.parser')
        user_box = body_soup.select_one('.user_box01')
        name_raw = user_box.select_one('.user_text01').text.strip()
        student_num_raw = user_box.select_one('.user_text02').text.strip()
        dept_raw = user_box.select_one('.user_text03').text.strip()
        name = name_raw

        # 사이 공백이 &nbsp; 로 표시되어이쏙, 이는 파이썬에서 "\xa0"으로 이용된다.
        student_num = student_num_raw.split("\xa0")[0]
        dept = dept_raw.split("\xa0")[-1]
        print(name)
        print(student_num)
        print(dept)

        result = UserInfo(name, student_num, dept)
        return result

    def result(self):
        pass


class UserInfo:
    name = ""
    student_num = ""
    dept = ""

    def __init__(self, name, student_num, dept):
        self.name = name
        self.student_num = student_num
        self.dept = dept