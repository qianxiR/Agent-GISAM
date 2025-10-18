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
import time
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


@tool
def toggle_layer_visibility(layer_name: str, action: str) -> Dict[str, Any]:
    """
    切换前端图层可见性（前端执行）。
    输入参数：
      - layer_name: string 图层名称
      - action: string 'show'|'hide'|'toggle'
    业务处理：
      - 后端不直接操作地图，仅返回动作与图层名称供前端执行
    输出数据格式：
      - { type: 'layer_control', action: string, params: { layer_name: string, action: string } }
    """
    return {
        "type": "layer_control",
        "action": f"{action}_layer",
        "params": {"layer_name": layer_name, "action": action}
    }


@tool
def query_features_by_attribute(layer_name: str, field: str, operator: str, value: str) -> Dict[str, Any]:
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
      - { type: 'query', action: 'attribute_query', params: { layer_name, field, operator, value } }
    """
    return {
        "type": "query",
        "action": "attribute_query",
        "params": {"layer_name": layer_name, "field": field, "operator": operator, "value": value}
    }


@tool
def save_query_results_as_layer(layer_name: str) -> Dict[str, Any]:
    """
    保存查询结果为新图层（前端执行）。
    输入参数：
      - layer_name: string 新图层名称
    业务处理：
      - 后端不直接操作地图，仅返回保存参数供前端执行
    输出数据格式：
      - { type: 'save', action: 'query.save_layer', params: { layer_name: string } }
    """
    print(f"[DEBUG] save_query_results_as_layer 被调用，参数: {layer_name}")
    return {"type": "save", "action": "query.save_layer", "params": {"layer_name": layer_name}}




@tool
def execute_buffer_analysis(layer_name: str, radius: float, unit: str = "meters") -> Dict[str, Any]:
    """
    执行缓冲区分析（前端执行）。
    输入参数：
      - layer_name: string 图层名称
      - radius: float 缓冲区半径
      - unit: string 单位（默认meters）
    业务处理：
      - 后端不直接操作地图，仅返回分析参数供前端执行
    输出数据格式：
      - { type: 'analysis', action: 'buffer_analysis', params: { layer_name, radius, unit } }
    """
    return {
        "type": "analysis",
        "action": "buffer_analysis",
        "params": {"layer_name": layer_name, "radius": radius, "unit": unit}
    }


@tool
def execute_intersection_analysis(target_layer_name: str, mask_layer_name: str) -> Dict[str, Any]:
    """
    执行相交分析（前端执行）。
    输入参数：
      - target_layer_name: string 目标图层名称
      - mask_layer_name: string 掩膜图层名称
    业务处理：
      - 后端不直接操作地图，仅返回分析参数供前端执行
    输出数据格式：
      - { type: 'analysis', action: 'intersection_analysis', params: { target_layer_name, mask_layer_name } }
    """
    return {
        "type": "analysis",
        "action": "intersection_analysis",
        "params": {"target_layer_name": target_layer_name, "mask_layer_name": mask_layer_name}
    }


@tool
def execute_erase_analysis(target_layer_name: str, erase_layer_name: str) -> Dict[str, Any]:
    """
    执行擦除分析（前端执行）。
    输入参数：
      - target_layer_name: string 目标图层名称
      - erase_layer_name: string 擦除图层名称
    业务处理：
      - 后端不直接操作地图，仅返回分析参数供前端执行
    输出数据格式：
      - { type: 'analysis', action: 'erase_analysis', params: { target_layer_name, erase_layer_name } }
    """
    return {
        "type": "analysis",
        "action": "erase_analysis",
        "params": {"target_layer_name": target_layer_name, "erase_layer_name": erase_layer_name}
    }


@tool
def execute_shortest_path_analysis(start_layer_name: str, end_layer_name: str, obstacle_layer_name: str = "") -> Dict[str, Any]:
    """
    执行最短路径分析（前端执行）。
    输入参数：
      - start_layer_name: string 起点图层名称
      - end_layer_name: string 终点图层名称
      - obstacle_layer_name: string 障碍物图层名称（可选）
    业务处理：
      - 后端不直接操作地图，仅返回分析参数供前端执行
    输出数据格式：
      - { type: 'analysis', action: 'shortest_path_analysis', params: { start_layer_name, end_layer_name, obstacle_layer_name } }
    """
    return {
        "type": "analysis",
        "action": "shortest_path_analysis",
        "params": {"start_layer_name": start_layer_name, "end_layer_name": end_layer_name, "obstacle_layer_name": obstacle_layer_name}
    }


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
      - { type: 'save', action: 'buffer.save_layer', params: { layer_name: string } }
    """
    print(f"[DEBUG] save_buffer_results_as_layer 被调用，参数: {layer_name}")
    return {"type": "save", "action": "buffer.save_layer", "params": {"layer_name": layer_name}}




@tool
def save_intersection_results_as_layer(layer_name: str) -> Dict[str, Any]:
    """
    保存相交分析结果为图层（前端执行）。
    输入参数：
      - layer_name: string 新图层名称
    业务处理：
      - 后端不直接操作地图，仅返回保存参数供前端执行
    输出数据格式：
      - { type: 'save', action: 'intersection.save_layer', params: { layer_name: string } }
    """
    return {"type": "save", "action": "intersection.save_layer", "params": {"layer_name": layer_name}}




@tool
def save_erase_results_as_layer(layer_name: str) -> Dict[str, Any]:
    """
    保存擦除分析结果为图层（前端执行）。
    输入参数：
      - layer_name: string 新图层名称
    业务处理：
      - 后端不直接操作地图，仅返回保存参数供前端执行
    输出数据格式：
      - { type: 'save', action: 'erase.save_layer', params: { layer_name: string } }
    """
    return {"type": "save", "action": "erase.save_layer", "params": {"layer_name": layer_name}}




@tool
def save_path_results_as_layer(layer_name: str) -> Dict[str, Any]:
    """
    保存最短路径分析结果为图层（前端执行）。
    输入参数：
      - layer_name: string 新图层名称
    业务处理：
      - 后端不直接操作地图，仅返回保存参数供前端执行
    输出数据格式：
      - { type: 'save', action: 'path.save_layer', params: { layer_name: string } }
    """
    return {"type": "save", "action": "path.save_layer", "params": {"layer_name": layer_name}}


@tool
def rename_layer(layer_name: str, new_name: str) -> Dict[str, Any]:
    """
    重命名图层（前端执行）。
    输入参数：
      - layer_name: string 原图层名称
      - new_name: string 新图层名称
    业务处理：
      - 后端不直接操作地图，仅返回重命名参数供前端执行
    输出数据格式：
      - { type: 'layer_control', action: 'rename_layer', params: { layer_name: string, new_name: string } }
    """
    return {"type": "layer_control", "action": "rename_layer", "params": {"layer_name": layer_name, "new_name": new_name}}




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


# ===== 工具注册表 (全局变量) =====
TOOL_REGISTRY = {
    "toggle_layer_visibility": toggle_layer_visibility,
    "query_features_by_attribute": query_features_by_attribute,
    "save_query_results_as_layer": save_query_results_as_layer,
    "execute_buffer_analysis": execute_buffer_analysis,
    "execute_intersection_analysis": execute_intersection_analysis,
    "execute_erase_analysis": execute_erase_analysis,
    "execute_shortest_path_analysis": execute_shortest_path_analysis,
    "save_buffer_results_as_layer": save_buffer_results_as_layer,
    "save_intersection_results_as_layer": save_intersection_results_as_layer,
    "save_erase_results_as_layer": save_erase_results_as_layer,
    "save_path_results_as_layer": save_path_results_as_layer,
    "rename_layer": rename_layer,
}

router = APIRouter(prefix="/agent", tags=["agent"])

# 会话操作历史结构化存储：conversation_id -> [{ type, action, params, timestamp }, ...]
_conversation_layer_history: Dict[str, List[Dict[str, Any]]] = {}


def get_last_analysis_type(conversation_id: str) -> Optional[str]:
    """
    提取最近一次分析操作类型
    输入参数:
      - conversation_id: string 会话ID
    业务处理:
      - 倒序遍历历史记录,找到第一个type='analysis'的操作
      - 提取其action字段作为分析类型
    输出数据格式:
      - Optional[string]: 'buffer_analysis' | 'intersection_analysis' | 'erase_analysis' | 'shortest_path_analysis' | None
    """
    history = _conversation_layer_history.get(conversation_id, [])
    for record in reversed(history):
        if isinstance(record, dict) and record.get("type") == "analysis":
            return record.get("action")
    return None


class ToolChatRequest(BaseModel):
    model: str
    temperature: float
    prompt: str
    stream: bool = False
    conversation_id: str = "default"


@router.post("/tool-chat", response_model=ChatResponse)
async def tool_chat(req: ToolChatRequest):
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
        toggle_layer_visibility, 
        query_features_by_attribute, 
        save_query_results_as_layer, 
        execute_buffer_analysis, 
        execute_intersection_analysis, 
        execute_erase_analysis, 
        execute_shortest_path_analysis,
        save_buffer_results_as_layer,
        save_intersection_results_as_layer,
        save_erase_results_as_layer,
        save_path_results_as_layer,
        rename_layer
    ])
    # 获取历史记录(最多展示最近5条,避免token浪费)
    history_list = _conversation_layer_history.get(req.conversation_id, [])
    recent_history = history_list[-5:] if len(history_list) > 5 else history_list
    
    # 格式化历史记录为可读文本
    parsed_lines: List[str] = []
    for record in recent_history:
        if isinstance(record, dict):
            action = record.get("action", "unknown")
            params = record.get("params", {})
            parsed_line = f"操作类型={record.get('type')}, 动作={action}, 参数={params}"
            parsed_lines.append(parsed_line)
    history_text = "\n".join(parsed_lines) if parsed_lines else "暂无历史操作"
    
    # 获取最近一次分析类型,用于智能上下文提示
    last_analysis = get_last_analysis_type(req.conversation_id)
    context_hint = ""
    if last_analysis:
        analysis_name_map = {
            "buffer_analysis": "缓冲区分析",
            "intersection_analysis": "相交分析",
            "erase_analysis": "擦除分析",
            "shortest_path_analysis": "最短路径分析"
        }
        context_hint = f"\n当前上下文：最近执行了【{analysis_name_map.get(last_analysis, last_analysis)}】，若用户说'保存'则默认保存该分析结果。"
    first_ai: AIMessage = llm_with_tools.invoke([
        SystemMessage(content=(
            "你有十二个工具，分为三组：\n\n"
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
            "=== 第二组：保存为图层 ===\n"
            "8) save_query_results_as_layer(layer_name:str)\n"
            "- 当用户说'保存查询结果为图层'、'另存为图层'、'保存为新图层'时调用。\n"
            "- 图层名称可选：未指定时系统自动生成默认名称。\n"
            "9) save_buffer_results_as_layer(layer_name:str)\n"
            "- 当用户说'保存缓冲区分析结果为图层'、'另存缓冲区结果为图层'时调用。\n"
            "- 重要：只有在执行了缓冲区分析(execute_buffer_analysis)后，用户要求保存结果时才调用此工具。\n"
            "- 图层名称可选：未指定时系统自动生成默认名称。\n"
            "10) save_intersection_results_as_layer(layer_name:str)\n"
            "- 当用户说'保存相交分析结果为图层'、'另存相交结果为图层'时调用。\n"
            "- 重要：只有在执行了相交分析(execute_intersection_analysis)后，用户要求保存结果时才调用此工具。\n"
            "- 图层名称可选：未指定时系统自动生成默认名称。\n"
            "11) save_erase_results_as_layer(layer_name:str)\n"
            "- 当用户说'保存擦除分析结果为图层'、'另存擦除结果为图层'时调用。\n"
            "- 重要：只有在执行了擦除分析(execute_erase_analysis)后，用户要求保存结果时才调用此工具。\n"
            "- 图层名称可选：未指定时系统自动生成默认名称。\n"
            "12) save_path_results_as_layer(layer_name:str)\n"
            "- 当用户说'保存最短路径分析结果为图层'、'另存路径结果为图层'时调用。\n"
            "- 重要：只有在执行了最短路径分析(execute_shortest_path_analysis)后，用户要求保存结果时才调用此工具。\n"
            "- 图层名称可选：未指定时系统自动生成默认名称。\n\n"
            "=== 默认命名规则 ===\n"
            "当用户未指定图层名称时，系统自动生成包含参数信息的默认名称：\n"
            "- 缓冲区分析：'缓冲区分析_源图层名_半径_分段数'\n"
            "- 相交分析：'相交分析_目标图层_掩膜图层'\n"
            "- 擦除分析：'擦除分析_目标图层_擦除图层'\n"
            "- 最短路径：'最短路径分析_起始图层_目标图层_障碍图层_单位_分辨率'\n"
            "- 属性查询：'属性查询_图层名_字段操作值'\n\n"
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
            f"历史操作(最近5条):\n{history_text}{context_hint}"
        )),
        HumanMessage(content=req.prompt)
    ])
    if not first_ai.tool_calls:
        return ChatResponse(success=True, data={"first_call": {"tool_calls": []}, "tool_result": None, "final_answer": first_ai.content})
    tool_call = first_ai.tool_calls[0]
    tool_args = tool_call.get("args", {})
    tool_name = tool_call.get("name", "")
    
    # 使用工具注册表动态调用(优化1:替代if-elif链)
    tool_func = TOOL_REGISTRY.get(tool_name)
    if tool_func:
        tool_result = tool_func.invoke(tool_args)
    else:
        tool_result = {"type": "error", "action": "unknown_tool", "params": {"tool_name": tool_name}}
    
    # 结构化记录历史(优化3:改为Dict格式存储)
    if isinstance(tool_result, dict):
        history_entry = {
            "type": tool_result.get("type", "unknown"),
            "action": tool_result.get("action", "unknown"),
            "params": tool_result.get("params", {}),
            "timestamp": time.time()
        }
    else:
        # 兼容旧格式(字符串返回值)
        history_entry = {
            "type": "legacy",
            "action": "string_result",
            "params": {"result": str(tool_result)},
            "timestamp": time.time()
        }
    
    if req.conversation_id in _conversation_layer_history:
        _conversation_layer_history[req.conversation_id].append(history_entry)
    else:
        _conversation_layer_history[req.conversation_id] = [history_entry]
    tool_message = ToolMessage(content=str(tool_result), tool_call_id=tool_call["id"])
    final_ai: AIMessage = llm_with_tools.invoke([
        SystemMessage(content=(
            "你有十二个工具，分为三组：\n\n"
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
            "=== 第二组：保存为图层 ===\n"
            "8) save_query_results_as_layer(layer_name:str)\n"
            "- 遇到'保存查询结果为图层'、'另存为图层'、'保存为新图层'的请求时调用。\n"
            "- 图层名称可选：未指定时系统自动生成默认名称。\n"
            "9) save_buffer_results_as_layer(layer_name:str)\n"
            "- 遇到'保存缓冲区分析结果为图层'、'另存缓冲区结果为图层'的请求时调用。\n"
            "- 重要：只有在执行了缓冲区分析(execute_buffer_analysis)后，用户要求保存结果时才调用此工具。\n"
            "- 图层名称可选：未指定时系统自动生成默认名称。\n"
            "10) save_intersection_results_as_layer(layer_name:str)\n"
            "- 遇到'保存相交分析结果为图层'、'另存相交结果为图层'的请求时调用。\n"
            "- 重要：只有在执行了相交分析(execute_intersection_analysis)后，用户要求保存结果时才调用此工具。\n"
            "- 图层名称可选：未指定时系统自动生成默认名称。\n"
            "11) save_erase_results_as_layer(layer_name:str)\n"
            "- 遇到'保存擦除分析结果为图层'、'另存擦除结果为图层'的请求时调用。\n"
            "- 重要：只有在执行了擦除分析(execute_erase_analysis)后，用户要求保存结果时才调用此工具。\n"
            "- 图层名称可选：未指定时系统自动生成默认名称。\n"
            "12) save_path_results_as_layer(layer_name:str)\n"
            "- 遇到'保存最短路径分析结果为图层'、'另存路径结果为图层'的请求时调用。\n"
            "- 重要：只有在执行了最短路径分析(execute_shortest_path_analysis)后，用户要求保存结果时才调用此工具。\n"
            "- 图层名称可选：未指定时系统自动生成默认名称。\n"
            "13) rename_layer(layer_name:str, new_name:str)\n"
            "- 遇到'修改图层@图层名称的名称为新名称'、'重命名@图层名称为新名称'的请求时调用。\n"
            "- 自动解析@图层名称格式，提取图层名称和新名称。\n"
            "- 服务图层不允许重命名，只能重命名分析、查询、上传图层。\n\n"
            "=== 默认命名规则 ===\n"
            "当用户未指定图层名称时，系统自动生成包含参数信息的默认名称：\n"
            "- 缓冲区分析：'缓冲区分析_源图层名_半径_分段数'\n"
            "- 相交分析：'相交分析_目标图层_掩膜图层'\n"
            "- 擦除分析：'擦除分析_目标图层_擦除图层'\n"
            "- 最短路径：'最短路径分析_起始图层_目标图层_障碍图层_单位_分辨率'\n"
            "- 属性查询：'属性查询_图层名_字段操作值'\n\n"
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
            "严禁说'看起来'、'可能'、'如果'、'请确认'等不确定词汇。\n"
            "严禁解释系统工作原理或引导用户查看界面。\n"
            "严禁回复具体的要素数量或详细结果。\n"
            "严禁编造或猜测操作结果。\n"
            "只回复简单的操作结果状态，一句话结束。"
        )),
        HumanMessage(content=req.prompt),
        first_ai,
        tool_message,
    ])
    return ChatResponse(success=True, data={"first_call": {"tool_calls": first_ai.tool_calls}, "tool_result": tool_result, "final_answer": final_ai.content})

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
            "Knowledge Base Management"
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