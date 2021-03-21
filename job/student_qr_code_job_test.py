import logging
from unittest import TestCase

from job.student_qr_code_job import StudentQrCodeJob
logger = logging.getLogger(__name__)

# django-test로 실행해야한다.
# target은 job.student_qr_code_job_test.TestStudentQrCodeJobTest
class TestStudentQrCodeJobTest(TestCase):
    def test_base64_encode(self):
        job = StudentQrCodeJob()
        # 진수 학번
        self.assertEqual(job.student_number_to_base64_str('2016101168'), 'MjAxNjEwMTE2OA==')

    def test_jinsu_qr_code(self):
        job = StudentQrCodeJob()
        result = job.process('2016101168')

        # 응답은 직접 확인
        print(result)
        self.assertTrue(result.qr_code_str.startswith('KH     '))
