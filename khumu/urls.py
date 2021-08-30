from django.conf.urls import url
from django.contrib import admin
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from django.http.response import HttpResponseRedirect

from django.urls import include, path, reverse
from rest_framework import routers

import khu_domain
from job import student_qr_code_job
from user import views as userView
from article import views as articleView
from comment import views as commentView
from khu_domain import views as khu_domain_view
from board import views as boardView
from adapter.slack.views import SlackFeedbackAPIView
from .jwt import KhumuJWTObtainPairView

router = routers.DefaultRouter(trailing_slash=False)
# Basename is used for hyperlink
router.register(r'/users', userView.KhumuUserViewSet, basename='khumuuser')
router.register(r'/groups', userView.GroupViewSet, basename='groups')
router.register(r'/boards', boardView.BoardViewSet, basename='board')
router.register(r'/boards/(?P<board_name>[^/.]+)/follows', boardView.FollowBoardViewSet, basename='follow-board')
router.register(r'/articles', articleView.ArticleViewSet, basename='article')
router.register(r'/study-articles', articleView.StudyArticleViewSet, basename='study-article')
router.register(r'/haksa-schedules', khu_domain_view.HaksaScheduleViewSet, basename='haksa-schedule')
# router.register(r'/comments', commentView.CommentViewSet)

urlpatterns = [
    path(r'', lambda req:HttpResponseRedirect("/api")),
    path(r'healthz', include('health_check.urls')),
    path(r'api', include(router.urls)),
    path(r'api/token', KhumuJWTObtainPairView.as_view(), name='token_obtain_pair'),
    path(r'api/token/refresh', TokenRefreshView.as_view(), name='token_refresh'),

    # 나의 QR코드 가져오기
    path(r'api/users/me/qr-code', student_qr_code_job.GetQrCodeInfoView.as_view(), name='get-qr-code'),
    # 내가 수강 중인 강의 목록과 이것 저것을 Sync 맞추기
    path(r'api/users/me/sync', khu_domain_view.KhuSyncAPIView.as_view(), name='khu-sync'),
    path(r'api/articles/<id>/likes', articleView.LikeArticleToggleView.as_view(), name='like-article'),
    path(r'api/articles/<id>/bookmarks', articleView.BookmarkArticleToggleView.as_view(), name='bookmark-article'),
    path(r'api/study-articles/<id>/bookmarks', articleView.BookmarkStudyArticleToggleView.as_view(), name='bookmark-study-article'),
    path(r'api/study-fields', articleView.StudyFieldListView.as_view(), name='study-field'),

    path(r'api/departments', khu_domain_view.DepartmentListView.as_view(), name='departments'),
    path(r'api/lecture-suites', khu_domain_view.LectureSuiteListView.as_view(), name='lecture-suites'),
    path(r'api/organizations', khu_domain_view.OrganizationListView.as_view(), name='organizations'),
    path(r'api/feedbacks', SlackFeedbackAPIView.as_view(), name='slack-feedback'),

    path(r'admin', admin.site.urls),

    path(r'auth', include('rest_framework.urls', namespace='rest_framework')),
]
