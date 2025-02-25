import requests
import re
import os

rag_api_url = os.getenv("rag_api_url")

def preprocess_text(text):
    text = re.sub(r"<br\s*/?>", ". ", text)  # 或者替换为空格
    text = re.sub(r"\s+", " ", text.strip())  # 清理多余空格 如果有一個以上空白會變成一個空白
    return text

def Call_RAG_API(event):

    texts = preprocess_text(event.message.text)
        # FastAPI 伺服器網址（如果在本機運行）
    url = rag_api_url

    # 要發送的 JSON 數據 
    payload = {
        "question": f"{texts}"
    }

    # 設定 Headers，告訴伺服器這是 JSON 格式的請求
    headers = {
        "Content-Type": "application/json"
    }

    # 發送 POST 請求
    response = requests.post(url, json=payload, headers=headers)

    # 印出 API 回應
    print("Status Code:", response.status_code)
    print("Response:", response.json())
    result = response.json()
    answer = result["answer"]
    reply = preprocess_text(answer)
    return(reply)
