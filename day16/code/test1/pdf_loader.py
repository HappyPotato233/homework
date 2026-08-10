'''
    从指定目录中提取目标pdf文件并且进行分本分块
'''
import os
from langchain_community.document_loaders import DirectoryLoader, PDFPlumberLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from dotenv import load_dotenv

load_dotenv("code/.env")

def load_and_split_pdfs(docs_dir="./code/docs"):
    '''
        从指定目录中提取pdf文件并且进行分本分块
    '''
    if not os.path.exists(docs_dir):
        os.makedirs(docs_dir)
        print(f"提示：已自动创建 '{docs_dir}' 文件夹，请将5个 PDF 文件放入该文件夹后重新运行。")
        return []
    print(f"正在从[{docs_dir}] 加载PDF文件")
    loader = DirectoryLoader(
        docs_dir,
        glob="**/*.pdf",
        loader_cls=PDFPlumberLoader
    )
    documents = loader.load()

    if not documents:
        print(f"[{docs_dir}文件夹下没有一个pdf文件]")
        return []
    
    print(f"✅ 成功加载 {len(documents)} 页内容")
    
    # ====================文本分割======================
    print("正在进行文本分割...")
    text_splitter = RecursiveCharacterTextSplitter(
        separators=[
            "\n\n\n",  # 大段落分隔（章/节）
            "\n\n",    # 段落分隔
            "\n",      # 换行
            "。",      # 中文句号
            "！",      # 感叹号
            "？",      # 问号
            "；",      # 分号
            "，",      # 逗号
            " ",       # 空格
            ""         # 最后兜底：按字符切
        ],
        chunk_size=400,    # 文本块最大长度（年报用小一点，保证财务数据独立）
        chunk_overlap=80   # 文本块之间的重叠长度，保持上下文连贯
    )

    split_docs = text_splitter.split_documents(documents)

    # ====================为每个 chunk 添加 metadata======================
    # PDFPlumberLoader 已提供 source(文件路径) 和 page(页码) 元数据
    # 额外添加 chunk_id 方便溯源
    for i, doc in enumerate(split_docs):
        source = doc.metadata.get("source", "未知")
        page = doc.metadata.get("page", 0)
        # 从完整路径中提取文件名
        filename = os.path.basename(source) if source != "未知" else "未知"
        doc.metadata.update({
            "source": filename,        # 文件名（简化显示）
            "page": page + 1,          # 页码从1开始（更直观）
            "chunk_id": f"{filename}_p{page + 1}_c{i}",  # 唯一标识：文件名_页码_序号
            "chunk_index": i           # 全局序号
        })

    print(f"✅ 成功分割 {len(split_docs)} 个文本块")
    # 打印前3个 chunk 的 metadata 示例
    print(f"📄 前3个文本块元数据示例：")
    for i, doc in enumerate(split_docs[:3]):
        print(f"  [chunk {i}] 来源: {doc.metadata['source']} | 页码: {doc.metadata['page']} | chunk_id: {doc.metadata['chunk_id']}")
    return split_docs

if __name__ == "__main__":
    load_and_split_pdfs()