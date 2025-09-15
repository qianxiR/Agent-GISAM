"""
Agent Service - FastAPI entry for LLM chat proxy with full LLM management features

Usage (dev):
  python -m uvicorn agent.app:app --reload --host 0.0.0.0 --port 8089
"""
from fastapi import FastAPI, APIRouter, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import uvicorn
import os
import uuid
import json
from pathlib import Path
from dotenv import load_dotenv
from langchain_community.chat_models.tongyi import ChatTongyi
from langchain_core.tools import tool
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage, ToolMessage
import urllib3
from langchain.chat_models import init_chat_model
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import create_react_agent
from langchain_tavily import TavilySearch
from openai import OpenAI

# 关闭全局SSL验证以规避企业网络或中间代理引起的握手问题
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
os.environ["PYTHONHTTPSVERIFY"] = "0"


class LLMSettings(BaseModel):
    api_key: str = Field(default_factory=lambda: os.getenv("DASHSCOPE_API_KEY", ""))
    base_url: str = Field(default_factory=lambda: os.getenv("DASHSCOPE_BASE_URL", "https://dashscope.aliyuncs.com/compatible-mode/v1"))
    model: str = Field(default_factory=lambda: os.getenv("DASHSCOPE_MODEL", "qwen-plus"))
    temperature: float = Field(default_factory=lambda: float(os.getenv("DASHSCOPE_TEMPERATURE", "0.7")))
    max_tokens: int = Field(default_factory=lambda: int(os.getenv("DASHSCOPE_MAX_TOKENS", "3000")))
    cors_origins: str = Field(default_factory=lambda: os.getenv("CORS_ORIGINS", "*"))

    def cors_list(self) -> List[str]:
        raw = self.cors_origins or "*"
        if raw == "*":
            return ["*"]
        return [o.strip() for o in raw.split(",")]


# 加载后端环境变量文件 Backend/.env
_ROOT = Path(__file__).resolve().parents[2]
_ENV_PATH = _ROOT / ".env"
if _ENV_PATH.exists():
    load_dotenv(dotenv_path=str(_ENV_PATH))

settings = LLMSettings()
os.environ.setdefault("OPENAI_API_KEY", settings.api_key)
os.environ.setdefault("OPENAI_BASE_URL", settings.base_url)
class ChatResponse(BaseModel):
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    task_id: Optional[str] = None



# 导入工具函数
from .tools import (
    toggle_layer_visibility,
    query_features_by_attribute,
    save_query_results_as_layer,
    get_open_layers,
    execute_buffer_analysis,
    execute_intersection_analysis,
    execute_erase_analysis,
    execute_shortest_path_analysis,
    save_buffer_results_as_layer,
    save_intersection_results_as_layer,
    save_erase_results_as_layer,
    save_path_results_as_layer
)

# 导入RAG系统
import sys
from pathlib import Path
rag_path = Path(__file__).resolve().parents[1] / "rag"
sys.path.append(str(rag_path))
from rag_system import RAGSystem

# 知识库查询工具
@tool
def query_knowledge_base(question: str) -> str:
    """
    查询知识库获取相关信息
    
    Args:
        question: 用户问题，例如"武汉市的基本概况是什么？"
    
    Returns:
        str: 基于知识库的回答，包含参考来源
    """
    try:
        # 检查并更新知识库
        update_knowledge_base_if_needed()
        
        # 获取RAG系统并查询
        rag_system = get_rag_system()
        result = rag_system.query(question, include_sources=True)
        
        # 构建包含来源信息的完整回答
        answer = result['answer']
        
        # 如果RAG系统没有自动添加来源信息，手动添加
        if '**📚 参考来源：**' not in answer and result.get('source_documents'):
            source_info = "\n\n**📚 参考来源：**\n"
            for i, doc in enumerate(result['source_documents'], 1):
                filename = doc.get('filename', '未知文件')
                source_info += f"{i}. {filename}\n"
            answer += source_info
        
        return answer
        
    except Exception as e:
        return f"知识库查询失败: {str(e)}"

@tool
def update_knowledge_base() -> str:
    """
    手动更新知识库
    
    Returns:
        str: 更新结果信息
    """
    try:
        global _rag_system_cache
        _rag_system_cache = None  # 清除缓存
        get_rag_system()  # 重新初始化
        return "知识库更新成功"
        
    except Exception as e:
        return f"知识库更新失败: {str(e)}"

# 系统提示词缓存 - 在模块加载时初始化
_system_prompt_cache: Optional[str] = None

def _initialize_system_prompt():
    """初始化系统提示词（在模块加载时调用）"""
    global _system_prompt_cache
    
    if _system_prompt_cache is not None:
        return _system_prompt_cache
    
    base = Path(__file__).resolve().parent
    prompt_path = base / "prompt.md"
    try:
        content = prompt_path.read_text(encoding="utf-8")
        _system_prompt_cache = content
        print(f"✅ 系统提示词已预加载并缓存: {prompt_path}")
        return content
    except Exception as e:
        print(f"❌ 加载系统提示词失败: {e}")
        fallback_prompt = "You are a helpful spatial analysis assistant."
        _system_prompt_cache = fallback_prompt
        return fallback_prompt

def load_system_prompt() -> str:
    """获取系统提示词（从缓存中读取，无需重复加载）"""
    global _system_prompt_cache
    
    if _system_prompt_cache is None:
        return _initialize_system_prompt()
    
    return _system_prompt_cache

# 在模块加载时预加载系统提示词
_initialize_system_prompt()


router = APIRouter(prefix="/agent", tags=["agent"])

# 会话图层操作历史：conversation_id -> ["action:layer_id", ...]
_conversation_layer_history: Dict[str, List[str]] = {}

# 多轮对话历史：conversation_id -> [{"role": "user/assistant", "content": "...", "timestamp": "..."}, ...]
_conversation_history: Dict[str, List[Dict[str, Any]]] = {}

# RAG系统实例缓存
_rag_system_cache: Optional[RAGSystem] = None

# 工具调用统计
_tool_call_stats: Dict[str, int] = {}

# 工具执行状态历史
_tool_execution_history: List[Dict[str, Any]] = []


def generate_task_id() -> str:
    """生成唯一任务ID"""
    return f"task_{uuid.uuid4().hex[:12]}"

def get_current_timestamp() -> str:
    """获取当前时间戳"""
    from datetime import datetime
    return datetime.now().isoformat()

def detect_keywords_and_structure(user_input: str, conversation_id: str) -> str:
    """
    关键词检测与结构化处理
    
    输入数据格式：
      - user_input: 用户原始输入
      - conversation_id: 对话ID
    
    数据处理方法：
      - 检测关键词（缓冲区分析、相交分析等）
      - 提取图层名称和参数
      - 基于对话历史推断分析类型
      - 生成结构化的工具调用指令
    
    输出数据格式：
      - 结构化的用户指令，包含明确的工具调用意图
    """
    # 关键词检测
    keywords = {
        "导出为图层": ["导出为图层", "保存为图层", "导出图层", "保存图层"],
        "缓冲区分析": ["缓冲区分析", "缓冲区", "缓冲"],
        "相交分析": ["相交分析", "相交", "交集"],
        "擦除分析": ["擦除分析", "擦除", "去除"],
        "最短路径": ["最短路径", "路径分析", "路径规划"],
        "显示图层": ["显示", "打开", "show"],
        "隐藏图层": ["隐藏", "关闭", "hide"],
        "查询属性": ["查询", "查找", "筛选"]
    }
    
    # 图层名称关键词
    layer_keywords = ["学校", "医院", "居民点", "水系", "道路", "铁路", "水文站点"]
    
    # 检测关键词
    detected_keywords = []
    for key, values in keywords.items():
        for value in values:
            if value in user_input:
                detected_keywords.append(key)
                break
    
    # 检测图层名称
    detected_layers = []
    for layer in layer_keywords:
        if layer in user_input:
            detected_layers.append(layer)
    
    # 获取对话历史中的最近分析类型
    recent_analysis_type = get_recent_analysis_type(conversation_id)
    
    # 生成结构化指令
    if detected_keywords:
        structured_instruction = f"检测到关键词: {', '.join(detected_keywords)}"
        if detected_layers:
            structured_instruction += f"\n检测到图层: {', '.join(detected_layers)}"
        if recent_analysis_type:
            structured_instruction += f"\n最近分析类型: {recent_analysis_type}"
        
        structured_instruction += f"\n原始用户输入: {user_input}"
        structured_instruction += "\n\n请基于关键词强制调用对应的工具，不要询问用户确认。"
        
        return structured_instruction
    
    return user_input

def get_recent_analysis_type(conversation_id: str) -> str:
    """获取最近的分析类型"""
    if conversation_id not in _conversation_layer_history:
        return ""
    
    history = _conversation_layer_history[conversation_id]
    if not history:
        return ""
    
    # 检查最近的操作
    recent_operations = history[-3:]  # 检查最近3个操作
    
    for operation in reversed(recent_operations):
        if "buffer" in operation.lower():
            return "缓冲区分析"
        elif "intersection" in operation.lower():
            return "相交分析"
        elif "erase" in operation.lower():
            return "擦除分析"
        elif "shortest_path" in operation.lower():
            return "最短路径分析"
        elif "query" in operation.lower():
            return "属性查询"
    
    return ""

def force_tool_call_based_on_keywords(user_input: str, conversation_id: str) -> Optional[Dict[str, Any]]:
    """
    基于关键词强制生成工具调用
    
    输入数据格式：
      - user_input: 用户输入
      - conversation_id: 对话ID
    
    数据处理方法：
      - 检测关键词并确定工具类型
      - 基于对话历史推断分析类型
      - 生成对应的工具调用结构
    
    输出数据格式：
      - 工具调用字典或None
    """
    
    # 检测保存为图层相关关键词
    if any(keyword in user_input for keyword in ["导出为图层", "保存为图层", "导出图层", "保存图层"]):
        recent_analysis = get_recent_analysis_type(conversation_id)
        
        if recent_analysis == "缓冲区分析":
            return {
                "name": "save_buffer_results_as_layer",
                "args": {"layer_name": "缓冲区分析结果"},
                "id": f"call_{uuid.uuid4().hex[:8]}"
            }
        elif recent_analysis == "相交分析":
            return {
                "name": "save_intersection_results_as_layer",
                "args": {"layer_name": "相交分析结果"},
                "id": f"call_{uuid.uuid4().hex[:8]}"
            }
        elif recent_analysis == "擦除分析":
            return {
                "name": "save_erase_results_as_layer",
                "args": {"layer_name": "擦除分析结果"},
                "id": f"call_{uuid.uuid4().hex[:8]}"
            }
        elif recent_analysis == "最短路径分析":
            return {
                "name": "save_path_results_as_layer",
                "args": {"layer_name": "最短路径分析结果"},
                "id": f"call_{uuid.uuid4().hex[:8]}"
            }
        elif recent_analysis == "属性查询":
            return {
                "name": "save_query_results_as_layer",
                "args": {"layer_name": "查询结果"},
                "id": f"call_{uuid.uuid4().hex[:8]}"
            }
    
    return None

async def create_task() -> str:
    """创建新任务"""
    task_id = generate_task_id()
    return task_id

def get_rag_system() -> RAGSystem:
    """获取RAG系统实例（单例模式）"""
    global _rag_system_cache
    
    if _rag_system_cache is None:
        try:
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
            
        except Exception as e:
            print(f"❌ RAG系统初始化失败: {e}")
            raise
    
    return _rag_system_cache

# 在get_rag_system函数定义后初始化RAG系统
def _initialize_rag_system():
    """在模块加载时初始化RAG系统"""
    try:
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
        
        # 强制初始化RAG系统
        global _rag_system_cache
        _rag_system_cache = RAGSystem()
        _rag_system_cache.build_knowledge_base(force_rebuild=False)
        
        print("✅ RAG知识库系统初始化完成")
        print("🎯 知识库已准备就绪，可以开始查询！")
        
    except Exception as e:
        print(f"⚠️ RAG系统初始化失败: {e}")
        print("💡 系统将在首次使用时重新尝试初始化")

# 初始化RAG系统
_initialize_rag_system()

def check_knowledge_base_update():
    """检查知识库是否需要更新"""
    global _rag_system_cache
    
    if _rag_system_cache is None:
        return False
    
    try:
        # 检查知识库目录的修改时间
        knowledge_base_path = Path(__file__).resolve().parents[1] / "rag" / "知识库"
        vector_db_path = Path(__file__).resolve().parents[1] / "rag" / "vector_db"
        
        if not vector_db_path.exists():
            return True
        
        # 获取知识库目录的最新修改时间
        latest_kb_time = 0
        for file_path in knowledge_base_path.rglob("*"):
            if file_path.is_file():
                latest_kb_time = max(latest_kb_time, file_path.stat().st_mtime)
        
        # 获取向量数据库的修改时间
        vector_db_time = vector_db_path.stat().st_mtime
        
        # 如果知识库比向量数据库新，则需要更新
        return latest_kb_time > vector_db_time
        
    except Exception as e:
        print(f"⚠️ 检查知识库更新状态失败: {e}")
        return False

def update_knowledge_base_if_needed():
    """如果需要，更新知识库"""
    if check_knowledge_base_update():
        print("🔄 检测到知识库更新，正在重建...")
        global _rag_system_cache
        _rag_system_cache = None  # 清除缓存
        get_rag_system()  # 重新初始化
        print("✅ 知识库更新完成")

def add_to_conversation_history(conversation_id: str, role: str, content: str):
    """添加对话历史"""
    if conversation_id not in _conversation_history:
        _conversation_history[conversation_id] = []
    
    _conversation_history[conversation_id].append({
        "role": role,
        "content": content,
        "timestamp": get_current_timestamp()
    })
    
    # 限制历史记录长度，保留最近20轮对话
    if len(_conversation_history[conversation_id]) > 40:  # 20轮对话 = 40条消息
        _conversation_history[conversation_id] = _conversation_history[conversation_id][-40:]

def get_conversation_context(conversation_id: str, max_turns: int = 5) -> str:
    """获取对话上下文"""
    if conversation_id not in _conversation_history:
        return ""
    
    history = _conversation_history[conversation_id]
    if not history:
        return ""
    
    # 获取最近几轮对话
    recent_history = history[-(max_turns * 2):]  # 每轮包含用户和助手消息
    
    context_parts = []
    for msg in recent_history:
        role = "用户" if msg["role"] == "user" else "助手"
        context_parts.append(f"{role}: {msg['content']}")
    
    return "\n".join(context_parts)

def clear_conversation_history(conversation_id: str):
    """清除对话历史"""
    if conversation_id in _conversation_history:
        _conversation_history[conversation_id] = []
    if conversation_id in _conversation_layer_history:
        _conversation_layer_history[conversation_id] = []



class ToolChatRequest(BaseModel):
    model: str
    temperature: float
    prompt: str
    conversation_id: str = "default"




@router.post("/tool-chat")
async def tool_chat(req: ToolChatRequest):
    """
    LangChain 工具调用接口：
    输入数据格式：
      - model: LLM 模型名称
      - temperature: 采样温度
      - prompt: 用户问题（例如 What's 5 times forty two）
      - conversation_id: 对话会话ID
    数据处理方法：
      - 创建任务ID
      - 创建 OpenAI 兼容模型，并通过 bind_tools 绑定所有工具
      - 第一步调用：发送 HumanMessage(prompt)，获取包含 tool_calls 的 AIMessage
      - 执行工具：根据 AIMessage 中的工具与参数，执行相应工具并得到结果
      - 第二步调用：将工具结果以 ToolMessage 形式回传给模型，生成最终回答
    输出数据格式：
      - { success: true, data: { first_call: AIMessage, tool_result: string, final_answer: string }, task_id: string }
    """
    # 创建任务
    task_id = await create_task()
    print(f"\n🚀 开始处理对话请求")
    print(f"📋 任务ID: {task_id}")
    print(f"💬 用户输入: {req.prompt}")
    print(f"🆔 对话ID: {req.conversation_id}")
    print(f"🤖 模型: {req.model}")
    try:
        # 创建OpenAI客户端
        client = OpenAI(
            api_key=settings.api_key,
            base_url=settings.base_url,
        )
        
        model = init_chat_model(f"openai:{req.model}")

        # 特殊处理：异常值检测消息走纯文本分析路径（不调用任何工具）
        anomaly_mode = req.prompt.strip().startswith("🚨 [异常值检测]")
        if anomaly_mode:
            history_list = _conversation_layer_history.get(req.conversation_id, [])
            parsed_lines: List[str] = []
            last_action_text = ""
            for entry in history_list:
                if ":" in entry:
                    action, layer = entry.split(":", 1)
                    parsed_line = f"action={action}; layer={layer}"
                    parsed_lines.append(parsed_line)
                    last_action_text = f"action={action}; layer={layer}"
                else:
                    parsed_lines.append(entry)
                    last_action_text = entry
            history_text = "\n".join(parsed_lines)
            system_prompt = load_system_prompt()
            conversation_context = get_conversation_context(req.conversation_id)
            full_system_prompt = system_prompt
            if history_text:
                full_system_prompt += f"\n\n历史操作(顺序, 最新在下):\n{history_text}\n"
                full_system_prompt += f"最近一次操作: {last_action_text}。若用户问'刚才做了什么'，请直接依据最近几次操作回答。"
            if conversation_context:
                full_system_prompt += f"\n\n对话历史上下文:\n{conversation_context}\n"
                full_system_prompt += "请结合对话历史上下文理解用户的问题，保持对话的连贯性。"

            # 注入异常值检测专用分析指令
            full_system_prompt += (
                "\n\n【异常值检测处理规则】\n"
                "当用户消息以'🚨 [异常值检测]'开头时：\n"
                "1) 仅基于消息中的监测点化学指标（水温、pH、溶解氧、浊度、高锰酸盐指数、氨氮、总磷、总氮、叶绿素a、藻类密度等）进行详细的专业分析；\n"
                "2) 输出结构包含：异常项判读、潜在成因研判、对水资源与生态的影响评估、监测与治理的下一步建议；\n"
                "3) 不调用任何工具与外部接口，不返回工具调用指令或图层操作指令；\n"
                "4) 用简洁专业的中文给出结论与可执行建议。\n"
            )

            add_to_conversation_history(req.conversation_id, "user", req.prompt)
            final_ai = model.invoke([
                SystemMessage(content=full_system_prompt),
                HumanMessage(content=req.prompt)
            ])

            if not getattr(final_ai, "content", None) or str(final_ai.content).strip() == "":
                final_ai.content = "已完成异常值检测消息的分析与建议。"

            add_to_conversation_history(req.conversation_id, "assistant", final_ai.content)
            return ChatResponse(success=True, data={"first_call": {"tool_calls": []}, "tool_result": None, "final_answer": final_ai.content}, task_id=task_id)

        llm_with_tools = model.bind_tools([
            # 知识库工具
            query_knowledge_base,
            update_knowledge_base,
            # 图层管理工具
            toggle_layer_visibility, 
            query_features_by_attribute, 
            save_query_results_as_layer, 
            get_open_layers,
            # 空间分析工具
            execute_buffer_analysis, 
            execute_intersection_analysis, 
            execute_erase_analysis, 
            execute_shortest_path_analysis,
            # 结果保存工具
            save_buffer_results_as_layer,
            save_intersection_results_as_layer,
            save_erase_results_as_layer,
            save_path_results_as_layer
        ])
        history_list = _conversation_layer_history.get(req.conversation_id, [])
        parsed_lines: List[str] = []
        last_action_text = ""
        for entry in history_list:
            if ":" in entry:
                action, layer = entry.split(":", 1)
                parsed_line = f"action={action}; layer={layer}"
                parsed_lines.append(parsed_line)
                last_action_text = f"action={action}; layer={layer}"
            else:
                parsed_lines.append(entry)
                last_action_text = entry
        history_text = "\n".join(parsed_lines)
        
        # 加载系统提示词
        system_prompt = load_system_prompt()
        
        # 获取对话上下文
        conversation_context = get_conversation_context(req.conversation_id)
        
        # 构建完整的系统提示词
        full_system_prompt = system_prompt
        if history_text:
            full_system_prompt += f"\n\n历史操作(顺序, 最新在下):\n{history_text}\n"
            full_system_prompt += f"最近一次操作: {last_action_text}。若用户问'刚才做了什么'，请直接依据最近几次操作回答。"
        
        if conversation_context:
            full_system_prompt += f"\n\n对话历史上下文:\n{conversation_context}\n"
            full_system_prompt += "请结合对话历史上下文理解用户的问题，保持对话的连贯性。"
        
        # 添加用户消息到对话历史
        add_to_conversation_history(req.conversation_id, "user", req.prompt)
        
        # 关键词检测与结构化处理
        structured_prompt = detect_keywords_and_structure(req.prompt, req.conversation_id)
        
        first_ai: AIMessage = llm_with_tools.invoke([
            SystemMessage(content=full_system_prompt),
            HumanMessage(content=structured_prompt)
        ])
        
        # 如果没有工具调用，尝试强制调用基于关键词检测
        if not first_ai.tool_calls:
            print("🔍 未检测到工具调用，尝试基于关键词强制调用...")
            forced_tool_call = force_tool_call_based_on_keywords(req.prompt, req.conversation_id)
            if forced_tool_call:
                print(f"⚡ 强制调用工具: {forced_tool_call['name']}")
                first_ai.tool_calls = [forced_tool_call]
            else:
                print("💬 无工具调用，返回纯文本回复")
                return ChatResponse(success=True, data={"first_call": {"tool_calls": []}, "tool_result": None, "final_answer": first_ai.content}, task_id=task_id)
        
        tool_call = first_ai.tool_calls[0]
        tool_args = tool_call.get("args", {})
        
        # 根据工具名称执行相应的工具
        tool_name = tool_call.get("name", "")
        print(f"🔧 Agent调用工具: {tool_name}")
        print(f"📝 工具参数: {tool_args}")
        
        if tool_name == "query_knowledge_base":
            tool_result = query_knowledge_base.invoke(tool_args)
        elif tool_name == "update_knowledge_base":
            tool_result = update_knowledge_base.invoke(tool_args)
        elif tool_name == "toggle_layer_visibility":
            tool_result = toggle_layer_visibility.invoke(tool_args)
        elif tool_name == "query_features_by_attribute":
            tool_result = query_features_by_attribute.invoke(tool_args)
        elif tool_name == "save_query_results_as_layer":
            tool_result = save_query_results_as_layer.invoke(tool_args)
        elif tool_name == "get_open_layers":
            tool_result = get_open_layers.invoke(tool_args)
        elif tool_name == "execute_buffer_analysis":
            tool_result = execute_buffer_analysis.invoke(tool_args)
        elif tool_name == "execute_intersection_analysis":
            tool_result = execute_intersection_analysis.invoke(tool_args)
        elif tool_name == "execute_erase_analysis":
            tool_result = execute_erase_analysis.invoke(tool_args)
        elif tool_name == "execute_shortest_path_analysis":
            tool_result = execute_shortest_path_analysis.invoke(tool_args)
        elif tool_name == "save_buffer_results_as_layer":
            tool_result = save_buffer_results_as_layer.invoke(tool_args)
        elif tool_name == "save_intersection_results_as_layer":
            tool_result = save_intersection_results_as_layer.invoke(tool_args)
        elif tool_name == "save_erase_results_as_layer":
            tool_result = save_erase_results_as_layer.invoke(tool_args)
        elif tool_name == "save_path_results_as_layer":
            tool_result = save_path_results_as_layer.invoke(tool_args)
        else:
            tool_result = f"未知工具: {tool_name}"
        
        print(f"✅ 工具执行完成: {tool_name}")
        print(f"📊 工具结果: {str(tool_result)[:200]}{'...' if len(str(tool_result)) > 200 else ''}")
        
        # 更新工具调用统计
        _tool_call_stats[tool_name] = _tool_call_stats.get(tool_name, 0) + 1
        print(f"📈 工具调用统计: {tool_name} (总计: {_tool_call_stats[tool_name]}次)")
        
        # 记录工具执行状态
        execution_record = {
            "timestamp": get_current_timestamp(),
            "task_id": task_id,
            "conversation_id": req.conversation_id,
            "tool_name": tool_name,
            "tool_args": tool_args,
            "execution_status": "success",
            "result_preview": str(tool_result)[:100] + "..." if len(str(tool_result)) > 100 else str(tool_result)
        }
        _tool_execution_history.append(execution_record)
        
        # 限制历史记录长度，保留最近100条
        if len(_tool_execution_history) > 100:
            _tool_execution_history[:] = _tool_execution_history[-100:]
        
        # 记录历史：优先记录action；若保存/导出操作，按分析类型归档
        if isinstance(tool_result, dict) and "action" in tool_result:
            history_entry = tool_result.get("action")
        else:
            history_entry = tool_result if isinstance(tool_result, str) else str(tool_result)
        if req.conversation_id in _conversation_layer_history:
            _conversation_layer_history[req.conversation_id].append(history_entry)
        else:
            _conversation_layer_history[req.conversation_id] = [history_entry]
        
        tool_message = ToolMessage(content=str(tool_result), tool_call_id=tool_call["id"])
        
        # 构建最终回复的系统提示词，特别强调知识库查询后的回复要求
        final_system_prompt = full_system_prompt
        if tool_name == "query_knowledge_base":
            final_system_prompt += "\n\n重要：你刚刚查询了知识库，现在必须基于查询结果给用户一个完整、有用的回复。工具返回的结果已经包含了参考来源信息，请直接使用这些信息，不要重复添加来源。要结合用户的问题提供有价值的回答，并确保来源信息清晰可见。"
        
        # 加强上下文记忆规则，特别针对保存操作
        if tool_name in ["save_buffer_results_as_layer", 
                        "save_intersection_results_as_layer",
                        "save_erase_results_as_layer",
                        "save_path_results_as_layer",
                        "save_query_results_as_layer"]:
            final_system_prompt += "\n\n重要：你刚刚执行了保存操作，请记住当前的分析结果状态。当用户再次说'保存为图层'等操作时，必须基于刚才的分析类型调用对应的工具。"
        
        # 添加指令：不要回复记忆规则相关内容
        final_system_prompt += "\n\n⚠️ 重要提醒：如果用户输入包含'分析结果反馈'、'关键记忆规则'、'缓冲区分析完成'、'相交分析完成'、'擦除分析完成'、'最短路径分析完成'、'属性查询完成'等系统内部记忆信息，请直接回复'好的，我已记住'或类似简短确认，不要重复这些记忆规则内容。"
        
        final_ai: AIMessage = llm_with_tools.invoke([
            SystemMessage(content=final_system_prompt),
            HumanMessage(content=req.prompt),
            first_ai,
            tool_message,
        ])
        
        # 确保AI有回复内容，如果没有则生成默认回复
        if not final_ai.content or final_ai.content.strip() == "":
            if tool_name == "query_knowledge_base":
                final_ai.content = f"已查询知识库获取相关信息：\n\n{tool_result}"
            else:
                final_ai.content = f"操作已完成：{tool_result}"
        
        # 添加助手回复到对话历史
        add_to_conversation_history(req.conversation_id, "assistant", final_ai.content)
        
        print(f"✅ 对话处理完成")
        print(f"📝 最终回复: {final_ai.content[:100]}{'...' if len(final_ai.content) > 100 else ''}")
        print(f"🔚 任务结束: {task_id}\n")
        
        return ChatResponse(success=True, data={"first_call": {"tool_calls": first_ai.tool_calls}, "tool_result": tool_result, "final_answer": final_ai.content}, task_id=task_id)
    
    except Exception as e:
        print(f"❌ 对话处理失败: {str(e)}")
        
        # 记录错误到工具执行历史
        error_record = {
            "timestamp": get_current_timestamp(),
            "task_id": task_id,
            "conversation_id": req.conversation_id,
            "tool_name": "system_error",
            "tool_args": {"error": str(e)},
            "execution_status": "error",
            "result_preview": f"系统错误: {str(e)}"
        }
        _tool_execution_history.append(error_record)
        
        print(f"🔚 任务结束: {task_id}\n")
        return ChatResponse(success=False, error=f"LLM请求失败: {str(e)}", task_id=task_id)





@router.get("/knowledge/status")
async def get_knowledge_status():
    """获取知识库状态"""
    try:
        # 检查知识库是否需要更新
        needs_update = check_knowledge_base_update()
        
        # 获取知识库信息
        knowledge_base_path = Path(__file__).resolve().parents[1] / "rag" / "知识库"
        vector_db_path = Path(__file__).resolve().parents[1] / "rag" / "vector_db"
        
        # 统计文档数量
        doc_count = 0
        if knowledge_base_path.exists():
            doc_count = len([f for f in knowledge_base_path.rglob("*") if f.is_file()])
        
        return {
            "success": True,
            "data": {
                "needs_update": needs_update,
                "document_count": doc_count,
                "vector_db_exists": vector_db_path.exists(),
                "knowledge_base_path": str(knowledge_base_path),
                "vector_db_path": str(vector_db_path)
            }
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

@router.post("/knowledge/update")
async def update_knowledge():
    """手动更新知识库"""
    try:
        update_knowledge_base_if_needed()
        return {"success": True, "message": "知识库更新完成"}
    except Exception as e:
        return {"success": False, "error": str(e)}

@router.post("/knowledge/rebuild")
async def rebuild_knowledge():
    """强制重建知识库"""
    try:
        global _rag_system_cache
        _rag_system_cache = None  # 清除缓存
        get_rag_system()  # 重新初始化
        return {"success": True, "message": "知识库重建完成"}
    except Exception as e:
        return {"success": False, "error": str(e)}

@router.get("/conversation/{conversation_id}/history")
async def get_conversation_history(conversation_id: str):
    """获取对话历史"""
    try:
        history = _conversation_history.get(conversation_id, [])
        layer_history = _conversation_layer_history.get(conversation_id, [])
        
        return {
            "success": True,
            "data": {
                "conversation_id": conversation_id,
                "message_count": len(history),
                "layer_operations": len(layer_history),
                "messages": history,
                "layer_history": layer_history
            }
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

@router.delete("/conversation/{conversation_id}")
async def clear_conversation(conversation_id: str):
    """清除对话历史"""
    try:
        clear_conversation_history(conversation_id)
        return {"success": True, "message": f"对话历史 {conversation_id} 已清除"}
    except Exception as e:
        return {"success": False, "error": str(e)}

@router.get("/conversations")
async def list_conversations():
    """列出所有活跃的对话会话"""
    try:
        conversations = []
        for conv_id in _conversation_history.keys():
            history = _conversation_history[conv_id]
            layer_history = _conversation_layer_history.get(conv_id, [])
            
            conversations.append({
                "conversation_id": conv_id,
                "message_count": len(history),
                "layer_operations": len(layer_history),
                "last_activity": history[-1]["timestamp"] if history else None
            })
        
        return {
            "success": True,
            "data": {
                "total_conversations": len(conversations),
                "conversations": conversations
            }
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

@router.get("/tool-stats")
async def get_tool_stats():
    """获取工具调用统计信息"""
    try:
        total_calls = sum(_tool_call_stats.values())
        sorted_stats = sorted(_tool_call_stats.items(), key=lambda x: x[1], reverse=True)
        
        return {
            "success": True,
            "data": {
                "total_tool_calls": total_calls,
                "tool_statistics": dict(sorted_stats),
                "most_used_tool": sorted_stats[0] if sorted_stats else None
            }
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

@router.get("/tool-execution-history")
async def get_tool_execution_history(limit: int = 20):
    """获取工具执行历史"""
    try:
        recent_history = _tool_execution_history[-limit:] if limit > 0 else _tool_execution_history
        
        return {
            "success": True,
            "data": {
                "total_executions": len(_tool_execution_history),
                "recent_executions": recent_history,
                "execution_summary": {
                    "success_count": len([h for h in _tool_execution_history if h.get("execution_status") == "success"]),
                    "error_count": len([h for h in _tool_execution_history if h.get("execution_status") == "error"]),
                    "most_recent_tool": _tool_execution_history[-1]["tool_name"] if _tool_execution_history else None
                }
            }
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


app = FastAPI(
    title="Agent Service", 
    version="2.0.0",
    description="LLM Agent服务 - 提供完整的AI助手管理功能"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_list(),
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
    allow_origin_regex=".*",
)

app.include_router(router)


@app.get("/health")
async def health():
    """健康检查接口"""
    try:
        # 检查RAG系统状态
        rag_status = "unknown"
        rag_details = {}
        try:
            if _rag_system_cache is not None:
                rag_status = "ready"
                # 获取知识库详细信息
                knowledge_base_path = Path(__file__).resolve().parents[1] / "rag" / "知识库"
                vector_db_path = Path(__file__).resolve().parents[1] / "rag" / "vector_db"
                
                if knowledge_base_path.exists():
                    doc_count = len([f for f in knowledge_base_path.rglob("*") if f.is_file()])
                    rag_details["document_count"] = doc_count
                
                rag_details["vector_db_exists"] = vector_db_path.exists()
                rag_details["knowledge_base_path"] = str(knowledge_base_path)
            else:
                rag_status = "not_initialized"
        except Exception as e:
            rag_status = "error"
            rag_details["error"] = str(e)
        
        return {
            "status": "ok",
            "service": "Agent Service",
            "version": "2.0.0",
            "features": [
                "LLM Chat with System Prompt Injection",
                "API Key Management", 
                "Prompt Template Management",
                "Knowledge Base Management",
                "RAG Knowledge Base Integration",
                "Automatic Knowledge Base Updates",
                "Multi-turn Conversation Support",
                "Conversation History Management"
            ],
            "prompt_loaded": load_system_prompt() != "You are a helpful spatial analysis assistant.",
            "rag_system_status": rag_status,
            "rag_details": rag_details,
            "tools_count": 14,  # 12个原有工具 + 2个知识库工具
            "tool_call_statistics": _tool_call_stats,
            "total_tool_calls": sum(_tool_call_stats.values()),
            "tool_execution_history_count": len(_tool_execution_history),
            "recent_tool_executions": _tool_execution_history[-5:] if _tool_execution_history else []
        }
    except Exception as e:
        return {
            "status": "error",
            "service": "Agent Service",
            "version": "2.0.0",
            "error": str(e)
        }


@app.get("/")
async def root():
    """根路径信息"""
    return {
        "message": "Agent Service API",
        "docs": "/docs",
        "health": "/health",
        "endpoints": {
            "tool_chat": "/agent/tool-chat",
            "knowledge_status": "/agent/knowledge/status",
            "knowledge_update": "/agent/knowledge/update",
            "knowledge_rebuild": "/agent/knowledge/rebuild",
            "conversation_history": "/agent/conversation/{conversation_id}/history",
            "clear_conversation": "/agent/conversation/{conversation_id}",
            "list_conversations": "/agent/conversations",
            "tool_stats": "/agent/tool-stats",
            "tool_execution_history": "/agent/tool-execution-history",
            "health": "/health"
        }
    }



if __name__ == "__main__":
    uvicorn.run("agent.app:app", host="0.0.0.0", port=8089, reload=False)