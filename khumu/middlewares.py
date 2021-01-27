import json

from khumu import settings
import logging
from django.http import JsonResponse
logger = logging.getLogger(__name__)
from django.http import HttpResponseForbidden
def logging(get_response):
    def middleware(request):
        if settings.DEBUG == True:
            logger.debug(f'user: {request.user}')
            if request.body:
                logger.info(f'POST: application/json body: {request.body}')
        response = get_response(request)
        return response
    return middleware

def force_content_type_multipart_form_data_on_post(get_response):
    def middleware(request):
        http_method = request.method
        content_type = str(request.META.get('CONTENT_TYPE')) # type assert
        desired_content_types = ['application/json']
        is_desired_content_types = any(content_type.startswith(desired) for desired in desired_content_types)
        if http_method == 'POST' and not is_desired_content_types:
            # return UnsupportedContentTypeResponse(content_type, "application/json")
            return JsonResponse({
                "data": None,
                "message": f'Unsupported Content-Type {content_type}. Please try {",".join(desired_content_types)}'
            })
        return get_response(request)
    return middleware