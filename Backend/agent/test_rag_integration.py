"""
测试RAG集成后的Agent系统
"""
import requests
import json

def test_rag_integration():
    """测试RAG集成功能"""
    base_url = "http://localhost:8089"
    
    print("🧪 测试RAG集成后的Agent系统")
    print("="*50)
    
    # 1. 测试健康检查
    print("1️⃣ 测试健康检查...")
    try:
        response = requests.get(f"{base_url}/health")
        if response.status_code == 200:
            health_data = response.json()
            print(f"✅ 服务状态: {health_data['status']}")
            print(f"✅ RAG系统状态: {health_data.get('rag_system_status', 'unknown')}")
            print(f"✅ 工具数量: {health_data.get('tools_count', 0)}")
        else:
            print(f"❌ 健康检查失败: {response.status_code}")
            return
    except Exception as e:
        print(f"❌ 连接失败: {e}")
        return
    
    # 2. 测试知识库状态
    print("\n2️⃣ 测试知识库状态...")
    try:
        response = requests.get(f"{base_url}/agent/knowledge/status")
        if response.status_code == 200:
            kb_data = response.json()
            if kb_data['success']:
                data = kb_data['data']
                print(f"✅ 文档数量: {data['document_count']}")
                print(f"✅ 需要更新: {data['needs_update']}")
                print(f"✅ 向量数据库存在: {data['vector_db_exists']}")
            else:
                print(f"❌ 知识库状态查询失败: {kb_data.get('error')}")
        else:
            print(f"❌ 知识库状态查询失败: {response.status_code}")
    except Exception as e:
        print(f"❌ 知识库状态查询异常: {e}")
    
    # 3. 测试知识库查询工具
    print("\n3️⃣ 测试知识库查询工具...")
    try:
        test_request = {
            "model": "qwen-plus",
            "temperature": 0.7,
            "prompt": "请查询武汉市的基本概况信息",
            "conversation_id": "test_rag"
        }
        
        response = requests.post(
            f"{base_url}/agent/tool-chat",
            json=test_request,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            if result['success']:
                print("✅ 知识库查询工具调用成功")
                print(f"📝 回答: {result['data']['final_answer'][:200]}...")
                
                # 检查是否调用了知识库工具
                tool_calls = result['data'].get('first_call', {}).get('tool_calls', [])
                if tool_calls:
                    tool_name = tool_calls[0].get('name', '')
                    if tool_name == 'query_knowledge_base':
                        print("✅ 成功调用了知识库查询工具")
                    else:
                        print(f"⚠️ 调用了其他工具: {tool_name}")
                else:
                    print("⚠️ 没有调用任何工具")
            else:
                print(f"❌ 查询失败: {result.get('error')}")
        else:
            print(f"❌ 请求失败: {response.status_code}")
    except Exception as e:
        print(f"❌ 知识库查询测试异常: {e}")
    
    # 4. 测试知识库更新工具
    print("\n4️⃣ 测试知识库更新工具...")
    try:
        test_request = {
            "model": "qwen-plus",
            "temperature": 0.7,
            "prompt": "请更新知识库",
            "conversation_id": "test_update"
        }
        
        response = requests.post(
            f"{base_url}/agent/tool-chat",
            json=test_request,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            if result['success']:
                print("✅ 知识库更新工具调用成功")
                print(f"📝 回答: {result['data']['final_answer']}")
            else:
                print(f"❌ 更新失败: {result.get('error')}")
        else:
            print(f"❌ 请求失败: {response.status_code}")
    except Exception as e:
        print(f"❌ 知识库更新测试异常: {e}")
    
    print("\n" + "="*50)
    print("🎉 RAG集成测试完成！")

if __name__ == "__main__":
    test_rag_integration()
