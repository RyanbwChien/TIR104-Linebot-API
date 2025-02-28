import pymysql
from datetime import datetime
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.models import TextMessage, MessageEvent

# Database connection details
db_config = {
    "host": "35.201.141.125",
    "user": "root",
    "password": "my-secret-pw",
    "database": "Anti_Fraud",
    "charset": "utf8mb4"
}

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
            print(f"⚠️ 您輸入的可能為詐騙網址!請小心此網站: {matched_list}。查詢次數已更新為: {new_count}")
        else:
            print("✅ 您輸入的為安全網址")
    
    except pymysql.MySQLError as e:
        print("Database error:", e)
    
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

# Example usage
user_input_url = input("Enter a URL: ").strip()
check_url(user_input_url)