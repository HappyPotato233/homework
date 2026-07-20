import pymysql

# 1. 建立数据库连接（不指定database）
connect = pymysql.connect(
    host='localhost',
    port=3306,
    user='root',
    password='123456',
    charset='utf8mb4'
)
cursor = connect.cursor()

# ========== 新增：在 test_db 中创建 test_table ==========
# 写法1：先切换数据库，再建表
cursor.execute("USE test_db;")  

# 建表SQL示例（id自增主键，name、age字段）
create_table_sql = """
CREATE TABLE IF NOT EXISTS test_table (
    id INT PRIMARY KEY AUTO_INCREMENT COMMENT '主键ID',
    name VARCHAR(50) NOT NULL COMMENT '姓名',
    age TINYINT COMMENT '年龄',
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='测试数据表';
"""
cursor.execute(create_table_sql)
print("test_db库中的 test_table 数据表创建完成")

# 4. 关闭游标和连接
cursor.close()
connect.close()