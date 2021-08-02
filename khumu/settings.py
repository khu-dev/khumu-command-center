"""
Django settings for khumu project.

Generated by 'django-admin startproject' using Django 3.0.5.

For more information on this file, see
https://docs.djangoproject.com/en/3.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.0/ref/settings/
"""

import os,datetime
from khumu.csrf import CsrfExemptSessionAuthentication
from khumu import config

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '7yrw2(*^f^od8pb8qdfthxg+!p*d-^lu_+wmb4rni6ntrg8@qm'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ["*"]


# Application definition

INSTALLED_APPS = [
    'khu_domain',
    'health_check',
    'rest_framework',
    'user',
    'article',
    'comment',
    'board',
    'khumu',
    'cacheops',
    'corsheaders',
    'drf_yasg',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'khumu.middlewares.logging',
    'khumu.middlewares.force_content_type_application_json_on_post',
]

ROOT_URLCONF = 'khumu.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR + '/' + 'templates']
        ,
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'khumu.wsgi.application'


# Database
# https://docs.djangoproject.com/en/3.0/ref/settings/#databases

DATABASES = config.load_database_config()


# Password validation
# https://docs.djangoproject.com/en/3.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

AUTH_USER_MODEL = 'user.KhumuUser'

REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'khumu.csrf.CsrfExemptSessionAuthentication',
        # 'rest_framework.authentication.SessionAuthentication', # temporarily using CsrfExenot
        'rest_framework.authentication.BasicAuthentication',
    ),
}

SIMPLE_JWT = {
    'USER_ID_FIELD': 'username',
    'SIGNING_KEY': SECRET_KEY,
    'ACCESS_TOKEN_LIFETIME': datetime.timedelta(days=90),
    'REFRESH_TOKEN_LIFETIME': datetime.timedelta(days=1),
    # 'ROTATE_REFRESH_TOKENS': False,
    # 'BLACKLIST_AFTER_ROTATION': True,
    #
    # 'ALGORITHM': 'HS256',
    # 'VERIFYING_KEY': None,
    # 'AUDIENCE': None,
    # 'ISSUER': None,
    #
    # 'AUTH_HEADER_TYPES': ('Bearer',),
    # 'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
}

# 개발용 CORS
CORS_ORIGIN_ALLOW_ALL = True
CORS_ALLOW_CREDENTIALS = True

CORS_ALLOW_METHODS = (
    'DELETE',
    'GET',
    'OPTIONS',
    'PATCH',
    'POST',
    'PUT',
)

CORS_ALLOW_HEADERS = (
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
)


# Internationalization
# https://docs.djangoproject.com/en/3.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Asia/Seoul'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.0/howto/static-files/

STATIC_URL = '/static/'
APPEND_SLASH = False

SITE_ROOT = os.path.dirname(os.path.realpath(__file__))
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'simple': {"format": "[%(name)s] %(message)s"},
        'detailed' : {
            "format": "%(asctime)s %(levelname)s [%(name)s] [%(filename)s:%(lineno)d] - %(message)s"
        }
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'detailed'
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
        'formatter': 'simple'
    },
}

CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379'
    }
}

# CACHEOPS 설정
# 참고: https://github.com/Suor/django-cacheops
# 참고: https://jay-ji.tistory.com/76

if config.CONFIG.get('cache').get('enabled', False):
    CACHEOPS = {
        'board.*': {},  # 앱.모델에 대해서 캐시적용
        'user.*': {},
        'article.*': {},
        'comment.*': {},
    }
    CACHEOPS_LRU = True  # maxmemory-policy: volatile-lru 설정
    CACHEOPS_REDIS = config.CONFIG.get('cache').get('endpoint')
    CACHEOPS_DEFAULTS = {
        'timeout': 60 * 60 * 24 * 3,  # 3일, 1시간 = 60 * 60
        'ops': 'all',  # get, fetch ... 모든 동작 ex) 'ops': 'get' 이러면 get 할 때만 캐시
        'cache_on_save': True  # save()할때 캐시 할건지
    }



SNS = config.CONFIG.get("sns")
NOTIFICATION_SERVICE = config.CONFIG.get("notificationService")
