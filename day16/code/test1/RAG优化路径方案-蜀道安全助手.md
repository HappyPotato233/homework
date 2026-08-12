---
AIGC:
    Label: "1"
    ContentProducer: 001191440300708461136T1XGW3
    ProduceID: 619a68374c198f2d1dccd9a31deded68_1f0de9ef95ef11f1b6b5525400287e28
    ReservedCode1: avGHNxHt/mVfoNOLXM1awAGVAamWbyRahHu403KptPbtLbvZHWRpvUK8z29VKJAcL8FVwa0HbLBdCTF1rbZYxDjUvDFIW8UEFQZ4xBRy4NPlgg0+oP4EKazWyTxgxDG9J+lpyZJXqJC4JcmhGoUqFSp/8nTPOvpp1n7HAksMyj9ZW2T9O+fabFdiZr8=
    ContentPropagator: 001191440300708461136T1XGW3
    PropagateID: 619a68374c198f2d1dccd9a31deded68_1f0de9ef95ef11f1b6b5525400287e28
    ReservedCode2: avGHNxHt/mVfoNOLXM1awAGVAamWbyRahHu403KptPbtLbvZHWRpvUK8z29VKJAcL8FVwa0HbLBdCTF1rbZYxDjUvDFIW8UEFQZ4xBRy4NPlgg0+oP4EKazWyTxgxDG9J+lpyZJXqJC4JcmhGoUqFSp/8nTPOvpp1n7HAksMyj9ZW2T9O+fabFdiZr8=
---

# 蜀道安全助手 — RAG优化路径方案

> **项目名称**：蜀道安全助手
> **文档版本**：V1.0
> **编写日期**：2026-08-12
> **适用范围**：AI智能助手模块 — RAG（检索增强生成）子系统

---

## 目录

- [一、背景与基线定义](#一背景与基线定义)
- [二、优化路线总览](#二优化路线总览)
- [三、P0 基线方案 — 跑通可用 RAG](#三p0-基线方案--跑通可用-rag)
- [四、P1 分块治理 — 不切坏语义](#四p1-分块治理--不切坏语义)
- [五、P2 混合检索 — 术语也能命中](#五p2-混合检索--术语也能命中)
- [六、P3 精排+改写 — 答案更准](#六p3-精排改写--答案更准)
- [七、P4 领域深化（可选） — 知识图谱+微调+闭环](#七p4-领域深化可选--知识图谱微调闭环)
- [八、实施计划与资源评估](#八实施计划与资源评估)
- [九、评估体系构建](#九评估体系构建)

---

## 一、背景与基线定义

### 1.1 项目背景

蜀道安全助手 RAG 子系统是 AI 智能问答模块的核心引擎，负责将用户自然语言提问转化为基于企业安全知识库的精准回答。知识库涵盖国家法律法规（安全生产法、建筑法等）、行业标准规范（JTG 系列）、企业内部制度、安全操作规程、应急预案、事故案例分析六大类。

### 1.2 基线方案定义（P0）

基线方案采用业界最通用的 RAG 起点架构——**固定窗口分块 + 纯稠密向量检索**，旨在以最小工程复杂度快速跑通端到端流程。

```
┌─────────────────────────────────────────────────────────┐
│                   P0 基线 RAG 架构                       │
│                                                         │
│  ┌──────────┐    ┌──────────────┐    ┌──────────────┐  │
│  │ 用户提问  │───▶│ 查询向量化    │───▶│ 稠密向量检索  │  │
│  │          │    │ (Embedding)   │    │ Top-4 → Top-5│  │
│  └──────────┘    └──────────────┘    └──────┬───────┘  │
│                                             │           │
│                      ┌──────────────┐        │           │
│                      │  大模型生成   │◀───────┘           │
│                      │  (文心一言)   │                    │
│                      └──────┬───────┘                    │
│                             │                            │
│                      ┌──────▼───────┐                    │
│                      │  返回回答     │                    │
│                      └──────────────┘                    │
│                                                         │
│  离线管线:                                              │
│  文档 → 固定窗口分块(500字/块,100字重叠)                 │
│       → BGE-large-zh 向量化 → Chroma 入库               │
└─────────────────────────────────────────────────────────┘
```

**基线各项参数**：

| 参数 | 设定值 | 说明 |
|------|--------|------|
| 分块策略 | 固定窗口 (RecursiveCharacterTextSplitter) | chunk_size=500, overlap=100 |
| 检索方式 | 纯稠密向量检索（余弦相似度） | 单路向量检索 Top-5 |
| Embedding | BGE-large-zh-v1.5 | 1024 维，本地部署 |
| 向量数据库 | Chroma (HNSW 索引) | 嵌入式持久化 |
| 重排序 | 无 | — |
| 混合检索 | 无 | — |
| 查询改写 | 无 | 直接使用原始 Query |
| 评估标准 | 端到端能答 | 仅验证流程贯通 |

### 1.3 基线的局限性

P0 基线能够跑通流程，但在安全知识库场景下存在明显短板：

| 短板 | 现象 | 根因 |
|------|------|------|
| **语义断裂** | 法规条款被切碎，上下文丢失 | 固定窗口分块不考虑文档结构，条款与解释分离 |
| **术语漏检** | "三同时制度"搜不到含"安全设施"的内容 | 纯向量检索对精确术语匹配不足 |
| **相关性差** | 回答引用了不相关的文档片段 | 无精排环节，Top-5 中混入弱相关内容 |
| **查询表达不足** | 口语化提问（"咋办"）匹配不到正式表述 | 无查询改写，用户表达与知识库表述存在 gap |
| **领域深度不足** | 跨文档的关联知识无法召回 | 缺乏知识图谱，案例与法规之间无显式关联 |

---

## 二、优化路线总览

### 2.1 五阶段优化路线图

基于基线短板分析，制定分阶段、数据驱动的 RAG 优化路线：

```
P0 基线 ──→ P1 分块治理 ──→ P2 混合检索 ──→ P3 精排+改写 ──→ P4 领域深化(可选)

跑通流程    不切坏语义     术语也能命中    答案更准        知识图谱+微调+闭环
```

| 阶段 | 目标 | 关键动作 | 验证指标 | 技术栈增量 |
|------|------|---------|---------|-----------|
| **P0 基线** | 跑通可用 RAG | 固定窗口分块 + 稠密检索 Top-4 | 端到端能答 | RecursiveCharacterTextSplitter + Chroma |
| **P1 分块治理** | 不切坏语义 | 结构感知分块 + 父子块 + 中文嵌入(bge-m3) | Recall@4 ≥ 0.7 | MarkdownHeaderTextSplitter + ParentDocumentRetriever |
| **P2 混合检索** | 术语也能命中 | 稠密+稀疏 RRF + 元数据过滤 | Recall@10 ≥ 0.85 | BM25Retriever + RRF 融合 + metadata filter |
| **P3 精排+改写** | 答案更准 | Reranker 重排 + 查询改写/HyDE | 人工评分 ≥ 4/5 | CrossEncoder(bge-reranker) + HyDE |
| **P4 进阶(可选)** | 领域深化 | 事故案例知识图谱 + 嵌入微调 + 反馈闭环(A07 点赞/踩) | 持续迭代 | Neo4j/NetworkX + LoRA 微调 |

### 2.2 数据驱动原则

每个阶段的优化决策严格基于数据，而非主观判断：

> **核心方法**：构建固定 Golden QA 集（人工标注 50-100 条安全问答对），每阶段用同一套 QA 集测量 Recall@K 与人工评分，作为调参依据，避免"拍脑袋优化"。

```
评估闭环:

Golden QA 集
     │
     ├──→ 自动测量 Recall@K (检索召回率)
     │         │
     │         ▼
     │    调参优化 ──→ 重新测量 ──→ 是否达标?
     │                              │
     │                         是   │   否
     │                         ▼    ▼
     │                      通过   继续迭代
     │
     └──→ 人工评分 (答案质量)
               │
               ▼
          达标 → 进入下一阶段
```

---

## 三、P0 基线方案 — 跑通可用 RAG

### 3.1 架构

```
离线管线:
  文档(PDF/Word/MD) → 文档加载 → 固定窗口分块(500字/块) 
                    → BGE-large-zh 向量化 → Chroma 入库

在线问答:
  用户提问 → 敏感词检测 → 查询向量化 → 稠密检索 Top-5
           → Prompt 构建(检索结果+系统指令) → 文心一言生成 → SSE流式返回
```

### 3.2 分块策略

采用 LangChain `RecursiveCharacterTextSplitter`，固定窗口参数：

| 参数 | 值 | 说明 |
|------|-----|------|
| chunk_size | 500 | 每块目标 500 字符 |
| chunk_overlap | 100 | 块间重叠 100 字符 |
| separators | `["\n\n", "\n", "。", "；", "，", " "]` | 优先按自然段落、句子边界切分 |

```
原始文档（约5000字）
│
├── 按 "\n\n" 段落分割
│   ├── 段落1（600字）→ 超过500字限制
│   │   ├── 按 "。" 句号分割
│   │   │   ├── 句子1~3 合并 → Chunk 1（约480字）
│   │   │   └── 句子3~5 合并 → Chunk 2（约450字）[与Chunk1重叠100字]
│   │   └── ...
│   └── 段落2（400字）→ Chunk 3
```

### 3.3 检索策略

- **检索方式**：单路稠密向量检索（余弦相似度）
- **召回数量**：Top-5
- **向量数据库**：Chroma (HNSW 索引)
- **Embedding 模型**：BGE-large-zh-v1.5（1024 维）

### 3.4 基线指标

| 指标 | 基线值 | 测量方式 |
|------|--------|---------|
| 端到端可用 | ✅ 通过 | 发送 Golden QA 集中 20 条问题，检查是否能返回非空回答 |
| 首字响应 | ~2-3s | 计时测量 |
| 检索延迟 | ~200-300ms | HNSW 检索耗时 |
| 粗略准确率 | ~50-60%（估计） | 人工抽检回答是否相关 |

### 3.5 基线代码骨架

```python
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

# 分块
splitter = RecursiveCharacterTextSplitter(
    chunk_size=500, chunk_overlap=100,
    separators=["\n\n", "\n", "。", "；", "，", " "]
)

# 向量化
embeddings = HuggingFaceEmbeddings(model_name="BAAI/bge-large-zh-v1.5")

# 向量存储
vector_store = Chroma(
    embedding_function=embeddings,
    collection_name="safety_knowledge",
    persist_directory="./chroma_data"
)

# 检索 → 生成
retrieved_docs = vector_store.similarity_search(query, k=5)
context = "\n\n".join(doc.page_content for doc in retrieved_docs)
answer = llm.invoke(f"基于以下知识回答问题：\n{context}\n\n问题：{query}")
```

---

## 四、P1 分块治理 — 不切坏语义

### 4.1 目标

解决 P0 基线中固定窗口分块导致的语义断裂问题。安全法规具有严格条款结构（"第X条  ……"），固定窗口可能将条款与解释说明切分到不同块中，导致检索召回失败。

**验证指标**：Recall@4 ≥ 0.7（在 Top-4 结果中至少 70% 的相关文档被召回）

### 4.2 优化手段

#### 4.2.1 结构感知分块

从 P0 的纯字符级分块升级为**文档结构感知分块**，识别 Markdown 标题层级、法律条款编号、表格结构：

```
P0 分块 (固定窗口)                    P1 分块 (结构感知)
                                  
  按字符数强制切分                     按文档逻辑结构切分
  ┌─────────────────┐               ┌─────────────────┐
  │ ## 第三十一条    │               │ ## 第三十一条    │
  │ 建设项目安全设   │               │ 建设项目安全设施  │
  │ 施，必须与主体   │               │ 必须与主体工程    │
  │ ── 切分点 ──    │               │ 同时设计、同时    │
  │ 工程同时设计、   │               │ 施工、同时投入    │
  │ 同时施工...      │               │ 生产和使用。     │
  └─────────────────┘               └─────────────────┘
                                     ↑ 完整保留条款语义
  条款被切成两半！
```

**实现方案**：使用 LangChain `MarkdownHeaderTextSplitter`，按标题层级（H1/H2/H3）切分，每个标题段落作为独立单元。

```python
from langchain_text_splitters import MarkdownHeaderTextSplitter

headers_to_split_on = [
    ("#", "h1"),       # 一级标题（法规名称）
    ("##", "h2"),      # 二级标题（章节）
    ("###", "h3"),     # 三级标题（条款）
]

splitter = MarkdownHeaderTextSplitter(
    headers_to_split_on=headers_to_split_on,
    strip_headers=False  # 保留标题在内容中
)
```

**适用前提**：知识库文档需要预先整理为规范的 Markdown 格式，包含清晰的标题层级。

#### 4.2.2 父子块（Parent-Child Chunking）

结构感知分块保证了语义完整性，但可能产生较大的块（如一个完整法规条款可能 1000+ 字）。大块在检索时精度下降（向量表征被稀释），小块又破坏语义。

**解决方案**：父子块模式——用小块做检索（子块），用大块做生成（父块）。

```
原始文档
│
├── 父块（Parent Chunk）—— 一个完整的法规条款（~1000字）
│   │   用于：填充 LLM Prompt 上下文
│   │
│   ├── 子块 1（Child Chunk）—— 条款前半段（~300字）
│   │   用于：向量检索（精度高）
│   │
│   └── 子块 2（Child Chunk）—— 条款后半段（~300字）
│       用于：向量检索（精度高）
│
│   检索命中子块 → 自动回溯到父块 → 将完整条款注入 Prompt
```

**实现方案**：LangChain `ParentDocumentRetriever`

```python
from langchain.retrievers import ParentDocumentRetriever
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma

# 父块分割器（大块）
parent_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000, chunk_overlap=100
)

# 子块分割器（小块，用于检索）
child_splitter = RecursiveCharacterTextSplitter(
    chunk_size=300, chunk_overlap=50
)

retriever = ParentDocumentRetriever(
    vectorstore=Chroma(
        embedding_function=embeddings,
        collection_name="parent_child_store"
    ),
    docstore=InMemoryStore(),  # 存储父块
    child_splitter=child_splitter,
    parent_splitter=parent_splitter,
    search_kwargs={"k": 4}  # 检索 4 个子块
)
```

#### 4.2.3 Embedding 模型评估

P1 阶段需评估是否升级 Embedding 模型。当前 BGE-large-zh-v1.5 已在 C-MTEB 榜单表现优异，但 bge-m3 在多语言和长文本场景下优势明显：

| 模型 | 维度 | 最大长度 | 中文效果 | 部署资源 |
|------|------|---------|---------|---------|
| bge-large-zh-v1.5 | 1024 | 512 tokens | ★★★★★ | GPU 1.3GB |
| bge-m3 | 1024 | 8192 tokens | ★★★★★ | GPU 2.2GB |

**建议**：P1 阶段先沿用 bge-large-zh-v1.5，若结构感知分块后仍出现长文本表征不佳，再切换至 bge-m3。

### 4.3 预期效果

| 改进项 | P0 基线 | P1 目标 |
|--------|---------|---------|
| 语义完整性 | 条款常被切碎 | 每个块对应完整条款/章节 |
| 检索召回率 | ~50% | Recall@4 ≥ 70% |
| 回答引用准确率 | ~60% | ~75% |

---

## 五、P2 混合检索 — 术语也能命中

### 5.1 目标

安全生产领域有大量专业术语（如"三同时""四不放过""两票三制"），这些术语在纯向量检索中可能被归为通用语义而漏检。例如用户搜索"三同时"时，向量检索可能因语义近似而返回大量"同时进行"的通用段落。

**验证指标**：Recall@10 ≥ 0.85

### 5.2 优化手段

#### 5.2.1 稠密+稀疏混合检索

将 P0/P1 的单路稠密检索升级为**稠密检索（语义）+ 稀疏检索（关键词）双路并行 + RRF 融合**：

```
用户提问: "三同时制度的具体要求是什么？"
                │
        ┌───────┴───────┐
        ▼               ▼
  ┌──────────┐    ┌──────────┐
  │ 稠密检索  │    │ 稀疏检索  │
  │(向量语义) │    │(BM25关键字)│
  │          │    │          │
  │ 返回10条  │    │ 返回10条  │
  └────┬─────┘    └─────┬────┘
       │                │
       └───────┬────────┘
               ▼
       ┌──────────────┐
       │  RRF 融合排序  │  (Reciprocal Rank Fusion, k=60)
       │  取 Top-10    │
       └──────────────┘
```

**稠密检索**：语义理解强，能匹配"高处作业安全要求"与"坠落防护措施"的语义关联。

**稀疏检索（BM25）**：精确匹配强，能精准命中"三同时""安全生产法第五十七条"等术语和编号。

**RRF 融合**：两条路径的结果加权融合，两边都排名靠前的文档获得更高分数。

```python
import asyncio
from langchain_community.retrievers import BM25Retriever

async def hybrid_search(query: str, top_k: int = 10):
    # 并行执行
    dense_results, sparse_results = await asyncio.gather(
        vector_store.asimilarity_search_with_score(query, k=top_k * 2),
        asyncio.to_thread(bm25_retriever.get_relevant_documents, query)
    )
    
    # RRF 融合
    k = 60.0
    scores = {}
    for rank, (doc, _) in enumerate(dense_results):
        key = doc.page_content[:50]
        scores[key] = scores.get(key, 0) + 1.0 / (k + rank + 1)
    for rank, doc in enumerate(sparse_results[:top_k * 2]):
        key = doc.page_content[:50]
        scores[key] = scores.get(key, 0) + 1.0 / (k + rank + 1)
    
    return sorted(scores.items(), key=lambda x: x[1], reverse=True)[:top_k]
```

#### 5.2.2 元数据过滤

Chroma 支持 `where` 条件过滤，可在检索时按文档类型、适用范围等元数据筛选：

| 过滤维度 | 示例 | 使用场景 |
|---------|------|---------|
| 文档类型 | `doc_type == "REGULATION"` | 用户明确问法规类问题 |
| 适用范围 | `scope == "高处作业"` | 限定专业领域检索 |
| 生效状态 | `status == "ACTIVE"` | 排除已废止的法规 |

```python
# 按文档类型 + 适用范围联合过滤
filter_dict = {
    "$and": [
        {"doc_type": {"$in": ["REGULATION", "STANDARD"]}},
        {"scope": "高处作业"}
    ]
}
results = vector_store.similarity_search(
    query, k=10, filter=filter_dict
)
```

#### 5.2.3 关键词索引优化

对安全领域高频术语建立**关键词词典**，在 BM25 索引时进行分词优化：

```
通用分词器: "三同时制度" → ["三", "同时", "制度"]  ← 语义丢失
定制分词器: "三同时制度" → ["三同时", "制度"]       ← 保留术语
```

### 5.3 预期效果

| 改进项 | P1 | P2 目标 |
|--------|-----|---------|
| 术语命中率 | ~60% | ~90% |
| 召回率 | Recall@4 ≥ 0.7 | Recall@10 ≥ 0.85 |
| 检索延迟 | ~200ms | ~300ms（双路并行，增幅可控） |

---

## 六、P3 精排+改写 — 答案更准

### 6.1 目标

P2 混合检索大幅提升了召回率，但 Top-10 结果中仍可能混入部分弱相关内容。P3 通过精排和查询改写，确保送入大模型的最优 5 条知识片段高度相关。

**验证指标**：人工评分 ≥ 4/5

### 6.2 优化手段

#### 6.2.1 Reranker 精排

P2 的混合检索采用 Bi-Encoder 架构（Query 和 Chunk 独立编码），速度快但精度有上限。P3 引入 Cross-Encoder 对 Top-10 结果进行精排。

```
Bi-Encoder (P2 检索)              Cross-Encoder (P3 精排)

Query ──▶ [Embedding]             Query ──┐
                                       ├──▶ [Cross-Encoder] ──▶ Score
Chunk ──▶ [Embedding]             Chunk ──┘

独立编码，速度快（~200ms）         联合编码，精度高（~500ms/10条）
适合大规模召回（Top-10）           适合小规模精排（Top-10 → Top-5）
```

**实现**：使用 BGE-Reranker-Large (CrossEncoder)

```python
from sentence_transformers import CrossEncoder

reranker = CrossEncoder("BAAI/bge-reranker-large")

def rerank(query: str, candidates: list, top_n: int = 5):
    pairs = [(query, doc.page_content) for doc in candidates]
    scores = reranker.predict(pairs)
    
    scored = sorted(zip(candidates, scores), key=lambda x: x[1], reverse=True)
    # 过滤相关性低于阈值的结果
    return [doc for doc, score in scored[:top_n] if score > 0.3]
```

**效果**：将 Top-10 中真正相关的文档提升到 Top-5，同时过滤低分噪音。

#### 6.2.2 查询改写

一线员工的口语化提问（如"高处掉下来怎么办"）与知识库中的正式表述（如"高处作业坠落防护措施"）存在显著 gap。查询改写桥接这一差距。

**三种改写策略**：

| 策略 | 说明 | 示例 |
|------|------|------|
| **大模型改写** | 用小模型将口语转化为正式表述 | "咋整" → "如何处理" |
| **HyDE** | 先生成假设性答案，用答案向量检索 | "高处坠落怎么办" → 生成假设答案 → 用答案向量检索 |
| **多 Query 生成** | 从不同角度生成多个 Query 并行检索 | "高处坠落防护" + "高空作业安全" + "防坠落措施" |

**推荐方案**：P3 阶段优先采用 **大模型改写 + HyDE** 组合。

```
HyDE 流程:

用户提问: "高处掉下来怎么办"
     │
     ▼
┌────────────────┐
│ LLM 生成假设答案 │  "高处作业时应佩戴安全带，设置安全网，
│ (HyDE)         │   确保作业平台稳固，遵守操作规程..."
└───────┬────────┘
        │
        ▼
┌────────────────┐
│ 用假设答案向量   │  假设答案的向量与知识库中正式文档更接近
│ 进行检索        │
└───────┬────────┘
        │
        ▼
   检索结果（相关性显著提升）
```

```python
def hyde_retrieval(query: str, llm, vector_store, top_k: int = 5):
    # Step 1: 生成假设答案
    hyde_prompt = f"请用一段话回答以下安全问题：{query}"
    hypothetical_answer = llm.invoke(hyde_prompt)
    
    # Step 2: 用假设答案向量检索
    results = vector_store.similarity_search(
        hypothetical_answer, k=top_k
    )
    return results
```

### 6.3 预期效果

| 改进项 | P2 | P3 目标 |
|--------|-----|---------|
| Top-5 精确率 | ~70% | ≥ 90% |
| 回答准确度（人工评分） | ~3.5/5 | ≥ 4.0/5 |
| 口语化提问覆盖率 | ~50% | ~85% |
| 端到端延迟 | ~2-3s | ~2.5-3.5s（增加精排+改写耗时） |

---

## 七、P4 领域深化（可选） — 知识图谱+微调+闭环

### 7.1 目标

P4 是进阶阶段，面向需要深度领域知识的场景。当 P3 已稳定运行且积累了足够的用户反馈数据后启动。

**验证指标**：持续迭代（无硬性数值指标，通过反馈数据驱动优化）

### 7.2 优化手段

#### 7.2.1 事故案例知识图谱

安全生产领域的核心特征之一是**事故案例与法规条款之间的强关联**。例如，"某工地脚手架坍塌事故"关联到"《建筑施工安全检查标准》JGJ 59"的多个条款。知识图谱显式建模这种关系。

```
知识图谱 Schema:

┌──────────┐     关联法规     ┌──────────┐
│  法规条款  │◀──────────────▶│  事故案例  │
│          │                │          │
│ · 安全生产│    ┌─────────┐ │ · 坍塌    │
│   法第31条│◀───│ 案例关联  │─▶│   事故   │
│ · JGJ 59 │    └─────────┘ │ · 高处坠落│
│   第3.1条│                │   事故   │
└────┬─────┘                └────┬─────┘
     │                           │
     │      ┌──────────┐         │
     └─────▶│ 操作规程  │◀────────┘
            │          │
            │ · 脚手架  │
            │   搭设规程│
            └──────────┘
```

**实现方案**：

| 组件 | 选型 | 说明 |
|------|------|------|
| 图数据库 | Neo4j / NetworkX | 轻量场景可用 NetworkX，生产环境推荐 Neo4j |
| 实体识别 | 基于规则 + 小模型 NER | 识别法规编号、事故类型、操作规程名称 |
| 关系抽取 | LLM 辅助 | 用大模型从案例文档中提取法规引用关系 |
| 检索增强 | GraphRAG | 检索时同时查询向量库和知识图谱，融合结果 |

**GraphRAG 增强检索流程**：

```
用户提问: "脚手架坍塌事故涉及哪些法规？"
     │
     ├──→ 向量检索: 召回相关案例和法规文档
     │
     ├──→ 图谱检索: 从事故节点出发，沿"关联法规"边，获取法规列表
     │
     └──→ 融合: 向量结果 + 图谱结果 → Prompt → LLM 生成
```

#### 7.2.2 Embedding 模型微调

通用 Embedding 模型（bge-large-zh）在安全领域可能对特定术语的表征不够精准。基于标注数据微调可提升领域适配度。

**微调策略**：

| 策略 | 数据需求 | 效果 | 成本 |
|------|---------|------|------|
| LoRA 微调 | 500-1000 条正负例对 | 术语向量表征显著提升 | 中（单卡 A100 2-3h） |
| 全量微调 | 5000+ 条 | 全面领域适配 | 高 |
| 对比学习 | 1000+ 条三元组 (Query, Pos, Neg) | 检索精度提升 | 中 |

**推荐**：P4 阶段使用 LoRA 微调 bge-large-zh-v1.5，仅需少量标注数据。

#### 7.2.3 反馈闭环

利用 PRD 中定义的 **A07（点赞/踩）功能** 构建反馈闭环：

```
用户反馈闭环:

用户提问 → RAG 检索 → LLM 生成 → 用户评价(👍/👎)
                                        │
                          ┌─────────────┘
                          ▼
                    ┌──────────┐
                    │ 反馈分析  │
                    │          │
                    │ · 踩的原因│
                    │   分类统计│
                    │ · 低分案例│
                    │   回流标注│
                    └────┬─────┘
                         │
              ┌──────────┼──────────┐
              ▼          ▼          ▼
        调整分块策略  更新关键词库  Fine-tune 模型
```

**闭环机制**：

1. 收集踩反馈中"回答不准确""回答不完整"的案例
2. 人工标注正确回答，加入 Golden QA 集
3. 每两周用更新的 Golden QA 集重新评估各阶段指标
4. 根据评估结果触发针对性优化

### 7.3 预期效果

| 改进项 | P3 | P4 目标 |
|--------|-----|---------|
| 跨文档关联回答 | 不支持 | 支持（知识图谱增强） |
| 领域术语表征 | 通用 | 经微调适配 |
| 回答满意度 | ~4.0/5 | 持续提升至 4.5+/5 |
| 优化迭代效率 | 依赖人工分析 | 数据驱动闭环 |

---

## 八、实施计划与资源评估

### 8.1 实施路径

```
        第1周    第2-3周    第4-5周    第6-7周    第8周+（可选）
P0: ████████████
P1:           ████████████
P2:                       ████████████
P3:                                   ████████████
P4:                                               ████████████
```

### 8.2 各阶段资源评估

| 阶段 | 开发工时 | 标注数据 | 新增依赖 | 硬件需求 |
|------|---------|---------|---------|---------|
| P0 基线 | 3 人天 | 0 | Chroma, BGE-large-zh | 1 × GPU (T4/RTX 3060+) |
| P1 分块治理 | 5 人天 | Golden QA 50-100 条 | MarkdownHeaderTextSplitter | 同 P0 |
| P2 混合检索 | 5 人天 | 术语词典 100+ 条 | BM25Retriever | 同 P0 |
| P3 精排+改写 | 8 人天 | 100 条人工评分 | bge-reranker-large | GPU 显存 +1.3GB |
| P4 领域深化 | 15 人天+ | 500+ 条标注 | Neo4j/NetworkX, LoRA | 单卡 A100 微调 |

### 8.3 风险与应对

| 风险 | 影响阶段 | 应对措施 |
|------|---------|---------|
| Golden QA 集标注质量不足 | 全阶段 | 由安全员参与标注，双人交叉校验 |
| 知识库文档格式不统一 | P1 | 预处理脚本统一转为 Markdown 格式 |
| P3 精排导致延迟超标 | P3 | 异步精排 + 提前返回 Top-3 流式输出，后续补充精排结果 |
| P4 知识图谱构建成本过高 | P4 | 先用 NetworkX 做轻量实现验证效果，确认 ROI 后再上 Neo4j |

---

## 九、评估体系构建

### 9.1 Golden QA 集规范

| 维度 | 规范 |
|------|------|
| 数量 | 50-100 条（初期 50，每阶段可扩充） |
| 覆盖 | 六大知识类别各 ≥ 5 条，涵盖不同难度 |
| 格式 | `{question, expected_answer, relevant_docs[], difficulty}` |
| 标注人 | 安全管理部门 + 产品组联合标注 |
| 维护 | 每阶段结束后根据反馈新增 10-20 条 |

### 9.2 评估指标体系

| 指标 | 定义 | 测量方式 | 适用阶段 |
|------|------|---------|---------|
| Recall@K | Top-K 结果中包含相关文档的比例 | 自动（基于 Golden QA 的 relevant_docs） | P1-P4 |
| Precision@K | Top-K 结果中相关文档的比例 | 自动 | P2-P4 |
| MRR | 第一个相关文档排名的倒数均值 | 自动 | P2-P4 |
| 人工评分 | 对生成答案的 1-5 分评分 | 人工 | P3-P4 |
| 首字延迟 | 用户提问到第一个 token 返回的时间 | 计时 | 全阶段 |
| 用户满意度 | 点赞率（点赞数/总评价数） | 自动（A07 反馈） | P3-P4 |
| 拒绝率 | 因知识库无信息而拒绝回答的比例 | 自动 | 全阶段 |

### 9.3 每阶段评估 Checkpoint

| 阶段 | 评估节点 | 必须通过的指标 |
|------|---------|--------------|
| P0 | 上线前 | 端到端 20 条 QA 全通 |
| P1 | 第 3 周 | Recall@4 ≥ 0.7 |
| P2 | 第 5 周 | Recall@10 ≥ 0.85 |
| P3 | 第 7 周 | 人工评分 ≥ 4.0/5 |
| P4 | 持续 | 人工评分与满意度趋势上升 |

---

## 附录：各阶段技术栈对照

| 组件 | P0 基线 | P1 分块治理 | P2 混合检索 | P3 精排+改写 | P4 进阶 |
|------|---------|------------|------------|-------------|---------|
| 分块器 | RecursiveCharacterTextSplitter | MarkdownHeaderTextSplitter + ParentDocumentRetriever | 同 P1 | 同 P1 | 同 P1 + 图谱增强 |
| Embedding | bge-large-zh-v1.5 | bge-large-zh-v1.5 / bge-m3 | 同 P1 | 同 P1 | LoRA 微调版 |
| 检索方式 | 纯稠密 (Top-5) | 稠密 (Top-4) | 稠密+稀疏 RRF (Top-10) | 同 P2 + Reranker | 同 P3 + GraphRAG |
| 精排 | 无 | 无 | 无 | bge-reranker-large | 同 P3 |
| 查询优化 | 无 | 无 | 元数据过滤 | HyDE + 查询改写 | 同 P3 |
| 知识图谱 | 无 | 无 | 无 | 无 | Neo4j/NetworkX |
| 向量数据库 | Chroma | Chroma | Chroma | Chroma | Chroma + Neo4j |
| 评估 | 端到端能答 | Recall@4 | Recall@10 | 人工评分 | 满意度趋势 |

---

*— 文档结束 —*
*（内容由AI生成，仅供参考）*
