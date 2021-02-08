from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView


class KhumuJWTSerializer(TokenObtainPairSerializer):

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        token['nickname'] = user.nickname
        return token


class KhumuJWTObtainPairView(TokenObtainPairView):
    serializer_class = KhumuJWTSerializer