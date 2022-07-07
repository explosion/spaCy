import os
import sys
import json
from datetime import datetime

from slack_sdk.web.client import WebClient

CHANNEL = "#alerts-universe"
SLACK_TOKEN = os.environ.get("SLACK_BOT_TOKEN", "ENV VAR not available!")
DATETIME_FORMAT = "%Y-%m-%dT%H:%M:%SZ"

client = WebClient(SLACK_TOKEN)
github_context = json.loads(sys.argv[1])

event = github_context['event']
pr_title = event['pull_request']["title"]
pr_link = event['pull_request']["patch_url"].replace(".patch", "")
pr_author_url = event['sender']["html_url"]
pr_author_name = pr_author_url.rsplit('/')[-1]
pr_created_at_dt = datetime.strptime(
    event['pull_request']["created_at"],
    DATETIME_FORMAT
)
pr_created_at = pr_created_at_dt.strftime("%c")
pr_updated_at_dt = datetime.strptime(
    event['pull_request']["updated_at"],
    DATETIME_FORMAT
)
pr_updated_at = pr_updated_at_dt.strftime("%c")

blocks = [
    {
      "type": "section",
      "text": {
        "type": "mrkdwn",
        "text": "📣 New spaCy Universe Project Alert ✨"
      }
    },
    {
      "type": "section",
      "fields": [
        {
          "type": "mrkdwn",
          "text": f"*Pull Request:*\n<{pr_link}|{pr_title}>"
        },
        {
          "type": "mrkdwn",
          "text": f"*Author:*\n<{pr_author_url}|{pr_author_name}>"
        },
        {
          "type": "mrkdwn",
          "text": f"*Created at:*\n {pr_created_at}"
        },
        {
          "type": "mrkdwn",
          "text": f"*Last Updated:*\n {pr_updated_at}"
        }
      ]
    }
  ]


client.chat_postMessage(
    channel=CHANNEL,
    text="spaCy universe project PR alert",
    blocks=blocks
)
