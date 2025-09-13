"""
测试多轮对话功能
"""
import requests
import json
import time

def test_multi_turn_conversation():
    """测试多轮对话功能"""
    base_url = "http://localhost:8089"
    conversation_id = "test_multi_turn"
    
    print("🧪 测试多轮对话功能")
    print("="*50)
    
    # 测试对话序列
    conversation_flow = [
        {
            "step": 1,
            "user_input": "请查询武汉市的基本概况信息",
            "expected_behavior": "应该调用知识库查询工具"
        },
        {
            "step": 2,
            "user_input": "刚才查询的结果中，武汉有哪些主要水系？",
            "expected_behavior": "应该结合上一轮对话上下文，继续查询知识库"
        },
        {
            "step": 3,
            "user_input": "基于刚才的信息，帮我分析一下长江武汉段的水质监测情况",
            "expected_behavior": "应该结合对话历史，调用相关分析工具"
        },
        {
            "step": 4,
            "user_input": "刚才做了什么操作？",
            "expected_behavior": "应该基于操作历史回答"
        }
    ]
    
    print(f"📝 使用对话ID: {conversation_id}")
    print(f"🔄 将进行 {len(conversation_flow)} 轮对话测试\n")
    
    for i, turn in enumerate(conversation_flow, 1):
        print(f"--- 第 {i} 轮对话 ---")
        print(f"👤 用户: {turn['user_input']}")
        print(f"🎯 预期行为: {turn['expected_behavior']}")
        
        try:
            # 发送请求
            response = requests.post(
                f"{base_url}/agent/tool-chat",
                json={
                    "model": "qwen-max",
                    "temperature": 0.7,
                    "prompt": turn['user_input'],
                    "conversation_id": conversation_id
                },
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                result = response.json()
                if result['success']:
                    print(f"✅ 请求成功")
                    
                    # 显示AI回复
                    final_answer = result['data']['final_answer']
                    print(f"🤖 AI回复: {final_answer[:200]}...")
                    
                    # 检查工具调用
                    tool_calls = result['data'].get('first_call', {}).get('tool_calls', [])
                    if tool_calls:
                        tool_name = tool_calls[0].get('name', '')
                        print(f"🔧 调用工具: {tool_name}")
                    else:
                        print("💬 直接回复（未调用工具）")
                    
                    print(f"🆔 任务ID: {result['task_id']}")
                    
                else:
                    print(f"❌ 请求失败: {result.get('error')}")
            else:
                print(f"❌ HTTP错误: {response.status_code}")
                
        except Exception as e:
            print(f"❌ 请求异常: {e}")
        
        print()  # 空行分隔
        time.sleep(1)  # 短暂延迟
    
    # 测试对话历史查询
    print("--- 查询对话历史 ---")
    try:
        response = requests.get(f"{base_url}/agent/conversation/{conversation_id}/history")
        if response.status_code == 200:
            history_data = response.json()
            if history_data['success']:
                data = history_data['data']
                print(f"✅ 对话历史查询成功")
                print(f"📊 消息数量: {data['message_count']}")
                print(f"🔧 图层操作: {data['layer_operations']}")
                
                # 显示最近几条消息
                messages = data['messages']
                if messages:
                    print(f"📝 最近消息:")
                    for msg in messages[-4:]:  # 显示最近4条消息
                        role = "👤 用户" if msg['role'] == 'user' else "🤖 助手"
                        content = msg['content'][:100] + "..." if len(msg['content']) > 100 else msg['content']
                        print(f"   {role}: {content}")
            else:
                print(f"❌ 历史查询失败: {history_data.get('error')}")
        else:
            print(f"❌ 历史查询HTTP错误: {response.status_code}")
    except Exception as e:
        print(f"❌ 历史查询异常: {e}")
    
    # 测试会话列表
    print("\n--- 查询会话列表 ---")
    try:
        response = requests.get(f"{base_url}/agent/conversations")
        if response.status_code == 200:
            conversations_data = response.json()
            if conversations_data['success']:
                data = conversations_data['data']
                print(f"✅ 会话列表查询成功")
                print(f"📊 总会话数: {data['total_conversations']}")
                
                for conv in data['conversations']:
                    print(f"   📝 {conv['conversation_id']}: {conv['message_count']} 条消息")
            else:
                print(f"❌ 会话列表查询失败: {conversations_data.get('error')}")
        else:
            print(f"❌ 会话列表HTTP错误: {response.status_code}")
    except Exception as e:
        print(f"❌ 会话列表查询异常: {e}")
    
    print("\n" + "="*50)
    print("🎉 多轮对话测试完成！")

def test_conversation_management():
    """测试对话管理功能"""
    base_url = "http://localhost:8089"
    test_conversation_id = "test_management"
    
    print("\n🧪 测试对话管理功能")
    print("="*40)
    
    # 1. 创建一些对话
    print("1️⃣ 创建测试对话...")
    for i in range(3):
        try:
            response = requests.post(
                f"{base_url}/agent/tool-chat",
                json={
                    "model": "qwen-max",
                    "temperature": 0.7,
                    "prompt": f"这是第{i+1}条测试消息",
                    "conversation_id": f"{test_conversation_id}_{i}"
                }
            )
            if response.status_code == 200:
                print(f"   ✅ 创建对话 {test_conversation_id}_{i}")
        except Exception as e:
            print(f"   ❌ 创建对话失败: {e}")
    
    # 2. 查询会话列表
    print("\n2️⃣ 查询会话列表...")
    try:
        response = requests.get(f"{base_url}/agent/conversations")
        if response.status_code == 200:
            data = response.json()
            if data['success']:
                print(f"   ✅ 当前活跃会话: {data['data']['total_conversations']} 个")
            else:
                print(f"   ❌ 查询失败: {data.get('error')}")
    except Exception as e:
        print(f"   ❌ 查询异常: {e}")
    
    # 3. 清除特定对话
    print("\n3️⃣ 清除测试对话...")
    try:
        response = requests.delete(f"{base_url}/agent/conversation/{test_conversation_id}_0")
        if response.status_code == 200:
            data = response.json()
            if data['success']:
                print(f"   ✅ 对话已清除: {data['message']}")
            else:
                print(f"   ❌ 清除失败: {data.get('error')}")
    except Exception as e:
        print(f"   ❌ 清除异常: {e}")
    
    print("\n✅ 对话管理测试完成！")

if __name__ == "__main__":
    test_multi_turn_conversation()
    test_conversation_management()
