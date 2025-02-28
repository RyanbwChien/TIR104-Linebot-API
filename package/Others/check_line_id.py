import pymysql
from datetime import datetime
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.models import PostbackAction,URIAction, MessageAction, TemplateSendMessage, ButtonsTemplate


# GCP SQL database connection
host = '35.201.141.125'
port = 3306
user = 'root'
passwd = 'my-secret-pw'
db = 'Anti_Fraud'
charset = 'utf8mb4'


# 查詢 LINE ID
def check_lineID(line_id):
    # Connect to the database
    conn = pymysql.connect(host=host,
                           user=user,
                           passwd=passwd,
                           db=db,
                           charset=charset)
    cursor = conn.cursor()

    # 查詢 LINE ID 是否在資料庫中
    query = "SELECT Searched_count FROM Fraud_Line_ID WHERE Line_ID = %s"
    cursor.execute(query, (line_id,))
    result = cursor.fetchone()

    if result:  
        searched_count = result[0]  # 取得當前的 Searched_count
        new_count = searched_count + 1  # 計算新的查詢次數
        recent_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')  # 取得當前時間

        # 更新 `Searched_count` 和 `Recent_searched_time`
        update_query = """
            UPDATE Fraud_Line_ID 
            SET Searched_count = %s, Recent_searched_time = %s 
            WHERE Line_ID = %s
        """
        cursor.execute(update_query, (new_count, recent_time, line_id))
        conn.commit()  # 提交變更

        print(f"⚠️ 您輸入的為詐騙ID! 請小心! 查詢次數已更新為: {new_count}")
    else:
        print("✅ 您輸入的為安全ID!")

    # 關閉連線
    cursor.close()
    conn.close()
    return result

# Example usage
user_input = input("請輸入 LINE ID: ").strip()
check_lineID(user_input)