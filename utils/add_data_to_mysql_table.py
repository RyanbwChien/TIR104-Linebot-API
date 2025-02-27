# -*- coding: utf-8 -*-
"""
Created on Sat Feb  8 15:08:12 2025

@author: user
"""
import pymysql
import os

class MySQL_Insert_Data:
    def __init__(self, 
                 host=os.getenv('DB_HOST', 'localhost'), 
                 port=3306, 
                 user=os.getenv('DB_USER', 'root'), 
                 password=os.getenv('DB_PASSWORD', 'password'),
                 database=os.getenv('DB_NAME', 'linebot')):
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.database = database
        self.conn = None
        self.cur = None
    
    def connect_to_DB(self):
        try:
            db_login = {
                'host':self.host,
                'port':self.port,
                "user":self.user,
                "password":self.password,
                "database":self.database,
                "charset": "utf8mb4"
                }
            self.conn = pymysql.connect(**db_login)
            self.cur = self.conn.cursor()
            print("✅ MySQL 連線成功！")
        except pymysql.MySQLError as e:
            print("❌ 無法連線 MySQL：", e)

    def add_data_to_mysqltable(self, table_name:str, column_name:tuple, column_value:tuple)->None:
        
        try:
            self.connect_to_DB()
            column_name_adj = ", ".join( f"`{i}`" for i in column_name)
            placeholders = ", ".join(["%s"] * len(column_name))
            sql_command = f"Insert into {table_name}" + \
                            " " + f"({column_name_adj})" + " " + "values" + \
                            " " + f"({placeholders});"
            
            self.cur.execute(sql_command, column_value)
            
            self.conn.commit()
            self.cur.close()
            self.conn.close()
        except Exception as e:
            print(e)

if __name__ == '__main__':
    mysql_object = MySQL_Insert_Data()
    mysql_object.add_data_to_mysqltable("Line_Member",("UserID", "Username", "Create_Time"),("123","ABC","2025-02-25") )