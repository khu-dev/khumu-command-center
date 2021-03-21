import logging

from rest_framework import status
from rest_framework.views import APIView

from job.student_qr_code_job import StudentQrCodeJob
from khumu.response import DefaultResponse
from user.models import KhumuUser

logger = logging.getLogger(__name__)
