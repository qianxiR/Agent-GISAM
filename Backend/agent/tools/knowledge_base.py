"""
工具文档知识库 - 使用RAG动态检索工具说明
入参:
  - query: string 用户问题
方法:
  - 从Markdown文档加载工具说明
  - 向量检索top-k相关工具文档
  - 组装精简的SystemMessage提示词
出参:
  - string: 包含相关工具说明的提示词片段
"""
from pathlib import Path
from typing import List, Dict, Any
from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_community.embeddings import DashScopeEmbeddings
from langchain_core.vectorstores import VectorStore
from langchain_community.document_loaders import DirectoryLoader, UnstructuredMarkdownLoader
from langchain_text_splitters import MarkdownHeaderTextSplitter

# ===== 全局变量: 工具文档目录路径 =====
TOOLS_DOCS_DIR = Path(__file__).parent / "docs"


class ToolKnowledgeBase:
    """
    工具知识库管理类
    入参:
      - persist_directory: string 向量数据库持久化目录
      - api_key: string OpenAI API密钥
      - base_url: string OpenAI API地址
    方法:
      - 初始化Chroma向量存储
      - 索引工具文档
      - 检索相关工具
    出参:
      - VectorStore: Chroma向量存储实例
    """
    
    def __init__(
        self,
        persist_directory: str = "./tools/chroma_db",
        api_key: str = None,
        base_url: str = None
    ):
        self.persist_directory = persist_directory
        
        # 初始化Embedding模型(使用DashScope专用Embeddings)
        self.embeddings = DashScopeEmbeddings(
            model="text-embedding-v3",  # 阿里云DashScope的Embedding模型
            dashscope_api_key=api_key
        )
        
        # 初始化向量存储
        self.vectorstore: VectorStore = None
        self._init_vectorstore()
    
    def _init_vectorstore(self) -> None:
        """
        初始化向量存储
        入参: 无
        方法:
          - 检查持久化目录是否存在
          - 若不存在则创建并索引工具文档
          - 若存在则加载已有索引
        出参: 无 (设置self.vectorstore)
        """
        persist_path = Path(self.persist_directory)
        
        if persist_path.exists() and (persist_path / "chroma.sqlite3").exists():
            # 加载已有索引
            print(f"✅ 加载已有工具知识库: {self.persist_directory}")
            self.vectorstore = Chroma(
                collection_name="tool_docs",
                embedding_function=self.embeddings,
                persist_directory=self.persist_directory
            )
        else:
            # 创建新索引
            print(f"🔨 创建工具知识库: {self.persist_directory}")
            persist_path.mkdir(parents=True, exist_ok=True)
            self._build_index()
    
    def _build_index(self) -> None:
        """
        从Markdown文件构建工具文档索引
        入参: 无
        方法:
          - 使用DirectoryLoader加载tools/docs/目录下所有MD文件
          - 使用MarkdownHeaderTextSplitter按标题分割
          - 创建Chroma向量存储
        出参: 无 (设置self.vectorstore)
        """
        # 加载所有Markdown文档
        loader = DirectoryLoader(
            str(TOOLS_DOCS_DIR),
            glob="**/*.md",
            loader_cls=UnstructuredMarkdownLoader,
            show_progress=True
        )
        
        try:
            documents = loader.load()
            print(f"📖 已加载 {len(documents)} 个Markdown文档")
        except Exception as e:
            print(f"❌ 加载Markdown文档失败: {e}")
            documents = []
        
        if not documents:
            print("⚠️ 未找到工具文档,请检查 tools/docs/ 目录")
            return
        
        # 按Markdown标题分割文档(可选,提升检索精度)
        headers_to_split_on = [
            ("#", "h1"),
            ("##", "h2"),
            ("###", "h3"),
        ]
        markdown_splitter = MarkdownHeaderTextSplitter(
            headers_to_split_on=headers_to_split_on
        )
        
        # 对每个文档进行分割
        all_splits = []
        for doc in documents:
            try:
                splits = markdown_splitter.split_text(doc.page_content)
                # 保留原始文档的source元数据
                for split in splits:
                    split.metadata.update(doc.metadata)
                all_splits.extend(splits)
            except Exception as e:
                print(f"⚠️ 分割文档 {doc.metadata.get('source', 'unknown')} 失败: {e}")
                all_splits.append(doc)  # 保留原始文档
        
        print(f"📄 共分割为 {len(all_splits)} 个文档片段")
        
        # 创建向量存储
        self.vectorstore = Chroma.from_documents(
            documents=all_splits,
            embedding=self.embeddings,
            collection_name="tool_docs",
            persist_directory=self.persist_directory
        )
        print(f"✅ 工具知识库构建完成: {len(all_splits)} 个文档片段已索引")
    
    def retrieve_relevant_tools(
        self,
        query: str,
        k: int = 3,
        score_threshold: float = 0.5
    ) -> str:
        """
        检索相关工具并组装提示词
        入参:
          - query: string 用户问题
          - k: int 返回top-k个相关文档片段 (默认3)
          - score_threshold: float 相关性阈值 (0-1, 默认0.5)
        方法:
          - 向量相似度搜索
          - 按相关性分数过滤
          - 拼接为SystemMessage片段
        出参:
          - string: 包含相关工具说明的提示词
        """
        if not self.vectorstore:
            return "工具知识库未初始化"
        
        # 执行相似度搜索(带分数)
        docs_with_scores = self.vectorstore.similarity_search_with_score(query, k=k)
        
        # 过滤低相关性文档
        relevant_docs = [
            doc for doc, score in docs_with_scores 
            if score >= score_threshold
        ]
        
        if not relevant_docs:
            # 回退: 至少返回top-1
            relevant_docs = [docs_with_scores[0][0]] if docs_with_scores else []
        
        # 拼接提示词
        if relevant_docs:
            tools_content = "\n\n".join([doc.page_content for doc in relevant_docs])
            return f"=== 相关工具说明 ===\n{tools_content}\n"
        else:
            return "未找到相关工具"
    


# ===== 全局单例实例 =====
_knowledge_base_instance: ToolKnowledgeBase = None


def get_knowledge_base(
    persist_directory: str = None,
    api_key: str = None,
    base_url: str = None
) -> ToolKnowledgeBase:
    """
    获取工具知识库单例实例
    入参:
      - persist_directory: string 持久化目录(可选)
      - api_key: string API密钥(可选)
      - base_url: string API地址(可选)
    方法:
      - 单例模式,只初始化一次
    出参:
      - ToolKnowledgeBase: 知识库实例
    """
    global _knowledge_base_instance
    if _knowledge_base_instance is None:
        _knowledge_base_instance = ToolKnowledgeBase(
            persist_directory=persist_directory or "./tools/chroma_db",
            api_key=api_key,
            base_url=base_url
        )
    return _knowledge_base_instance

