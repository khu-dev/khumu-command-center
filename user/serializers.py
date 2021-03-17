import logging

from django.contrib.auth.models import Group
from rest_framework import serializers

from board.models import FollowBoard
from user.models import KhumuUser

logger = logging.getLogger(__name__)

class KhumuUserSerializer(serializers.ModelSerializer):

    class Meta:
        model = KhumuUser
        fields = '__all__'

    def create(self, validated_data):
        # KhumuUser Instance를 직접 저장하는 것이 아니라
        # Serializer를 통하는 경우는 무조건 student kind로 등록
        # student는 password를 저장할 필요도 없고, 그 때 그 때 Info 21 로그인
        validated_data['kind'] = 'student'
        validated_data['password'] = ''
        user = super().create(validated_data)
        # 지금은 password 사용 안함.
        # user.set_password(validated_data['password'])
        # user.save()
        logging.info(user.username + '의 초기 게시판으로 자유게시판을 follow 함.')
        follow_board = FollowBoard(user=user, board_id='free')
        follow_board.save()
        return user

class KhumuUserSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = KhumuUser
        fields = ['url', 'state', 'username']

class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ['url', 'name']
