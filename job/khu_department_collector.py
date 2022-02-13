# data_XXX.py 파일을 이용해 학과 정보를 데이터베이스에 저장한다.

from job import data_2022
from job.khu_auth_job import *
from khu_domain.models import NewOrganization
from khu_domain.models import NewDepartment

logger = logging.getLogger(__name__)

class KhuDepartmentCollectorJob:
    def process(self):
        for major_data in data_2022.major_202210['rows'] + data_2022.major_202215['rows'] + data_2022.major_202220['rows'] + data_2022.major_202225['rows']:
            organizations = NewOrganization.objects.filter(code = major_data['dh'])
            if not organizations:
                print(f'ERROR - {major_data["dh"]}에 해당하는 Organizatoin이 존재하지 않습니다.')
            else:
                organization = organizations.first()
                department = NewDepartment(code=major_data['cd'], name=major_data['nm'], organization=organization)
                exists = NewDepartment.objects.filter(code=department.code).exists()
                if exists:
                    print(f'{department.code} {department.name}은 이미 존재합니다.')
                else:
                    department.save()
                    print(f'{department}을 생성했습니다.')
