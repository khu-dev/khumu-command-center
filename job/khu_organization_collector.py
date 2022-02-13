from job import data_2022
from job.khu_auth_job import *
from khu_domain.models import NewOrganization

logger = logging.getLogger(__name__)

class KhuOrganizationCollectorJob:
    def process(self):
        for organization_data in data_2022.daehak_202210['rows'] + data_2022.daehak_202215['rows'] + data_2022.daehak_202220['rows'] + data_2022.daehak_202225['rows']:
            organization = NewOrganization(code=organization_data['cd'], name=organization_data['nm'])
            exists = NewOrganization.objects.filter(code=organization.code).exists()
            if exists:
                print(f'{organization.code} {organization.name}은 이미 존재합니다.')
            else:
                organization.save()
                print(f'{organization}을 생성했습니다.')
