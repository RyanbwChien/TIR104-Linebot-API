
from flask import Flask, request, abort
from linebot.models import MessageEvent, TextMessage, ImageMessage
from linebot import LineBotApi, WebhookHandler
from linebot.models import TextSendMessage
import time
from flask import Flask, request, jsonify
from package import *          # 匯入處理器   
from threading import Thread   
# import inspect
# import inspect
# # 列出套件內的所有函數
# functions = [name for name, obj in inspect.getmembers( package, inspect.isfunction)]

# print("套件中的函數有：")
# for func in functions:
#     print(func)
import os
access_token = os.getenv("LINE_ACCESS_TOKEN")
secret = os.getenv("LINE_SECRET")

line_bot_api = LineBotApi(access_token)
handler = WebhookHandler(secret)
user_states = {}
link_msg = ["請直接輸入或轉貼要查詢是否為詐騙的訊息", 
            "請直接輸入或轉貼要查詢是否為詐騙的LINE ID、網站或電話（帶+號即為境外來電，請留意）",
            "開啟連結","請直接輸入或轉貼您要詢問的問題",
            "最新消息"]

app = Flask(__name__)

def fetch_answer_and_reply(user_id, even, api_func):
    # time.sleep(5)  # 模擬 API 請求延遲
    answer = api_func(even)
    line_bot_api.push_message(user_id, TextSendMessage(text=answer))

@app.route("/webhook", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']  # 簽名驗證
    body = request.get_data(as_text=True)            # 接收請求的內容

    try:
        handler.handle(body, signature)  # 處理來自 LINE 的請求
    except Exception as e:
        print("Error:", e)
        abort(400)  # 請求失敗返回 400
    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def even(event):
    global user_states
    # 1. 獲取用戶 ID
    user_id = event.source.user_id
    # 2. 獲取用戶名稱
    profile = line_bot_api.get_profile(user_id)
    user_name = profile.display_name
    # 3. 獲取訊息發送時間
    timestamp = event.timestamp / 1000.0
    # formatted_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(timestamp))
    if user_id not in user_states:
        user_states[user_id] = ""
    user_id = event.source.user_id

    msg = event.message.text
    print(msg)

    if msg in link_msg:
        if msg == "請直接輸入或轉貼要查詢是否為詐騙的訊息":
            user_states[user_id] = "模式1"
            return jsonify({"status": "ok"}), 200
        if msg == "最新消息":
            user_states[user_id] = "模式5"
            reply = "內政部統計110年詐騙案件發生情形，依序為「假投資」、「解除分期付款」及「假網拍」3種手法最多"
            user_states[user_id] = "" 
            # return(TextMessage(text=reply))
            line_bot_api.reply_message(event.reply_token, TextMessage(text=reply))
            return jsonify({"status": "ok"}), 200
        if msg == "請直接輸入或轉貼您要詢問的問題":
            user_states[user_id] = "模式4"
            return jsonify({"status": "ok"}), 200
    else:
        if user_states[user_id] == "模式1":
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text="請稍等，正在處理您的問題..."))
            # reply = Call_Bert_API(event)
            # reply = "回答模式1"
            user_states[user_id] = "" 
            Thread(target=fetch_answer_and_reply, args=(user_id, event, Call_Bert_API)).start()
            # line_bot_api.push_message(user_id, TextSendMessage(text=reply))
            # line_bot_api.reply_message(event.reply_token, TextMessage(text=reply))
            return jsonify({"status": "ok"}), 200
        if user_states[user_id] == "模式4":
            # 先回應使用者，避免 LINE 超時重送
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text="請稍等，正在處理您的問題..."))
            user_states[user_id] = "" 
            # 使用 Thread 在背景執行 API 請求
            Thread(target=fetch_answer_and_reply, args=(user_id, event,Call_RAG_API)).start()
            # reply = Call_RAG_API(event)
            # # reply = "回答模式4"
            # user_states[user_id] = "" 
            # line_bot_api.push_message(user_id, TextSendMessage(text=reply))
            # line_bot_api.reply_message(event.reply_token, TextMessage(text=reply))
            return jsonify({"status": "ok"}), 200
    return jsonify({"status": "ok"}), 200

# @handler.add(MessageEvent, message=ImageMessage)
# def even(event):

#     Ryan_image_response_a = Ryan_handle_image_message_a(event, line_bot_api)

    
#     responses = [item for item in [Ryan_image_response_a] if item is not None][0]
#     # 合併回覆訊息
#     if responses == []:
#         return 
#     if responses:
#         line_bot_api.reply_message(event.reply_token, responses)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080) #host='0.0.0.0', port=8080
