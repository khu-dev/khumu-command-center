import logging
import os
import traceback
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

from django.conf import settings

logger = logging.getLogger(__name__)

client = WebClient(token=settings.SLACK_BOT_TOKEN)

# 성공한 경우 True, 실패한 경우 False를 return
def send_feedback(username, content) -> bool:
    try:
        response = client.chat_postMessage(channel='#khumu', text="", attachments=[
            {
                "fallback": "Plain-text summary of the attachment.",
                "color": "#2eb886",
                # "pretext": "Optional text that appears above the attachment block",
                # "author_name": "Bobby Tables",
                # "author_link": "http://flickr.com/bobby/",
                # "author_icon": "http://flickr.com/icons/bobby.jpg",
                "title": "새로운 피드백이 작성되었습니다!",
                "text": content,
                "fields": [
                    {
                        "title": "작성자(username)",
                        "value": username,
                        "short": False
                    }
                ],
                # "image_url": "http://my-website.com/path/to/image.jpg",
                # "thumb_url": "http://example.com/path/to/thumb.png",
                # "footer": "Slack API",
                # "footer_icon": "https://platform.slack-edge.com/img/default_application_icon.png",
                # "ts": 123456789
            }
        ])
        logging.info(response)
        return True
    except SlackApiError as e:
        traceback.print_exc()
        # You will get a SlackApiError if "ok" is False
        if not e.response["ok"]:
            print(f"Got an error: {e.response['error']}")
        return False
