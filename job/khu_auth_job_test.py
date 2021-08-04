import abc
import logging
import os
import unittest

import requests
from bs4 import BeautifulSoup

from job.base_khu_job import BaseKhuJob, BaseKhuException
from job.khu_auth_job import KhuAuthJob


class KhuAuthJobTest(unittest.TestCase):
    def test_khu_auth_job(self):
        for trial in range(50):
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