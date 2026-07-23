from flask import Flask, request, jsonify, session
from datetime import datetime
import secrets
from functools import wraps
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text
from sqlalchemy.orm import sessionmaker, declarative_base
from enum import Enum
from werkzeug.security import generate_password_hash, check_password_hash
import os
'''
    ==========================后端处理==========================
'''
# 创建数据库引擎（使用绝对路径，确保数据库在代码文件同一目录下）
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'cms.db')
engine = create_engine(f'sqlite:///{DB_PATH}', echo=False)
# 创建模型基类
Base = declarative_base()
# 创建数据库会话
Session = sessionmaker(bind=engine)

# 新闻数据表
class News(Base):
    __tablename__ = 'news'
    id = Column(Integer, primary_key=True, autoincrement=True,comment='新闻ID')
    title = Column(String(255), nullable=False,comment='新闻标题')
    content = Column(Text, nullable=False,comment='新闻内容')
    category = Column(String(100), nullable=False, default='公司动态', comment='新闻分类')
    publish_time = Column(DateTime, default=datetime.now,comment='发布时间')

# 管理员信息表
class Admin(Base):
    __tablename__ = 'admin'
    id = Column(Integer, primary_key=True, autoincrement=True,comment='管理员ID')
    username = Column(String(255), nullable=False, unique=True,comment='管理员用户名')
    password = Column(String(255), nullable=False,comment='管理员密码')
    create_time = Column(DateTime, default=datetime.now,comment='创建时间')

# 公司简介表
class Introduction(Base):
    __tablename__ = 'introduction'
    id = Column(Integer, primary_key=True, autoincrement=True,comment='公司简介ID')
    content = Column(Text, nullable=False,comment='公司简介内容')
    create_time = Column(DateTime, default=datetime.now,comment='创建时间')

Base.metadata.create_all(engine)

class OptionType(Enum):
    NEWS = 1
    INTRODUCTION = 2
    ADMIN = 3
# 利用数据库工具类操作数据库
'''
    数据库工具类
    作用：封装数据库操作方法，提供统一的接口
'''
class DBUtils:
    '''
        构造方法
        作用：初始化数据库会话对象
    '''
    def __init__(self):
        self.db = Session()
    '''
        析构方法
        作用：关闭数据库会话
    '''
    def close(self):
        self.db.close()
    '''
        提交新闻或公司简介或管理员账号数据方法（目前只实现提交新闻）
        作用：通过输入的操作类型批量提交数据
        参数:
            data: 要添加的数据列表，每个元素是一个字典，包含操作类型和数据
            option: 操作类型枚举值，指定要添加的内容类型
    '''
    def add_data(self, data: list[dict],option: OptionType):
        match option:
            case OptionType.NEWS: 
                try:
                    for item in data:
                        self.db.add(News(title=item['title'], 
                                         content=item['content'], 
                                         category=item.get('category', '公司动态'), 
                                         publish_time=datetime.now()))
                except Exception as e:
                    self.db.rollback()
                    return {"code": 500, "msg": str(e)}
                self.db.commit()
                return {"code": 200, "msg": "新闻添加成功"}
            case OptionType.INTRODUCTION:
                try:
                    for item in data:
                        self.db.add(Introduction(content=item['content']))
                except Exception as e:
                    self.db.rollback()
                    return {"code": 500, "msg": str(e)}
                self.db.commit()
                return {"code": 200, "msg": "公司简介添加成功"}
            case OptionType.ADMIN:
                try:
                    for item in data:
                        self.db.add(Admin(username=item['username'], password=generate_password_hash(item['password'])))
                except Exception as e:
                    self.db.rollback()
                    return {"code": 500, "msg": str(e)}
                self.db.commit()
                return {"code": 200, "msg": "管理员添加成功"}

    '''
        根据id获取新闻具体详情的方法
        参数:
            id: 要获取的新闻ID，是一个整数
    '''
    def get_news_by_id(self, id: int):
        try:
            news = self.db.query(News).filter_by(id=id).first()
        except Exception as e:
            self.db.rollback()
            return {"code": 500, "msg": str(e)}
        if news:
            news_list = [{
                "id": news.id,
                "title": news.title,
                "content": news.content,
                "category": news.category,
                "publish_time": news.publish_time.strftime('%Y-%m-%d %H:%M:%S')
            }]
        else:
            return {"code": 404, "msg": "新闻不存在"}
        return {"code": 200, "data": news_list}

    '''
        获取新闻或公司简介或管理员账号数据方法（目前只实现获取新闻）
        作用：通过输入的操作类型获取数据
        参数:
            id: 要获取的新闻ID列表，每个元素是一个整数
            option: 操作类型枚举值，指定要获取的内容类型
    '''
    def get_data(self, option: OptionType, id: list[int] = None):
        match option:
            # 获取新闻数据
            case OptionType.NEWS:
                try:
                    if id:
                        news = self.db.query(News).filter(News.id.in_(id)).order_by(News.publish_time.desc()).all()
                    else:
                        news = self.db.query(News).order_by(News.publish_time.desc()).all()
                except Exception as e:
                    self.db.rollback()
                    return {"code": 500, "msg": str(e)}
                news_list = []
                for n in news:
                    news_list.append({
                        "id": n.id,
                        "title": n.title,
                        "content": n.content,
                        "category": n.category,
                        "publish_time": n.publish_time.strftime('%Y-%m-%d %H:%M:%S')
                    })
                return {"code": 200, "data": news_list}
            # 获取公司简介数据
            case OptionType.INTRODUCTION:
                try:
                    introduction = self.db.query(Introduction).first()
                except Exception as e:
                    self.db.rollback()
                    return {"code": 500, "msg": str(e)}
                if introduction:
                    return {"code": 200, "data": introduction.content}
                else:
                    return {"code": 200, "data": ""}
            # 获取管理员账号数据
            case OptionType.ADMIN:
                try:
                    admins = self.db.query(Admin).all()
                except Exception as e:
                    self.db.rollback()
                    return {"code": 500, "msg": str(e)}
                admin_list = []
                for a in admins:
                    admin_list.append({
                        "id": a.id,
                        "username": a.username,
                        "password": a.password,
                        "create_time": a.create_time.strftime('%Y-%m-%d %H:%M:%S')
                    })
                return {"code": 200, "data": admin_list}

    '''
        删除新闻或公司简介或管理员账号数据方法（目前只实现删除新闻）
        作用：通过输入的操作类型删除数据
        参数:
            option: 操作类型枚举值，指定要删除的内容类型
            id: 要删除的新闻ID列表，每个元素是一个整数
    '''
    def delete_data(self, option: OptionType, id: list[int]):
        match option:
            case OptionType.NEWS: 
                try:
                    for item in id:
                        news = self.db.query(News).filter_by(id=item).first()
                        if news:
                            self.db.delete(news)
                except Exception as e:
                    self.db.rollback() # 回滚事务
                    return {"code": 500, "msg": str(e)}
                self.db.commit() # 提交事务
                return {"code": 200, "msg": "新闻删除成功"}
            # case OptionType.INTRODUCTION:
            #     try:
            #         introduction = self.db.query(Introduction).first()
            #         if introduction:
            #             self.db.delete(introduction)
            #     except Exception as e:
            #         self.db.rollback()
            #         return {"code": 500, "msg": str(e)}
            # #     self.db.commit()
            # #     return {"code": 200, "msg": "公司简介删除成功"}
            # case OptionType.ADMIN:
            #     try:
            #         for item in id:
            #             admin = self.db.query(Admin).filter_by(id=item).first()
            #             if admin:
            #                 self.db.delete(admin)
            #     except Exception as e:
            #         self.db.rollback()
            #         return {"code": 500, "msg": str(e)}
            #     self.db.commit()
            #     return {"code": 200, "msg": "管理员删除成功"}

'''
    ==========================前端接口部分==========================
'''
app = Flask(__name__)
app.secret_key = secrets.token_hex(16)
'''
登录检查装饰器
'''
def check_login(func):
    @wraps(func)
    def decorator(*args, **kwargs):
        if session.get('role') != 'admin':
            return jsonify({"code": 403, "msg": "无权限"}), 403
        return func(*args, **kwargs)
    return decorator

'''
    展示公司首页
'''
@app.route('/')
def index():
    db = DBUtils()
    intro_result = db.get_data(OptionType.INTRODUCTION)
    news_result = db.get_data(OptionType.NEWS)
    db.close()
    news_list = news_result.get('data', [])[:3]
    return jsonify({
        "code": 200,
        "data": {
            "introduction": intro_result.get('data', ''),
            "news": news_list
        }
    })

'''
    返回公司简介
'''
@app.route('/api/introduction', methods=['GET'])
def get_introduction():
    """
    📥 Postman 测试：获取公司简介
    --------------------------------------------------
    Method: GET
    URL: http://127.0.0.1:5003/api/introduction
    Expected Response:
    {
        "code": 200,
        "data": "公司简介内容"
    }
    --------------------------------------------------
    说明：此接口无需登录，返回公司简介（按时间倒序）
    """
    db = DBUtils()
    result = db.get_data(OptionType.INTRODUCTION)   
    db.close()
    return jsonify(result)

'''
    获取新闻列表（支持按发布时间倒叙）
'''
@app.route('/api/news', methods=['GET'])
def get_news():
    db = DBUtils()
    result = db.get_data(OptionType.NEWS)   
    db.close()
    return jsonify(result)

'''
    获取新闻详情
'''
@app.route('/api/news/<int:news_id>', methods=['GET'])
def get_news_detail(news_id):
    db = DBUtils()
    news = db.get_news_by_id(news_id)
    db.close()
    if news:
        return jsonify({"code": 200, "data": news})
    else:
        return jsonify({"code": 404, "msg": "新闻不存在"}), 404

'''
    管理员登陆
'''
@app.route('/admin/login', methods=['POST'])
def admin_login():
    data = request.get_json()
    if not data or 'username' not in data or 'password' not in data:
        return jsonify({"code": 400, "msg": "缺少username或password"}), 400
    db = DBUtils()
    admin_dict = db.get_data(OptionType.ADMIN) # 获取所有管理员信息, 返回的是一个字典{'code': 200, 'data': [{}]}
    db.close()
    # 如果没有查询成功
    if admin_dict['code'] != 200 or not admin_dict:
        return jsonify({"code": 500, "msg": admin_dict.get('msg', '系统异常')}), 500
    # 如果接收到的的管理员账号和密码不对，则提示输入的账号或密码有错误
    for info in admin_dict['data']:
        if info['username'] == data['username'] and check_password_hash(info['password'], data['password']):
            session['user_id'] = info['id']
            session['username'] = info['username']
            session['role'] = 'admin'
            return jsonify({"code": 200, "msg": "登录成功"})
    else:
        return jsonify({"code": 400, "msg": "用户名或密码错误"}), 400

'''
    管理员发布新闻
'''
@app.route('/admin/news', methods=['POST'])
@check_login
def admin_add_news():
    data = request.get_json()
    if not data or 'title' not in data or 'content' not in data:
        return jsonify({"code": 400, "msg": "缺少title或content"}), 400
    news_data = [{
        "title": data['title'],
        "content": data['content'],
        "category": data.get('category', '公司动态')
    }]
    db = DBUtils()
    result = db.add_data(news_data, OptionType.NEWS)
    db.close()
    return jsonify(result)

'''
    管理员删除指定新闻
'''
@app.route('/admin/news/<int:news_id>', methods=['DELETE'])
@check_login
def admin_delete_news(news_id):
    db = DBUtils()
    result = db.delete_data(OptionType.NEWS, [news_id])
    db.close()
    return jsonify(result)
'''
    管理员退出登录
'''
@app.route('/admin/logout', methods=['POST'])
@check_login
def admin_logout():
    session.clear()
    return jsonify({"code": 200, "msg": "退出登录成功"})
'''
    数据持久化存储（暂时先不做），使用sqlite和sqlalchemy存入数据库cms.db
    管理员页面输入数据，存入数据库中
'''
@app.route('/admin/input', methods=['POST'])
@check_login
def input_data_to_db(data: list, option: OptionType):
    db = DBUtils()
    result = db.add_data(data, option)
    db.close()
    return result

def main():
    db = DBUtils()
    # 预设管理员账号（如果不存在）
    admin = db.get_data(OptionType.ADMIN)
    if not admin['data']:
        db.add_data([{"username": "admin", "password": "admin123"}], OptionType.ADMIN)
        print("已初始化管理员账号: admin/admin123")
    else:
        print("管理员账号已存在")
    # 预设公司简介（如果不存在）
    intro_result = db.get_data(OptionType.INTRODUCTION)
    if not intro_result.get('data', ''):
        db.add_data([{"content": "智云科技（CloudSmart）成立于2023年，是一家专注于人工智能与云计算领域的科技创新企业。公司致力于为企业提供智能化解决方案，助力传统行业数字化转型升级。\n\n【核心优势】\n- 技术研发：拥有来自清华、北大等顶尖高校的技术团队，在大语言模型、计算机视觉、数据挖掘等领域具有深厚积累\n- 产品创新：自主研发的SmartOffice智能办公系统已服务超过10万家企业客户\n- 生态建设：与阿里云、华为云等主流云服务商建立深度合作，构建开放共赢的产业生态\n\n【发展愿景】\n成为中国领先的企业级AI解决方案提供商，用技术创新驱动产业变革，让人工智能普惠千行百业。"}], OptionType.INTRODUCTION)
        print("已初始化公司简介")
    else:
        print("公司简介已存在")
    db.close()


if __name__ == '__main__':
    main()
    app.run(host='127.0.0.1', debug=True, port=5003)