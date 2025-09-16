"""
Agent Service - FastAPI entry for LLM chat proxy with full LLM management features

Usage (dev):
  python -m uvicorn agent.app:app --reload --host 0.0.0.0 --port 8089
"""
from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import uvicorn
import os
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
import uuid

# 导入RAG系统
import sys
from pathlib import Path
rag_path = Path(__file__).resolve().parents[1] / "rag"
sys.path.append(str(rag_path))
from rag.rag_system import RAGSystem

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
_ROOT = Path(__file__).resolve().parents[1]
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


@tool
def toggle_layer_visibility(layer_name: str, action: str) -> str:
    """
    切换前端图层可见性（前端执行）。
    输入参数：
      - layer_name: string 图层名称
      - action: string 'show'|'hide'|'toggle'
    业务处理：
      - 后端不直接操作地图，仅返回动作与图层名称供前端执行
    输出数据格式：
      - string: 格式 "action:layer_name"
    """
    return f"{action}:{layer_name}"


@tool
def query_features_by_attribute(layer_name: str, field: str, operator: str, value: str) -> str:
    """
    按属性选择要素（前端执行）。
    输入参数：
      - layer_name: string 图层名称
      - field: string 属性字段名
      - operator: string 比较操作符 '='|'!='|'>'|'>='|'<'|'<='|'like'
      - value: string 查询值
    业务处理：
      - 后端不直接操作地图，仅返回查询参数供前端执行
    输出数据格式：
      - string: 格式 "query:layer_name:field:operator:value"
    """
    return f"query:{layer_name}:{field}:{operator}:{value}"


@tool
def save_query_results_as_layer(layer_name: str) -> str:
    """
    保存查询结果为新图层（前端执行）。
    输入参数：
      - layer_name: string 新图层名称
    业务处理：
      - 后端不直接操作地图，仅返回保存参数供前端执行
    输出数据格式：
      - string: 格式 "save_layer:layer_name"
    """
    print(f"[DEBUG] save_query_results_as_layer 被调用，参数: {layer_name}")
    return f"保存操作已发送到前端，图层名称：{layer_name}"


@tool
def export_query_results_as_json(file_name: str) -> str:
    """
    导出查询结果为GeoJSON文件（前端执行）。
    输入参数：
      - file_name: string 文件名（不包含扩展名）
    业务处理：
      - 后端不直接操作地图，仅返回导出指令供前端执行
    输出数据格式：
      - string: 格式 "export_json:file_name"
    """
    return f"导出操作已发送到前端，文件名：{file_name}"


# ===== RAG知识库查询工具函数 =====

@tool
def query_knowledge_base(question: str) -> str:
    """
    查询知识库获取相关信息（前端执行）。
    输入参数：
      - question: string 用户问题，例如"武汉市的基本概况是什么？"
    业务处理：
      - 调用RAG系统查询知识库
      - 返回基于知识库的回答，包含参考来源
    输出数据格式：
      - string: 包含答案和参考来源的完整回复
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
    手动更新知识库（前端执行）。
    输入参数：
      - 无参数
    业务处理：
      - 清除RAG系统缓存并重新初始化
    输出数据格式：
      - string: 更新结果信息
    """
    try:
        global _rag_system_cache
        _rag_system_cache = None  # 清除缓存
        get_rag_system()  # 重新初始化
        return "知识库更新成功"
        
    except Exception as e:
        return f"知识库更新失败: {str(e)}"


@tool
def execute_buffer_analysis(layer_name: str, radius: float, unit: str = "meters") -> str:
    """
    执行缓冲区分析（前端执行）。
    输入参数：
      - layer_name: string 图层名称
      - radius: float 缓冲区半径
      - unit: string 单位（默认meters）
    业务处理：
      - 后端不直接操作地图，仅返回分析参数供前端执行
    输出数据格式：
      - string: 格式 "buffer_analysis:layer_name:radius:unit"
    """
    return f"缓冲区分析操作已发送到前端，图层：{layer_name}，半径：{radius}{unit}"


@tool
def execute_intersection_analysis(target_layer_name: str, mask_layer_name: str) -> str:
    """
    执行相交分析（前端执行）。
    输入参数：
      - target_layer_name: string 目标图层名称
      - mask_layer_name: string 掩膜图层名称
    业务处理：
      - 后端不直接操作地图，仅返回分析参数供前端执行
    输出数据格式：
      - string: 格式 "intersection_analysis:target_layer_name:mask_layer_name"
    """
    return f"相交分析操作已发送到前端，目标图层：{target_layer_name}，掩膜图层：{mask_layer_name}"


@tool
def execute_erase_analysis(target_layer_name: str, erase_layer_name: str) -> str:
    """
    执行擦除分析（前端执行）。
    输入参数：
      - target_layer_name: string 目标图层名称
      - erase_layer_name: string 擦除图层名称
    业务处理：
      - 后端不直接操作地图，仅返回分析参数供前端执行
    输出数据格式：
      - string: 格式 "erase_analysis:target_layer_name:erase_layer_name"
    """
    return f"擦除分析操作已发送到前端，目标图层：{target_layer_name}，擦除图层：{erase_layer_name}"


@tool
def execute_shortest_path_analysis(start_layer_name: str, end_layer_name: str, obstacle_layer_name: str = "") -> str:
    """
    执行最短路径分析（前端执行）。
    输入参数：
      - start_layer_name: string 起点图层名称
      - end_layer_name: string 终点图层名称
      - obstacle_layer_name: string 障碍物图层名称（可选）
    业务处理：
      - 后端不直接操作地图，仅返回分析参数供前端执行
    输出数据格式：
      - string: 格式 "shortest_path_analysis:start_layer_name:end_layer_name:obstacle_layer_name"
    """
    obstacle_info = f"，障碍物图层：{obstacle_layer_name}" if obstacle_layer_name else ""
    return f"最短路径分析操作已发送到前端，起点图层：{start_layer_name}，终点图层：{end_layer_name}{obstacle_info}"


# ===== 4个分析功能的导出和保存工具函数 =====

@tool
def save_buffer_results_as_layer(layer_name: str) -> Dict[str, Any]:
    """
    保存缓冲区分析结果为图层（前端执行）。
    输入参数：
      - layer_name: string 新图层名称
    业务处理：
      - 后端不直接操作地图，仅返回保存参数供前端执行
    输出数据格式：
      - { action: 'buffer.save_layer', params: { layer_name: string } }
    """
    print(f"[DEBUG] save_buffer_results_as_layer 被调用，参数: {layer_name}")
    return {"action": "buffer.save_layer", "params": {"layer_name": layer_name}}


@tool
def export_buffer_results_as_json(file_name: str) -> Dict[str, Any]:
    """
    导出缓冲区分析结果为GeoJSON文件（前端执行）。
    输入参数：
      - file_name: string 文件名（不包含扩展名）
    业务处理：
      - 后端不直接操作地图，仅返回导出指令供前端执行
    输出数据格式：
      - { action: 'buffer.export_json', params: { file_name: string } }
    """
    return {"action": "buffer.export_json", "params": {"file_name": file_name}}


@tool
def save_intersection_results_as_layer(layer_name: str) -> Dict[str, Any]:
    """
    保存相交分析结果为图层（前端执行）。
    输入参数：
      - layer_name: string 新图层名称
    业务处理：
      - 后端不直接操作地图，仅返回保存参数供前端执行
    输出数据格式：
      - { action: 'intersection.save_layer', params: { layer_name: string } }
    """
    return {"action": "intersection.save_layer", "params": {"layer_name": layer_name}}


@tool
def export_intersection_results_as_json(file_name: str) -> Dict[str, Any]:
    """
    导出相交分析结果为GeoJSON文件（前端执行）。
    输入参数：
      - file_name: string 文件名（不包含扩展名）
    业务处理：
      - 后端不直接操作地图，仅返回导出指令供前端执行
    输出数据格式：
      - { action: 'intersection.export_json', params: { file_name: string } }
    """
    return {"action": "intersection.export_json", "params": {"file_name": file_name}}


@tool
def save_erase_results_as_layer(layer_name: str) -> Dict[str, Any]:
    """
    保存擦除分析结果为图层（前端执行）。
    输入参数：
      - layer_name: string 新图层名称
    业务处理：
      - 后端不直接操作地图，仅返回保存参数供前端执行
    输出数据格式：
      - { action: 'erase.save_layer', params: { layer_name: string } }
    """
    return {"action": "erase.save_layer", "params": {"layer_name": layer_name}}


@tool
def export_erase_results_as_json(file_name: str) -> Dict[str, Any]:
    """
    导出擦除分析结果为GeoJSON文件（前端执行）。
    输入参数：
      - file_name: string 文件名（不包含扩展名）
    业务处理：
      - 后端不直接操作地图，仅返回导出指令供前端执行
    输出数据格式：
      - { action: 'erase.export_json', params: { file_name: string } }
    """
    return {"action": "erase.export_json", "params": {"file_name": file_name}}


@tool
def save_path_results_as_layer(layer_name: str) -> Dict[str, Any]:
    """
    保存最短路径分析结果为图层（前端执行）。
    输入参数：
      - layer_name: string 新图层名称
    业务处理：
      - 后端不直接操作地图，仅返回保存参数供前端执行
    输出数据格式：
      - { action: 'path.save_layer', params: { layer_name: string } }
    """
    return {"action": "path.save_layer", "params": {"layer_name": layer_name}}


@tool
def export_path_results_as_json(file_name: str) -> Dict[str, Any]:
    """
    导出最短路径分析结果为GeoJSON文件（前端执行）。
    输入参数：
      - file_name: string 文件名（不包含扩展名）
    业务处理：
      - 后端不直接操作地图，仅返回导出指令供前端执行
    输出数据格式：
      - { action: 'path.export_json', params: { file_name: string } }
    """
    return {"action": "path.export_json", "params": {"file_name": file_name}}


def load_system_prompt() -> str:
    """加载系统提示词，优先从prompt/tools.md读取"""
    base = Path(__file__).resolve().parent
    prompt_path = base / "prompt" / "tools.md"
    if not prompt_path.exists():
        prompt_path = base / "tools.md"
    try:
        content = prompt_path.read_text(encoding="utf-8")
        print(f"✅ 成功加载系统提示词: {prompt_path}")
        return content
    except Exception as e:
        print(f"⚠️ 加载系统提示词失败: {e}")
        return "You are a helpful spatial analysis assistant."

def load_tools_prompt() -> str:
    base = Path(__file__).resolve().parent
    # 优先使用独立工具提示词文件 agent/tools/tools.md
    tools_path = base / "tools" / "tools.md"
    if not tools_path.exists():
        # 回退到 prompt/tools.md（如果存在）
        tools_path = base / "prompt" / "tools.md"
    try:
        return tools_path.read_text(encoding="utf-8")
    except Exception:
        return ""


router = APIRouter(prefix="/agent", tags=["agent"])

# 会话图层操作历史：conversation_id -> ["action:layer_id", ...]
_conversation_layer_history: Dict[str, List[str]] = {}

# RAG系统实例缓存
_rag_system_cache: Optional[RAGSystem] = None

def generate_task_id() -> str:
    """生成唯一任务ID"""
    return f"task_{uuid.uuid4().hex[:12]}"

def get_current_timestamp() -> str:
    """获取当前时间戳"""
    from datetime import datetime
    return datetime.now().isoformat()

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

# 在模块加载时初始化RAG系统
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


class ToolChatRequest(BaseModel):
    model: str
    temperature: float
    prompt: str
    stream: bool = False
    conversation_id: str = "default"


@router.post("/tool-chat", response_model=ChatResponse)
async def tool_chat(req: ToolChatRequest):
    # 创建任务ID
    task_id = generate_task_id()
    """
    LangChain 工具调用接口（仅保留图层可见性工具）：
    输入数据格式：
      - model: LLM 模型名称
      - temperature: 采样温度
      - prompt: 用户问题（例如 What's 5 times forty two）
      - stream: 是否流式
    数据处理方法：
      - 创建 OpenAI 兼容模型，并通过 bind_tools 仅绑定 toggle_layer_visibility 工具
      - 第一步调用：发送 HumanMessage(prompt)，获取包含 tool_calls 的 AIMessage
      - 执行工具：根据 AIMessage 中的工具与参数，执行 toggle_layer_visibility 并得到结果
      - 第二步调用：将工具结果以 ToolMessage 形式回传给模型，生成最终回答
    输出数据格式：
      - { success: true, data: { first_call: AIMessage(JSON), tool_result: string, final_answer: string } }
    """
    model = init_chat_model(f"openai:{req.model}")
    llm_with_tools = model.bind_tools([
        # 知识库工具
        query_knowledge_base,
        update_knowledge_base,
        # 图层管理工具
        toggle_layer_visibility, 
        query_features_by_attribute, 
        save_query_results_as_layer, 
        export_query_results_as_json, 
        # 空间分析工具
        execute_buffer_analysis, 
        execute_intersection_analysis, 
        execute_erase_analysis, 
        execute_shortest_path_analysis,
        # 结果保存工具
        save_buffer_results_as_layer,
        export_buffer_results_as_json,
        save_intersection_results_as_layer,
        export_intersection_results_as_json,
        save_erase_results_as_layer,
        export_erase_results_as_json,
        save_path_results_as_layer,
        export_path_results_as_json
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
    first_ai: AIMessage = llm_with_tools.invoke([
        SystemMessage(content=(
            "你有十九个工具，分为四组：\n\n"
            "=== 第零组：知识库查询工具 ===\n"
            "0) query_knowledge_base(question: str)\n"
            "- 当用户询问武汉市地理、水文、环境等相关知识时调用。\n"
            "- 例如：'武汉市的基本概况是什么？'、'长江流域的水文特征'、'武汉市的水质标准'等。\n"
            "- 返回基于知识库的专业回答，包含参考来源。\n"
            "1) update_knowledge_base()\n"
            "- 当用户要求更新知识库或手动刷新知识库时调用。\n"
            "- 清除缓存并重新构建知识库索引。\n\n"
            "=== 重要：上下文记忆规则 ===\n"
            "你必须记住当前对话中最近执行的分析操作类型。当用户说'保存为图层'、'导出为JSON'等操作时：\n"
            "- 如果最近执行了缓冲区分析 → 使用save_buffer_results_as_layer或export_buffer_results_as_json\n"
            "- 如果最近执行了相交分析 → 使用save_intersection_results_as_layer或export_intersection_results_as_json\n"
            "- 如果最近执行了擦除分析 → 使用save_erase_results_as_layer或export_erase_results_as_json\n"
            "- 如果最近执行了最短路径分析 → 使用save_path_results_as_layer或export_path_results_as_json\n"
            "- 如果最近执行了属性查询 → 使用save_query_results_as_layer或export_query_results_as_json\n"
            "禁止询问用户要保存哪个分析的结果，必须基于上下文自动判断。\n\n"
            "=== 第一组：图层显示与查询 ===\n"
            "1) toggle_layer_visibility(layer_name:str, action:'show'|'hide'|'toggle')\n"
            "- 当用户说'打开@图层名称'或'隐藏@图层名称'或'切换@图层名称'时调用。\n"
            "- 使用图层名称而非图层ID进行操作。\n"
            "2) query_features_by_attribute(layer_name:str, field:str, operator:str, value:str)\n"
            "- 当用户说'在@图层名称中查找字段=值'、'查询@图层名称的属性'、'筛选@图层名称'时调用。\n"
            "- 操作符映射要求: 必须使用前端支持的格式\n"
            "  * '=' 映射为 'eq'\n"
            "  * '!=' 映射为 'ne'\n"
            "  * '>' 映射为 'gt'\n"
            "  * '>=' 映射为 'gte'\n"
            "  * '<' 映射为 'lt'\n"
            "  * '<=' 映射为 'lte'\n"
            "  * 'like' 保持不变\n"
            "- 例如: 用户说'查找NAME=学校'时，operator参数必须传递'eq'而不是'='\n"
            "3) export_query_results_as_json(file_name:str)\n"
            "- 当用户说'导出为JSON'、'导出为GeoJSON'、'导出查询结果'时调用。\n"
            "- 需要指定文件名（不包含扩展名）。\n\n"
            "=== 第二组：空间分析 ===\n"
            "4) execute_buffer_analysis(layer_name:str, radius:float, unit:str)\n"
            "- 当用户说'对@图层名称进行缓冲区分析'、'创建@图层名称的缓冲区'、'缓冲区分析'时调用。\n"
            "- 需要指定图层名称、半径和单位（默认meters）。\n"
            "5) execute_intersection_analysis(target_layer_name:str, mask_layer_name:str)\n"
            "- 当用户说'对@图层名称进行相交分析'、'计算@图层名称与@图层名称的相交'、'相交分析'时调用。\n"
            "- 需要指定目标图层名称和掩膜图层名称。\n"
            "6) execute_erase_analysis(target_layer_name:str, erase_layer_name:str)\n"
            "- 当用户说'对@图层名称进行擦除分析'、'从@图层名称中擦除@图层名称'、'擦除分析'时调用。\n"
            "- 需要指定目标图层名称和擦除图层名称。\n"
            "7) execute_shortest_path_analysis(start_layer_name:str, end_layer_name:str, obstacle_layer_name:str)\n"
            "- 当用户说'计算@图层名称到@图层名称的最短路径'、'最短路径分析'时调用。\n"
            "- 需要指定起点图层名称、终点图层名称，障碍物图层名称可选。\n"
            "8) export_buffer_results_as_json(file_name:str)\n"
            "- 当用户说'导出缓冲区分析结果为JSON'、'导出缓冲区结果为GeoJSON'时调用。\n"
            "- 需要指定文件名（不包含扩展名）。\n"
            "9) export_intersection_results_as_json(file_name:str)\n"
            "- 当用户说'导出相交分析结果为JSON'、'导出相交结果为GeoJSON'时调用。\n"
            "- 需要指定文件名（不包含扩展名）。\n"
            "10) export_erase_results_as_json(file_name:str)\n"
            "- 当用户说'导出擦除分析结果为JSON'、'导出擦除结果为GeoJSON'时调用。\n"
            "- 需要指定文件名（不包含扩展名）。\n"
            "11) export_path_results_as_json(file_name:str)\n"
            "- 当用户说'导出最短路径分析结果为JSON'、'导出路径结果为GeoJSON'时调用。\n"
            "- 需要指定文件名（不包含扩展名）。\n\n"
            "=== 第三组：保存为图层 ===\n"
            "12) save_query_results_as_layer(layer_name:str)\n"
            "- 当用户说'保存查询结果为图层'、'另存为图层'、'保存为新图层'时调用。\n"
            "- 图层名称可选：未指定时系统自动生成默认名称。\n"
            "13) save_buffer_results_as_layer(layer_name:str)\n"
            "- 当用户说'保存缓冲区分析结果为图层'、'另存缓冲区结果为图层'时调用。\n"
            "- 重要：只有在执行了缓冲区分析(execute_buffer_analysis)后，用户要求保存结果时才调用此工具。\n"
            "- 图层名称可选：未指定时系统自动生成默认名称。\n"
            "14) save_intersection_results_as_layer(layer_name:str)\n"
            "- 当用户说'保存相交分析结果为图层'、'另存相交结果为图层'时调用。\n"
            "- 重要：只有在执行了相交分析(execute_intersection_analysis)后，用户要求保存结果时才调用此工具。\n"
            "- 图层名称可选：未指定时系统自动生成默认名称。\n"
            "15) save_erase_results_as_layer(layer_name:str)\n"
            "- 当用户说'保存擦除分析结果为图层'、'另存擦除结果为图层'时调用。\n"
            "- 重要：只有在执行了擦除分析(execute_erase_analysis)后，用户要求保存结果时才调用此工具。\n"
            "- 图层名称可选：未指定时系统自动生成默认名称。\n"
            "16) save_path_results_as_layer(layer_name:str)\n"
            "- 当用户说'保存最短路径分析结果为图层'、'另存路径结果为图层'时调用。\n"
            "- 重要：只有在执行了最短路径分析(execute_shortest_path_analysis)后，用户要求保存结果时才调用此工具。\n"
            "- 图层名称可选：未指定时系统自动生成默认名称。\n\n"
            "=== 默认命名规则 ===\n"
            "当用户未指定图层名称时，系统自动生成包含参数信息的默认名称：\n"
            "- 缓冲区分析：'缓冲区分析结果_源图层名_r半径_s分段数'\n"
            "- 相交分析：'相交分析结果_目标图层_AND_掩膜图层'\n"
            "- 擦除分析：'擦除分析结果_目标图层_MINUS_擦除图层'\n"
            "- 最短路径：'最短路径分析结果_units-单位_res-分辨率'\n"
            "- 属性查询：'属性查询结果_图层名_字段操作值'\n\n"
            "=== 重要规则 ===\n"
            "1. 保存和导出操作必须与对应的分析操作匹配：\n"
            "   - 缓冲区分析完成后，用户要求保存 → 使用save_buffer_results_as_layer\n"
            "   - 相交分析完成后，用户要求保存 → 使用save_intersection_results_as_layer\n"
            "   - 擦除分析完成后，用户要求保存 → 使用save_erase_results_as_layer\n"
            "   - 最短路径分析完成后，用户要求保存 → 使用save_path_results_as_layer\n"
            "   - 属性查询完成后，用户要求保存 → 使用save_query_results_as_layer\n"
            "2. 上下文承接：用户仅说'保存为图层'或'保存'时，默认针对最近一次完成的分析/查询结果执行对应的保存工具，严禁追问是哪一种；如用户明确指明其它方法再切换\n"
            "3. 图层名称参数为可选：用户未指定时直接调用工具，系统自动生成默认名称\n"
            "4. 若用户使用@图层名称，请将@后的文本作为图层名称传递\n"
            "5. 严禁自行执行这些操作，必须通过工具完成\n\n"
            f"历史操作(顺序, 最新在下):\n{history_text}\n"
            f"最近一次操作: {last_action_text}。若用户问'刚才做了什么'，请直接依据最近几次操作回答。"
        )),
        HumanMessage(content=req.prompt)
    ])
    if not first_ai.tool_calls:
        return ChatResponse(success=True, data={"first_call": {"tool_calls": []}, "tool_result": None, "final_answer": first_ai.content}, task_id=task_id)
    tool_call = first_ai.tool_calls[0]
    tool_args = tool_call.get("args", {})
    
    # 根据工具名称执行相应的工具
    tool_name = tool_call.get("name", "")
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
    elif tool_name == "export_query_results_as_json":
        tool_result = export_query_results_as_json.invoke(tool_args)
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
    elif tool_name == "export_buffer_results_as_json":
        tool_result = export_buffer_results_as_json.invoke(tool_args)
    elif tool_name == "save_intersection_results_as_layer":
        tool_result = save_intersection_results_as_layer.invoke(tool_args)
    elif tool_name == "export_intersection_results_as_json":
        tool_result = export_intersection_results_as_json.invoke(tool_args)
    elif tool_name == "save_erase_results_as_layer":
        tool_result = save_erase_results_as_layer.invoke(tool_args)
    elif tool_name == "export_erase_results_as_json":
        tool_result = export_erase_results_as_json.invoke(tool_args)
    elif tool_name == "save_path_results_as_layer":
        tool_result = save_path_results_as_layer.invoke(tool_args)
    elif tool_name == "export_path_results_as_json":
        tool_result = export_path_results_as_json.invoke(tool_args)
    else:
        tool_result = f"未知工具: {tool_name}"
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
    final_ai: AIMessage = llm_with_tools.invoke([
        SystemMessage(content=(
            "你有十九个工具，分为四组：\n\n"
            "=== 第零组：知识库查询工具 ===\n"
            "0) query_knowledge_base(question: str)\n"
            "- 当用户询问武汉市地理、水文、环境等相关知识时调用。\n"
            "- 例如：'武汉市的基本概况是什么？'、'长江流域的水文特征'、'武汉市的水质标准'等。\n"
            "- 返回基于知识库的专业回答，包含参考来源。\n"
            "1) update_knowledge_base()\n"
            "- 当用户要求更新知识库或手动刷新知识库时调用。\n"
            "- 清除缓存并重新构建知识库索引。\n\n"
            "=== 重要：上下文记忆规则 ===\n"
            "你必须记住当前对话中最近执行的分析操作类型。当用户说'保存为图层'、'导出为JSON'等操作时：\n"
            "- 如果最近执行了缓冲区分析 → 使用save_buffer_results_as_layer或export_buffer_results_as_json\n"
            "- 如果最近执行了相交分析 → 使用save_intersection_results_as_layer或export_intersection_results_as_json\n"
            "- 如果最近执行了擦除分析 → 使用save_erase_results_as_layer或export_erase_results_as_json\n"
            "- 如果最近执行了最短路径分析 → 使用save_path_results_as_layer或export_path_results_as_json\n"
            "- 如果最近执行了属性查询 → 使用save_query_results_as_layer或export_query_results_as_json\n"
            "禁止询问用户要保存哪个分析的结果，必须基于上下文自动判断。\n\n"
            "=== 第一组：图层显示与查询 ===\n"
            "1) toggle_layer_visibility(layer_name:str, action:'show'|'hide'|'toggle')\n"
            "- 遇到'打开/隐藏/切换@图层名称'的请求，必须调用该工具。\n"
            "- 使用图层名称而非图层ID进行操作。\n"
            "2) query_features_by_attribute(layer_name:str, field:str, operator:str, value:str)\n"
            "- 遇到'在@图层名称中查找/查询/筛选'的请求，必须调用该工具。\n"
            "- 操作符映射要求: 必须使用前端支持的格式\n"
            "  * '=' 映射为 'eq'\n"
            "  * '!=' 映射为 'ne'\n"
            "  * '>' 映射为 'gt'\n"
            "  * '>=' 映射为 'gte'\n"
            "  * '<' 映射为 'lt'\n"
            "  * '<=' 映射为 'lte'\n"
            "  * 'like' 保持不变\n"
            "- 例如: 用户说'查找NAME=学校'时，operator参数必须传递'eq'而不是'='\n"
            "3) export_query_results_as_json(file_name:str)\n"
            "- 遇到'导出为JSON'、'导出为GeoJSON'、'导出查询结果'的请求时调用。\n"
            "- 需要指定文件名（不包含扩展名）。\n\n"
            "=== 第二组：空间分析 ===\n"
            "4) execute_buffer_analysis(layer_name:str, radius:float, unit:str)\n"
            "- 遇到'对@图层名称进行缓冲区分析'、'创建@图层名称的缓冲区'、'缓冲区分析'的请求时调用。\n"
            "- 需要指定图层名称、半径和单位（默认meters）。\n"
            "5) execute_intersection_analysis(target_layer_name:str, mask_layer_name:str)\n"
            "- 遇到'对@图层名称进行相交分析'、'计算@图层名称与@图层名称的相交'、'相交分析'的请求时调用。\n"
            "- 需要指定目标图层名称和掩膜图层名称。\n"
            "6) execute_erase_analysis(target_layer_name:str, erase_layer_name:str)\n"
            "- 遇到'对@图层名称进行擦除分析'、'从@图层名称中擦除@图层名称'、'擦除分析'的请求时调用。\n"
            "- 需要指定目标图层名称和擦除图层名称。\n"
            "7) execute_shortest_path_analysis(start_layer_name:str, end_layer_name:str, obstacle_layer_name:str)\n"
            "- 遇到'计算@图层名称到@图层名称的最短路径'、'最短路径分析'的请求时调用。\n"
            "- 需要指定起点图层名称、终点图层名称，障碍物图层名称可选。\n"
            "8) export_buffer_results_as_json(file_name:str)\n"
            "- 遇到'导出缓冲区分析结果为JSON'、'导出缓冲区结果为GeoJSON'的请求时调用。\n"
            "- 需要指定文件名（不包含扩展名）。\n"
            "9) export_intersection_results_as_json(file_name:str)\n"
            "- 遇到'导出相交分析结果为JSON'、'导出相交结果为GeoJSON'的请求时调用。\n"
            "- 需要指定文件名（不包含扩展名）。\n"
            "10) export_erase_results_as_json(file_name:str)\n"
            "- 遇到'导出擦除分析结果为JSON'、'导出擦除结果为GeoJSON'的请求时调用。\n"
            "- 需要指定文件名（不包含扩展名）。\n"
            "11) export_path_results_as_json(file_name:str)\n"
            "- 遇到'导出最短路径分析结果为JSON'、'导出路径结果为GeoJSON'的请求时调用。\n"
            "- 需要指定文件名（不包含扩展名）。\n\n"
            "=== 第三组：保存为图层 ===\n"
            "12) save_query_results_as_layer(layer_name:str)\n"
            "- 遇到'保存查询结果为图层'、'另存为图层'、'保存为新图层'的请求时调用。\n"
            "- 图层名称可选：未指定时系统自动生成默认名称。\n"
            "13) save_buffer_results_as_layer(layer_name:str)\n"
            "- 遇到'保存缓冲区分析结果为图层'、'另存缓冲区结果为图层'的请求时调用。\n"
            "- 重要：只有在执行了缓冲区分析(execute_buffer_analysis)后，用户要求保存结果时才调用此工具。\n"
            "- 图层名称可选：未指定时系统自动生成默认名称。\n"
            "14) save_intersection_results_as_layer(layer_name:str)\n"
            "- 遇到'保存相交分析结果为图层'、'另存相交结果为图层'的请求时调用。\n"
            "- 重要：只有在执行了相交分析(execute_intersection_analysis)后，用户要求保存结果时才调用此工具。\n"
            "- 图层名称可选：未指定时系统自动生成默认名称。\n"
            "15) save_erase_results_as_layer(layer_name:str)\n"
            "- 遇到'保存擦除分析结果为图层'、'另存擦除结果为图层'的请求时调用。\n"
            "- 重要：只有在执行了擦除分析(execute_erase_analysis)后，用户要求保存结果时才调用此工具。\n"
            "- 图层名称可选：未指定时系统自动生成默认名称。\n"
            "16) save_path_results_as_layer(layer_name:str)\n"
            "- 遇到'保存最短路径分析结果为图层'、'另存路径结果为图层'的请求时调用。\n"
            "- 重要：只有在执行了最短路径分析(execute_shortest_path_analysis)后，用户要求保存结果时才调用此工具。\n"
            "- 图层名称可选：未指定时系统自动生成默认名称。\n\n"
            "=== 默认命名规则 ===\n"
            "当用户未指定图层名称时，系统自动生成包含参数信息的默认名称：\n"
            "- 缓冲区分析：'缓冲区分析结果_源图层名_r半径_s分段数'\n"
            "- 相交分析：'相交分析结果_目标图层_AND_掩膜图层'\n"
            "- 擦除分析：'擦除分析结果_目标图层_MINUS_擦除图层'\n"
            "- 最短路径：'最短路径分析结果_units-单位_res-分辨率'\n"
            "- 属性查询：'属性查询结果_图层名_字段操作值'\n\n"
            "=== 重要规则 ===\n"
            "1. 保存和导出操作必须与对应的分析操作匹配：\n"
            "   - 缓冲区分析完成后，用户要求保存 → 使用save_buffer_results_as_layer\n"
            "   - 相交分析完成后，用户要求保存 → 使用save_intersection_results_as_layer\n"
            "   - 擦除分析完成后，用户要求保存 → 使用save_erase_results_as_layer\n"
            "   - 最短路径分析完成后，用户要求保存 → 使用save_path_results_as_layer\n"
            "   - 属性查询完成后，用户要求保存 → 使用save_query_results_as_layer\n"
            "2. 图层名称参数为可选：用户未指定时直接调用工具，系统自动生成默认名称\n"
            "3. 若用户使用@图层名称，请将@后的文本作为图层名称传递\n"
            "4. 严禁自行执行这些操作，必须通过工具完成\n\n"
            "=== 回复规则 ===\n"
            "当工具执行完成后，必须简洁回复，禁止废话：\n"
            "- 查询操作：直接说'正在执行请稍后'\n"
            "- 图层操作：直接说'图层已显示/隐藏'\n"
            "- 保存操作：直接说'正在执行请稍后'\n"
            "- 导出操作：直接说'正在执行请稍后'\n"
            "- 缓冲区分析：直接说'正在执行请稍后'\n"
            "- 相交分析：直接说'正在执行请稍后'\n"
            "- 擦除分析：直接说'正在执行请稍后'\n"
            "- 最短路径分析：直接说'正在执行请稍后'\n"
            "严禁说'看起来'、'可能'、'如果'、'请确认'等不确定词汇。\n"
            "严禁解释系统工作原理或引导用户查看界面。\n"
            "严禁回复具体的要素数量或详细结果。\n"
            "严禁编造或猜测操作结果。\n"
            "只回复'正在执行请稍后'或简单的操作状态，一句话结束。"
        )),
        HumanMessage(content=req.prompt),
        first_ai,
        tool_message,
    ])
    return ChatResponse(success=True, data={"first_call": {"tool_calls": first_ai.tool_calls}, "tool_result": tool_result, "final_answer": final_ai.content}, task_id=task_id)

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
    return {
        "status": "ok",
        "service": "Agent Service",
        "version": "2.0.0",
        "features": [
            "LLM Chat with System Prompt Injection",
            "API Key Management", 
            "Prompt Template Management",
            "Knowledge Base Management",
            "RAG Knowledge Base Integration"
        ],
        "prompt_loaded": load_system_prompt() != "You are a helpful spatial analysis assistant."
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
            "api_keys": "/api/v1/api-keys",
            "prompts": "/api/v1/prompts", 
            "knowledge": "/api/v1/knowledge"
        }
    }



if __name__ == "__main__":
    uvicorn.run("agent.app:app", host="0.0.0.0", port=8089, reload=True)