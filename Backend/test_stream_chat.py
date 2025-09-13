#!/usr/bin/env python3
"""
聊天功能测试脚本
"""
import requests
import json
import time


def test_normal_chat():
    """测试聊天接口"""
    url = "http://localhost:8089/agent/tool-chat"
    
    # 测试数据
    data = {
        "model": "qwen-plus",
        "temperature": 0.7,
        "prompt": "你好，请简单介绍一下自己",
        "conversation_id": "test_normal"
    }
    
    print("🚀 开始测试聊天接口...")
    print(f"📝 请求数据: {json.dumps(data, ensure_ascii=False, indent=2)}")
    print("=" * 50)
    
    try:
        response = requests.post(url, json=data)
        response.raise_for_status()
        
        result = response.json()
        print("📡 响应结果:")
        print("-" * 30)
        
        if result.get('success'):
            print("✅ 请求成功")
            print(f"📋 任务ID: {result.get('task_id', 'N/A')}")
            
            data_content = result.get('data', {})
            if 'final_answer' in data_content:
                print(f"💬 回复内容: {data_content['final_answer']}")
            
            if 'tool_result' in data_content and data_content['tool_result']:
                print(f"🔧 工具结果: {data_content['tool_result']}")
        else:
            print(f"❌ 请求失败: {result.get('error', '未知错误')}")
        
        print("\n" + "=" * 50)
        print("✅ 聊天测试完成")
        
    except requests.exceptions.RequestException as e:
        print(f"❌ 请求失败: {e}")
    except Exception as e:
        print(f"❌ 测试失败: {e}")

def test_health_check():
    """测试健康检查接口"""
    url = "http://localhost:8089/health"
    
    print("🔍 检查服务健康状态...")
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        
        data = response.json()
        print(f"✅ 服务状态: {data['status']}")
        print(f"📋 服务版本: {data['version']}")
        print(f"🔧 功能列表:")
        for feature in data['features']:
            print(f"   - {feature}")
        
        if 'LLM Chat' in str(data):
            print("✅ 聊天功能已启用")
        else:
            print("⚠️ 聊天功能未检测到")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ 健康检查失败: {e}")
    except Exception as e:
        print(f"❌ 健康检查异常: {e}")

if __name__ == "__main__":
    print("🧪 Agent Service 聊天功能测试")
    print("=" * 60)
    
    # 先检查服务状态
    test_health_check()
    print()
    
    # 测试聊天功能
    test_normal_chat()
