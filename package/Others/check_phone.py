import re
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
            print(f"⚠️ 您輸入的可能為詐騙電話!請小心此電話: {matched_list}。查詢次數已更新為: {new_count}")
        else:
            print("✅ 您輸入的為安全電話")
    
    except pymysql.MySQLError as e:
        print("Database error:", e)
    
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

# Example usage
user_input_phone = input("Enter a phone number: ").strip()
check_phone(user_input_phone)