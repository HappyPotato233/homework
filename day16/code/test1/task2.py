'''
    基于现有的构建阶段，检索阶段的3个代码，进行代码改造。同时需要升级：
    ①华为的年报下载下来，选择一个合适的分块策略，跑通基本的rag流程，
    ②embedding（bge-large-zh）本地加载。
    ③增加混合检索机制，自己写也可以调用langchain
    ④项目代码架构改（可暂缓）
'''
from dotenv import load_dotenv
import os
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_chroma import Chroma
from rank_bm25 import BM25Okapi
import jieba

load_dotenv("code/.env")
'''
    导入对话模型
'''
BASE_URL = os.getenv("BASE_URL")
MODEL_NAME = os.getenv("MODEL_NAME")
API_KEY = os.getenv("API_KEY")
LOCAL_MODEL_PATH = os.getenv("LOCAL_MODEL_PATH")

llm = ChatOpenAI(
    model=MODEL_NAME,
    temperature=0,
    api_key=API_KEY,
    base_url=BASE_URL,
)

'''
    导入embedding模型
'''
embeddings = HuggingFaceEmbeddings(
    model_name=LOCAL_MODEL_PATH,
    model_kwargs={"device":"cuda"},
    encode_kwargs={"normalize_embeddings":True}
)

'''
    加载本地向量数据库
'''
vector_store = Chroma(
    persist_directory="code/chroma_db",
    embedding_function=embeddings
)

def retrieve(query):
    '''
    检索函数
    '''
    # 创建检索器,仅检索相关程度最高的前三个文档块
    retriever = vector_store.as_retriever(search_kwargs={"k": 3})
    # 执行检索,doc类型是Document对象
    docs = retriever.invoke(query)
    return docs

def combination_retriever(query):
    '''
        混合检索函数
        1. 向量检索
        2. BM25检索
        3. 加权合并结果
    '''
    # ===============BM25检索===============
    # 定义分词函数
    def tokenize(query):
        return list(jieba.lcut(query))
    # 获取问题的分词结果
    tokenize_query = tokenize(query)
    # 从Chroma中获取所有文档
    all_docs = vector_store._collection.get(
        include=["documents", "metadatas"]
    )
    # 所有文本块
    all_texts = all_docs["documents"]
    # 所有元数据
    all_metadatas = all_docs["metadatas"]
    # 对向量数据库中的每一个文本块进行切分
    tokenize_docs = [tokenize(text) for text in all_texts]
    # 创建BM25模型
    bm25 = BM25Okapi(tokenize_docs)
    # 取得分值
    scores = bm25.get_scores(tokenize_query)
    # ===============向量检索===============
    # 执行向量检索并获取分数
    vector_docs_and_scores = vector_store.similarity_search_with_score(query, k=3)
    # ===============加权合并结果===============
    # 1.BM25分数归一化
    bm25_max = max(scores) if max(scores) else 1
    bm25_norm = [s / bm25_max for s in scores]
    # 2.向量分数归一化
    vector_scores = {}
    for doc, distance in vector_docs_and_scores:
        vector_scores[doc.page_content] = 1 / (1 + distance)
    # 3.设置权重
    weight_bm25 = 0.6
    weight_vector = 0.4
    # 建立 分数字典：key=文本内容, value=融合得分
    fusion_scores = {}
    docs_map = {}  # 保存 content -> Document 的映射
    
    # 加入 BM25 分数（遍历所有文档）
    for i, text in enumerate(all_texts):
        fusion_scores[text] = fusion_scores.get(text, 0) + weight_bm25 * bm25_norm[i]
        from langchain_core.documents import Document
        docs_map[text] = Document(page_content=text, metadata=all_metadatas[i])
    
    # 加入向量分数（只覆盖被检索到的文档）
    for doc, _ in vector_docs_and_scores:
        content = doc.page_content
        fusion_scores[content] = fusion_scores.get(content, 0) + weight_vector * vector_scores[content]
        docs_map[content] = doc
    
    # 4. 按融合得分降序排序，取 top-3
    sorted_contents = sorted(fusion_scores.items(), key=lambda x: x[1], reverse=True)
    top_k = 3
    result_docs = [docs_map[content] for content, _ in sorted_contents[:top_k]]
    return result_docs

def format_answer(docs):
    '''
    格式化回答函数
    '''
    formatted_parts = []
    for i, doc in enumerate(docs):
        source = doc.metadata.get("source", "未知")
        page = doc.metadata.get("page", "未知")
        chunk_id = doc.metadata.get("chunk_id", "未知")
        formatted_parts.append(
            f"【参考文档{i+1}】来源: {source} | 页码: {page} | chunk_id: {chunk_id}\n{doc.page_content}"
        )
    return "\n\n".join(formatted_parts)

def test(query):
    system_prompt = (
        "你是华为公司的内部智能人事/行政助手\n"
        "请严格基于以下提供的公司内部文档内容回答用户问题。\n"
        "如果你在文档中找不到答案，请直接说“根据提供的文档，我无法回答该问题”。\n"
        "【参考文档内容】\n"
        "{context}"
    )
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", "{input}"),
    ])

    # 执行检索
    ops = input("请输入检索方式（1.向量检索，2.混合检索）：")
    if ops == "1":
        docs = retrieve(query)
    elif ops == "2":
        docs = combination_retriever(query)
    else:
        docs = retrieve(query)

    # 创建rag链，执行整个流程
    rag_chain = (
        {"context": lambda x: format_answer(x["docs"]), "input": lambda x: x["input"]}
        | prompt
        | llm
        | StrOutputParser()
    )
    # 执行链
    answer = rag_chain.invoke({"docs": docs, "input": query})
    # 附带引用来源
    sources = set()
    for doc in docs:
        source = doc.metadata.get("source", "未知")
        page = doc.metadata.get("page", "未知")
        sources.add(f"{source} 第{page}页")
    answer += "\n\n📚 参考来源: " + " | ".join(sources)
    return answer

def main():
    query = "华为2025年的销售收入和净利润是多少？" # - 销售收入：126,018 百万美元 / 880,941 百万人民币。净利润：9,732 百万美元 / 68,036 百万人民币
    answer = test(query)
    if answer:
        print(answer)
    else:
        print(f"😯 返回失败了")

if __name__ == "__main__":
    main()