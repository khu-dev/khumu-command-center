from django.contrib.auth.models import User, Group
from rest_framework import serializers
from user.models import KhumuUser


class KhumuUserSerializer(serializers.ModelSerializer):

    class Meta:
        model = KhumuUser
        fields = ['pk', 'url', 'is_superuser', 'username', 'nickname',
                  'student_number', 'email', 'groups', 'password', 'memo']

    def create(self, validated_data):
        user = super().create(validated_data)
        user.set_password(validated_data['password'])
        user.save()
        return user

class KhumuUserSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = KhumuUser
        fields = ['username']

class GroupSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Group
        fields = ['url', 'name']
