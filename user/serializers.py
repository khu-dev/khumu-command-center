from django.contrib.auth.models import User, Group
from rest_framework import serializers
from user.models import KhumuUser


class KhumuUserSerializer(serializers.ModelSerializer):

    class Meta:
        model = KhumuUser
        exclude = ['password', 'user_permissions']

    def create(self, validated_data):
        user = super().create(validated_data)
        user.set_password(validated_data['password'])
        user.save()
        return user

class KhumuUserSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = KhumuUser
        fields = ['kind', 'username']
    kind = serializers.SerializerMethodField()

    def get_kind(self, user): return 'active'


class GroupSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Group
        fields = ['url', 'name']
