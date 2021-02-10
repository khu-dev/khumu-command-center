import json

from khumu import settings
import logging
from rest_framework.response import Response
logger = logging.getLogger(__name__)
from django.http import HttpResponseForbidden, JsonResponse, HttpResponse


def logging(get_response):
    def middleware(request):
        if settings.DEBUG == True:
            logger.debug(f'user: {request.user}')
            if request.body:
                logger.info(f'POST: application/json body: {request.body}')
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