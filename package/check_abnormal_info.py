import pymysql
from datetime import datetime
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.models import PostbackAction,URIAction, MessageAction, TemplateSendMessage, ButtonsTemplate
import re
import os

# GCP SQL database connection
db_config = {
    "database": "Anti_Fraud",
    "charset": "utf8mb4",
    "host": os.getenv('DB_HOST', 'localhost'),
    "user": os.getenv('DB_USER', 'root'),
    "password": os.getenv('DB_PASSWORD', 'password') 
   
}



# 查詢 LINE ID
def check_lineID(line_id):
    # Connect to the database
    conn = pymysql.connect(**db_config)
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
        text = f"⚠️ 您輸入的為詐騙ID! 請小心! 查詢次數已更新為: {new_count}"
        print(text)
        answer = text
    else:
        text = "✅ 您輸入的為安全ID!"
        print("✅ 您輸入的為安全ID!")
        answer = text
    

    # 關閉連線
    cursor.close()
    conn.close()
    return answer


def normalize_phone(user_phone):
    """移除電話號碼中的 `+` 或 `00` 開頭的國際區號，統一格式"""
    return re.sub(r'^[+0]+', '', user_phone)  # 移除開頭的 `+` 或 `00`

def check_phone(user_phone):
    try:
        # Connect to MySQL
        conn = pymysql.connect(**db_config)
        cursor = conn.cursor()

        # Fetch all stored phone numbers
        cursor.execute("SELECT PhoneNumber, Searched_count FROM Fraud_PhoneNumber")  
        stored_phones = {row[0]: row[1] for row in cursor.fetchall()}  # 轉成字典 {PhoneNumber: Searched_count}

        # 標準化使用者輸入的電話號碼
        normalized_user_phone = normalize_phone(user_phone)

        matched_numbers = []  # 紀錄匹配到的詐騙電話

        for stored_phone, count in stored_phones.items():
            if normalized_user_phone in stored_phone:
                matched_numbers.append((stored_phone, count))

        if matched_numbers:
            for stored_phone, count in matched_numbers:
                new_count = count + 1  # 更新查詢次數
                recent_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')  # 取得當前時間

                # 更新 `Searched_count` 和 `Recent_searched_time`
                update_query = """
                    UPDATE Fraud_PhoneNumber 
                    SET Searched_count = %s, Recent_searched_time = %s 
                    WHERE PhoneNumber = %s
                """
                cursor.execute(update_query, (new_count, recent_time, stored_phone))

            conn.commit()  # 提交變更
            
            matched_list = ", ".join([num[0] for num in matched_numbers])
            text = f"⚠️ 您輸入的可能為詐騙電話!請小心此電話: {matched_list}。查詢次數已更新為: {new_count}"
            print(text)
            answer = text
            
            
        else:
            text = "✅ 您輸入的為安全電話"
            print(text)
            answer = text
    
    except pymysql.MySQLError as e:
        print("Database error:", e)
    
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
    return answer


def check_url(user_url):
    try:
        # Connect to MySQL
        conn = pymysql.connect(**db_config)
        cursor = conn.cursor()

        # Fetch all stored URLs and their search counts
        cursor.execute("SELECT url, Searched_count FROM Fraud_Weburl")  
        stored_urls = {row[0]: row[1] for row in cursor.fetchall()}  # 轉成字典 {url: Searched_count}

        matched_urls = []  # 紀錄匹配的詐騙網址

        for stored_url, count in stored_urls.items():
            if stored_url in user_url:
                matched_urls.append((stored_url, count))

        if matched_urls:
            for stored_url, count in matched_urls:
                new_count = count + 1  # 更新查詢次數
                recent_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')  # 取得當前時間

                # 更新 `Searched_count` 和 `Recent_searched_time`
                update_query = """
                    UPDATE Fraud_Weburl 
                    SET Searched_count = %s, Recent_searched_time = %s 
                    WHERE url = %s
                """
                cursor.execute(update_query, (new_count, recent_time, stored_url))

            conn.commit()  # 提交變更
            
            matched_list = ", ".join([url[0] for url in matched_urls])
            text = f"⚠️ 您輸入的可能為詐騙網址!請小心此網站: {matched_list}。查詢次數已更新為: {new_count}"
            print(text)
            answer = text
        else:
            text = "✅ 您輸入的為安全網址"
            print(text)
            answer = text
    
    except pymysql.MySQLError as e:
        print("Database error:", e)
    
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
    return answer

if __name__ == '__main__':
    # Example usage
    user_input = input("請輸入 LINE ID: ").strip()
    check_lineID(user_input)
    
    # Example usage
    user_input_phone = input("Enter a phone number: ").strip()
    check_phone(user_input_phone)
    
    # Example usage
    user_input_url = input("Enter a URL: ").strip()
    check_url(user_input_url)