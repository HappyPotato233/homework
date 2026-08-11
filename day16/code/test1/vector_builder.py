'''
    根据pdf_loader.py中分块的结果构建向量数据库
'''
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
import importlib
import os

# 导入模块
pdf_loader = importlib.import_module("pdf_loader")
# 导入“加载pdf并分块”(load_and_split_pdfs)函数
load_and_split_pdfs = pdf_loader.load_and_split_pdfs

def build_vector_store(docs_dir="./code/docs", persist_directory="./code/chroma_db"):
    '''
        根据pdf_loader.py中分块的结果构建向量数据库
    '''
    # 获取分块后的文档块
    split_docs = load_and_split_pdfs(docs_dir)
    if not split_docs:
        print("❌ 分块后的文档块为空，无法构建向量数据库")
        return None
    # 加载本地已下载好的bge-large模型
    print("正在加载本地已下载好的bge-large模型")
    model_name = "./code/BAAI"
    embeddings = HuggingFaceEmbeddings(
        model_name=model_name,
        model_kwargs={"device":"cuda"}, 
        encode_kwargs={"normalize_embeddings":True} # BGE模型要求必须L2归一化，否则余弦相似度计算会出错
    )

    # 向量化并存储到Chroma
    print("正在向量化并存储到Chroma数据库")
    vector_store = Chroma.from_documents(
        documents=split_docs,
        embedding=embeddings,
        persist_directory=persist_directory
    )
    print("✅ 向量数据库构建完成")
    return vector_store

if __name__ == "__main__":
    build_vector_store()
