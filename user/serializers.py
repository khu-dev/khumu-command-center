import logging

from django.contrib.auth.models import Group
from rest_framework import serializers
from rest_framework.utils import model_meta
from board.models import FollowBoard
from khumu.response import DefaultResponse
from user.models import KhumuUser

logger = logging.getLogger(__name__)

def validate_username(username: str):
    if KhumuUser.objects.filter(username=username).exists():
        raise serializers.ValidationError('해당 ID의 유저가 존재합니다.')

def validate_nickname(nickname: str):
    if KhumuUser.objects.filter(nickname=nickname).exists():
        raise serializers.ValidationError('해당 닉네임의 유저가 존재합니다.')

class KhumuUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = KhumuUser
        fields = '__all__'
        # 기본 validator 끄기. 기본 validator는 에러 메시지가 수정이 안 됨.
        extra_kwargs = {
            'username': {
                'validators': [validate_username]
            },
            'nickname': {
                'validators': [validate_nickname]
            },
            'password': {
                'write_only': True
            }
        }
        # 커스텀하게 업데이트 가능한 필드를 정의하기 위함
        updatable_fields = ['nickname', 'department', 'profile_image'] # state나 kind는 업데이트 불가능하게 하려고.
    groups = serializers.SerializerMethodField()

    # user는 수정 가능한 필드만 수정하도록 커스텀한 KhumuUserSerializer.Meta.updatable_fields을 이용함.
    # 따로 update 메소드를 오버라이드하기 보다는 validator를 추가하는 방식을 이용해 간단히 수정 가능한 필드를 정의할 수 있었다.
    # super().validate(data)는 validated_data를 생성할 때 이용된다.
    # 함수로 validator 정의하는 방법 ref: https://www.django-rest-framework.org/api-guide/validators/#writing-custom-validators
    # 필드 레벨이 아닌 오브젝트 레벨의 validator 정의하는 방법 ref: https://www.django-rest-framework.org/api-guide/serializers/#field-level-validation
    def validate(self, data):
        if self.context['view'].action == 'create':
            pass
        if self.context['view'].action == 'update':
            for key in data.keys():
                if key not in KhumuUserSerializer.Meta.updatable_fields:
                    # error key를 주지 않으면
                    # 에러 메시지가 non_field_errors라는 키에 대한 값으로 전달됨.
                    # ref: https://stackoverflow.com/questions/40202858/django-rest-framework-how-to-set-a-custom-name-form-non-field-errors
                    raise serializers.ValidationError({'not_updatable_field_error': key + "는 수정할 수 없는 필드입니다."})
        return super().validate(data)

    def create(self, validated_data):
        # KhumuUser Instance를 직접 저장하는 것이 아니라
        # Serializer를 통하는 경우는 무조건 student kind로 등록
        # student는 password를 저장할 필요도 없고, 그 때 그 때 Info 21 로그인
        validated_data['kind'] = validated_data.get('kind', 'student')
        user = super().create(validated_data)
        # 지금은 password 사용 안함.
        user.set_password(validated_data['password'])
        user.save()
        logging.info(user.username + '의 초기 게시판으로 자유게시판을 follow 함.')
        follow_board = FollowBoard(user=user, board_id='free')
        follow_board.save()
        return user

    def get_groups(self, obj):
        return list(map(lambda group: {
            "id": group.id,
            "name": group.name,
        }, obj.groups.all()))


class KhumuUserSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = KhumuUser
        fields = ['url', 'state', 'username']

class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ['url', 'name']

