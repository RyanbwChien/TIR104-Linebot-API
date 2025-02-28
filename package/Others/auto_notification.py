from linebot import LineBotApi
from linebot.models import TextSendMessage, TemplateSendMessage, ButtonsTemplate, URITemplateAction
import requests
import schedule
import time
import pymysql
import os
from threading import Thread

# 設置你的 Channel Access Token
CHANNEL_ACCESS_TOKEN = os.getenv('LINE_ACCESS_TOKEN')

def get_env_or_none(var_name, default=None):
    value = os.getenv(var_name, default)
    return None if value == 'None' else value

Line_push_unit = os.getenv('Line_push_unit', 'days')
Line_push_interval = int(os.getenv('Line_push_interval', 1))
Line_push_at = None if os.getenv('Line_push_at', None) == 'None' else str(os.getenv('Line_push_at', None))

def get_user_id():
    db = pymysql.connect(
        host=os.getenv('DB_HOST', 'localhost'),
        user=os.getenv('DB_USER', 'root'),
        password=os.getenv('DB_PASSWORD', 'password'),
        database=os.getenv('DB_NAME', 'linebot'),
        cursorclass=pymysql.cursors.DictCursor
    )
    cursor = db.cursor()
    cursor.execute("SELECT UserID FROM Line_User.Line_Member")
    result = cursor.fetchall()
    cursor.close()
    db.close()
    return [row["UserID"] for row in result]

def push_message(user_id, message, url):
    try:
        # 創建 Buttons Template Message
        buttons_template = TemplateSendMessage(
            alt_text='內政部警政署新聞快訊',
            template=ButtonsTemplate(
                title='⭐️最新詐騙消息⭐️',
                text=message,
                actions=[
                    URITemplateAction(
                        label='查看內文',
                        uri=url
                    )
                ]
            )
        )
        line_bot_api = LineBotApi(CHANNEL_ACCESS_TOKEN)
        # 推播訊息
        line_bot_api.push_message(user_id, buttons_template)
        
        print(f'訊息已成功推播至 {user_id}')
    except Exception as e:
        print(f'推播訊息失敗: {e}')

def auto_notification():
    # 獲取新聞
    news = requests.get('https://165.npa.gov.tw/api/article/list/1').json()
    MESSAGE = (
        news[1]["title"] + "\n"
        "\n" + "🔗 請點擊按鈕查看內文"
    )
    URL = "https://165.npa.gov.tw/#/article/1/" + str(news[1]["id"])
    # 獲取所有用戶 ID
    user_ids = get_user_id()
    # 推送訊息給每個用戶
    # for user_id in user_ids:
    #     push_message(user_id, MESSAGE, URL)
    push_message('Ud08147e96cd51f385dca00d4348a6098', MESSAGE, URL)
    

# # 設定每週一的推播時間
# schedule.every(30).minutes.do(auto_notification)
# a = schedule.every(30)
# a.unit = "hours"

def schedule_task(unit=Line_push_unit, interval=Line_push_interval, at=Line_push_at):
    if at:
        exec(f'schedule.every({interval}).{unit}.at("{at}").do(auto_notification)')
    else:
        exec(f'schedule.every({interval}).{unit}.do(auto_notification)')
    return None

def run_scheduler():
    schedule_task(Line_push_unit, Line_push_interval, Line_push_at)
    while True:
        schedule.run_pending()
        time.sleep(60)  # 每 60 秒檢查一次

# schedule_task(unit=Line_push_unit, interval=Line_push_interval, at=Line_push_at)

# 每分鐘檢查一次是否有排程的任務需要執行
if __name__ == '__main__':
    # job = schedule_task(interval=None, unit='minutes', at=None)
    # job.do(auto_notification)
    # while True:
    #     schedule.run_pending()
    #     time.sleep(1)
    scheduler_thread = Thread(target=run_scheduler, daemon=True)
    scheduler_thread.start()
    

