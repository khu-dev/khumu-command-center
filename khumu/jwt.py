import json
import logging

from rest_framework import status
from rest_framework.response import Response
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken
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
        auth_job = KhuAuthJob()

        user_info = auth_job.process({
            'id': attrs[self.username_field],
            'password': attrs['password']
        })

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

    # 부모 클래스인 TokenObtainPairView의
    # post 메소드를 override
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        try:
            serializer.is_valid(raise_exception=True)
        except TokenError as e:
            raise InvalidToken(e.args[0])
        # BaseKhuException은 많은 Info21 로그인 관련 Exception들의 부모이며 .message field를 갖는다.
        except BaseKhuException as e:
            return DefaultResponse(data=None, message=e.message, status=401)

        return Response(serializer.validated_data, status=status.HTTP_200_OK)