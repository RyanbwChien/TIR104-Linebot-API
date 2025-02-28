# -*- coding: utf-8 -*-
"""
Created on Thu Feb  6 16:26:57 2025

@author: user
"""

import openai
# from linebot.models import  TextMessage
import os
import re
from langchain.chat_models import ChatOpenAI
from langchain.chains import RetrievalQA
import os
# from pathlib import Path
# model_path = Path(__file__).parent / "faiss_index_dir"

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
source_folder_name = "RAG/faiss_index_dir/index.faiss"  # GCS 中的資料夾路徑
destination_folder_name = "/tmp/index.faiss"  # 本地下載位置

download_model(bucket_name, source_folder_name, destination_folder_name)

bucket_name = "ryanbwchien"
source_folder_name = "RAG/faiss_index_dir/index.pkl"  # GCS 中的資料夾路徑
destination_folder_name = "/tmp/index.pkl"  # 本地下載位置

download_model(bucket_name, source_folder_name, destination_folder_name)
openai.api_key = os.environ["openai_apikey"]

# RAG
from langchain.vectorstores import FAISS
from langchain.embeddings import HuggingFaceEmbeddings
embeddings = HuggingFaceEmbeddings(model_name="BAAI/bge-base-zh")
# 重新載入 FAISS
db = FAISS.load_local("/tmp", embeddings,allow_dangerous_deserialization=True)

def preprocess_text(text):
    text = re.sub(r"<br\s*/?>", ". ", text)  # 或者替换为空格
    text = re.sub(r"\s+", " ", text.strip())  # 清理多余空格 如果有一個以上空白會變成一個空白
    return text

# 定義運行問答的函數
def run_my_rag(qa, query):
    print(f"Query: {query}\n")
    result = qa.run(query)
    print("\nResult: ", result)
    return(result)


def RAG_Model(event,line_bot_api):

    texts = preprocess_text(event.message.text)
    # embeddings = OpenAIEmbeddings()
    from langchain.prompts.chat import (
        ChatPromptTemplate,
        HumanMessagePromptTemplate,
        SystemMessagePromptTemplate,
    )
    system_template = """Use the following pieces of context to answer the user's question.
    , explain the concept prompt engineering. Keep the explanation short, only a few sentences, and don't be too descriptive.

    ----------------
    {context}"""

    human_template = "{question}"
    from langchain.prompts import PromptTemplate
    messages = [
        SystemMessagePromptTemplate.from_template(system_template),
        HumanMessagePromptTemplate.from_template(human_template),
    ]

    qa_prompt = ChatPromptTemplate.from_messages(messages)
    retriever = db.as_retriever(search_kwargs={'k': 10})

    # def similarity_search_retriever(query, k=10):
    #     return db.similarity_search(query, k=k)
    # 使用 OpenAI Chat 模型
    llm = ChatOpenAI(model="gpt-4o", api_key=os.environ["openai_apikey"])
    qa = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=retriever,
        verbose=False,
        chain_type_kwargs={"verbose": False,"prompt": qa_prompt},

    )

    ### Ask Queries Now
    reply = run_my_rag(qa, texts)
    return(reply)

