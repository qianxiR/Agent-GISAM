"""
多轮对话演示脚本
展示AI如何在不同轮次中保持上下文连贯性
"""
import requests
import json

def demo_conversation():
    """演示多轮对话"""
    base_url = "http://localhost:8089"
    conversation_id = "demo_conversation"
    
    print("🎭 多轮对话演示")
    print("="*60)
    print("这个演示将展示AI如何在多轮对话中保持上下文连贯性")
    print("="*60)
    
    # 演示对话序列
    demo_turns = [
        {
            "user": "你好，我想了解武汉市的基本情况",
            "context": "第一轮：用户询问武汉基本情况，AI应该查询知识库"
        },
        {
            "user": "刚才提到的长江和汉江，它们的水质情况如何？",
            "context": "第二轮：用户基于上一轮回答继续询问，AI应该结合上下文"
        },
        {
            "user": "如果我要分析长江武汉段的水质监测点，应该怎么做？",
            "context": "第三轮：用户询问具体分析方法，AI应该结合知识库和工具调用"
        },
        {
            "user": "刚才你建议的分析方法中，缓冲区分析的具体参数是什么？",
            "context": "第四轮：用户询问具体参数，AI应该基于之前的建议回答"
        }
    ]
    
    for i, turn in enumerate(demo_turns, 1):
        print(f"\n🔄 第 {i} 轮对话")
        print(f"📝 上下文: {turn['context']}")
        print(f"👤 用户: {turn['user']}")
        print("-" * 40)
        
        try:
            response = requests.post(
                f"{base_url}/agent/tool-chat",
                json={
                    "model": "qwen-max",
                    "temperature": 0.7,
                    "prompt": turn['user'],
                    "conversation_id": conversation_id
                },
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                result = response.json()
                if result['success']:
                    # 显示AI回复
                    final_answer = result['data']['final_answer']
                    print(f"🤖 AI回复:")
                    print(f"   {final_answer}")
                    
                    # 显示工具调用信息
                    tool_calls = result['data'].get('first_call', {}).get('tool_calls', [])
                    if tool_calls:
                        tool_name = tool_calls[0].get('name', '')
                        print(f"🔧 调用的工具: {tool_name}")
                    
                    print(f"🆔 任务ID: {result['task_id']}")
                    
                else:
                    print(f"❌ 请求失败: {result.get('error')}")
            else:
                print(f"❌ HTTP错误: {response.status_code}")
                
        except Exception as e:
            print(f"❌ 请求异常: {e}")
        
        print("-" * 40)
    
    # 显示对话历史
    print(f"\n📚 对话历史总结")
    print("="*40)
    try:
        response = requests.get(f"{base_url}/agent/conversation/{conversation_id}/history")
        if response.status_code == 200:
            history_data = response.json()
            if history_data['success']:
                data = history_data['data']
                print(f"📊 总消息数: {data['message_count']}")
                print(f"🔧 图层操作数: {data['layer_operations']}")
                
                # 显示完整对话历史
                messages = data['messages']
                print(f"\n📝 完整对话历史:")
                for j, msg in enumerate(messages, 1):
                    role = "👤 用户" if msg['role'] == 'user' else "🤖 助手"
                    content = msg['content'][:150] + "..." if len(msg['content']) > 150 else msg['content']
                    print(f"   {j}. {role}: {content}")
            else:
                print(f"❌ 历史查询失败: {history_data.get('error')}")
        else:
            print(f"❌ 历史查询HTTP错误: {response.status_code}")
    except Exception as e:
        print(f"❌ 历史查询异常: {e}")
    
    print("\n" + "="*60)
    print("🎉 多轮对话演示完成！")
    print("💡 观察AI如何在多轮对话中保持上下文连贯性")

if __name__ == "__main__":
    demo_conversation()
