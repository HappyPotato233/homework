'''
**场景**：你为一个旅游 APP 开发了智能问答系统，根据用户的旅游问题，分发给不同的专业顾问。

**需求**：

1. 定义 **5 个顾问 Chain**：
  * `destination`: 目的地顾问
  * `budget`: 预算规划师
  * `transportation`: 交通顾问
  * `food`: 美食顾问
  * `culture`: 文化顾问
2. 主管节点分析用户需求，判断需要哪些顾问参与
3. 支持单个顾问回答和多顾问并发回答
4. 实现一个**旅行计划生成器**：用户输入目的地 + 天数 + 预算，自动调用所有顾问生成完整旅行计划
5. 打印分发决策
'''
import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough, RunnableBranch, RunnableParallel
from datetime import datetime
import asyncio
load_dotenv()

api_key = os.getenv("API_KEY")
base_url = os.getenv("BASE_URL")
model_name = os.getenv("MODEL_NAME")
# 创建路由分发模型
superviser  = ChatOpenAI(
    model=model_name,
    api_key=api_key,
    base_url=base_url,
    temperature=0.1
)
# 创建顾问/规划师
llm = ChatOpenAI(
    model=model_name,
    api_key=api_key,
    base_url=base_url,
    temperature=0.7
)


# 主管节点（分发任务）
supervisor_prompt = ChatPromptTemplate.from_template(
    "你是一个专业的旅游顾问主管。请根据客户的问题：【{question}】，决定由哪几个顾问或规划师来回答。\n"
    "你只能从以下六个词中选择一个或多个输出，除此之外不能输出其他内容：\n"
    "1. destination (如果问题关于目的地)\n"
    "2. budget (如果问题关于预算)\n"
    "3. transportation (如果问题关于交通)\n"
    "4. food (如果问题关于美食)\n"
    "5. culture (如果问题关于文化)\n"
    "6. unknown (如果不属于以上技术问题)\n\n"
    "你的输出：")

# 主管链条    

supervisor_chain = supervisor_prompt | superviser | StrOutputParser() | (lambda x: x.strip().lower())

# 目的地顾问节点
destination_prompt = ChatPromptTemplate.from_template("你是一个专业的目的地顾问。请用不超过50字，回答客户的问题{question}，的专业领域无关，就不回复。")
destination_chain = destination_prompt | llm | StrOutputParser() | (lambda x: f"【目的地顾问回复】{x}")
# 预算规划师节点
budget_prompt = ChatPromptTemplate.from_template("你是一个专业的预算规划师。请用不超过50字，回答客户的问题{question}，如果问题中与你的专业领域无关，就不回复。")
budget_chain = budget_prompt | llm | StrOutputParser() | (lambda x: f"【预算规划师回复】{x}")
# 交通顾问节点
transportation_prompt = ChatPromptTemplate.from_template("你是一个专业的交通顾问。请用不超过50字，回答客户的问题{question}，如果问题中与你的专业领域无关，就不回复。")
transportation_chain = transportation_prompt | llm | StrOutputParser() | (lambda x: f"【交通顾问回复】{x}")
# 美食顾问节点
food_prompt = ChatPromptTemplate.from_template("你是一个专业的美食顾问。请用不超过50字，回答客户的问题{question}，如果问题中与你的专业领域无关，就不回复。")    
food_chain = food_prompt | llm | StrOutputParser() | (lambda x: f"【美食顾问回复】{x}")
# 文化顾问节点
culture_prompt = ChatPromptTemplate.from_template("你是一个专业的文化顾问。请用不超过50字，回答客户的问题{question}，如果问题中与你的专业领域无关，就不回复。")
culture_chain = culture_prompt | llm | StrOutputParser() | (lambda x: f"【文化顾问回复】{x}")
# 客服节点
unknown_chain = (lambda x: f"【客服回复】您好，我门是一家旅游公司，您的问题超出了我门的服务范围。")




# 2.组装路由
context_chain = {
    "question":RunnablePassthrough(),
    "assistant":supervisor_chain
}

routing_branch = RunnableBranch(
    (lambda x: "destination" in x["assistant"], lambda x: destination_chain.invoke({"question": x["question"]})),
    (lambda x: "budget" in x["assistant"], lambda x: budget_chain.invoke({"question": x["question"]})),
    (lambda x: "transportation" in x["assistant"], lambda x: transportation_chain.invoke({"question": x["question"]})),
    (lambda x: "food" in x["assistant"], lambda x: food_chain.invoke({"question": x["question"]})),
    (lambda x: "culture" in x["assistant"], lambda x: culture_chain.invoke({"question": x["question"]})),
    (lambda x: unknown_chain(x))
)

# final_pipline = context_chain | routing_branch

async def travel_maker(destination, days, budget):
    """
        旅行计划生成器：输入目的地+天数+预算，并发调用所有顾问生成完整旅行计划
    """
    question = f"我要去{destination}，旅游{days}天，预算{budget}元，请给出专业建议。"
    start = datetime.now()
    task = [
        destination_chain.ainvoke({"question": question}),
        budget_chain.ainvoke({"question": question}),
        transportation_chain.ainvoke({"question": question}),
        food_chain.ainvoke({"question": question}),
        culture_chain.ainvoke({"question": question}),
    ]
    response = await asyncio.gather(*task)
    end = datetime.now()
    print(f"处理时间: {end - start}")
    result = "="*40 + "\n"
    for r in response:
        result += r + "\n"
    return result + "="*40



async def main():
    while True:
        user_input = input("\n您(输入'exit'退出):")
        if user_input.lower() == 'exit':
            break
        if not user_input.strip():
            continue
        try:
            # response = final_pipline.invoke({"question": user_input})
            decision = supervisor_chain.invoke({"question": user_input})
            print(f"分发决策: {decision}") # 它是会选择多个顾问或规划师的，所以我们要让多个顾问或规划师回复则需要修改routing_branch
            decision = list(decision.split(" "))
            response = []
            mission = []
            start = datetime.now()
            for d in decision:
                mission.append(routing_branch.ainvoke({"question": user_input, "assistant": d}))
            response = await asyncio.gather(*mission)
            end = datetime.now()
            response = "\n".join(response)
            print(response)
            
            print(f"处理时间: {end - start}")
        except Exception as e:
            print(f"处理失败: {e}")
            continue

    print("测试旅行计划生成器")
    await travel_maker("海口", "2", "20000")
if __name__ == "__main__":
    asyncio.run(main())

'''
    测试用例：
    输入：我要去海口旅游，玩两天，预算20000块
    非并发串行花费时间
    平均50s
    并发(异步)花费时间
    平均20s
    并发(Parallel)花费时间
    平均30s
'''