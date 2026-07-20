from venv import create
import pymysql
from pymysql.cursors import DictCursor

# 1. 建立数据库连接
connect = pymysql.connect(
    host='localhost',
    port=3306,
    user='root',
    password='123456',
    charset='utf8mb4'
)
cursor = connect.cursor()

cursor.execute("USE test_db;")



# ===================== CRUD 操作 =====================
try:
    # ---------------------- C Create 新增数据 ----------------------
    insert_sql = "INSERT INTO test_table(name, age) VALUES (%s, %s)"
    # 单条插入
    cursor.execute(insert_sql, ("张三", 20))
    # 批量插入 executemany
    data_list = [("李四", 22), ("王五", 19)]
    cursor.executemany(insert_sql, data_list)
    print(f"新增成功，共插入{cursor.rowcount}条数据")

    # ---------------------- R Read 查询数据 ----------------------
    # 1. 查询全部数据
    cursor.execute("SELECT * FROM test_table;")
    all_data = cursor.fetchall()
    print("\\n==== 全部数据 ====")
    for row in all_data:
        print(row)

    # 2. 根据id单条查询
    cursor.execute("SELECT * FROM test_table WHERE id=%s", (1,))
    one_data = cursor.fetchone()
    print("\\n==== id=1 的单条数据 ====")
    print(one_data)

    # 3. 条件查询（年龄大于20）
    cursor.execute("SELECT name,age FROM test_table WHERE age > %s", (20,))
    filter_data = cursor.fetchall()         
    print("\\n==== 年龄大于20的数据 ====")
    print(filter_data)

    # ---------------------- U Update 修改数据 ----------------------
    update_sql = "UPDATE test_table SET age=%s WHERE name=%s"
    cursor.execute(update_sql, (25, "张三"))    
    print(f"\\n修改成功，影响行数：{cursor.rowcount}")

    # ---------------------- D Delete 删除数据 ----------------------
    delete_sql = "DELETE FROM test_table WHERE id=%s"
    cursor.execute(delete_sql, (3,))    
    print(f"删除成功，影响行数：{cursor.rowcount}")

    # 所有增/改/删执行完成，提交事务永久保存
    connect.commit()

except Exception as e:
    # 出现任何错误，回滚所有操作，防止脏数据
    connect.rollback()
    print("操作出错，已回滚：", e)

finally:
    # 最终再查询一遍，验证结果
    print("\\n==== 操作后最终表数据 ====")
    cursor.execute("SELECT * FROM test_table;")
    print(cursor.fetchall())

    # 关闭资源
    cursor.close()
    connect.close()
    print("\\n数据库连接已关闭")