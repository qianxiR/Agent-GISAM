# RAG知识库系统

基于LangChain和通义千问(Qwen)模型构建的检索增强生成(RAG)知识库系统。

## 功能特性

- 📚 **多格式文档支持**: 支持PDF、Markdown、TXT等格式
- 🔍 **智能文档分块**: 自动将长文档切分为适合检索的文本块
- 🧠 **向量化存储**: 使用FAISS向量数据库进行高效检索
- 🤖 **智能问答**: 基于检索内容生成准确回答
- 🔧 **灵活配置**: 参考app.py的配置方式，支持环境变量配置

## 系统架构

```
RAG系统
├── 文档加载 (Document Loader)
├── 文本分块 (Text Splitter)
├── 向量化 (Embedding)
├── 向量存储 (Vector Store)
├── 检索器 (Retriever)
└── 生成器 (LLM)
```

## 快速开始

### 1. 环境准备

```bash
# 安装依赖
pip install -r requirements.txt

# 配置环境变量（参考Backend/.env）
DASHSCOPE_API_KEY=your_api_key
DASHSCOPE_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
DASHSCOPE_MODEL=qwen-plus
```

### 2. 准备知识库

将您的文档放入 `知识库/` 目录：
```
知识库/
├── 武汉市介绍.md
├── 水文.md
├── 基本概况.md
└── 其他文档...
```

### 3. 运行测试

```bash
# 运行完整测试
python test_rag.py

# 或者直接运行RAG系统
python rag_system.py
```

## 使用示例

### 基础使用

```python
from rag_system import RAGSystem

# 初始化系统
rag = RAGSystem()

# 构建知识库
rag.build_knowledge_base()

# 查询
result = rag.query("武汉市的地理位置是什么？")
print(result['answer'])
```

### 高级配置

```python
# 自定义知识库路径
rag = RAGSystem(knowledge_base_path="/path/to/your/knowledge")

# 强制重建向量数据库
rag.build_knowledge_base(force_rebuild=True)

# 查询并获取详细信息
result = rag.query("武汉的气候特征如何？")
print(f"回答: {result['answer']}")
print(f"参考文档: {len(result['source_documents'])} 个")
```

## 配置说明

### 环境变量

| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| DASHSCOPE_API_KEY | 通义千问API密钥 | - |
| DASHSCOPE_BASE_URL | API基础URL | https://dashscope.aliyuncs.com/compatible-mode/v1 |
| DASHSCOPE_MODEL | 模型名称 | qwen-plus |

### 系统参数

- **chunk_size**: 文档分块大小 (默认: 1000字符)
- **chunk_overlap**: 分块重叠大小 (默认: 200字符)
- **search_k**: 检索文档数量 (默认: 3个)

## 文件结构

```
Backend/rag/
├── rag_system.py          # 核心RAG系统
├── test_rag.py           # 测试脚本
├── requirements.txt      # 依赖包
├── README.md            # 说明文档
├── 知识库/              # 知识库文档目录
│   ├── 武汉市介绍.md
│   ├── 水文.md
│   └── 基本概况.md
└── vector_db/           # 向量数据库（自动生成）
```

## 测试用例

系统包含以下测试用例：

1. **武汉市基本概况查询**
2. **水系和湖泊信息查询**
3. **气候特征查询**
4. **历史发展查询**
5. **交互式问答测试**

## 注意事项

1. **API密钥**: 确保正确配置通义千问API密钥
2. **文档编码**: 确保文档使用UTF-8编码
3. **向量数据库**: 首次运行会创建向量数据库，后续运行会直接加载
4. **内存使用**: 大型知识库可能需要较多内存

## 故障排除

### 常见问题

1. **模型初始化失败**
   - 检查API密钥是否正确
   - 确认网络连接正常

2. **文档加载失败**
   - 检查文件编码是否为UTF-8
   - 确认文件路径正确

3. **向量数据库错误**
   - 删除vector_db目录重新构建
   - 检查磁盘空间是否充足

## 扩展功能

- 🔄 **增量更新**: 支持知识库增量更新
- 🌐 **Web接口**: 可扩展为Web API服务
- 📊 **性能监控**: 添加查询性能统计
- 🎯 **多模态支持**: 支持图片、表格等多媒体内容
