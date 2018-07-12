import os, sys

from flask import Flask, request, abort, render_template
from flask_sqlalchemy import SQLAlchemy

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

# Postgresql
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', None)

db = SQLAlchemy(app)

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


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/register", methods=['POST'])
def register():
    name = request.form['name']
    period1 = request.form['1genme']
    period2 = request.form['2genme']
    period3 = request.form['3genme']
    period4 = request.form['4genme']
    sch = Schedule(name, period1, period2, period3, period4)
    db.session.add(sch)
    db.session.commit()
    return render_template("success.html")


class Schedule(db.Model):
    __tablename__ = 'schedules'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    period1 = db.Column(db.String(200), nullable=False)
    period2 = db.Column(db.String(200), nullable=False)
    period3 = db.Column(db.String(200), nullable=False)
    period4 = db.Column(db.String(200), nullable=False)

    def __init__(self, name, period1, period2, period3, period4):
        self.name = name
        self.period1 = period1
        self.period2 = period2
        self.period3 = period3
        self.period4 = period4


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
        reply_message(event, "明日の授業はxx")

    text_splited = ('', '')
    if ' ' in text and len(text.split(' ')) == 2:
        text_splited = text.split(' ')
    elif '　' in text and len(text.split('　')) == 2:
        text_splited = text.split('　')

    if text_splited[0] == "時間割":
        index = int(text_splited[1])
        sch = Schedule.query.filter(Schedule.id==index).all()[0]
        text = f'{sch.name}\n1限目:{sch.period1}\n2限目:{sch.period2}\n3限目:{sch.period3}\n4限目:{sch.period4}'
        reply_message(event, text)



def reply_message(event, message):
    line_bot_api.reply_message(
        event.reply_token, [TextSendMessage(text=message)]
    )


if __name__ == "__main__":
    app.run(debug=True)
