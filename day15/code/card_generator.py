from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import JsonOutputParser, StrOutputParser
from langchain_core.prompts import PromptTemplate, ChatPromptTemplate
import os
from dotenv import load_dotenv
from pydantic import BaseModel, Field
# 导入环境变量
load_dotenv()

# 从环境变量中获取模型所需的配置信息
api_key = os.getenv("API_KEY")  # 获取API密钥
base_url = os.getenv("BASE_URL")  # 获取API请求的基础URL（指向硅基流动等第三方平台的接口）
model_name = os.getenv("MODEL_NAME")  # 获取要调用的具体模型名称（例如qwen-flash等）

# 导入大模型
llm = ChatOpenAI(
    model=model_name,
    base_url=base_url,
    api_key=api_key,
    temperature=0.3 
)

class Card(BaseModel):
    name:str = Field(description="姓名")
    job:str = Field(description="工作")
    intro:str = Field(description="自我介绍")
    slogan:str = Field(description="个人slogan")
    skills:str = Field(description="技能列表")

def generate_introduction(info):
    # 输入信息检验
    if info==None:
        raise ValueError("请输入个人信息")
    if info["name"] == None or info["job"] == None or info["job"] == None:
        raise ValueError(f"缺少关键信息")
    # 使用ChatPromptTemplate+LCEL+StrOutputParser生成自我介绍
    chat_prompt = ChatPromptTemplate.from_messages([
        ("system", "你是一个专业的人力资源顾问，擅长帮人写简洁有力的自我介绍"),
        ("human", "请根据以下信息，帮我写一段 50 字以内的自我介绍。姓名：{name}，职位：{job}，技能：{skill}")
    ])
    str_parser = StrOutputParser() 
    chain = chat_prompt | llm | str_parser
    # 调用链子
    res = chain.invoke({"name":info["name"],"job":info["job"],"skill":info["skill"]})
    return res

def generate_slogan(name, job):
    if name == None or job == None:
        raise ValueError("关键信息缺失，无法生成slogan")
    # 创建纯文本模板
    prompt = PromptTemplate.from_template("请根据以下信息，生成一句 15 字以内的个人 slogan，要求朗朗上口，返回只包括文字即可和必要标点符号即可。姓名：{name}，职位：{job}")
    # 创建纯文本解析器
    str_parse = StrOutputParser()
    # 创建链子
    chain = prompt | llm | str_parse
    # 调用链子
    res = chain.invoke({"name":name, "job":job})
    return res 

def generate_card(info, intro, slogan):
    if info == None or intro == None or slogan == None:
        raise ValueError("输入参数有缺失")
    if info["name"] == None or info["job"] == None or info["skill"] == None:
        raise ValueError("关键信息缺失")
    # 创造解析器
    json_parser = JsonOutputParser(pydantic_object=Card)
    # 创建prompt
    chat_prompt = ChatPromptTemplate.from_messages([
        ("system", "你是一个专业的卡片制作专家"),
        ("system", "{format_instructions}"),
        ("human", "请根据以下信息，帮我制作一张完整的卡片。姓名：{name}，职位：{job}，技能：{skills}，自我介绍：{intro}，个人slogan：{slogan}"),
        ("human", "生成出来的卡片模板如下:" +
        """
        ============================
                AI 智能名片         
        ============================
        姓名：张三
        职位：Python 开发工程师
        自我介绍：xxxxxx
        个人 slogan：xxxxxx
        技能：Python, LangChain, FastAPI
        ============================
        """
    ),
    ])
    chain = chat_prompt | llm | json_parser
    # 调用链子
    # res = chain.invoke(message)
    res = chain.invoke({"name":info["name"],"job":info["job"],"skills":info["skill"],"intro":intro,"slogan":slogan,"format_instructions":json_parser.get_format_instructions()})
    return res

def create_card(card: dict) -> str:
    """把卡片字典渲染成带边框的文本名片"""
    return f"""
        ============================
                AI 智能名片
        ============================
        姓名：{card['name']}
        职位：{card['job']}
        自我介绍：{card['intro']}
        个人 slogan：{card['slogan']}
        技能：{card['skills']}
        ============================"""

if __name__ == "__main__":
    inputs = {"name":"张三","job":"Python 开发工程师","skill":"Python, LangChain, FastAPI"}
    introduction = generate_introduction(inputs)
    if isinstance(introduction, str):
        print(introduction)
    slogan = generate_slogan(inputs["name"], inputs["job"])
    if isinstance(slogan, str):
        print(slogan)
    card = generate_card(inputs, introduction, slogan)
    print(create_card(card))
