import re

def preprocess_text(text):
    text = re.sub(r"<br\s*/?>", ". ", text)  # 或者替换为空格
    text = re.sub(r"\s+", " ", text.strip())  # 清理多余空格 如果有一個以上空白會變成一個空白
    return text
