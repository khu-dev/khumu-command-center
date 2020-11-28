import json

from khumu import settings
import logging
logger = logging.getLogger(__name__)

def logging(get_response):
    def middleware(request):
        if settings.DEBUG == True:
            logger.debug(f'user: {request.user}')
            if request.body:
                print(f'body: {request.body}')
        response = get_response(request)
        return response
    return middleware