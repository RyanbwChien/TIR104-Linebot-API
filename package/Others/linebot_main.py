from flask import Flask, request, abort
import json
import pymysql
from datetime import datetime
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage, PostbackEvent,
    TemplateSendMessage, ButtonsTemplate, PostbackAction, MessageAction, URIAction
)

# Flask 應用程式
app = Flask(__name__)

# 設定你的 LINE Bot 金鑰
LINE_CHANNEL_ACCESS_TOKEN = '7XcEyBLMplC5cT7kgyz0h685YN62nwDiITOQ5rDOTnpLwhPMf+PpnzGQ88ULDENU7yCGTbiI9YSEnCreMJcX41hmgmbeP2lBkSR1qXN/zBFicnwRsUDgnKj6MDL5S6YnEfSwVrwK6SvCCcK8uHMRFwdB04t89/1O/w1cDnyilFU='
LINE_CHANNEL_SECRET = '58ab80c26ee9262a818ba5fef437e23c'

# 建立 LINE Bot 連線
line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

# MySQL 資料庫設定
db_config = {
    "host": "35.201.141.125",
    "user": "root",
    "password": "my-secret-pw",
    "database": "Anti_Fraud",
    "charset": "utf8mb4"
}

# 查詢 LINE ID
def check_lineID(line_id):
    conn = pymysql.connect(**db_config)
    cursor = conn.cursor()
    query = "SELECT Searched_count FROM Fraud_Line_ID WHERE Line_ID = %s"
    cursor.execute(query, (line_id,))
    result = cursor.fetchone()
    if result:
        searched_count = result[0] + 1
        recent_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        update_query = """
            UPDATE Fraud_Line_ID 
            SET Searched_count = %s, Recent_searched_time = %s 
            WHERE Line_ID = %s
        """
        cursor.execute(update_query, (searched_count, recent_time, line_id))
        conn.commit()
        response = f"⚠️ 詐騙 ID! 查詢次數已更新為: {searched_count}"
    else:
        response = "✅ 您輸入的 LINE ID 是安全的!"
    cursor.close()
    conn.close()
    return response

# 查詢電話號碼
def check_phone(user_phone):
    conn = pymysql.connect(**db_config)
    cursor = conn.cursor()
    query = "SELECT Searched_count FROM Fraud_PhoneNumber WHERE PhoneNumber = %s"
    cursor.execute(query, (user_phone,))
    result = cursor.fetchone()
    if result:
        searched_count = result[0] + 1
        recent_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        update_query = """
            UPDATE Fraud_PhoneNumber 
            SET Searched_count = %s, Recent_searched_time = %s 
            WHERE PhoneNumber = %s
        """
        cursor.execute(update_query, (searched_count, recent_time, user_phone))
        conn.commit()
        response = f"⚠️ 詐騙電話! 查詢次數已更新為: {searched_count}"
    else:
        response = "✅ 您輸入的電話號碼是安全的!"
    cursor.close()
    conn.close()
    return response

# 查詢網址
def check_url(user_url):
    conn = pymysql.connect(**db_config)
    cursor = conn.cursor()
    query = "SELECT Searched_count FROM Fraud_Weburl WHERE url = %s"
    cursor.execute(query, (user_url,))
    result = cursor.fetchone()
    if result:
        searched_count = result[0] + 1
        recent_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        update_query = """
            UPDATE Fraud_Weburl 
            SET Searched_count = %s, Recent_searched_time = %s 
            WHERE url = %s
        """
        cursor.execute(update_query, (searched_count, recent_time, user_url))
        conn.commit()
        response = f"⚠️ 詐騙網址! 查詢次數已更新為: {searched_count}"
    else:
        response = "✅ 您輸入的網址是安全的!"
    cursor.close()
    conn.close()
    return response

# 處理 Webhook 事件
@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'

# 處理使用者訊息
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_text = event.message.text.strip()

    if user_text.lower() == "查詢":
        buttons_template = TemplateSendMessage(
            alt_text='請選擇查詢類別',
            template=ButtonsTemplate(
                thumbnail_image_url='https://steam.oxxostudio.tw/download/python/line-template-message-demo.jpg',
                title='請選擇欲查詢類別',
                text='請點選一個選項',
                actions=[
                    PostbackAction(label='LINE ID', data='action=line_id'),
                    PostbackAction(label='電話號碼', data='action=phone'),
                    PostbackAction(label='網址', data='action=url')
                ]
            )
        )
        line_bot_api.reply_message(event.reply_token, buttons_template)
    else:
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text="請輸入 '查詢' 開始查詢"))

# 處理按鈕點擊事件
@handler.add(PostbackEvent)
def handle_postback(event):
    data = event.postback.data

    if data == "action=line_id":
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text="請輸入要查詢的 LINE ID"))
    elif data == "action=phone":
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text="請輸入要查詢的電話號碼"))
    elif data == "action=url":
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text="請輸入要查詢的網址"))

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)


