import os
import unittest
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

from adapter.slack.slack import send_feedback


class TestSlack(unittest.TestCase):
    def test_send_feedback(self):
        send_feedback("jinsu", "hello, world")
