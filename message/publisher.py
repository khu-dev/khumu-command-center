import json
import os

import redis

from khumu import config

import boto3
from django.conf import settings
from django.core.serializers.json import DjangoJSONEncoder
from django.forms import model_to_dict
from django.db.models import Model

# 기본적으로 따로 process에 대한 AWS 자격 증명을 부여하진 않음.
# Node나 container 등에 붙은 IAM 이용.
client = boto3.client('sns')

class ExtendedEncoder(DjangoJSONEncoder):
    def default(self, o):

        if isinstance(o, Model):
            return model_to_dict(o)

        return super().default(o)

# ref: https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/sns.html#SNS.Client.publish
def publish(resource_kind:str, event_kind:str, obj):
    print("메시지 발행.", obj)
    response = client.publish(
        TopicArn=settings.SNS['topicArn'],
        Message=json.dumps(obj, cls=ExtendedEncoder),
        # MessageStructure='JSON',
        MessageAttributes={
            'resource_kind': {
                'DataType': 'String',
                'StringValue': resource_kind,
            },
            'event_kind': {
                'DataType': 'String',
                'StringValue': event_kind,
            }
        }
    )

