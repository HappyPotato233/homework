'''
    基于现有的构建阶段，检索阶段的3个代码，进行代码改造。同时需要升级：
    ①华为的年报下载下来，选择一个合适的分块策略，跑通基本的rag流程，
    ②embedding（bge-large-zh）本地加载。
    ③增加混合检索机制，自己写也可以调用langchain
    ④项目代码架构改（可暂缓）
    2026.8.11
    今日任务：1.完善昨天的rag系统，增加rrf融合稠密检索和稀疏检索，增加reranker模型（github）。
'''
from dotenv import load_dotenv
import os
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_chroma import Chroma
from langchain_community.retrievers import BM25Retriever
from langchain_core.documents import Document
import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer

load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".env"))
'''
    导入对话模型
'''
BASE_URL = os.getenv("BASE_URL")
MODEL_NAME = os.getenv("MODEL_NAME")
API_KEY = os.getenv("API_KEY")
LOCAL_EMBEDDING_MODEL_PATH = os.getenv("LOCAL_EMBEDDING_MODEL_PATH")
LOCAL_RERANKER_MODEL_PATH = os.getenv("LOCAL_RERANKER_MODEL_PATH")

RRF_K = 60 # RRF检索常数
TOP_K = 8
FINAL_K = 5 # 精排前保留多少条
RERANKER_TOP_K =2 # reranker模型返回的前2个文档
BM25_WEIGHT = 0.4 # BM25检索权重
VECTOR_WEIGHT = 0.6 # 向量检索权重

'''
    导入对话模型
'''
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
    model_name=LOCAL_EMBEDDING_MODEL_PATH,
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
'''
    创建reranker模型
'''
class LocalReranker:
    def __init__(self, model_path):
        self.tokenizer = AutoTokenizer.from_pretrained(model_path) # transformer的用于将文本转化为模型输入的token序列， .pretrained是加载预训练的模型
        self.model = AutoModelForSequenceClassification.from_pretrained(model_path) # transformer的用于将token序列转化为模型输出
        self.model.eval()
        self.model.to("cuda")

    def rank(self, query, docs):
        '''
        对文档进行rerank
        '''
        pairs = [[query, doc.page_content] for doc in docs]
        with torch.no_grad(): # 禁止计算梯度反向传播
            inputs = self.tokenizer(
                pairs,
                return_tensors="pt",
                padding=True,
                truncation=True,
                max_length=512
            ) # 将文档对转换为模型输入的token序列
            inputs = {k: v.to(self.model.device) for k, v in inputs.items()} # 将输入张量移到模型所在设备(CUDA)，避免CPU/GPU设备不一致报错
            scores = self.model(**inputs, return_dict=True).logits.view(-1).float() # 前向传播，获取模型输出，取分类结果为1的分数，作为文档对的相关度
            scores = scores.tolist()
        # 按分数从高到低排序
        ranked = sorted(zip(docs, scores), key=lambda x: x[1], reverse=True)
        return [doc for doc, score in ranked]

reranker = LocalReranker(LOCAL_RERANKER_MODEL_PATH)

def retrieve(query):
    '''
    检索函数
    '''
    # 创建检索器,仅检索相关程度最高的前三个文档块
    retriever = vector_store.as_retriever(search_kwargs={"k": 3})
    # 执行检索,doc类型是Document对象
    docs = retriever.invoke(query)
    return docs

def get_all_docs(vector_store):
    '''
    获取所有文档块的函数
    '''
    data = vector_store.get(include=["documents", "metadatas"])
    return [Document(page_content=d, metadata=m if m else {}) for d, m in zip(data["documents"], data["metadatas"])]

def combination_retriever(query):
    '''
        混合检索函数
        1. 向量检索
        2. BM25检索
        3. 加权合并结果
    '''
    all_docs = get_all_docs(vector_store) # 获取所有文档块，返回类型是Document对象列表，每个对象包含page_content和metadata属性
    # 1. BM25检索
    bm25_retriever = BM25Retriever.from_documents(all_docs) # 创建BM25检索器
    bm25_retriever.k = TOP_K # 设置检索返回的文档数量为TOP_K
    bm25_docs = bm25_retriever.invoke(query) # 执行BM25检索，返回类型是Document对象列表，每个对象包含page_content和metadata属性

    # 2. 向量检索
    vector_retriever = vector_store.as_retriever(search_kwargs={"k": TOP_K}) # 调用向量数据库的向量检索器
    vector_docs = vector_retriever.invoke(query) # 执行向量检索，返回类型是Document对象列表，每个对象包含page_content和metadata属性

    # 3.加权求和
    bm25_scores = {d.page_content: (TOP_K - i) * BM25_WEIGHT for i, d in enumerate(bm25_docs)}
    vector_scores = {d.page_content: (TOP_K - i) * VECTOR_WEIGHT for i, d in enumerate(vector_docs)}

    # 4.合并结果
    all_docs_dict = {}
    for doc in bm25_docs + vector_docs:
        content = doc.page_content
        total_scores = bm25_scores.get(content, 0) + vector_scores.get(content, 0)
        all_docs_dict[content] = (total_scores, doc)
    sorted_docs = sorted(all_docs_dict.items(), key=lambda x: x[1][0], reverse=True)
    fused_docs = [doc for _, (score, doc) in sorted_docs[:FINAL_K]]

    # 5. rerank重排
    reranked_docs = reranker.rank(query, fused_docs)
    return reranked_docs[:RERANKER_TOP_K]
def dual_path_retrieve(query, vectorstore):
    '''
        双路径检索函数
    '''
    all_docs = get_all_docs(vector_store) # 获取所有文档块，返回类型是Document对象列表，每个对象包含page_content和metadata属性

    # 1. BM25检索
    bm25_retriever = BM25Retriever.from_documents(all_docs) # 创建BM25检索器
    bm25_retriever.k = TOP_K # 设置检索返回的文档数量为TOP_K
    bm25_docs = bm25_retriever.invoke(query) # 执行BM25检索，返回类型是Document对象列表，每个对象包含page_content和metadata属性
    
    # 2.向量检索
    vector_retriever = vector_store.as_retriever(search_kwargs={"k": TOP_K}) # 调用向量数据库的向量检索器
    vector_docs = vector_retriever.invoke(query) # 执行向量检索，返回类型是Document对象列表，每个对象包含page_content和metadata属性
    
    # 3. 双路结果合并去重（保持BM25优先的找回顺序）
    seen = set()
    merged = []
    for doc in bm25_docs + vector_docs:
        content = doc.page_content
        if content not in seen:
            merged.append(doc)
            seen.add(content)
    
    return merged

def rrf_retrieve(query, vectorstore):
    '''
        RRF融合检索函数
    '''
    all_docs = get_all_docs(vector_store) # 获取所有文档块，返回类型是Document对象列表，每个对象包含page_content和metadata属性
    # 1.BM25检索
    bm25_retriever = BM25Retriever.from_documents(all_docs) # 创建BM25检索器
    bm25_retriever.k = TOP_K # 设置检索返回的文档数量为TOP_K
    bm25_docs = bm25_retriever.invoke(query) # 执行BM25检索，返回类型是Document对象列表，每个对象包含page_content和metadata属性
    
    # 2.向量检索
    vector_retriever = vector_store.as_retriever(search_kwargs={"k": TOP_K}) # 调用向量数据库的向量检索器
    vector_docs = vector_retriever.invoke(query) # 执行向量检索，返回类型是Document对象列表，每个对象包含page_content和metadata属性
    
    # 3.RRF融合检索
    rrf_scores = {}
    for i, doc in enumerate(bm25_docs):
        content = doc.page_content
        rrf_scores[content] = rrf_scores.get(content, 0) + 1 / (RRF_K + i + 1)
    for i, doc in enumerate(vector_docs):
        cnt = doc.page_content
        rrf_scores[cnt] = rrf_scores.get(cnt, 0) + 1 / (RRF_K + i + 1)
    # 4. 合并结果
    all_docs_dict = {}
    for doc in bm25_docs + vector_docs:
        cnt = doc.page_content
        all_docs_dict[cnt] = (rrf_scores.get(cnt, 0), doc)

    sorted_docs = sorted(all_docs_dict.values(), key=lambda x: x[0], reverse=True)
    fused_docs = [doc for score, doc in sorted_docs[:FINAL_K]]
    return fused_docs

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
    ops = input("请输入检索方式（1.向量检索，2.混合检索，3.双路径检索，4.RRF融合检索）：")
    if ops == "1":
        docs = retrieve(query)
    elif ops == "2":
        docs = combination_retriever(query)
    elif ops == "3":
        docs = dual_path_retrieve(query, vector_store)
    elif ops == "4":
        docs = rrf_retrieve(query, vector_store)
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
    query = "华为创建于哪一年？\n" # 1987
    answer = test(query)
    if answer:
        print(answer)
    else:
        print(f"😯 返回失败了")

if __name__ == "__main__":
    main()