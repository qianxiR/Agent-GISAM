"""
共享的知识库（RAG）管理模块
提供 RAGSystem 的单例获取与知识库更新检查/重建方法
"""
from pathlib import Path
from typing import Optional

# 导入RAG系统
import sys
rag_path = Path(__file__).resolve().parents[1] / "rag"
sys.path.append(str(rag_path))
from rag.rag_system import RAGSystem  # type: ignore


# RAG系统实例缓存（模块级单例）
_rag_system_cache: Optional[RAGSystem] = None


def get_rag_system() -> RAGSystem:
    """获取RAG系统实例（单例模式）"""
    global _rag_system_cache
    if _rag_system_cache is None:
        print("🔧 初始化RAG知识库系统...")
        _rag_system_cache = RAGSystem()

        # 检查知识库状态
        knowledge_base_path = Path(__file__).resolve().parents[1] / "rag" / "知识库"
        vector_db_path = Path(__file__).resolve().parents[1] / "rag" / "vector_db"

        if knowledge_base_path.exists():
            doc_count = len([f for f in knowledge_base_path.rglob("*") if f.is_file()])
            print(f"📚 发现知识库文档: {doc_count} 个文件")
        else:
            print("⚠️ 知识库目录不存在")

        if vector_db_path.exists():
            print("📊 发现已存在的向量数据库，正在加载...")
        else:
            print("🔄 向量数据库不存在，将创建新的向量数据库...")

        _rag_system_cache.build_knowledge_base(force_rebuild=False)
        print("✅ RAG知识库系统初始化完成")

    return _rag_system_cache


def _initialize_rag_system():
    """在模块加载时初始化RAG系统"""
    print("🔧 正在初始化RAG知识库系统...")

    # 检查知识库状态
    knowledge_base_path = Path(__file__).resolve().parents[1] / "rag" / "知识库"
    vector_db_path = Path(__file__).resolve().parents[1] / "rag" / "vector_db"

    if knowledge_base_path.exists():
        doc_count = len([f for f in knowledge_base_path.rglob("*") if f.is_file()])
        print(f"📚 发现知识库文档: {doc_count} 个文件")
    else:
        print("⚠️ 知识库目录不存在")
        return

    if vector_db_path.exists():
        print("📊 发现已存在的向量数据库，正在加载...")
    else:
        print("🔄 向量数据库不存在，将创建新的向量数据库...")

    global _rag_system_cache
    _rag_system_cache = RAGSystem()
    _rag_system_cache.build_knowledge_base(force_rebuild=False)

    print("✅ RAG知识库系统初始化完成")
    print("🎯 知识库已准备就绪，可以开始查询！")


def check_knowledge_base_update():
    """检查知识库是否需要更新"""
    global _rag_system_cache
    if _rag_system_cache is None:
        return False

    knowledge_base_path = Path(__file__).resolve().parents[1] / "rag" / "知识库"
    vector_db_path = Path(__file__).resolve().parents[1] / "rag" / "vector_db"

    if not vector_db_path.exists():
        return True

    latest_kb_time = 0
    for file_path in knowledge_base_path.rglob("*"):
        if file_path.is_file():
            latest_kb_time = max(latest_kb_time, file_path.stat().st_mtime)

    vector_db_time = vector_db_path.stat().st_mtime
    return latest_kb_time > vector_db_time


def update_knowledge_base_if_needed():
    """如果需要，更新知识库"""
    if check_knowledge_base_update():
        print("🔄 检测到知识库更新，正在重建...")
        global _rag_system_cache
        _rag_system_cache = None
        get_rag_system()
        print("✅ 知识库更新完成")


# 模块加载时预热
_initialize_rag_system()


__all__ = [
    "get_rag_system",
    "check_knowledge_base_update",
    "update_knowledge_base_if_needed",
    "_rag_system_cache",
]


