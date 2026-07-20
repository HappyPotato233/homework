import pymysql

#1. 建立数据库连接(此时不指定database)
connect = pymysql.connect(
    host='localhost', 
    port=3306, 
    user='root', 
    password='123456',
    charset='utf8mb4'
)

#2. 获取游标
cursor = connect.cursor()

# 3.创建数据库
sql1 = 'create database if not exists test_db default character set utf8mb4'
sql2 = 'create database if not exists student_db default character set utf8mb4'

cursor.execute(sql1)
print("数据库test_db创建成功")
cursor.execute(sql2)
print("数据库student_db创建成功")

# 4. 关闭游标和连接
cursor.close()
connect.close()