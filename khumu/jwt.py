import json
import logging

from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView

from job.khu_auth_job import *
from .response import DefaultResponse
from user.models import KhumuUser

logger = logging.getLogger(__name__)

class KhumuJWTSerializer(TokenObtainPairSerializer):

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['nickname'] = user.nickname
        return token

    @classmethod
    def validate(self, attrs):
        authenticate_kwargs = {
            self.username_field: attrs[self.username_field],
            'password': attrs['password'],
        }
        try:
            auth_job = KhuAuthJob()

            user_info = auth_job.process({
                'id': attrs[self.username_field],
                'password': attrs['password']
            })

        except Info21LoginWrongHtmlException as e:
            logger.error(e)
            return {
                'message': e.message
            }
        except Info21LoginParsingException as e:
            logger.error(e)
            return {
                'message': e.message
            }
        except Info21WrongCredential as e:
            logger.error(e)
            return {
                'message': e.message
            }
        if not user_info.verified:
            logger.error('알 수 없는 이유로 info21 로그인에 실패했습니다.')
            return {
                'message': '알 수 없는 이유로 info21 로그인에 실패했습니다.'
            }

        self.user = KhumuUser.objects.get(username=attrs[self.username_field], student_number=user_info.student_num)

        result = {}
        refresh = self.get_token(self.user)

        result['refresh'] = str(refresh)
        result['access'] = str(refresh.access_token)
        return result


class KhumuJWTObtainPairView(TokenObtainPairView):
    serializer_class = KhumuJWTSerializer