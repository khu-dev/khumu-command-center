import json
import os

import redis

from khumu import config

redis_client = redis.StrictRedis(host=config.CONFIG['redis']['host'], port=int(config.CONFIG['redis']['port']), db=1)

def publish(obj, channel_name):
    redis_client.publish(channel=channel_name, message=json.dumps(obj))

