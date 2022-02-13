# info21 인증이 잘 되는지 확인하기 위한 테스트 코드

import os
import traceback
import unittest
from job.khu_auth_job import KhuAuthJob, Info21WrongCredential


class KhuAuthJobTest(unittest.TestCase):
    def test_process_성공(self):
        # 반복 테스트 하려는 경우 loop
        # for trial in range(50):
        for trial in range(1):
            print(f'{trial} th Trial')
            data = {
                'id': os.getenv("KHUMU_INFO21_TEST_ID"),
                'password': os.getenv("KHUMU_INFO21_TEST_PASSWORD"),
            }
            print(data)
            job = KhuAuthJob(data)

            user_info = job.process()
            assert user_info.name == '박진수'
            assert user_info.student_num == '2016101168'

    def test_process_에러_잘못된_credential(self):
        print(os.environ)
        data = {
            'id': os.getenv("KHUMU_INFO21_TEST_ID"),
            'password': 'wrong_pass'
        }
        print(data)
        try:
            job = KhuAuthJob(data)
            job.process()
            self.fail('Info21WrongCredential Exception을 throw해야합니다.')
        except Info21WrongCredential as e:
            pass
        except Exception as e:
            traceback.print_exc()
            self.fail('Info21WrongCredential Exception이 아닌 다른 Exception을 raise 했습니다.')