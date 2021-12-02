import json
import logging
import os

import redis

from khumu import config

import boto3
from django.conf import settings
from django.core.serializers.json import DjangoJSONEncoder
from django.forms import model_to_dict
from django.db.models import Model
from botocore.config import Config

logger = logging.getLogger(__name__)

# 기본적으로 따로 process에 대한 AWS 자격 증명을 부여하진 않음.
# Node나 container 등에 붙은 IAM 이용.
boto_config = Config(
    region_name = 'ap-northeast-2'
)
client = boto3.client('sns', config=boto_config)

class ExtendedEncoder(DjangoJSONEncoder):
    def default(self, o):

        if isinstance(o, Model):
            return model_to_dict(o)

        return super().default(o)

# ref: https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/sns.html#SNS.Client.publish
def publish(resource_kind:str, event_kind:str, obj):
    logger.info(f'메시지 발행. {str(obj)}')
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
    logger.info(settings.SNS['topicArn'], response)

