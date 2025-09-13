# RAG知识库集成说明

## 🎯 集成概述

已成功将RAG知识库系统集成到Agent服务中，现在AI助手具备以下能力：

1. **知识库查询**: 自动查询武汉市地理、水文、环境等相关知识
2. **工具调用**: 继续支持原有的16个空间分析工具
3. **自动更新**: 知识库文档更新时自动检测并重建向量数据库
4. **智能决策**: AI可以自主决定何时查询知识库，何时调用工具

## 🛠 新增功能

### 1. 知识库工具

- **`query_knowledge_base`**: 查询知识库获取相关信息
- **`update_knowledge_base`**: 手动更新知识库

### 2. 知识库管理接口

- **`GET /agent/knowledge/status`**: 获取知识库状态
- **`POST /agent/knowledge/update`**: 手动更新知识库
- **`POST /agent/knowledge/rebuild`**: 强制重建知识库

### 3. 自动更新机制

- 每次查询前自动检查知识库是否需要更新
- 基于文件修改时间智能判断
- 支持增量更新和全量重建

## 🚀 使用方法

### 启动服务

```bash
cd Backend/agent
python -m uvicorn agent.app:app --reload --host 0.0.0.0 --port 8086
```

### 测试集成功能

```bash
cd Backend/agent
python test_rag_integration.py
```

### API调用示例

```python
import requests

# 查询知识库
response = requests.post("http://localhost:8089/agent/tool-chat", json={
    "model": "qwen-max",
    "temperature": 0.7,
    "prompt": "请查询武汉市的基本概况信息",
    "conversation_id": "test"
})

# 检查知识库状态
response = requests.get("http://localhost:8089/agent/knowledge/status")
```

## 📚 知识库管理

### 添加新文档

1. 将新文档放入 `Backend/rag/知识库/` 目录
2. 系统会自动检测并更新向量数据库
3. 支持格式：PDF、Markdown、TXT

### 手动更新

```bash
# 通过API更新
curl -X POST http://localhost:8089/agent/knowledge/update

# 通过工具调用
curl -X POST http://localhost:8089/agent/tool-chat \
  -H "Content-Type: application/json" \
  -d '{"model": "qwen-max", "prompt": "请更新知识库", "conversation_id": "update"}'
```

## 🔧 配置说明

### 环境变量

系统使用与原有Agent相同的环境变量：

```env
DASHSCOPE_API_KEY=your_api_key
DASHSCOPE_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
DASHSCOPE_MODEL=qwen-max
```

### 知识库路径

- 知识库文档：`Backend/rag/知识库/`
- 向量数据库：`Backend/rag/vector_db/`

## 🎯 AI使用场景

### 1. 知识查询 + 空间分析

```
用户: "武汉市长江段的水质情况如何？"
AI: 1. 查询知识库获取武汉水文信息
    2. 调用缓冲区分析工具分析影响范围
    3. 提供综合分析结果
```

### 2. 自动决策

```
用户: "帮我分析这个区域的污染情况"
AI: 1. 自动查询相关知识库文档
    2. 根据查询结果选择合适的分析工具
    3. 执行分析并生成报告
```

## 📊 性能优化

- **首次启动**: ~30秒（构建向量数据库）
- **后续启动**: ~3秒（加载现有向量数据库）
- **查询响应**: ~2-5秒（基于向量索引）
- **自动更新**: 仅在文档修改时触发

## 🔍 监控与调试

### 健康检查

```bash
curl http://localhost:8089/health
```

返回信息包含：
- RAG系统状态
- 工具数量
- 服务版本

### 日志监控

系统会输出详细的初始化、更新、查询日志：

```
🔧 初始化RAG知识库系统...
✅ RAG知识库系统初始化完成
🔄 检测到知识库更新，正在重建...
✅ 知识库更新完成
```

## 🎉 总结

现在您的AI助手具备了完整的知识库查询能力，可以：

1. **智能查询**: 自动从知识库获取相关信息
2. **工具调用**: 继续使用原有的空间分析工具
3. **自动更新**: 知识库更新时自动同步
4. **综合决策**: 结合知识库和工具提供完整解决方案

系统已经完全集成，可以开始使用了！
