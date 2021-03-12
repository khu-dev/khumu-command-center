import os
import time
from os import path

from django.test import TestCase

# Create your tests here.
from khu.job.khu_auth_job import KhuAuthJob
import abc
from selenium import webdriver
from khumu.settings import SITE_ROOT
# ref: https://www.selenium.dev/selenium/docs/api/py/
import requests
from bs4 import BeautifulSoup
class JobTest(TestCase):
    # def test_khu_auth_job_test(self):
    #     job = KhuAuthJob()
    #     job.login()

    def test_login(self):
        job = KhuAuthJob()
        job.login({
            'id': os.getenv('KHUMU_INFO21_TEST_ID'),
            'password': os.getenv('KHUMU_INFO21_TEST_PASSWORD')
        })

    def test_after_login_parse(self):
        body_soup = BeautifulSoup(example_user_info_response_html, 'html.parser')
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

    def test_khu_auth_job(self):
        job = KhuAuthJob()
        body = job.login({
            'id': os.getenv('KHUMU_INFO21_TEST_ID'),
            'password': os.getenv('KHUMU_INFO21_TEST_PASSWORD')
        })
        user_info = job.process(body)
        print(user_info)
example_user_info_response_html = '''
<div class="user_box01"><div class="user_img01"><span><img alt="유저사진" src="/common/user/userPhoto.do?id=7d5efbbcc8e0a1160693be14240616d8"></span><!-- <a href="#;" class="btn_img">7</a> --></div><p class="user_text01">박진수</p><p class="user_text02">2016101168&nbsp;( 재학 )</p><p class="user_text03">소프트웨어융합대학&nbsp;컴퓨터공학과</p><!-- 							<p class="user_text04"></p>
--><div class="user_text05"><dl><dt class="lg">이수학기</dt><dd>5</dd></dl><dl><dt class="lg">이수학점</dt><dd>93</dd></dl></div></div><div class="user_box box04 khu_push_div"><dl class="khu_push"><dt class="lg">PUSH알림</dt><dd><a href="#;" id="khutalk1"><!-- <b>PUSH알림</b> --><span>469<b>개</b></span><b>도착하였습니다.</b></a></dd></dl></div><div class="user_btn_w2"><a href=" ../haksa/comm/board/0cd06baca5ccc68f801de6a0b8f0c3d2/index.do" class="btn01 col01" title="매뉴얼게시판" ><span class="icon03">매뉴얼게시판</span></a></div></div></div>
'''