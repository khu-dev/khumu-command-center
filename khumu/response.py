from rest_framework.response import Response

def BadRequestResponse(message:str=""):
    return Response({
        "status_code": 400,
        "message": message.strip(),
    })

def UnAuthorizedResponse(message:str=""):
    return Response({
        "status_code": 401,
        "message":message.strip(),
    })

def DefaultResponse(data, message="", status=200):
    return Response({
        "data": data,
        "message": message,
    }, status)
