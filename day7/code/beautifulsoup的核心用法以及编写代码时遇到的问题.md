# beautifulsoup的核心语法

```python
# ==================== 1. 创建对象 ====================
soup = BeautifulSoup(html, 'lxml') # 处理破损或不规范的HTML，自动修复
soup = BeautifulSoup(html, 'html.parser') # 适用简单HTML结构
# ==================== 2. 查找方法 ====================
CSS选择器（最常用）
soup.select('.title')                      # 类
# 返回: [<div class="title">...</div>, <h1 class="title">...</h1>, ...]
soup.select('#main')                       # ID
# 返回: [<div id="main">...</div>]
soup.select('div ul li')                   # 层级
# 返回: [<li>...</li>, <li>...</li>, <li>...</li>]
soup.select('.list.list_1.list_2 ul li')  # 多类
# 返回: [<li>新闻1</li>, <li>新闻2</li>, ...]
soup.select('[href]')                      # 属性存在
# 返回: [<a href="...">链接1</a>, <a href="...">链接2</a>, ...]
# ==================== 3. 提取数据 ====================
# 提取文本
element.get_text()
element.get_text(strip=True)               # 去除空格
element.string                              # 
# 提取属性直接
element.get('href')                         # get方式（推荐）文本
```

# 编写作业时遇到的问题

使用soup = BeautifulSoup(html, 'lxml')获取BeautifulSoup实例时，发现soup.select的内容总是空的，无论怎么改变soup.select()的参数都没用，但是命名有爬取信息，后面改成了soup = BeautifulSoup(html, 'html.parser')，soup.select()就有内容了。


