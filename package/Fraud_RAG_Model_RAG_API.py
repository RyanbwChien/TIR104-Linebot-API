import requests
import os
import sys

print(sys.path)
# 讓在執行package資料夾底下py檔案的時候，可以去上一層有utils package資料路徑去找到module

# Python 會自動把執行的 .py 檔案所在的目錄加入 sys.path，所以可以直接 import 同目錄的模組。
# 不會自動包含子資料夾，如果要 import 子資料夾的模組：
# 確保子資料夾有 __init__.py
# 使用 sys.path.append() 手動加入路徑

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# #相對路徑 os.path.join(os.path.dirname(__file__), "..") 加上 ".."，意思是回到 上一層：
# print(os.path.join(os.path.dirname(__file__), ".."))
# #os.path.abspath(...) 會將 ".." 解析成實際的 絕對路徑： 這樣就成功取得了 package 的上一層資料夾，也就是 專案的根目錄。
# print(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from utils.preprocess_text import preprocess_text

rag_api_url = os.getenv("rag_api_url")

# def preprocess_text(text):
#     text = re.sub(r"<br\s*/?>", ". ", text)  # 或者替换为空格
#     text = re.sub(r"\s+", " ", text.strip())  # 清理多余空格 如果有一個以上空白會變成一個空白
#     return text

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
