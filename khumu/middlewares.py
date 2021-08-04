import json
import traceback

from khumu import settings
import logging
logger = logging.getLogger(__name__)
from rest_framework.response import Response

from django.http import HttpResponseForbidden, JsonResponse, HttpResponse


def logging(get_response):
    def middleware(request):
        if settings.DEBUG == True:
            logger.debug(f'user: {request.user}')
            if request.body:
                try:
                    tmp_json_body = json.loads(request.body.decode('utf-8'))
                    for key in tmp_json_body:
                        if key.startswith('password'):
                            tmp_json_body[key] = '***'
                    logger.info(f'POST: application/json body: {tmp_json_body}')
                except Exception as e:
                    logger.error("JSON body 출력 로깅 도중 에러 발생")
                    traceback.print_exc()
        response = get_response(request)
        return response
    return middleware

def force_content_type_application_json_on_post(get_response):
    def middleware(request):
        http_method = request.method
        content_type = str(request.META.get('CONTENT_TYPE')) # type assert
        desired_content_types = ['application/json']
        is_desired_content_types = any(content_type.startswith(desired) for desired in desired_content_types)
        if http_method == 'POST' and not is_desired_content_types:
            # return UnsupportedContentTypeResponse(content_type, "application/json")
            resp = {
                "data": None,
                "message": f'Unsupported Content-Type {content_type}. Please try {",".join(desired_content_types)}'
            }
            logger.error(resp)
            return JsonResponse(
                status=400,
                data=resp
            )
        return get_response(request)
    return middleware