import abc
import logging

import requests
from bs4 import BeautifulSoup
from base64 import b64encode

from rest_framework import status
from rest_framework.views import APIView

from job.base_khu_job import BaseKhuJob, BaseKhuException
from khumu.response import DefaultResponse
from user.models import KhumuUser

logger = logging.getLogger(__name__)

class StudentQrCodeJob(BaseKhuJob):
    sess = None

    # xml value에 붙는 Prefix와 Suffix
    PREFIX = '<![CDATA['
    SUFFIX = ']]>'

    def __init__(self):
        self.sess = requests.session()

    def process(self, student_number):
        logger.info(student_number + "의 QR 코드 인증 시작")
        body_xml = self.query_student(student_number)
        qr_code_str = self.parse_query_student_response(body_xml)
        return qr_code_str

    # body_data는 id와 password 필요.
    def query_student(self, student_number):
        student_query_response = self.sess.post('http://163.180.98.69/mobile/MAN/xml_userInfo.php',
                                                headers={'Content-Type': 'application/x-www-form-urlencoded'},
                                                data={
                                                    'real_id': self.student_number_to_base64_str(student_number),
                                                    'devide_gb': 'A',
                                                    'campus_gb': 'K',
                                                })

        if student_query_response.status_code != 200:
            raise QrCodeUnsuccessfulStatusException()
        # encoding이 utf가 아닌 경우에는 한글로 str화하면 깨지기 때문에 인코딩을 설정해준다.
        student_query_response.encoding = 'utf-8'

        return student_query_response.text



    def parse_query_student_response(self, body_xml):
        soup = BeautifulSoup(body_xml, 'html.parser')
        student_number = soup.select_one('user_code').text.strip()
        if not student_number:
            raise QrCodeWrongResponseException()
        dept_name = soup.select_one('user_deptName').text.encode('utf-8').decode('utf-8').strip()
        qr_code_str = soup.select_one('qr_code').text.strip()

        logger.info("응답: " + student_number + dept_name + qr_code_str)

        result = QrCodeInfo(qr_code_str)
        return result

    def student_number_to_base64_str(self, student_number:str):
        return b64encode(student_number.encode('utf-8')).decode('utf-8')

    def extract_value(self, v:str):
        if not (v.startswith(self.PREFIX) and v.endswith(self.SUFFIX)):
            raise QrCodeWrongResponseException()

        return v[len(self.PREFIX):len(v) - len(self.SUFFIX)].strip()

class GetQrCodeInfoView(APIView):
    def get(self, request, format=None, *args, **kwargs):
        logger.info(kwargs)
        user = KhumuUser.objects.filter(username=kwargs.get('id')).first()
        job = StudentQrCodeJob()
        qr_code_info = job.process(user.student_number)
        return DefaultResponse(data=qr_code_info, status=status.HTTP_200_OK)

class QrCodeInfo(dict):
    def __init__(self, qr_code_str):
        self.qr_code_str = qr_code_str
        dict.__init__(self, qr_code_str=qr_code_str)

class QrCodeWrongCredentialException(BaseKhuException):
    def __init__(self, message, exception=None):
        self.message = "올바른 학번을 입력해주세요." + message
        self.exception = exception

class QrCodeUnsuccessfulStatusException(BaseKhuException):
    def __init__(self, message, exception=None):
        self.message = "QR 코드 제공 서버와 통신할 수 없습니다." + message
        self.exception = exception

class QrCodeWrongResponseException(BaseKhuException):
    def __init__(self, message, exception=None):
        self.message = "QR 코드 서버의 응답이 올바르지 않습니다." + message
        self.exception = exception