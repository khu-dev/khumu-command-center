from rest_framework import viewsets, pagination, permissions, views, status, generics
from rest_framework.views import APIView
from khumu.response import UnAuthorizedResponse, BadRequestResponse, DefaultResponse
from adapter.slack.slack import send_feedback

from article.serializers import *

logger = logging.getLogger(__name__)

class SlackFeedbackAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    def post(self, request):
        logger.info(f'전달받은 피드백 데이터: {request.data}')
        result = send_feedback(request.user.username, request.data['content'])
        if result:
            return DefaultResponse(None)
        else:
            return DefaultResponse(None, "알 수 없는 이유로 피드백을 전달하지 못했습니다.", 500)
