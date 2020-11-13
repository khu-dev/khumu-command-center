from rest_framework.response import Response
def BadRequestResponse(message:str=""):
    return Response({
        "status_code": 400,
        "message": ("Bad request. " + message).strip(),
    })

def UnAuthorizedResponse(message:str=""):
    return Response({
        "status_code": 401,
        "message": ("Unauthorized request. " + message).strip(),
    })

def DefaultResponse(status_code, data, message=""):
    return Response({
        "status_code": status_code,
        "data": data,
        "message": message,
    })