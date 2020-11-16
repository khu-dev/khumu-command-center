from django.contrib.auth.models import Group
from rest_framework import serializers
from user.models import KhumuUser


class KhumuUserSerializer(serializers.ModelSerializer):

    class Meta:
        model = KhumuUser
        fields = '__all__'

    def create(self, validated_data):
        user = super().create(validated_data)
        user.set_password(validated_data['password'])
        user.save()
        return user

class KhumuUserSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = KhumuUser
        fields = ['url', 'state', 'username']

class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ['url', 'name']
