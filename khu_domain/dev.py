# 그냥 개발용 script

import os
import unittest

from django.test import TestCase
import yaml

# Create your tests here.
from models import Campus, Organization

def khu_domain_init():
    print(os.path.dirname(os.path.realpath(__file__)))
    with open('khu_domain/data.yaml') as f:
        y = yaml.load(f, Loader=yaml.FullLoader)
        for campus in y['campuses']:
            print(campus)
            campus_instance = Campus(id=campus['code'], name=campus['name'])
            campus_instance.save()
            for university in campus['universities']:
                for organization in university['organizations']:
                    organization_instance = Organization(id=organization['code'], name=organization['name'])
                    organization_instance.save()
                    for dept in organization['departments']:
                        # self.parse_user_info(organization['code'], dept['code'])
                        pass
