from comment.models import Comment
from rest_framework import serializers

from khu_domain.models import Department, LectureSuite, Lecture, Organization, HaksaSchedule


class OrganizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = '__all__'

class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = '__all__'


class LectureSuiteSerializer(serializers.ModelSerializer):
    class Meta:
        model = LectureSuite
        fields = ['id', 'name', 'department', 'organization', 'course_credit', 'school_year']
        read_only_fields = ['organization']
    organization = serializers.SerializerMethodField()
    def get_organization(self, instance: LectureSuite):
        org = Organization.objects.get(department=instance.department)
        simple_org = {'id': org.id, 'name': org.name}
        return simple_org

class LectureSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lecture
        fields = '__all__'

class HaksaScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = HaksaSchedule
        fields = '__all__'