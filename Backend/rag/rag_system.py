"""
RAG知识库系统 - 基于LangChain和Qwen模型
参考app.py的配置方式，使用知识库数据进行检索增强生成
"""
import os
import sys
from pathlib import Path
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv
import uuid

# 添加项目根目录到Python路径
project_root = Path(__file__).resolve().parents[2]
sys.path.append(str(project_root))

# 加载环境变量
env_path = project_root / ".env"
if env_path.exists():
    load_dotenv(dotenv_path=str(env_path))

# LangChain相关导入
from langchain_community.document_loaders import TextLoader, PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.chains import RetrievalQA
from langchain.chat_models import init_chat_model
from langchain.prompts import PromptTemplate
from langchain.schema import Document


class RAGSystem:
    """RAG知识库系统"""
    
    def __init__(self, knowledge_base_path: str = None):
        """
        初始化RAG系统
        
        Args:
            knowledge_base_path: 知识库文件路径
        """
        # 设置知识库路径
        if knowledge_base_path is None:
            self.knowledge_base_path = Path(__file__).parent / "知识库"
        else:
            self.knowledge_base_path = Path(knowledge_base_path)
            
        # 初始化模型配置（参考app.py的方式）
        self.api_key = os.getenv("DASHSCOPE_API_KEY", "")
        self.base_url = os.getenv("DASHSCOPE_BASE_URL", "https://dashscope.aliyuncs.com/compatible-mode/v1")
        self.model = os.getenv("DASHSCOPE_MODEL", "qwen-plus")
        
        # 设置环境变量
        os.environ.setdefault("OPENAI_API_KEY", self.api_key)
        os.environ.setdefault("OPENAI_BASE_URL", self.base_url)
        
        # 初始化组件
        self.embeddings = None
        self.llm = None
        self.vector_store = None
        self.qa_chain = None
        
        # 初始化模型
        self._initialize_models()
        
    def _initialize_models(self):
        """初始化Embedding和LLM模型"""
        try:
            # 初始化Embedding模型（使用通义千问的embedding模型）
            from langchain_community.embeddings import DashScopeEmbeddings
            self.embeddings = DashScopeEmbeddings(
                model="text-embedding-v2",
                dashscope_api_key=self.api_key
            )
            print("✅ Embedding模型初始化成功")
            
            # 初始化LLM模型（参考app.py的方式）
            self.llm = init_chat_model(f"openai:{self.model}")
            print("✅ LLM模型初始化成功")
            
        except Exception as e:
            print(f"❌ 模型初始化失败: {e}")
            raise
    
    def load_documents(self) -> List[Document]:
        """
        加载知识库文档
        
        Returns:
            List[Document]: 加载的文档列表
        """
        documents = []
        
        if not self.knowledge_base_path.exists():
            print(f"❌ 知识库路径不存在: {self.knowledge_base_path}")
            return documents
            
        print(f"📚 开始加载知识库: {self.knowledge_base_path}")
        
        # 支持的文件类型
        supported_extensions = {'.txt', '.md', '.pdf'}
        
        for file_path in self.knowledge_base_path.rglob("*"):
            if file_path.is_file() and file_path.suffix.lower() in supported_extensions:
                try:
                    print(f"📄 加载文件: {file_path.name}")
                    
                    if file_path.suffix.lower() == '.pdf':
                        loader = PyPDFLoader(str(file_path))
                    else:
                        loader = TextLoader(str(file_path), encoding='utf-8')
                    
                    docs = loader.load()
                    
                    # 为文档添加元数据
                    for doc in docs:
                        doc.metadata.update({
                            'source': str(file_path),
                            'filename': file_path.name,
                            'file_type': file_path.suffix
                        })
                    
                    documents.extend(docs)
                    print(f"✅ 成功加载 {len(docs)} 个文档片段")
                    
                except Exception as e:
                    print(f"❌ 加载文件失败 {file_path.name}: {e}")
                    continue
        
        print(f"📊 总共加载了 {len(documents)} 个文档片段")
        return documents
    
    def split_documents(self, documents: List[Document]) -> List[Document]:
        """
        文档分块处理
        
        Args:
            documents: 原始文档列表
            
        Returns:
            List[Document]: 分块后的文档列表
        """
        print("✂️ 开始文档分块处理...")
        
        # 创建文本分割器
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,      # 每个块的最大字符数
            chunk_overlap=200,    # 块之间的重叠字符数
            length_function=len,
            separators=["\n\n", "\n", "。", "！", "？", "；", " ", ""]
        )
        
        # 分割文档
        split_docs = text_splitter.split_documents(documents)
        
        print(f"✅ 文档分块完成，共生成 {len(split_docs)} 个文本块")
        return split_docs
    
    def create_vector_store(self, documents: List[Document], save_path: str = "vector_db"):
        """
        创建向量数据库
        
        Args:
            documents: 分块后的文档列表
            save_path: 向量数据库保存路径
        """
        print("🔍 开始创建向量数据库...")
        
        try:
            # 使用LangChain的标准方法创建向量存储
            from langchain_community.vectorstores import FAISS
            
            # 提取文档内容并清理
            clean_documents = []
            for doc in documents:
                # 确保内容是字符串类型且非空
                content = str(doc.page_content).strip()
                if content and len(content) > 10:  # 过滤太短的内容
                    clean_doc = Document(
                        page_content=content,
                        metadata=doc.metadata
                    )
                    clean_documents.append(clean_doc)
            
            print(f"📝 准备向量化 {len(clean_documents)} 个文本块...")
            
            # 使用LangChain的标准方法创建FAISS向量存储
            self.vector_store = FAISS.from_documents(clean_documents, self.embeddings)
            
            # 保存向量数据库
            self.vector_store.save_local(save_path)
            print(f"✅ 向量数据库创建完成，已保存到: {save_path}")
            
        except Exception as e:
            print(f"❌ 创建向量数据库失败: {e}")
            # 如果标准方法失败，尝试手动创建
            print("🔄 尝试使用备用方法创建向量数据库...")
            self._create_vector_store_manual(documents, save_path)
    
    def _create_vector_store_manual(self, documents: List[Document], save_path: str):
        """备用方法：手动创建向量数据库"""
        try:
            # 提取文本和元数据
            texts = []
            metadatas = []
            
            for doc in documents:
                content = str(doc.page_content).strip()
                if content and len(content) > 10:
                    texts.append(content)
                    metadatas.append(doc.metadata)
            
            print(f"📝 手动方法：准备向量化 {len(texts)} 个文本块...")
            
            # 分批处理embedding
            batch_size = 5  # 减小批次大小
            all_embeddings = []
            
            for i in range(0, len(texts), batch_size):
                batch_texts = texts[i:i + batch_size]
                print(f"🔄 处理批次 {i//batch_size + 1}/{(len(texts) + batch_size - 1)//batch_size}")
                
                try:
                    batch_embeddings = self.embeddings.embed_documents(batch_texts)
                    all_embeddings.extend(batch_embeddings)
                except Exception as batch_error:
                    print(f"⚠️ 批次处理失败，跳过该批次: {batch_error}")
                    continue
            
            if not all_embeddings:
                raise ValueError("没有成功生成任何向量")
            
            # 使用简单的FAISS索引
            import numpy as np
            import faiss
            
            embeddings_array = np.array(all_embeddings, dtype=np.float32)
            dimension = embeddings_array.shape[1]
            
            # 创建简单的L2距离索引
            index = faiss.IndexFlatL2(dimension)
            index.add(embeddings_array)
            
            # 创建FAISS向量存储
            from langchain_community.vectorstores import FAISS
            self.vector_store = FAISS(self.embeddings, index, metadatas, texts)
            
            # 保存向量数据库
            self.vector_store.save_local(save_path)
            print(f"✅ 备用方法创建向量数据库成功，已保存到: {save_path}")
            
        except Exception as e:
            print(f"❌ 备用方法也失败了: {e}")
            raise
    
    def load_vector_store(self, load_path: str = "vector_db"):
        """
        加载已存在的向量数据库
        
        Args:
            load_path: 向量数据库路径
        """
        print(f"📂 加载向量数据库: {load_path}")
        
        try:
            self.vector_store = FAISS.load_local(load_path, self.embeddings, allow_dangerous_deserialization=True)
            print("✅ 向量数据库加载成功")
        except Exception as e:
            print(f"❌ 加载向量数据库失败: {e}")
            raise
    
    def create_qa_chain(self):
        """创建问答链"""
        if self.vector_store is None:
            raise ValueError("向量数据库未初始化，请先创建或加载向量数据库")
        
        print("🔗 创建问答链...")
        
        # 创建检索器
        retriever = self.vector_store.as_retriever(
            search_type="similarity",
            search_kwargs={"k": 3}  # 检索最相关的3个文档块
        )
        
        # 创建自定义提示模板
        prompt_template = """
你是一个专业的GIS和地理信息助手。请基于以下检索到的文档内容回答用户的问题。

检索到的相关内容：
{context}

用户问题：{question}

请根据检索到的内容提供准确、详细的回答。如果检索到的内容不足以回答问题，请说明并建议用户提供更多信息。

回答：
"""
        
        PROMPT = PromptTemplate(
            template=prompt_template,
            input_variables=["context", "question"]
        )
        
        # 创建问答链
        self.qa_chain = RetrievalQA.from_chain_type(
            llm=self.llm,
            chain_type="stuff",
            retriever=retriever,
            chain_type_kwargs={"prompt": PROMPT},
            return_source_documents=True
        )
        
        print("✅ 问答链创建成功")
    
    def query(self, question: str, include_sources: bool = True) -> Dict[str, Any]:
        """
        执行查询
        
        Args:
            question: 用户问题
            include_sources: 是否在回答中包含来源信息
            
        Returns:
            Dict[str, Any]: 查询结果
        """
        if self.qa_chain is None:
            raise ValueError("问答链未初始化，请先创建问答链")
        
        print(f"❓ 用户问题: {question}")
        
        try:
            # 执行查询
            result = self.qa_chain.invoke({"query": question})
            
            # 处理来源文档
            source_documents = [
                {
                    "content": doc.page_content[:200] + "..." if len(doc.page_content) > 200 else doc.page_content,
                    "source": doc.metadata.get("source", "未知"),
                    "filename": doc.metadata.get("filename", "未知")
                }
                for doc in result["source_documents"]
            ]
            
            # 构建回答
            answer = result["result"]
            
            # 如果需要在回答中包含来源信息
            if include_sources and source_documents:
                source_info = "\n\n**📚 参考来源：**\n"
                for i, doc in enumerate(source_documents, 1):
                    filename = doc["filename"]
                    source_info += f"{i}. {filename}\n"
                
                answer += source_info
            
            # 格式化结果
            response = {
                "question": question,
                "answer": answer,
                "source_documents": source_documents,
                "task_id": f"rag_{uuid.uuid4().hex[:8]}"
            }
            
            print("✅ 查询完成")
            return response
            
        except Exception as e:
            print(f"❌ 查询失败: {e}")
            return {
                "question": question,
                "answer": f"查询失败: {str(e)}",
                "source_documents": [],
                "task_id": f"rag_{uuid.uuid4().hex[:8]}"
            }
    
    def build_knowledge_base(self, force_rebuild: bool = False):
        """
        构建知识库（完整流程）
        
        Args:
            force_rebuild: 是否强制重建
        """
        vector_db_path = "vector_db"
        
        # 检查是否已存在向量数据库
        if not force_rebuild and Path(vector_db_path).exists():
            print("📂 发现已存在的向量数据库，直接加载...")
            self.load_vector_store(vector_db_path)
            print("✅ 向量数据库加载完成")
        else:
            print("🔨 开始构建知识库...")
            
            # 1. 加载文档
            print("📖 正在加载文档...")
            documents = self.load_documents()
            if not documents:
                raise ValueError("未找到任何文档，请检查知识库路径")
            print(f"✅ 成功加载 {len(documents)} 个文档")
            
            # 2. 文档分块
            print("✂️ 正在分块处理文档...")
            split_docs = self.split_documents(documents)
            print(f"✅ 文档分块完成，共 {len(split_docs)} 个文本块")
            
            # 3. 创建向量数据库
            print("🔍 正在创建向量数据库...")
            self.create_vector_store(split_docs, vector_db_path)
            print("✅ 向量数据库创建完成")
        
        # 4. 创建问答链
        print("🔗 正在创建问答链...")
        self.create_qa_chain()
        print("✅ 问答链创建完成")
        
        print("🎉 知识库构建完成！")


def main():
    """主函数 - 测试RAG系统"""
    print("🚀 启动RAG知识库系统测试")
    
    try:
        # 初始化RAG系统
        rag = RAGSystem()
        
        # 构建知识库
        rag.build_knowledge_base()
        
        # 测试查询
        test_questions = [
            "武汉市的地理位置和气候特征是什么？",
            "武汉有哪些主要的水系和湖泊？",
            "武汉的历史发展概况如何？",
            "武汉的经济发展现状如何？"
        ]
        
        print("\n" + "="*50)
        print("开始测试查询...")
        print("="*50)
        
        for question in test_questions:
            print(f"\n🔍 测试问题: {question}")
            result = rag.query(question)
            
            print(f"📝 回答: {result['answer']}")
            print(f"📚 参考文档数量: {len(result['source_documents'])}")
            
            if result['source_documents']:
                print("📄 参考文档:")
                for i, doc in enumerate(result['source_documents'], 1):
                    print(f"  {i}. {doc['filename']}: {doc['content']}")
            
            print("-" * 50)
        
        print("\n✅ RAG系统测试完成！")
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
