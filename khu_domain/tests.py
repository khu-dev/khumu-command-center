from unittest import TestCase

from khu_domain.serializers import LectureSerializer
from khu_domain.views import LectureSuiteViewSet


class LectureSuiteViewSetTest(TestCase):
    def test_this(self):
        view = LectureSuiteViewSet.as_view()  # <-- Changed line
        view.get_queryset()