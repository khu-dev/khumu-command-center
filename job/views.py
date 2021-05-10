import traceback

from rest_framework import status
from rest_framework.views import APIView

from job.khu_lecture_sync import KhuLectureSyncJob
from khumu.permissions import IsAuthenticatedKhuStudent
from rest_framework.response import Response
