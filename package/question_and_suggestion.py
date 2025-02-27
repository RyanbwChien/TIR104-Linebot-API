from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.models import TextMessage, MessageEvent
import time
import os
import json
import mysql.connector

access_token = "wg321SFuqFF484DNCLeixtoVK7/ZZdw4xSBvEEZEaEjs3Bw8pH1FeTXztqujFBgEuFdzjzdU/8OoXxcxGSJDcNd9BneVtBUSE/fTBgXwIui7eQeU1PU3zv2T2J/q/q9ZWPXH3q+rabexGm5KuBmiNQdB04t89/1O/w1cDnyilFU="
secret = "1a6e48e115e89280ce72cffbc17e1a43"

line_bot_api = LineBotApi(access_token)
handler = WebhookHandler(secret)

app = Flask(__name__)

@app.route("/", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    
    try:
        handler.handle(body, signature)
    except Exception as e:
        print("Error:", e)
        abort(400)
    return 'OK'


user_feedbacks = {}

@handler.add(MessageEvent, message=TextMessage)
def question_and_suggestion(event):
    user_message = event.message.text
    user_id = event.source.user_id
    timestamp = event.timestamp / 1000.0
    message_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(timestamp))

    if user_message in ["請詳細描述您的問題", "請詳細描述您的建議"]:
        if user_message == "請詳細描述您的問題":
            user_feedbacks[user_id] = "question"

        elif user_message == "請詳細描述您的建議":
            user_feedbacks[user_id] = "suggestion"

    elif user_id in user_feedbacks:
    # 用戶已經選擇過反饋類型，現在等待他們詳細描述問題或建議
        feedback_type = user_feedbacks[user_id]
        
        if feedback_type == "question":
            line_bot_api.reply_message(
                event.reply_token,
                TextMessage(text="謝謝您的問題反饋！我們已收到您的訊息並會儘快處理。"))
            
        elif feedback_type == "suggestion":
            line_bot_api.reply_message(
                event.reply_token,
                TextMessage(text="謝謝您的建議反饋！我們已收到您的訊息。"))

        else:
            line_bot_api.reply_message(
                event.reply_token,
                TextMessage(text="請先選擇反饋類型，點擊「問題反饋」或「建議反饋」。"))

        # 儲存反饋資料
        save_feedback(user_id, user_message, feedback_type, message_time)

        # 完成後清除暫存資料
        del user_feedbacks[user_id]


def get_db_connection():
    connection = mysql.connector.connect(
        host="localhost",        # MySQL 主機
        port=3306,
        user="root",             # MySQL 使用者名稱
        password="password",  # MySQL 密碼
        database="feedback_db"    # 使用的數據庫
    )
    return connection

# 儲存反饋資料
def save_feedback(user_id, user_message, feedback_type, message_time):
    # 連接到 MySQL 數據庫
    connection = get_db_connection()
    cursor = connection.cursor()

     # 插入數據
    query = """
        INSERT INTO feedbacks (user_id, user_message, feedback_type, message_time)
        VALUES (%s, %s, %s, %s)
    """
    data = (user_id, user_message, feedback_type, message_time)

    try:
        cursor.execute(query, data)
        connection.commit()
    except mysql.connector.Error as err:
        print(f"Error: {err}")
    finally:
        cursor.close()
        connection.close()

if __name__ == "__main__":
    app.run(debug=False)

