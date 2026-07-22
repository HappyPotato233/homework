"""
课堂任务：政府新闻爬虫
技术栈：requests + BeautifulSoup4 + lxml(XPath) + SQLAlchemy + SQLite
规范要求：
1. 数据库：gov_news.db 表gov_news，link唯一约束
2. 完整浏览器headers、超时5s、随机休眠2~4s、捕获403终止
3. BS4 CSS选择器 select / select_one 、get_text(strip=True)、urljoin拼接链接
4. 仅抓取1~10页，单页异常不中断程序
5. 全部异常捕获，日志打印

新增功能：
6. 简易交互式菜单，支持指定单页抓取/批量抓取
7. 将数据库数据导出为csv文件
8. XPath和BeautifulSoup两种方式解析对比（XPath单独函数）
9. 空值过滤，标题/时间为空的数据不存入数据库
"""
import requests
import random
import time
import csv
import os
from urllib.parse import urljoin
from bs4 import BeautifulSoup
from lxml import etree
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy.exc import SQLAlchemyError
from enum import Enum

# ======================【第一部分：数据库模块 复用讲义规范】======================
# 生成 gov_news.db，放在程序同级目录
engine = create_engine("sqlite:///gov_news.db", echo=False)
Base = declarative_base()
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)

Options = Enum("Options", ("1", "2", "3", "4", "5", "6"))

'''
    数据表类
'''
class GovNews(Base):
    __tablename__ = "gov_news"
    id = Column(Integer, primary_key=True, autoincrement=True,comment="自增主键")
    title = Column(String(500), nullable=False, comment="新闻标题")
    publish_time = Column(String(30), nullable=False, comment="发布时间")
    link = Column(String(800), unique=True, nullable=False, comment="新闻链接，唯一约束")

# 首次运行自动创建数据表
Base.metadata.create_all(bind=engine)

'''
    数据库操作工具类
'''
class DBUtils:
    '''
        设置数据库会话
    '''
    @staticmethod
    def set_db():
        return SessionLocal()
    '''
        关闭数据库会话
    '''
    @staticmethod
    def close_db(db):
        db.close()

    '''
        新闻入库方法：写入失败自动回滚，捕获数据库异常
        参数:
            news_data: dict {title, publish_time, link}
        返回:
            True入库成功 / False入库失败
    '''
    @staticmethod
    def save_news(db, news_data: list[GovNews])-> bool:
        try:
            # 批量提交内容到数据库
            db.add_all(news_data)
            db.commit()
            return True
        except SQLAlchemyError as e:
            db.rollback()
            print(f"数据库操作失败：{e}")
            return False
    
    '''
        查询所有新闻
    '''
    @staticmethod
    def query_all_news(db):
        try:
            news = db.query(GovNews).all()      
            if not news:
                print("数据库中暂无新闻数据")
                return
            for new in news:
                print(f"新闻标题：{new.title}，发布时间：{new.publish_time}，链接：{new.link}")
            print(f"\n共查询到 {len(news)} 条新闻")
        except SQLAlchemyError as e:
            print(f"数据库读取操作失败：{e}")
    
    '''
        删除所有新闻方法（测试使用）
        返回:
            True删除成功 / False删除失败
    '''
    @staticmethod
    def delete_all_news(db):
        try:
            db.query(GovNews).delete()
            db.commit()
            print("所有新闻删除成功")
            return True
        except SQLAlchemyError as e:
            db.rollback()   
            print(f"数据库操作失败：{e}")
            return False

    '''
        将数据库数据导出为CSV文件
        参数:
            db: 数据库会话
            filename: 导出的CSV文件名
        返回:
            True导出成功 / False导出失败
    '''
    @staticmethod
    def export_to_csv(db, filename="gov_news_export.csv"):
        print(f"========开始导出数据到CSV文件=========")
        try:
            news = db.query(GovNews).all()
            if not news:
                print("数据库中暂无数据，无法导出")
                return False

            # 确保导出目录存在
            export_dir = os.path.dirname(os.path.abspath(filename))
            if export_dir and not os.path.exists(export_dir):
                os.makedirs(export_dir)

            # 写入CSV文件，utf-8-sig防止Excel打开乱码
            with open(filename, "w", newline="", encoding="utf-8-sig") as csvfile:
                writer = csv.writer(csvfile)
                # 写入表头
                writer.writerow(["ID", "新闻标题", "发布时间", "新闻链接"])
                # 写入数据
                for item in news:
                    writer.writerow([item.id, item.title, item.publish_time, item.link])

            print(f"成功导出 {len(news)} 条新闻到：{os.path.abspath(filename)}")
            return True
        except Exception as e:
            print(f"导出CSV失败：{e}")
            import traceback
            traceback.print_exc()
            return False
        finally:
            DBUtils.close_db(db)
        
'''
    爬虫操作工具类
'''        
class CUtils:
    '''
        爬取页面数据方法
        参数:
            page_num: 页码
            parser_type: 解析方式，"bs4" 或 "xpath"
        返回:
            True成功 / False失败
    '''
    @staticmethod
    def crawl_page(page_num: int, parser_type="bs4"):
        print(f"========开始爬取第{page_num}页（{parser_type}解析）========")
        if page_num == 1:
            url = "https://www.gov.cn/toutiao/liebiao/home.htm"
        elif page_num >= 2:
            url = f"https://www.gov.cn/toutiao/liebiao/home_{page_num}.htm"
        # 防反爬请求头
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "zh-CN,zh;q=0.9",
            "Referer": "https://www.gov.cn/"
        }
        try:
            # 发送GET请求
            response = requests.get(url, headers=headers, timeout=5)
            if response.status_code == 403:
                print(f"第{page_num}页访问受限，触发反爬")
                return False
            if response.status_code != 200:
                print(f"第{page_num}页访问失败，状态码：{response.status_code}")
                return False
            response.encoding = "utf-8"
            # 根据解析方式调用不同的解析方法
            if parser_type == "bs4":
                CUtils.parse_html_by_bs4(response.text, page_num)
            elif parser_type == "xpath":
                CUtils.parse_html_by_xpath(response.text, page_num)
            else:
                print(f"不支持的解析方式：{parser_type}，默认使用bs4")
                CUtils.parse_html_by_bs4(response.text, page_num)
            # 随机休眠2-4秒
            sleep_time = random.uniform(2, 4)
            time.sleep(sleep_time) 
            print(f"第{page_num}页爬取、解析完成、随机休眠{sleep_time:.2f}秒")
            return True
        except requests.RequestException as e:
            print(f"❌ {url} 请求失败：{str(e)}")
            return False

    '''
        使用BeautifulSoup解析HTML方法
        参数:
            html: 页面源码
            page_num: 页码
        返回:
            True成功 / False失败
    '''
    @staticmethod
    def parse_html_by_bs4(html, page_num: int):
        soup = BeautifulSoup(html, "html.parser")
        '''
            HTML结构：
            div.news_box > div.list.list_1.list_2 > ul > li > h4 > a + span.date
        '''
        news_list = soup.select(".news_box li")
        print(f"第{page_num}页找到 {len(news_list)} 条新闻（BS4解析）")
        if not news_list:
            print(f"第{page_num}页没有新闻")
            return False
        # 创建数据表对象列表
        db = DBUtils.set_db() 
        news_data = []
        # 获取标题、链接和发布时间
        try:    
            for item in news_list:
                h4 = item.select_one("h4")
                if not h4:
                    continue
                a_tag = h4.select_one("a")
                date_span = h4.select_one("span.date")
                # 空值过滤：标题或时间元素不存在则跳过
                if not a_tag or not date_span:
                    continue
                title = a_tag.get_text(strip=True)
                href = a_tag.get("href", "") # 如果该属性不存在默认返回""
                # 相对路径需要拼接域名
                full_link = urljoin("https://www.gov.cn", href)
                pub_time = date_span.get_text(strip=True)
                # 二次空值过滤：内容为空或空白字符的跳过
                if not title or not pub_time or not full_link:
                    continue
                news_data.append(GovNews(title=title, publish_time=pub_time, link=full_link))
            # 批量提交内容到数据库
            if news_data:
                DBUtils.save_news(db, news_data)
                print(f"第{page_num}页抓取完成，成功入库 {len(news_data)} 条")
            else:
                print(f"第{page_num}页未提取到有效新闻数据（已过滤空值）")
            return True
        except Exception as e:
            print(f"第{page_num}页处理异常：{e}")
            import traceback
            traceback.print_exc()
            return False
        finally:
            DBUtils.close_db(db)

    '''
        使用XPath解析HTML方法（单独函数）
        参数:
            html: 页面源码
            page_num: 页码
        返回:
            True成功 / False失败
    '''
    @staticmethod
    def parse_html_by_xpath(html, page_num: int):
        '''
            使用 lxml 的 etree.HTML 解析
            HTML结构：
            div.news_box > div.list.list_1.list_2 > ul > li > h4 > a + span.date
            XPath路径说明：
            - //div[@class='news_box']//li  ：找到news_box下所有li标签
            - ./h4/a/text()  ：当前li下h4下a的文本（标题）
            - ./h4/a/@href   ：当前li下h4下a的href属性（链接）
            - ./h4/span[@class='date']/text()  ：当前li下h4下date span的文本（时间）
        '''
        tree = etree.HTML(html)
        news_list = tree.xpath("//div[@class='news_box']//li")
        print(f"第{page_num}页找到 {len(news_list)} 条新闻（XPath解析）")
        if not news_list:
            print(f"第{page_num}页没有新闻")
            return False
        # 创建数据表对象列表
        db = DBUtils.set_db() 
        news_data = []
        # 获取标题、链接和发布时间
        try:    
            for item in news_list:
                # 提取标题列表（可能为空）
                title_list = item.xpath("./h4/a/text()")
                # 提取链接列表（可能为空）
                href_list = item.xpath("./h4/a/@href")
                # 提取发布时间列表（可能为空）
                date_list = item.xpath("./h4/span[@class='date']/text()")
                # 空值过滤：任一列表为空则跳过该条数据
                if not title_list or not href_list or not date_list:
                    continue
                title = title_list[0].strip()
                href = href_list[0].strip()
                pub_time = date_list[0].strip()
                # 相对路径需要拼接域名
                full_link = urljoin("https://www.gov.cn", href)
                # 二次空值过滤：去除空白后为空的跳过
                if not title or not pub_time or not full_link:
                    continue
                news_data.append(GovNews(title=title, publish_time=pub_time, link=full_link))
            # 批量提交内容到数据库
            if news_data:
                DBUtils.save_news(db, news_data)
                print(f"第{page_num}页抓取完成，成功入库 {len(news_data)} 条")
            else:
                print(f"第{page_num}页未提取到有效新闻数据（已过滤空值）")
            return True
        except Exception as e:
            print(f"第{page_num}页处理异常：{e}")
            import traceback
            traceback.print_exc()
            return False
        finally:
            DBUtils.close_db(db)

    '''
        同一页面分别用XPath和BeautifulSoup两种方式解析，对比区别
        参数:
            page_num: 对比的页码
    '''
    @staticmethod
    def compare_parsers(page_num: int = 1):
        print("=" * 70)
        print("【XPath 与 BeautifulSoup 解析对比实验】")
        print("=" * 70)
        if page_num == 1:
            url = "https://www.gov.cn/toutiao/liebiao/home.htm"
        else:
            url = f"https://www.gov.cn/toutiao/liebiao/home_{page_num}.htm"

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "zh-CN,zh;q=0.9",
            "Referer": "https://www.gov.cn/"
        }
        try:
            response = requests.get(url, headers=headers, timeout=5)
            if response.status_code != 200:
                print(f"请求失败，状态码：{response.status_code}")
                return
            response.encoding = "utf-8"
            html = response.text

            # BeautifulSoup 解析计时
            print("\n1. BeautifulSoup 解析方式：")
            print("-" * 50)
            start_time = time.time()
            soup = BeautifulSoup(html, "html.parser")
            bs4_news = soup.select(".news_box li")
            bs4_count = len(bs4_news)
            if bs4_count > 0:
                first_h4 = bs4_news[0].select_one("h4 a")
                first_date = bs4_news[0].select_one("h4 span.date")
                bs4_first_title = first_h4.get_text(strip=True) if first_h4 else "无"
                bs4_first_time = first_date.get_text(strip=True) if first_date else "无"
            else:
                bs4_first_title = "无"
                bs4_first_time = "无"
            bs4_time = time.time() - start_time
            print(f"  解析器：html.parser")
            print(f"  选择器语法：CSS选择器（.news_box li）")
            print(f"  提取条数：{bs4_count}")
            print(f"  第一条标题：{bs4_first_title[:40]}...")
            print(f"  第一条时间：{bs4_first_time}")
            print(f"  耗时：{bs4_time:.4f} 秒")

            # XPath 解析计时
            print("\n2. XPath 解析方式：")
            print("-" * 50)
            start_time = time.time()
            tree = etree.HTML(html)
            xpath_news = tree.xpath("//div[@class='news_box']//li")
            xpath_count = len(xpath_news)
            if xpath_count > 0:
                title_list = xpath_news[0].xpath("./h4/a/text()")
                date_list = xpath_news[0].xpath("./h4/span[@class='date']/text()")
                xpath_first_title = title_list[0].strip() if title_list else "无"
                xpath_first_time = date_list[0].strip() if date_list else "无"
            else:
                xpath_first_title = "无"
                xpath_first_time = "无"
            xpath_time = time.time() - start_time
            print(f"  解析器：lxml.etree")
            print(f"  路径语法：XPath（//div[@class='news_box']//li）")
            print(f"  提取条数：{xpath_count}")
            print(f"  第一条标题：{xpath_first_title[:40]}...")
            print(f"  第一条时间：{xpath_first_time}")
            print(f"  耗时：{xpath_time:.4f} 秒")

            # 对比总结
            print("\n3. 两者区别总结：")
            print("-" * 50)
            print("  【语法风格】")
            print("    - BeautifulSoup：CSS选择器 / 方法链式调用，直观易懂")
            print("    - XPath：路径表达式（类似文件路径），简洁强大")
            print("  【底层实现】")
            print("    - BeautifulSoup：纯Python（html.parser），容错性强")
            print("    - XPath：C语言实现（lxml），性能更优")
            print("  【定位能力】")
            print("    - BeautifulSoup：支持CSS选择器，层级定位方便")
            print("    - XPath：可通过父节点、兄弟节点等轴向定位，更灵活")
            print("  【适用场景】")
            print("    - BeautifulSoup：HTML不规范、快速开发调试、新手入门")
            print("    - XPath：结构清晰的页面、复杂条件定位、追求性能时")
            print("  【容错性】")
            print("    - BeautifulSoup：容错性极强，能处理各种畸形HTML")
            print("    - XPath：对HTML结构规范性要求较高")

            if bs4_count == xpath_count:
                print(f"\n✅ 两种方式提取数据条数一致（{bs4_count}条）")
            else:
                print(f"\n⚠️  两种方式提取数据条数不一致（BS4:{bs4_count}条 / XPath:{xpath_count}条）")

            print("\n" + "=" * 70)
            print("对比实验完成！")
            print("=" * 70)

        except Exception as e:
            print(f"对比解析失败：{e}")
            import traceback
            traceback.print_exc()

'''
    选择解析方式
    返回用户选择的解析方式字符串
'''
def get_parser_options():
    print("\n请选择解析方式：")
    print("  1. BeautifulSoup 解析")
    print("  2. XPath 解析")
    option = input("请输入选项：").strip()
    if option == "1":
        return "bs4"
    elif option == "2":
        return "xpath"
    else:
        print("输入错误，默认使用BeautifulSoup")
        return "bs4"

def main():
    while True:
        print("\n" + "=" * 55)
        print("欢迎使用政府新闻爬虫系统")
        print("=" * 55)
        print(f"1. 单页抓取新闻\n2.批量抓取新闻（指定页数，最多10页）\n3.查询所有新闻\n4.导出数据到CSV\n5.退出程序\n6.对比解析方式")
        print("=" * 55)

        try:
            num = input("请输入要进行的操作：").strip()
            num = int(num)
            # 单页抓取
            if num == Options["1"].value:
                print("\n【单页抓取新闻】")
                page = int(input("请输入要抓取的页码（1-10）："))
                if page < 1 or page > 10:
                    print("页码必须在1-10之间")
                    continue
                parser_type = get_parser_options()
                CUtils.crawl_page(page, parser_type)

            # 批量抓取
            elif num == Options["2"].value:
                print("\n【批量抓取新闻】")
                n = int(input("请输入要抓取的页数（最多10页）："))
                if n <= 0 or n > 10:
                    print("页数必须在1-10之间")
                    continue
                parser_type = get_parser_options()
                success_count = 0
                for page in range(1, n + 1):
                    try:
                        flag = CUtils.crawl_page(page, parser_type)
                        if flag:
                            success_count += 1
                    except Exception as e:
                        print(f"❌ 第{page}页整体抓取发生未知异常：{str(e)}，继续下一页")
                        continue
                print(f"\n批量爬取完成，共成功爬取 {success_count} 页")

            # 查询所有新闻
            elif num == Options["3"].value:
                print("\n【查询所有新闻】")
                db = DBUtils.set_db()
                DBUtils.query_all_news(db)
                DBUtils.close_db(db)

            # 导出CSV
            elif num == Options["4"].value:
                print("\n【导出数据到CSV】")
                db = DBUtils.set_db()
                filename = "gov_news_export.csv"
                DBUtils.export_to_csv(db, filename)

            # 解析对比
            elif num == Options["5"].value:
                print("\n【XPath与BeautifulSoup解析对比】")
                page = input("请输入对比的页码（默认第1页）：").strip()
                if not page:
                    page = 1
                else:
                    page = int(page)
                    if page < 1 or page > 10:
                        print("页码必须在1-10之间，使用默认第1页")
                        page = 1
                CUtils.compare_parsers(page)

            # 退出
            elif num == Options["6"].value:
                print("谢谢使用，再见！")
                break

            else:
                print("输入错误，请输入1-6之间的数字")

        except ValueError:
            print("输入错误，请输入有效的数字")
        except Exception as e:
            print(f"程序出错：{e}")

    print("程序结束")

if __name__ == "__main__":
    main()
