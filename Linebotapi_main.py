
import sys
from flask import Flask, request, abort
from linebot.models import MessageEvent, TextMessage, ImageMessage
from linebot import LineBotApi, WebhookHandler
from linebot.models import TextSendMessage
import time
from flask import Flask, request, jsonify
from package import *          # 匯入處理器 
from utils import *
from threading import Thread
import schedule

# from pathlib import Path   
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
            "最新消息",
            "請提出您的問題與建議",                        
            ]

app = Flask(__name__)

def time_fromat(timestamp):
    return(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(timestamp)))

def fetch_answer_and_reply(user_id, event, api_func, sql_connect, table, columns, msgid, user_msg):
    # time.sleep(5)  # 模擬 API 請求延遲
    answer = api_func(event)
    line_bot_api.push_message(user_id, TextSendMessage(text=answer))
    formatted_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
    msgid = msgid + "-1"
    values = (msgid, user_id, user_msg, answer, formatted_time)
    sql_connect.add_data_to_mysqltable(table, columns, values )

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
    timestamp = event.timestamp/1000
    formatted_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(timestamp))
    msgid = event.message.id
    Line_Member_connect = MySQL_Insert_Data()
 
    try:
        Line_Member_connect.add_data_to_mysqltable("Line_Member",("UserID", "Username", "Create_Time"),(user_id, user_name, formatted_time) )
    except Exception as e:
        print(e)

    if user_id not in user_states:
        user_states[user_id] = ""
    user_id = event.source.user_id

    msg = event.message.text
    
    Line_Message_Log_connect = MySQL_Insert_Data()
    reply_sql_connect = Line_Message_Log_connect
    table = "Line_Message_Log"
    columns = ("MsgID", "UserID", "User_Msg", "Sys_Reply_Msg", "Create_Time")
    
    values = (msgid,user_id, msg, "",formatted_time)
    
    
    
    Line_Message_Log_connect.add_data_to_mysqltable(table, columns,values)
    
    Line_Member_Feedback = MySQL_Insert_Data()
    
    
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
            values = (msgid + "-1",user_id, msg, reply,formatted_time)
            Line_Message_Log_connect.add_data_to_mysqltable(table, columns,values)
            line_bot_api.reply_message(event.reply_token, TextMessage(text=reply))



            return jsonify({"status": "ok"}), 200
        if msg == "請直接輸入或轉貼您要詢問的問題":
            user_states[user_id] = "模式4"
            return jsonify({"status": "ok"}), 200
        if msg == "請提出您的問題與建議":
            user_states[user_id] = "模式6"
            return jsonify({"status": "ok"}), 200
 
    else:
        if user_states[user_id] == "模式1":
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text="請稍等，正在處理您的問題..."))
            # reply = Call_Bert_API(event)
            # reply = "回答模式1"
            user_states[user_id] = ""
            Thread(target=fetch_answer_and_reply, args=(user_id, event, Call_Bert_API, reply_sql_connect, table, columns,msgid, msg)).start()
            return jsonify({"status": "ok"}), 200
        
        if user_states[user_id] == "模式4":
            # 先回應使用者，避免 LINE 超時重送
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text="請稍等，正在處理您的問題..."))
            user_states[user_id] = "" 
            # 使用 Thread 在背景執行 API 請求
            Thread(target=fetch_answer_and_reply, args=(user_id, event,Call_RAG_API, reply_sql_connect, table, columns,msgid, msg)).start()
            return jsonify({"status": "ok"}), 200
        
        if user_states[user_id] == "模式6":
            if msg == "請詳細描述您的問題":
                user_states[user_id] = "模式6-1"
                return jsonify({"status": "ok"}), 200
            elif msg == "請詳細描述您的建議":
                user_states[user_id] = "模式6-2"
                return jsonify({"status": "ok"}), 200
            else:
                line_bot_api.reply_message(
                    event.reply_token,
                    TextMessage(text="請先選擇反饋類型，點擊「問題反饋」或「建議反饋」。"))
                
        if user_states[user_id] == "模式6-1":
            user_states[user_id] = ""
            line_bot_api.reply_message(
                event.reply_token,
                TextMessage(text="謝謝您的問題反饋！我們已收到您的訊息並會儘快處理。"))
            
            table = "`Member_Feedbacks`"
            columns = ("UserID", "UserMessage", "FeedbackType", "MessageTime")            
            values = (user_id, msg, "question", formatted_time)            
            Line_Member_Feedback.add_data_to_mysqltable(table, columns,values)
            return jsonify({"status": "ok"}), 200    
                
        if user_states[user_id] == "模式6-2":
            user_states[user_id] = ""
            line_bot_api.reply_message(
                event.reply_token,
                TextMessage(text="謝謝您的建議反饋！我們已收到您的訊息。"))
            table = "`Member_Feedbacks`"
            columns = ("UserID", "UserMessage", "FeedbackType", "MessageTime")            
            values = (user_id, msg, "suggestion", formatted_time)            
            Line_Member_Feedback.add_data_to_mysqltable(table, columns,values)
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
    scheduler_thread = Thread(target=run_scheduler, daemon=True)
    scheduler_thread.start()
    app.run(host='0.0.0.0', port=8080) #host='0.0.0.0', port=8080
