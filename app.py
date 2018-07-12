import os, sys

from flask import Flask, request, abort
from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
)

app = Flask(__name__)

# get channel_secret and channel_access_token from your environment variable
channel_secret = os.getenv('LINE_CHANNEL_SECRET', None)
channel_access_token = os.getenv('LINE_CHANNEL_ACCESS_TOKEN', None)
if channel_secret is None:
    print('Specify LINE_CHANNEL_SECRET as environment variable.')
    sys.exit(1)
if channel_access_token is None:
    print('Specify LINE_CHANNEL_ACCESS_TOKEN as environment variable.')
    sys.exit(1)

line_bot_api = LineBotApi(channel_access_token)
handler = WebhookHandler(channel_secret)


@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'


@handler.add(MessageEvent, message=TextMessage)
def message_text(event):
    text = event.message.text
    if text == "ヘルプ":
        reply_message(event,
"""今日の時間割を知りたいときは
\"今日の授業\"
明日の時間割を知りたいときは
\"明日の授業\"
と入力してね!""")

    if text == "今日の授業":
        reply_message(event, "今日の授業はxx")

    if text == "明日の授業":
        reply_message(
            event.reply_token,
            TextSendMessage(text="明日の授業はxx")
        )

def reply_message(event, message):
    line_bot_api.reply_message(
        event.reply_token, [TextSendMessage(text=message)]
    )


if __name__ == "__main__":
    app.run(debug=True)
