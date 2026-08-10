'''
随堂任务1：
Embedding模型测试与向量相似度计算
### 作业要求
基于讲义中 `embedding.py` 的代码，完成以下任务：
1. **测试不同文本的向量表示**：
  * 编码以下5个句子，输出向量维度和前5个数值
  * "Java开发工程师要求3年以上经验"
  * "Python岗位要求熟悉Django框架"
  * "公司节日福利包括购物卡和电影票"
  * "员工享受带薪年假和五险一金"
  * "Java高级工程师需精通JVM调优"
2. **计算语义相似度**：
  * 计算上述5个句子两两之间的余弦相似度
  * 输出相似度矩阵（5x5）
  * 找出最相似的句子对
3. **实战问答**：
  * 用户提问："Java岗位有什么要求？"
  * 计算该问题与5个句子的相似度，返回最相似的Top 2
### 提示
* 使用 `sklearn.metrics.pairwise.cosine_similarity` 计算相似度
* 使用 `numpy` 进行数组操作

'''
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document
import numpy as np
'''
    任务1
'''
# 准备好原始数据（其实就是文挡分块后的文档块），要Document化，因为split_document分块后的类型是list[Document]
data = [
    Document(page_content="Java开发工程师要求3年以上经验"),
    Document(page_content="Python岗位要求熟悉Django框架"),
    Document(page_content="公司节日福利包括购物卡和电影票"),
    Document(page_content="员工享受带薪年假和五险一金"),
    Document(page_content="Java高级工程师需精通JVM调优")
]
def embedding_vectors(persist_directory="./code/task1.db"):
    '''
        构建向量数据
    '''

    # 本地embedding模型路径
    model_name = "./code/BAAI"
    # 用huggingface加载embedding模型
    embeddings = HuggingFaceEmbeddings(
        model_name=model_name,
        model_kwargs={'device': 'cuda'}, # 如果有GPU可改为 'cuda'
        encode_kwargs={'normalize_embeddings': True} # BGE 模型必须开启标准化
    )
    if embeddings:
        print(f"✅ 成功加载模型从 [{model_name}]")

    print("利用模型编码文本...")
    vectors = embeddings.embed_documents([d.page_content for d in data])
    print(f"✅ 成功编码文本，向量维度：{len(vectors[0])}")
    for i, vec in enumerate(vectors):
        print(f"文本 {i+1} 向量前5个数值：{vec[:5]}")

    return vectors
    # print(f"▶ 正在将文本向量化并存储到 Chroma 数据库 ({persist_directory})...")
    # # 向量化并存储到 Chroma
    # vector_store = Chroma.from_documents(
    #     documents=data,
    #     embedding=embeddings,
    #     persist_directory=persist_directory
    # )
    # print(f"✅ 成功将文本向量化并存储到 Chroma 数据库 ({persist_directory})")
    # return vector_store

def calculate_cosine_similarity_task1(vectors: list):
    '''
        计算向量之间的余弦相似度
    '''
    from sklearn.metrics.pairwise import cosine_similarity
    print(f"🧮 计算相似弦度矩阵...")
    # 计算相似度
    similarity_matrix = cosine_similarity(vectors)
    print(f"相似度矩阵维度：{similarity_matrix.shape}")
    print(f"相似度矩阵：\n{similarity_matrix}")

    return similarity_matrix

def find_most_similar_k(similarity_matrix: np.ndarray, k=1):
    print(f"🔍 找出top-{k}最相似的句子对...")
    n = len(similarity_matrix)
    # 收集上三角所有句子对（排除对角线自身）
    pairs = []
    for i in range(n):
        for j in range(i+1, n):
            pairs.append((similarity_matrix[i][j], i, j))
    # 按相似度降序排序，取前k个
    pairs.sort(reverse=True, key=lambda x: x[0])
    return pairs[:k]
    
if __name__ == "__main__":
    # 构建向量数据
    vectors = embedding_vectors()
    # 计算向量之间的余弦相似度
    similarity_matrix = calculate_cosine_similarity_task1(vectors)
    # 找出最相似的句子对
    pairs = find_most_similar_k(similarity_matrix)
    print(f"top1最相似:{data[pairs[0][1]].page_content} 与 {data[pairs[0][2]].page_content} 相似度: {pairs[0][0]:.4f}")
    # 实战问答
    query = "Java岗位有什么要求？"
    similarity_matrix = calculate_cosine_similarity_task1(vectors)
    # 找出最相似的句子对
    pairs = find_most_similar_k(similarity_matrix, k=2)
    for sim, i ,j in pairs:
        print(f"top2最相似:{data[i].page_content} 与 {data[j].page_content} 相似度: {sim:.4f}")
