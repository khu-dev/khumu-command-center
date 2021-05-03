from comment.models import Comment
from rest_framework import serializers

from khu_domain.models import Department, LectureSuite, Lecture


class OrganizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = ['__all__']

class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = ['__all__']

class LectureSuiteSerializer(serializers.ModelSerializer):
    class Meta:
        model = LectureSuite
        fields = ['__all__']

class LectureSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lecture
        fields = ['__all__']

