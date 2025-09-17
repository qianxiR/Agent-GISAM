"""
Agent工具定义模块
包含所有GIS分析工具的定义
"""
from typing import Dict, Any
from langchain_core.tools import tool
from .knowledge import get_rag_system, update_knowledge_base_if_needed


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
    result = f"{action}:{layer_name}"
    return result


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
    result = f"query:{layer_name}:{field}:{operator}:{value}"
    return result


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
    return f"save_layer:{layer_name}"




@tool
def get_open_layers() -> str:
    """
    获取当前打开的图层列表（前端执行）。
    输入参数：
      无
    业务处理：
      - 后端不直接操作地图，仅返回查询指令供前端执行
    输出数据格式：
      - string: 格式 "get_open_layers"
    """
    result = "get_open_layers"
    return result


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
    result = f"buffer_analysis:{layer_name}:{radius}:{unit}"
    return result


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
    result = f"intersection_analysis:{target_layer_name}:{mask_layer_name}"
    return result


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
    result = f"erase_analysis:{target_layer_name}:{erase_layer_name}"
    return result


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
    result = f"shortest_path_analysis:{start_layer_name}:{end_layer_name}:{obstacle_layer_name}"
    return result


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
    result = {"action": "buffer.save_layer", "params": {"layer_name": layer_name}}
    return result




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
    result = {"action": "intersection.save_layer", "params": {"layer_name": layer_name}}
    return result




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
    result = {"action": "erase.save_layer", "params": {"layer_name": layer_name}}
    return result




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
    result = {"action": "path.save_layer", "params": {"layer_name": layer_name}}
    return result


# ===== 知识库相关工具 =====

@tool
def query_knowledge_base(question: str) -> str:
    """
    查询知识库获取相关信息

    输入参数：
      - question: string 用户问题
    业务处理：
      - 调用共享的 RAG 管理模块，必要时更新知识库
      - 使用 RAGSystem 进行查询，返回包含来源的答案
    输出数据格式：
      - string: 基于知识库的回答，包含参考来源
    """
    update_knowledge_base_if_needed()
    rag_system = get_rag_system()
    result = rag_system.query(question, include_sources=True)
    answer = result['answer']
    if '**📚 参考来源：**' not in answer and result.get('source_documents'):
        source_info = "\n\n**📚 参考来源：**\n"
        for i, doc in enumerate(result['source_documents'], 1):
            filename = doc.get('filename', '未知文件')
            source_info += f"{i}. {filename}\n"
        answer += source_info
    return answer


@tool
def update_knowledge_base() -> str:
    """
    手动更新知识库

    输入参数：
      - 无
    业务处理：
      - 清理并重建知识库索引
    输出数据格式：
      - string: 更新结果信息
    """
    # 通过重置单例并重新初始化实现更新
    from .knowledge import _rag_system_cache  # type: ignore
    globals_dict = globals()
    # 直接赋值以确保缓存被清空
    # 注意：此处依赖 knowledge 模块的模块级变量
    # 在本项目结构中是安全的
    # 清空缓存并重建
    import importlib
    import agent.knowledge as knowledge_module  # type: ignore
    knowledge_module._rag_system_cache = None
    knowledge_module.get_rag_system()
    return "知识库更新成功"




# 导出所有工具函数
__all__ = [
    'toggle_layer_visibility',
    'query_features_by_attribute', 
    'save_query_results_as_layer',
    'get_open_layers',
    'execute_buffer_analysis',
    'execute_intersection_analysis',
    'execute_erase_analysis',
    'execute_shortest_path_analysis',
    'save_buffer_results_as_layer',
    'save_intersection_results_as_layer',
    'save_erase_results_as_layer',
    'save_path_results_as_layer',
    'query_knowledge_base',
    'update_knowledge_base'
]
