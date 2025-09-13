#!/usr/bin/env python3
"""
流式聊天功能测试脚本
"""
import requests
import json
import time

def test_stream_chat():
    """测试流式聊天接口"""
    url = "http://localhost:8089/agent/tool-chat"
    
    # 测试数据 - 流式输出
    data = {
        "model": "qwen-plus",
        "temperature": 0.7,
        "prompt": "请介绍一下自己",
        "conversation_id": "test_stream",
        "stream": True
    }
    
    print("🚀 开始测试流式聊天接口...")
    print(f"📝 请求数据: {json.dumps(data, ensure_ascii=False, indent=2)}")
    print("=" * 50)
    
    try:
        response = requests.post(url, json=data, stream=True)
        response.raise_for_status()
        
        print("📡 流式响应:")
        print("-" * 30)
        
        for line in response.iter_lines():
            if line:
                line_str = line.decode('utf-8')
                if line_str.startswith('data: '):
                    try:
                        data_str = line_str[6:]  # 移除 'data: ' 前缀
                        data_obj = json.loads(data_str)
                        
                        if data_obj['type'] == 'content':
                            print(data_obj['content'], end='', flush=True)
                        elif data_obj['type'] == 'usage':
                            print(f"\n\n📊 Token用量:")
                            print(f"   输入: {data_obj['usage']['prompt_tokens']}")
                            print(f"   输出: {data_obj['usage']['completion_tokens']}")
                            print(f"   总计: {data_obj['usage']['total_tokens']}")
                        elif data_obj['type'] == 'complete':
                            print(f"\n\n✅ 完整回复已接收")
                        elif data_obj['type'] == 'task_start':
                            print(f"\n🚀 任务开始: {data_obj.get('task_id', 'N/A')}")
                        elif data_obj['type'] == 'error':
                            print(f"\n❌ 错误: {data_obj['error']}")
                        elif data_obj['type'] == 'done':
                            print(f"\n🏁 流式响应完成 (任务ID: {data_obj.get('task_id', 'N/A')})")
                            break
                            
                    except json.JSONDecodeError as e:
                        print(f"\n⚠️ JSON解析错误: {e}")
                        print(f"原始数据: {line_str}")
        
        print("\n" + "=" * 50)
        print("✅ 流式聊天测试完成")
        
    except requests.exceptions.RequestException as e:
        print(f"❌ 请求失败: {e}")
    except Exception as e:
        print(f"❌ 测试失败: {e}")

def test_normal_chat():
    """测试普通聊天接口（非流式）"""
    url = "http://localhost:8089/agent/tool-chat"
    
    # 测试数据 - 非流式输出
    data = {
        "model": "qwen-plus",
        "temperature": 0.7,
        "prompt": "你好，请简单介绍一下自己",
        "conversation_id": "test_normal",
        "stream": False
    }
    
    print("🚀 开始测试普通聊天接口...")
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
        print("✅ 普通聊天测试完成")
        
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
        
        if 'Stream Chat' in str(data):
            print("✅ 流式聊天功能已启用")
        else:
            print("⚠️ 流式聊天功能未检测到")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ 健康检查失败: {e}")
    except Exception as e:
        print(f"❌ 健康检查异常: {e}")

if __name__ == "__main__":
    print("🧪 Agent Service 流式聊天功能测试")
    print("=" * 60)
    
    # 先检查服务状态
    test_health_check()
    print()
    
    # 测试普通聊天（非流式）
    test_normal_chat()
    print()
    
    # 测试流式聊天
    test_stream_chat()
