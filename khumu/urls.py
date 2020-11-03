from django.contrib import admin
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from django.http.response import HttpResponseRedirect

from django.urls import include, path, reverse
from rest_framework import routers
from user import views as userView
from article import views as articleView
from comment import views as commentView
from board import views as boardView


router = routers.DefaultRouter()
# Basename is used for hyperlink
router.register(r'users', userView.KhumuUserViewSet, basename='khumuuser')
router.register(r'groups', userView.GroupViewSet)
router.register(r'articles', articleView.ArticleViewSet, basename='article')
router.register(r'comments', commentView.CommentViewSet)
router.register(r'boards', boardView.BoardViewSet, basename='board')

urlpatterns = [
    path(r'', lambda req:HttpResponseRedirect("/api")),
    path('healthz', include('health_check.urls')),
    path('api/', include(router.urls)),
    path('admin/', admin.site.urls),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/', include('rest_framework.urls', namespace='rest_framework'))
    # path('api/blog/', include('blog.urls'))
]
