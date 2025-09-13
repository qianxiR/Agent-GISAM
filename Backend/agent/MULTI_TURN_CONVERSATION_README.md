# 多轮对话功能说明

## 🎯 功能概述

已成功实现多轮对话功能，AI助手现在可以：

1. **保持对话上下文**: 记住之前的对话内容，提供连贯的回复
2. **智能引用历史**: 基于对话历史理解用户的问题
3. **会话管理**: 支持多个独立的对话会话
4. **历史追溯**: 可以查询"刚才做了什么"等历史相关问题

## 🛠 核心特性

### 1. 对话历史管理

- **自动记录**: 每次对话自动记录用户输入和AI回复
- **上下文感知**: AI可以基于最近5轮对话理解用户意图
- **历史限制**: 自动限制历史记录长度（保留最近20轮对话）
- **会话隔离**: 不同conversation_id的对话完全独立

### 2. 智能上下文理解

AI现在可以理解以下类型的上下文引用：

```
用户: "请查询武汉市的基本概况"
AI: [查询知识库并回复武汉概况]

用户: "刚才提到的长江和汉江，它们的水质情况如何？"
AI: [基于上一轮对话，继续查询相关知识]
```

### 3. 操作历史追踪

- **图层操作**: 记录所有图层显示/隐藏、分析等操作
- **工具调用**: 记录每次工具调用的结果
- **历史查询**: 支持"刚才做了什么"等历史查询

## 🚀 使用方法

### 启动服务

```bash
cd Backend/agent
python -m uvicorn agent.app:app --reload --host 0.0.0.0 --port 8089
```

### 多轮对话示例

```python
import requests

conversation_id = "my_conversation"

# 第一轮对话
response1 = requests.post("http://localhost:8086/agent/tool-chat", json={
    "model": "qwen-max",
    "temperature": 0.7,
    "prompt": "请查询武汉市的基本概况信息",
    "conversation_id": conversation_id
})

# 第二轮对话（基于上下文）
response2 = requests.post("http://localhost:8086/agent/tool-chat", json={
    "model": "qwen-max",
    "temperature": 0.7,
    "prompt": "刚才提到的长江和汉江，它们的水质情况如何？",
    "conversation_id": conversation_id  # 使用相同的conversation_id
})

# 第三轮对话（询问历史操作）
response3 = requests.post("http://localhost:8086/agent/tool-chat", json={
    "model": "qwen-max",
    "temperature": 0.7,
    "prompt": "刚才做了什么操作？",
    "conversation_id": conversation_id
})
```

## 📊 对话管理接口

### 1. 获取对话历史

```bash
GET /agent/conversation/{conversation_id}/history
```

返回：
```json
{
  "success": true,
  "data": {
    "conversation_id": "my_conversation",
    "message_count": 6,
    "layer_operations": 2,
    "messages": [
      {
        "role": "user",
        "content": "请查询武汉市的基本概况信息",
        "timestamp": "2024-01-01T10:00:00"
      },
      {
        "role": "assistant", 
        "content": "根据知识库查询结果...",
        "timestamp": "2024-01-01T10:00:05"
      }
    ],
    "layer_history": ["action:show_layer", "action:buffer_analysis"]
  }
}
```

### 2. 列出所有会话

```bash
GET /agent/conversations
```

返回：
```json
{
  "success": true,
  "data": {
    "total_conversations": 3,
    "conversations": [
      {
        "conversation_id": "conversation_1",
        "message_count": 10,
        "layer_operations": 5,
        "last_activity": "2024-01-01T10:30:00"
      }
    ]
  }
}
```

### 3. 清除对话历史

```bash
DELETE /agent/conversation/{conversation_id}
```

## 🧪 测试多轮对话

### 运行完整测试

```bash
cd Backend/agent
python test_multi_turn_conversation.py
```

### 运行演示

```bash
cd Backend/agent
python demo_multi_turn.py
```

## 🎯 使用场景

### 1. 知识查询 + 深入分析

```
用户: "请查询武汉市的基本概况"
AI: [查询知识库，返回武汉概况]

用户: "刚才提到的长江和汉江，它们的水质情况如何？"
AI: [基于上下文，继续查询水质相关信息]

用户: "基于这些信息，帮我分析一下长江武汉段的水质监测情况"
AI: [结合知识库和工具调用，提供综合分析]
```

### 2. 操作历史查询

```
用户: "刚才做了什么操作？"
AI: [基于操作历史回答]

用户: "能重复一下刚才的缓冲区分析吗？"
AI: [基于历史操作提供相关信息]
```

### 3. 多会话管理

```
# 会话A：水质分析
conversation_id = "water_analysis"
用户: "分析长江水质"

# 会话B：地理查询  
conversation_id = "geography_query"
用户: "查询武汉地理信息"

# 两个会话完全独立，互不影响
```

## ⚡ 性能优化

- **历史限制**: 自动限制历史记录长度，避免内存溢出
- **智能上下文**: 只传递最近5轮对话给AI，提高效率
- **会话隔离**: 不同会话独立管理，互不干扰
- **自动清理**: 支持手动清除不需要的对话历史

## 🔍 监控与调试

### 查看对话状态

```bash
curl http://localhost:8086/agent/conversations
```

### 查看特定对话历史

```bash
curl http://localhost:8086/agent/conversation/my_conversation/history
```

### 清除对话历史

```bash
curl -X DELETE http://localhost:8086/agent/conversation/my_conversation
```

## 🎉 总结

多轮对话功能让您的AI助手更加智能和人性化：

1. **上下文连贯**: AI可以理解对话的上下文，提供更准确的回复
2. **历史追溯**: 支持查询历史操作和对话内容
3. **会话管理**: 支持多个独立的对话会话
4. **智能决策**: 结合知识库查询和工具调用，提供完整的解决方案

现在您可以与AI进行自然流畅的多轮对话了！
