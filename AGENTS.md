# AGENTS.md

面向 ZCode / AI 代理的工作区说明。项目细节另见 `CLAUDE.md`（较详尽）与根 `README.md`；二者与本文件冲突时，以本文件和实际启动脚本为准。

## 项目定位

基于微服务架构的 WebGIS 系统，面向武汉长江流域的实时地理空间监测与分析。前端（Vue 3）+ 后端三个微服务（Agent / User / Analysis），通过 EDA（事件驱动）方式将 LLM Agent 与传统 GIS 分析能力串联。

## 仓库结构

```
Agent-GISAM/
├─ Frontend/                 Vue 3 + TS + Vite + Pinia，端口 5173
│  └─ src/  (api, components, composables, stores, router, views, types)
├─ Backend/
│  ├─ agent/                 FastAPI + LangChain/LangGraph + 通义千问，端口 8089
│  │  ├─ app.py              FastAPI 入口（agent.app:app）
│  │  ├─ prompt.md           系统提示词，聊天时自动注入
│  │  ├─ tools.py / tools/   Agent 工具集（返回供前端解析的指令字符串）
│  │  └─ knowledge.py        RAG 知识库
│  ├─ user/                  FastAPI + PostgreSQL，DDD 架构，端口 8088
│  └─ analysis/              Node.js + Express + Turf.js，DDD 架构，端口 8087
│     └─ src/app.js          入口（npm run dev）
├─ Backend/.env              后端统一配置（DashScope、PostgreSQL、JWT 等）
├─ requirements.txt          Agent/User 服务 Python 依赖（根目录）
└─ start_services*.bat       Windows 一键启动脚本
```

注意：`.gitignore` 未跟踪大部分 `Frontend/src`（components/views/assets/public）、所有 `*.env`、`Backend/rag/知识库`、`node_modules` 等。这些目录在本地可能存在，但不在版本控制内；改动前先确认是否本地独有。

## 启动与运行

**权威启动方式以仓库内 `.bat` 脚本为准**（`Backend/README.md` 中 `pyside6`/8000 的说法已过时）：

| 脚本 | Python 环境 | 启动的服务 |
|------|------------|-----------|
| `start_services.bat`（推荐） | conda `py310` | Analysis + Agent + Frontend（**不启动 User**） |
| `start_services_venv_tmp.bat` | `.venv_tmp` 虚拟环境 | Analysis + User + Agent + Frontend（全部四个） |

两个脚本都会先释放 5173/8087/8088/8089 端口。手动启动单服务：

```bash
# Agent（必须在 conda py310 环境下）
conda activate py310
cd Backend && python -m uvicorn agent.app:app --reload --host 0.0.0.0 --port 8089

# User
cd Backend/user && python -m uvicorn main:app --reload --host 0.0.0.0 --port 8088

# Analysis（Node）
cd Backend/analysis && npm run dev

# Frontend
cd Frontend && npm run dev
```

> 重要：本项目 Python 服务使用 conda 环境 **`py310`**（由 `start_services.bat` 与 `CLAUDE.md` 共同确认），不要使用其它默认环境。User 服务依赖 PostgreSQL，首次部署需 `cd Backend/user/scripts && python init_database.py` 及 `python create_default_admin.py`。

## 常用命令

```bash
# Frontend
cd Frontend && npm run dev          # 开发服务，端口 5173
cd Frontend && npm run build        # 生产构建
cd Frontend && npm run test:all     # 路由测试 + 构建测试

# Analysis
cd Backend/analysis && npm run dev
cd Backend/analysis && npm run lint      # eslint src/
cd Backend/analysis && npm test          # jest
```

类型检查：`Frontend/tsconfig.json` 启用 `strict`，但前端入口与多数文件为 `.js`/`.vue`；`@/*` 别名指向 `Frontend/src`。Analysis 引擎要求 Node `>=18`，Frontend 要求 `^20.19.0 || >=22.12.0`。

## 关键架构约定（修改前必读）

1. **EDA 事件驱动通信**：Agent 工具**不直接操作地图**，而是返回形如 `"action:layer_name"` 或 `"buffer_analysis:layer:radius:unit"` 的格式化字符串；前端 `ChatAssistant.vue` 监听 `llm-tool-response` 等 CustomEvent 后解析并执行真正的地图操作。新增/修改工具时必须保持该返回契约。

2. **Agent 服务**（`Backend/agent/app.py`）使用 LangGraph `create_react_agent` + `MemorySaver`；系统提示词从 `Backend/agent/prompt.md` 自动注入。为规避企业代理，入口处全局关闭了 SSL 校验（`urllib3.disable_warnings`、`PYTHONHTTPSVERIFY=0`）——修改网络层时留意此约定。

3. **User 服务为 DDD 分层**：`api → application(use_cases/dto) → domains(实体/仓储抽象/领域服务) → infrastructure(Postgres 实现)`，依赖单向。新功能按此分层落位，`app/core/container.py` 负责用例装配。

4. **Analysis 服务为 DDD 分层**，空间分析（缓冲/相交/擦除/最短路径）基于 Turf.js。

5. **配置优先级**：环境变量 > `Backend/.env` > 代码默认。关键变量：`DASHSCOPE_API_KEY`、`DASHSCOPE_MODEL`（默认 qwen-plus）、`CORS_ORIGINS`、PostgreSQL 连接字段、JWT `SECRET_KEY`、`SUPERMAP_SERVER_URL`（默认 http://localhost:8090，需独立运行的 SuperMap iServer 提供瓦片）。

## 服务地址

| 服务 | 地址 | 文档 |
|------|------|------|
| Frontend | http://localhost:5173 | — |
| Agent | http://localhost:8089 | /docs |
| User | http://localhost:8088 | /docs |
| Analysis | http://localhost:8087 | /docs |
| SuperMap iServer | http://localhost:8090 | 独立部署，提供地图服务 |
