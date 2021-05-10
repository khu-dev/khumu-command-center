from django.conf.urls import url
from django.contrib import admin
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from django.http.response import HttpResponseRedirect

from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions

from django.urls import include, path, reverse
from rest_framework import routers

from job import student_qr_code_job
from user import views as userView
from article import views as articleView
from comment import views as commentView
from khu_domain import views as khu_domain_view
from board import views as boardView
from .jwt import KhumuJWTObtainPairView

router = routers.DefaultRouter(trailing_slash=False)
# Basename is used for hyperlink
router.register(r'/users', userView.KhumuUserViewSet, basename='khumuuser')
router.register(r'/groups', userView.GroupViewSet, basename='groups')
router.register(r'/boards', boardView.BoardViewSet, basename='board')
router.register(r'/boards/(?P<board_name>[^/.]+)/follows', boardView.FollowBoardViewSet, basename='follow-board')
router.register(r'/articles', articleView.ArticleViewSet, basename='article')
router.register(r'/article-tags', articleView.ArticleTagViewSet, basename='article-tag')
router.register(r'/lecture-suites', khu_domain_view.LectureSuiteViewSet, basename='lecture-suites')
router.register(r'/organizations', khu_domain_view.OrganizationViewSet, basename='organizations')
# router.register(r'/comments', commentView.CommentViewSet)

schema_view = get_schema_view(
   openapi.Info(
      title="KHUMU command center APIs",
      default_version='v0',
      description='''KHUMU의 대부분의 API를 제공하는 command-center 서버의 API에 대한 문서입니다.
<h3>KHUMU API Documentations</h3>
<ul>
<li><a href='https://api.khumu.jinsu.me/docs/command-center'>command-center</a>: 인증, 유저, 게시판, 게시물, 게시물 좋아요, 게시물 북마크 등 전반적인 쿠뮤의 API</li>
<li><a href='https://api.khumu.jinsu.me/docs/comment/index.html'>comment</a>: 댓글, 댓글 좋아요와 관련된 API</li>
</ul>
''',
      terms_of_service="https://www.google.com/policies/terms/",
      contact=openapi.Contact(email="khumu.dev@gmail.com"),
      license=openapi.License(name="MIT LICENSE"),
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path(r'', lambda req:HttpResponseRedirect("/api")),
    path(r'healthz', include('health_check.urls')),
    path(r'api', include(router.urls)),

    path(r'api/articles/<id>/likes', articleView.LikeArticleToggleView.as_view(), name='like-article'),
    path(r'api/articles/<id>/bookmarks', articleView.BookmarkArticleToggleView.as_view(), name='bookmark-article'),
    path(r'api/article-tags/<tag_name>/follows', articleView.FollowArticleTagView.as_view(), name='follow-article-tag'),
    path(r'admin', admin.site.urls),
    path(r'api/token', KhumuJWTObtainPairView.as_view(), name='token_obtain_pair'),
    path(r'api/token/refresh', TokenRefreshView.as_view(), name='token_refresh'),
    path(r'auth', include('rest_framework.urls', namespace='rest_framework')),
    path(r'api/qr-code', student_qr_code_job.GetQrCodeInfoView.as_view(), name='get-qr-code'),

    url(r'^docs/command-center', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
]
