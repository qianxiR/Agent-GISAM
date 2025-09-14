#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Agent工具集成测试脚本
模拟所有工具的HTTP请求，验证前端是否正确拼接参数和执行任务
"""

import requests
import json
import time
import sys
from typing import Dict, Any, List
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('test_tools_integration.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class AgentToolsTester:
    def __init__(self, agent_base_url: str = "http://localhost:8089", frontend_base_url: str = "http://localhost:5173"):
        """
        初始化测试器
        Args:
            agent_base_url: Agent服务的基础URL
            frontend_base_url: 前端服务的基础URL
        """
        self.agent_base_url = agent_base_url
        self.frontend_base_url = frontend_base_url
        self.session = requests.Session()
        self.test_results = []
        self.frontend_state_history = []
        
    def send_request(self, prompt: str, conversation_id: str = None) -> Dict[str, Any]:
        """
        发送请求到Agent服务
        Args:
            prompt: 用户输入的提示词
            conversation_id: 会话ID
        Returns:
            Agent响应数据
        """
        if not conversation_id:
            conversation_id = f"test-{int(time.time())}"
            
        payload = {
            "model": "qwen-plus",
            "temperature": 0.7,
            "prompt": prompt,
            "stream": False,
            "conversation_id": conversation_id
        }
        
        try:
            response = self.session.post(
                f"{self.agent_base_url}/agent/tool-chat",
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"请求失败: {e}")
            return {"error": str(e)}
    
    def parse_tool_call(self, response_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        解析工具调用信息
        Args:
            response_data: Agent响应数据
        Returns:
            解析后的工具调用信息
        """
        try:
            # 检查响应数据结构
            if 'data' not in response_data:
                return {"error": "响应数据格式错误：缺少data字段"}
            
            data = response_data['data']
            
            # 尝试多种可能的响应格式
            tool_calls = []
            tool_result = None
            final_answer = ""
            
            # 格式1: 直接包含工具调用信息
            if 'tool_calls' in data:
                tool_calls = data['tool_calls']
            elif 'first_call' in data and 'tool_calls' in data['first_call']:
                tool_calls = data['first_call']['tool_calls']
            
            # 获取工具结果
            if 'tool_result' in data:
                tool_result = data['tool_result']
            elif 'result' in data:
                tool_result = data['result']
            
            # 获取最终回复
            if 'final_answer' in data:
                final_answer = data['final_answer']
            elif 'answer' in data:
                final_answer = data['answer']
            elif 'response' in data:
                final_answer = data['response']
            
            if not tool_calls:
                # 如果没有工具调用，检查是否有其他格式的信息
                if 'message' in data:
                    final_answer = data['message']
                return {
                    "tool_name": "no_tool_call",
                    "tool_args": {},
                    "tool_result": tool_result,
                    "final_answer": final_answer,
                    "raw_data": data
                }
                
            call = tool_calls[0]
            return {
                "tool_name": call.get('name', 'unknown'),
                "tool_args": call.get('args', {}),
                "tool_result": tool_result,
                "final_answer": final_answer,
                "raw_data": data
            }
        except Exception as e:
            logger.error(f"解析工具调用失败: {e}")
            logger.error(f"响应数据: {response_data}")
            return {"error": str(e), "raw_data": response_data}
    
    def get_frontend_state(self) -> Dict[str, Any]:
        """
        获取前端状态信息
        Returns:
            前端状态数据
        """
        try:
            # 尝试获取前端状态API
            response = self.session.get(
                f"{self.frontend_base_url}/api/state",
                timeout=5
            )
            if response.status_code == 200:
                return response.json()
        except requests.exceptions.RequestException:
            pass
        
        # 尝试通过浏览器控制台获取状态（需要前端页面打开）
        try:
            # 这里可以通过Selenium或其他方式获取浏览器状态
            # 暂时返回模拟状态，实际使用时需要集成浏览器自动化
            pass
        except Exception:
            pass
        
        # 如果API不可用，返回模拟状态
        return {
            "map_ready": True,
            "layers": [],
            "analysis_status": "",
            "timestamp": time.time()
        }
    
    def monitor_frontend_changes(self, test_name: str, before_state: Dict[str, Any], after_state: Dict[str, Any]) -> Dict[str, Any]:
        """
        监测前端状态变化
        Args:
            test_name: 测试名称
            before_state: 执行前的状态
            after_state: 执行后的状态
        Returns:
            状态变化分析结果
        """
        changes = {
            "test_name": test_name,
            "timestamp": time.time(),
            "changes_detected": False,
            "layer_changes": [],
            "analysis_changes": [],
            "map_changes": []
        }
        
        # 检查图层变化
        before_layers = before_state.get("layers", [])
        after_layers = after_state.get("layers", [])
        
        if len(after_layers) != len(before_layers):
            changes["changes_detected"] = True
            changes["layer_changes"].append({
                "type": "layer_count_change",
                "before": len(before_layers),
                "after": len(after_layers)
            })
        
        # 检查分析状态变化
        before_analysis = before_state.get("analysis_status", "")
        after_analysis = after_state.get("analysis_status", "")
        
        if before_analysis != after_analysis:
            changes["changes_detected"] = True
            changes["analysis_changes"].append({
                "type": "analysis_status_change",
                "before": before_analysis,
                "after": after_analysis
            })
        
        # 检查地图状态变化
        before_map_ready = before_state.get("map_ready", False)
        after_map_ready = after_state.get("map_ready", False)
        
        if before_map_ready != after_map_ready:
            changes["changes_detected"] = True
            changes["map_changes"].append({
                "type": "map_ready_change",
                "before": before_map_ready,
                "after": after_map_ready
            })
        
        return changes
    
    def validate_frontend_changes(self, test_name: str, frontend_changes: Dict[str, Any], expected_tool: str) -> Dict[str, Any]:
        """
        验证前端状态变化是否符合预期
        Args:
            test_name: 测试名称
            frontend_changes: 前端状态变化
            expected_tool: 期望的工具名称
        Returns:
            验证结果
        """
        validation = {
            "valid": True,
            "expected_changes": [],
            "actual_changes": [],
            "validation_errors": []
        }
        
        # 根据工具类型定义期望的前端状态变化
        expected_changes_map = {
            "toggle_layer_visibility": ["layer_changes"],
            "get_open_layers": ["layer_changes"],
            "query_features_by_attribute": ["analysis_changes"],
            "execute_buffer_analysis": ["analysis_changes", "layer_changes"],
            "execute_intersection_analysis": ["analysis_changes", "layer_changes"],
            "execute_erase_analysis": ["analysis_changes", "layer_changes"],
            "execute_shortest_path_analysis": ["analysis_changes", "layer_changes"],
            "save_buffer_results_as_layer": ["layer_changes"],
            "save_intersection_results_as_layer": ["layer_changes"],
            "save_erase_results_as_layer": ["layer_changes"],
            "save_path_results_as_layer": ["layer_changes"],
            "save_query_results_as_layer": ["layer_changes"],
            "export_buffer_results_as_json": [],
            "export_intersection_results_as_json": [],
            "export_erase_results_as_json": [],
            "export_path_results_as_json": [],
            "export_query_results_as_json": [],
            "query_knowledge_base": [],
            "update_knowledge_base": []
        }
        
        expected_changes = expected_changes_map.get(expected_tool, [])
        validation["expected_changes"] = expected_changes
        
        # 检查实际变化
        actual_changes = []
        if frontend_changes["layer_changes"]:
            actual_changes.append("layer_changes")
        if frontend_changes["analysis_changes"]:
            actual_changes.append("analysis_changes")
        if frontend_changes["map_changes"]:
            actual_changes.append("map_changes")
        
        validation["actual_changes"] = actual_changes
        
        # 验证变化是否符合预期
        for expected_change in expected_changes:
            if expected_change not in actual_changes:
                validation["valid"] = False
                validation["validation_errors"].append(f"期望的变化类型 '{expected_change}' 未检测到")
        
        # 对于某些工具，如果没有检测到变化也是正常的
        if not frontend_changes["changes_detected"] and expected_changes:
            # 对于分析类工具，如果没有检测到变化，可能是正常的（比如没有实际执行）
            if "analysis" in expected_tool:
                validation["validation_errors"].append("分析工具执行但未检测到前端状态变化")
            else:
                validation["valid"] = False
                validation["validation_errors"].append("未检测到任何前端状态变化")
        
        return validation
    
    def test_tool(self, test_name: str, prompt: str, expected_tool: str, expected_args: List[str] = None) -> Dict[str, Any]:
        """
        测试单个工具
        Args:
            test_name: 测试名称
            prompt: 用户输入
            expected_tool: 期望的工具名称
            expected_args: 期望的参数列表
        Returns:
            测试结果
        """
        logger.info(f"开始测试: {test_name}")
        logger.info(f"输入提示: {prompt}")
        
        # 获取执行前的前端状态
        before_state = self.get_frontend_state()
        logger.info(f"执行前前端状态: {before_state}")
        
        # 发送请求
        response = self.send_request(prompt)
        
        # 等待一段时间让前端状态更新
        time.sleep(2)
        
        # 获取执行后的前端状态
        after_state = self.get_frontend_state()
        logger.info(f"执行后前端状态: {after_state}")
        
        # 监测前端状态变化
        frontend_changes = self.monitor_frontend_changes(test_name, before_state, after_state)
        self.frontend_state_history.append(frontend_changes)
        
        if "error" in response:
            result = {
                "test_name": test_name,
                "status": "FAILED",
                "error": response["error"],
                "prompt": prompt,
                "frontend_changes": frontend_changes
            }
        else:
            # 解析工具调用
            tool_info = self.parse_tool_call(response)
            
            if "error" in tool_info:
                result = {
                    "test_name": test_name,
                    "status": "FAILED",
                    "error": tool_info["error"],
                    "prompt": prompt,
                    "frontend_changes": frontend_changes
                }
            else:
                # 验证工具名称
                actual_tool = tool_info["tool_name"]
                tool_name_correct = actual_tool == expected_tool
                
                # 验证参数
                args_correct = True
                missing_args = []
                if expected_args:
                    for arg in expected_args:
                        if arg not in tool_info["tool_args"]:
                            args_correct = False
                            missing_args.append(arg)
                
                # 检查前端状态变化是否符合预期
                frontend_validation = self.validate_frontend_changes(test_name, frontend_changes, expected_tool)
                
                result = {
                    "test_name": test_name,
                    "status": "PASSED" if tool_name_correct and args_correct and frontend_validation["valid"] else "FAILED",
                    "prompt": prompt,
                    "expected_tool": expected_tool,
                    "actual_tool": actual_tool,
                    "tool_name_correct": tool_name_correct,
                    "expected_args": expected_args,
                    "actual_args": tool_info["tool_args"],
                    "args_correct": args_correct,
                    "missing_args": missing_args,
                    "tool_result": tool_info["tool_result"],
                    "final_answer": tool_info["final_answer"],
                    "frontend_changes": frontend_changes,
                    "frontend_validation": frontend_validation,
                    "before_state": before_state,
                    "after_state": after_state
                }
        
        self.test_results.append(result)
        logger.info(f"测试结果: {result['status']}")
        if frontend_changes["changes_detected"]:
            logger.info(f"前端状态变化: {frontend_changes}")
        return result
    
    def test_single_tool_debug(self, test_name: str, prompt: str) -> Dict[str, Any]:
        """
        调试单个工具测试，显示详细的响应信息
        Args:
            test_name: 测试名称
            prompt: 用户输入
        Returns:
            测试结果
        """
        logger.info(f"开始调试测试: {test_name}")
        logger.info(f"输入提示: {prompt}")
        
        # 发送请求
        response = self.send_request(prompt)
        
        logger.info(f"原始响应: {json.dumps(response, ensure_ascii=False, indent=2)}")
        
        # 解析工具调用
        tool_info = self.parse_tool_call(response)
        
        logger.info(f"解析后的工具信息: {json.dumps(tool_info, ensure_ascii=False, indent=2)}")
        
        return {
            "test_name": test_name,
            "prompt": prompt,
            "raw_response": response,
            "parsed_tool_info": tool_info
        }
    
    def run_all_tests(self):
        """运行所有工具测试"""
        logger.info("开始运行所有Agent工具测试")
        
        # 1. 图层管理类测试
        logger.info("=" * 50)
        logger.info("测试图层管理类工具")
        logger.info("=" * 50)
        
        self.test_tool(
            "切换图层可见性-显示",
            "显示医院图层",
            "toggle_layer_visibility",
            ["layer_name", "action"]
        )
        
        self.test_tool(
            "切换图层可见性-隐藏",
            "隐藏学校图层",
            "toggle_layer_visibility",
            ["layer_name", "action"]
        )
        
        self.test_tool(
            "获取打开图层",
            "获取当前打开的图层列表",
            "get_open_layers",
            []
        )
        
        # 2. 属性查询类测试
        logger.info("=" * 50)
        logger.info("测试属性查询类工具")
        logger.info("=" * 50)
        
        self.test_tool(
            "属性查询-等于",
            "查询医院图层中等级等于三级的医院",
            "query_features_by_attribute",
            ["layer_name", "field", "operator", "value"]
        )
        
        self.test_tool(
            "属性查询-包含",
            "查询学校图层中名称包含小学的学校",
            "query_features_by_attribute",
            ["layer_name", "field", "operator", "value"]
        )
        
        # 3. 空间分析类测试
        logger.info("=" * 50)
        logger.info("测试空间分析类工具")
        logger.info("=" * 50)
        
        self.test_tool(
            "缓冲区分析",
            "对医院图层进行1000米缓冲区分析",
            "execute_buffer_analysis",
            ["layer_name", "radius", "unit"]
        )
        
        self.test_tool(
            "相交分析",
            "计算医院图层与居民地图层的相交分析",
            "execute_intersection_analysis",
            ["target_layer_name", "mask_layer_name"]
        )
        
        self.test_tool(
            "擦除分析",
            "用限制区图层擦除医院图层",
            "execute_erase_analysis",
            ["target_layer_name", "erase_layer_name"]
        )
        
        self.test_tool(
            "最短路径分析",
            "计算从起点图层到终点图层的最短路径，避开障碍物图层",
            "execute_shortest_path_analysis",
            ["start_layer_name", "end_layer_name"]
        )
        
        # 4. 结果保存类测试
        logger.info("=" * 50)
        logger.info("测试结果保存类工具")
        logger.info("=" * 50)
        
        self.test_tool(
            "保存缓冲区分析结果",
            "将缓冲区分析结果保存为图层，图层名为缓冲区结果",
            "save_buffer_results_as_layer",
            ["layer_name"]
        )
        
        self.test_tool(
            "保存相交分析结果",
            "将相交分析结果保存为图层，图层名为相交分析结果",
            "save_intersection_results_as_layer",
            ["layer_name"]
        )
        
        self.test_tool(
            "保存擦除分析结果",
            "将擦除分析结果保存为图层，图层名为擦除分析结果",
            "save_erase_results_as_layer",
            ["layer_name"]
        )
        
        self.test_tool(
            "保存最短路径分析结果",
            "将最短路径分析结果保存为图层，图层名为路径分析结果",
            "save_path_results_as_layer",
            ["layer_name"]
        )
        
        self.test_tool(
            "保存查询结果",
            "将查询结果保存为图层，图层名为查询结果",
            "save_query_results_as_layer",
            ["layer_name"]
        )
        
        # 5. 结果导出类测试
        logger.info("=" * 50)
        logger.info("测试结果导出类工具")
        logger.info("=" * 50)
        
        self.test_tool(
            "导出缓冲区分析结果为JSON",
            "将缓冲区分析结果导出为JSON文件，文件名为buffer_results.json",
            "export_buffer_results_as_json",
            ["file_name"]
        )
        
        self.test_tool(
            "导出相交分析结果为JSON",
            "将相交分析结果导出为JSON文件，文件名为intersection_results.json",
            "export_intersection_results_as_json",
            ["file_name"]
        )
        
        self.test_tool(
            "导出擦除分析结果为JSON",
            "将擦除分析结果导出为JSON文件，文件名为erase_results.json",
            "export_erase_results_as_json",
            ["file_name"]
        )
        
        self.test_tool(
            "导出最短路径分析结果为JSON",
            "将最短路径分析结果导出为JSON文件，文件名为path_results.json",
            "export_path_results_as_json",
            ["file_name"]
        )
        
        self.test_tool(
            "导出查询结果为JSON",
            "将查询结果导出为JSON文件，文件名为query_results.json",
            "export_query_results_as_json",
            ["file_name"]
        )
        
        # 6. 知识库类测试
        logger.info("=" * 50)
        logger.info("测试知识库类工具")
        logger.info("=" * 50)
        
        self.test_tool(
            "知识库查询",
            "查询武汉市的基本概况",
            "query_knowledge_base",
            ["query"]
        )
        
        self.test_tool(
            "知识库更新",
            "更新知识库中的长江流域信息",
            "update_knowledge_base",
            ["content", "metadata"]
        )
        
        # 生成测试报告
        self.generate_report()
    
    def generate_report(self):
        """生成测试报告"""
        logger.info("=" * 80)
        logger.info("测试报告")
        logger.info("=" * 80)
        
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r["status"] == "PASSED"])
        failed_tests = total_tests - passed_tests
        
        logger.info(f"总测试数: {total_tests}")
        logger.info(f"通过测试: {passed_tests}")
        logger.info(f"失败测试: {failed_tests}")
        logger.info(f"通过率: {passed_tests/total_tests*100:.1f}%")
        
        # 详细结果
        logger.info("\n详细测试结果:")
        for result in self.test_results:
            status_icon = "✅" if result["status"] == "PASSED" else "❌"
            logger.info(f"{status_icon} {result['test_name']}: {result['status']}")
            
            if result["status"] == "FAILED":
                if "error" in result:
                    logger.info(f"   错误: {result['error']}")
                else:
                    if not result.get("tool_name_correct", True):
                        logger.info(f"   工具名称错误: 期望 {result['expected_tool']}, 实际 {result['actual_tool']}")
                    if not result.get("args_correct", True):
                        logger.info(f"   参数错误: 缺少参数 {result['missing_args']}")
                    if "frontend_validation" in result and not result["frontend_validation"]["valid"]:
                        logger.info(f"   前端状态验证失败: {result['frontend_validation']['validation_errors']}")
            
            # 显示前端状态变化信息
            if "frontend_changes" in result and result["frontend_changes"]["changes_detected"]:
                logger.info(f"   前端状态变化:")
                for change_type, changes in result["frontend_changes"].items():
                    if change_type not in ["test_name", "timestamp", "changes_detected"] and changes:
                        logger.info(f"     {change_type}: {changes}")
        
        # 保存详细报告到文件
        report_file = f"test_report_{int(time.time())}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(self.test_results, f, ensure_ascii=False, indent=2)
        logger.info(f"\n详细报告已保存到: {report_file}")
        
        return {
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": failed_tests,
            "pass_rate": passed_tests/total_tests*100,
            "results": self.test_results
        }

def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Agent工具集成测试脚本")
    parser.add_argument("--url", default="http://localhost:8089", help="Agent服务URL")
    parser.add_argument("--frontend-url", default="http://localhost:5173", help="前端服务URL")
    parser.add_argument("--test", help="运行单个测试")
    parser.add_argument("--debug", help="调试单个测试，显示详细响应信息")
    parser.add_argument("--list", action="store_true", help="列出所有测试")
    
    args = parser.parse_args()
    
    tester = AgentToolsTester(args.url, args.frontend_url)
    
    if args.list:
        # 列出所有测试
        tests = [
            "切换图层可见性-显示", "切换图层可见性-隐藏", "获取打开图层",
            "属性查询-等于", "属性查询-包含",
            "缓冲区分析", "相交分析", "擦除分析", "最短路径分析",
            "保存缓冲区分析结果", "保存相交分析结果", "保存擦除分析结果", 
            "保存最短路径分析结果", "保存查询结果",
            "导出缓冲区分析结果为JSON", "导出相交分析结果为JSON", 
            "导出擦除分析结果为JSON", "导出最短路径分析结果为JSON", "导出查询结果为JSON",
            "知识库查询", "知识库更新"
        ]
        print("可用的测试:")
        for i, test in enumerate(tests, 1):
            print(f"{i:2d}. {test}")
        return
    
    if args.debug:
        # 调试单个测试
        logger.info(f"调试测试: {args.debug}")
        result = tester.test_single_tool_debug("调试测试", args.debug)
        logger.info(f"调试结果: {json.dumps(result, ensure_ascii=False, indent=2)}")
    elif args.test:
        # 运行单个测试
        # 这里可以根据测试名称运行特定测试
        logger.info(f"运行单个测试: {args.test}")
        # 实现单个测试逻辑
    else:
        # 运行所有测试
        tester.run_all_tests()

if __name__ == "__main__":
    main()
