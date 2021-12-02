import abc
import logging
import os
from django.test import TestCase
import yaml
import requests
from bs4 import BeautifulSoup

from board.models import Board, FollowBoard
from board.serializers import FollowBoardSerializer
from job.base_khu_job import BaseKhuJob, BaseKhuException
from job.khu_auth_job import *
from khu_domain.models import Lecture, LectureSuite, Campus, Organization, Department
from user.models import KhumuUser

logger = logging.getLogger(__name__)

# 강의명을 바탕으로 현재 DB에 존재하지 않는 강의(LectureSuite)이 어떤 게 있는지 출력

class KhuLectureCheckJob(KhuAuthJob):
    
    def __init__(self, data: dict):
        super().__init__(data)
    def process(self):
        pass
