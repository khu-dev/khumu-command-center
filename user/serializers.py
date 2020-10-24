from django.contrib.auth.models import User, Group
from rest_framework import serializers
from khuauth import auth
from user.models import KhumuUser


class KhumuUserSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = KhumuUser
        fields = ['pk', 'url', 'is_superuser', 'username', 'nickname',
                  'student_number', 'email', 'groups', 'password', 'memo']

    def create(self, validated_data):
        print(auth.authenticate(validated_data['username'], validated_data['password']))
        user = super().create(validated_data)
        user.set_password(validated_data['password'])
        user.save()
        return user


class GroupSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Group
        fields = ['url', 'name']
