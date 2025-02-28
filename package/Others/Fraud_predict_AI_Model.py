# -*- coding: utf-8 -*-
"""
Created on Thu Feb  6 16:26:57 2025
@author: user
"""
import re
import torch
import torch.nn.functional as F
from google.cloud import storage

# from pathlib import Path
# model_path = Path(__file__).parent / "TIR104_G1_Fraud_Classification_text.pth"

def download_model(bucket_name, source_blob_name, destination_file_name):
    client = storage.Client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(source_blob_name)
    blob.download_to_filename(destination_file_name)
    print(f"Model downloaded to {destination_file_name}")

bucket_name = "ryanbwchien"
source_blob_name = "Fraud_predict_AI_Model/TIR104_G1_Fraud_Classification_text.pth"
destination_file_name = "/tmp/model.pth"

download_model(bucket_name, source_blob_name, destination_file_name)

model2 = torch.load(destination_file_name,map_location=torch.device('cpu'),weights_only=False)
from transformers import BertTokenizer
tokenizer = BertTokenizer.from_pretrained("bert-base-chinese")

def preprocess_text(text):
    text = re.sub(r"<br\s*/?>", ". ", text)  # 或者替换为空格
    text = re.sub(r"\s+", " ", text.strip())  # 清理多余空格 如果有一個以上空白會變成一個空白
    return text

def transformers_LLM_Model(event):

    texts = preprocess_text(event.message.text)

    tokens = tokenizer(
        texts,                      # 输入文本
        padding=True,                # 填充样本
        truncation=True,             # 超过 max_length 截断
        max_length=512,              # 最大长度限制
        return_tensors="pt"          # 返回 PyTorch 张量
    )

    input_ids = tokens["input_ids"]    # Token IDs shape: (batch_size, seq_length)
    attention_mask = tokens["attention_mask"]  # Attention mask shape: (batch_size, seq_length
    
    model2.eval()
    outputs = model2(input_ids, attention_mask=attention_mask)
    prob = F.softmax(outputs.logits, dim=1)[0][1]*100

    match prob:
        case prob if prob <= 35:
            risk_assessment = "該訊息風險較低，但請保持警覺，避免提供個人敏感資料。"
        case prob if prob > 35 and prob <= 55:
            risk_assessment = "該訊息風險為中度，可能包含詐騙元素，請小心處理。"
        case prob if prob > 55 and prob <= 70:
            risk_assessment = "該訊息判定為中高風險詐騙，請提高警惕並避免任何回應。"
        case prob if prob > 70 and prob < 85:
            risk_assessment = "這是一則高風險詐騙訊息，千萬提高警覺！"
        case prob if prob >= 85:
            risk_assessment = "這是一則極高風險的詐騙訊息，請勿回應或點擊任何連結"
    
    reply = f"詐騙機率是{prob:.2f}%，{risk_assessment}"
    return(reply)
