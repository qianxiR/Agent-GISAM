"""
Agent工具定义模块
包含所有GIS分析工具的定义
"""
from typing import Dict, Any
from langchain_core.tools import tool


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
    return "success"


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
    return "success"


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
    return "success"


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
    return "success"


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
    return "success"


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
    return "success"


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
    return "success"


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


# 导出所有工具函数
__all__ = [
    'toggle_layer_visibility',
    'query_features_by_attribute', 
    'save_query_results_as_layer',
    'export_query_results_as_json',
    'get_open_layers',
    'execute_buffer_analysis',
    'execute_intersection_analysis',
    'execute_erase_analysis',
    'execute_shortest_path_analysis',
    'save_buffer_results_as_layer',
    'export_buffer_results_as_json',
    'save_intersection_results_as_layer',
    'export_intersection_results_as_json',
    'save_erase_results_as_layer',
    'export_erase_results_as_json',
    'save_path_results_as_layer',
    'export_path_results_as_json'
]
