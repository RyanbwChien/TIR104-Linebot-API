import os
from flask import Flask, request, abort, jsonify
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import *
import pymysql

# @handler.add(PostbackEvent)
# def handle_postback(event):
#     data = event.postback.data
#     if data == 'get_latest_news':
#         reply_latest_news(event)

# @handler.add(MessageEvent, message=TextMessage)
# def handle_message(event):
#     msg = event.message.text
#     if msg == "最新消息":
#         reply_latest_news(event)

def reply_latest_news(event):
    # 從資料庫抓取次數最多的前四名詐騙類型以及其他類型
    db = pymysql.connect(
        host='35.201.141.125',
        user='root',
        password='my-secret-pw',
        database='Anti_Fraud',
        cursorclass=pymysql.cursors.DictCursor
      )
    cursor = db.cursor()
    typeSet = ["1", "3", "5", "12"]
    typeImg = {
        0: "https://i.imgur.com/zNw9Dg1.jpeg",
        1: "https://i.imgur.com/HLayShU.jpeg",
        3: "https://i.imgur.com/mfQmcpS.jpeg",
        5: "https://i.imgur.com/fXl6p9n.jpeg",
        12: "https://i.imgur.com/edzRqdY.jpeg"
    }
    sql=""
    for i in typeSet:
        sql+=f"""(SELECT t.Fraud_type_ID,t.Fraud_type,f.url FROM Fraud_case f 
        INNER JOIN Fraud_classification c 
        ON f.Case_ID = c.Case_ID
        INNER JOIN Fraud_type t 
        ON c.Fraud_type_ID = t.Fraud_type_ID 
        WHERE  c.Fraud_type_ID= {i}
        order by f.Create_time DESC LIMIT 1)UNION
        """
    sql+=f"""
        (SELECT 0 as Fraud_type_ID, '其他' as Fraud_type,f.url FROM Fraud_case f 
        INNER JOIN Fraud_classification c 
        ON f.Case_ID = c.Case_ID
        INNER JOIN Fraud_type t 
        ON c.Fraud_type_ID = t.Fraud_type_ID 
        WHERE  c.Fraud_type_ID NOT IN ({','.join(typeSet)})
        order by f.Create_time DESC LIMIT 1)
        """

    cursor.execute(sql)
    result = cursor.fetchall()
    news_list = []
    for row in result:
      news_list.append({"title": row["Fraud_type"]+"類型詐騙", "url": row["url"], "image_url": typeImg.get(row["Fraud_type_ID"])},)
    cursor.close()
    db.close()


    # 創建多頁訊息
    bubbles = []
    reply = ""
    for news in news_list:
        bubble = BubbleContainer(
            direction='ltr',
            hero=ImageComponent(
                url=news['image_url'],
                size='full',
                aspect_ratio='20:13',
                aspect_mode='cover',
                action=URIAction(uri=news['url'], label='查看內文')
            ),
            body=BoxComponent(
                layout='vertical',
                contents=[
                    TextComponent(text=news['title'], weight='bold', size='lg', margin='md', align='center', gravity='center')
                ]
            ),
            footer=BoxComponent(
                layout='vertical',
                contents=[
                    SeparatorComponent(margin='md'),
                    ButtonComponent(
                        style='link',
                        height='md',
                        action=URIAction(label='查看內文', uri=news['url'])
                    )
                ]
            )
        )
        bubbles.append(bubble)
        reply +=  "url:" + news['image_url'] +'\n'
        # news["title"] +" "+
    carousel = CarouselContainer(contents=bubbles)
    flex_message = FlexSendMessage(alt_text="最新消息", contents=carousel)
    return(flex_message, reply)
    # line_bot_api.reply_message(event.reply_token, flex_message)

