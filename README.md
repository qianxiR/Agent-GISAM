# 🗺️ SuperMap 智能地理信息分析系统
基于EDA事件驱动Agent的武汉市长江流域地理空间实时势态感知智能决策分析及多源信息综合可视化监测预警一体化平台
> 基于微服务架构的现代化 WebGIS 全栈应用，集成 EDA 事件驱动 AI Agent 与传统 GIS 分析功能

[![Vue](https://img.shields.io/badge/Vue-3.5.18-4FC08D?logo=vue.js)](https://vuejs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104-009688?logo=fastapi)](https://fastapi.tiangolo.com/)
[![Node.js](https://img.shields.io/badge/Node.js-18.0+-339933?logo=node.js)](https://nodejs.org/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.9.2-3178C6?logo=typescript)](https://www.typescriptlang.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-336791?logo=postgresql)](https://www.postgresql.org/)
[![SuperMap](https://img.shields.io/badge/SuperMap-iServer-00A0E9)](https://www.supermap.com/)

## 📋 目录

- [项目概述](#项目概述)
- [功能特性](#功能特性)
- [技术栈](#技术栈)
- [项目结构](#项目结构)
- [快速开始](#快速开始)
- [使用指南](#使用指南)
- [开发指南](#开发指南)
- [测试](#测试)
- [部署](#部署)
- [贡献指南](#贡献指南)

## 🎯 项目概述

SuperMap 智能地理信息分析系统是一个基于微服务架构的现代化 WebGIS 全栈应用，采用前后端分离设计，集成了传统 GIS 分析功能与 AI 智能助手。系统提供完整的用户管理、空间分析和智能交互功能。

### 系统架构

```
┌─────────────────────────────────────────────────────────────────┐
│                        前端应用层                                │
│  Vue 3 + TypeScript + Openlayers + Pinia + Ant Design Vue     │
│  ├── 事件驱动架构 (CustomEvent)                                │
│  ├── 21个Pinia状态管理模块                                     │
│  ├── 25个UI组件 + 14个地图组件 + 17个图表组件 + 3个Agent组件     │
│  └── 25个组合式函数 (Composables)                              │
└─────────────────┬───────────────────────────────────────────────┘
                  │ HTTP/REST API + 事件驱动通信
┌─────────────────┴───────────────────────────────────────────────┐
│                       后端服务层                                │
├─────────────────────────────────────────────────────────────────┤
│  EDA事件驱动Agent服务 (FastAPI + LangChain)                    │
│  - 长江水域监测专业背景知识                                     │
│  - 17个工具函数 (图层管理+空间分析+结果导出)                    │
│  - 上下文记忆和会话管理                                         │
│  - 工具调用和结果反馈机制                                       │
├─────────────────────────────────────────────────────────────────┤
│  用户认证服务 (FastAPI + PostgreSQL + DDD架构)                 │
│  - 用户注册/登录/认证                                           │
│  - JWT 令牌管理                                                │
│  - 用户资料管理                                                │
├─────────────────────────────────────────────────────────────────┤
│  空间分析服务 (Node.js + Express + DDD架构)                    │
│  - 缓冲区分析                                                  │
│  - 相交分析                                                    │
│  - 擦除分析                                                    │
│  - 最短路径分析                                                │
└─────────────────────────────────────────────────────────────────┘
```

### 核心特性

- **EDA事件驱动架构**: 基于CustomEvent的前后端解耦通信机制
- **微服务架构**: EDA Agent服务 + 用户服务 + 空间分析服务，独立部署和扩展
- **双模式设计**: LLM 智能模式 + 传统 GIS 模式
- **实时地图交互**: 基于 Openlayers 的高性能地图渲染
- **完整分析工具**: 缓冲区、相交、擦除、最短路径等空间分析
- **智能AI助手**: 长江水域监测专业背景的AI Agent，支持17个工具函数
- **事件驱动通信**: 前端事件监听器 + 后端工具调用 + 结果反馈机制
- **用户管理系统**: 完整的用户认证、授权和资料管理
- **响应式界面**: 现代化 UI 设计，支持主题切换
- **状态持久化**: 17个Pinia状态模块的完整应用状态管理

## ✨ 功能特性

### 🔐 用户管理系统
- **用户认证**: 注册、登录、JWT 令牌管理
- **资料管理**: 用户信息修改、密码变更
- **权限控制**: 基于角色的访问控制
- **会话管理**: 安全的用户会话和登出

### 🧠 EDA事件驱动LLM智能模式
- **自然语言交互**: 通过聊天界面操作地图，支持长江水域监测专业术语
- **17个工具函数**: 图层管理、空间分析、结果导出的完整工具链
- **事件驱动通信**: 前端CustomEvent监听 + 后端LangChain工具调用
- **上下文记忆**: 会话历史管理和操作上下文自动识别
- **专业背景知识**: 长江水系特征、水质监测标准、监测点布局等专业知识
- **智能结果反馈**: 分析结果自动反馈和智能回应生成
- **多轮对话**: 支持复杂的地图分析任务和连续操作

### 🛠️ 传统 GIS 模式
- **图层管理**: 完整的图层控制与样式设置
- **要素查询**: 属性查询与空间查询
- **区域选择**: 矩形框选和多边形选择
- **空间分析**: 
  - 缓冲区分析 (基于 Turf.js)
  - 相交分析 (图层叠加分析)
  - 擦除分析 (图层差集计算)
  - 最短路径分析 (路径规划)
  - 叠置分析 (几何运算)
- **编辑工具**: 要素创建、修改、删除
- **测量工具**: 距离测量、面积计算

### 🗺️ 地图功能
- **多底图支持**: SuperMap iServer 集成
- **实时交互**: 基于 Openlayers 的高性能渲染
- **坐标显示**: 实时鼠标坐标显示
- **比例尺**: 动态比例尺显示
- **鹰眼地图**: 地图概览和快速定位
- **要素弹窗**: 点击要素查看详细信息

### 🎨 用户界面
- **响应式设计**: 适配各种屏幕尺寸
- **主题切换**: 明暗主题自动切换
- **分割面板**: 可调整的布局分割
- **通知系统**: 实时操作反馈
- **状态管理**: 21个Pinia状态模块的完整应用状态持久化
- **模块化组件**: 25个UI组件 + 14个地图组件 + 17个图表组件 + 3个Agent组件
- **事件驱动UI**: 基于CustomEvent的组件间解耦通信
- **路由驱动**: 每个功能面板独立路由，支持懒加载

## 🛠️ 技术栈

### 前端技术栈
- **Vue 3.5.18**: 渐进式 JavaScript 框架
- **TypeScript 5.9.2**: 类型安全的 JavaScript
- **Vite 7.0.6**: 下一代前端构建工具
- **Pinia 3.0.3**: Vue 官方推荐的状态管理库
- **Vue Router 4.5.1**: Vue.js 官方路由管理器

### 地图与空间分析
- **Openlayers 10.6.1**: 开源高性能地图库
- **SuperMap iClient**: SuperMap 客户端 SDK
- **Turf.js 7.2.0**: JavaScript 空间分析库
- **SuperMap iServer**: 企业级 GIS 服务

### UI 组件与样式
- **Ant Design Vue 4.2.6**: 企业级 UI 组件库
- **Splitpanes 4.0.4**: 可拖拽分割面板
- **CSS 变量**: 主题系统和响应式设计

### 后端技术栈

#### EDA事件驱动Agent服务 (Python)
- **FastAPI 0.104**: 现代高性能 Web 框架
- **LangChain**: AI Agent 框架和工具调用
- **LangGraph**: 多智能体工作流管理
- **通义千问 (Qwen)**: 阿里云大语言模型
- **Tavily Search**: 联网搜索能力
- **Pydantic**: 数据验证和序列化
- **17个工具函数**: 图层管理、空间分析、结果导出

#### 用户认证服务 (Python)
- **FastAPI 0.104**: 现代高性能 Web 框架
- **PostgreSQL 15**: 关系型数据库
- **SQLAlchemy**: Python ORM 框架
- **Pydantic**: 数据验证和序列化
- **JWT**: JSON Web Token 认证
- **Asyncpg**: 异步 PostgreSQL 驱动
- **DDD 架构**: 领域驱动设计

#### 空间分析服务 (Node.js)
- **Node.js 18.0+**: JavaScript 运行时
- **Express**: Web 应用框架
- **Turf.js**: 服务端空间分析
- **Joi**: 数据验证库
- **Winston**: 日志记录
- **Helmet**: 安全中间件
- **DDD 架构**: 领域驱动设计

### 开发工具
- **Vite**: 前端构建工具
- **ESLint**: 代码质量检查
- **TypeScript**: 静态类型检查
- **Swagger**: API 文档生成
- **Git**: 版本控制

## 📁 项目结构

### 整体架构

```
SuperMap/
├── Frontend/                   # 前端应用 (Vue 3 + TypeScript + 事件驱动)
│   ├── src/
│   │   ├── components/         # 组件库 (19个UI + 8个地图 + 2个布局)
│   │   ├── composables/        # 组合式函数 (12个)
│   │   ├── stores/            # 状态管理 (17个Pinia模块)
│   │   ├── views/             # 页面组件 (路由驱动)
│   │   └── docs/              # 前端架构文档
├── Backend/                    # 后端服务
│   ├── agent/                  # EDA事件驱动Agent服务 (FastAPI + LangChain)
│   ├── user/                   # 用户认证服务 (FastAPI + PostgreSQL + DDD)
│   └── analysis/               # 空间分析服务 (Node.js + Express + DDD)
├── docs/                       # 项目文档
└── README.md                   # 项目说明文档
```

### 前端结构 (Frontend/)

```
Frontend/
├── src/
│   ├── api/                    # API 接口层 (5个文件)
│   │   ├── config.ts           # Axios 配置和拦截器
│   │   ├── supermap.ts         # SuperMap iServer 接口
│   │   ├── hydrologyData.ts    # 水文数据接口
│   │   ├── waterQualityData.ts # 水质数据接口
│   │   └── yangtzeData.ts      # 长江数据接口
│   │
│   ├── components/             # 组件库 (4个分类)
│   │   ├── Agent/              # AI Agent组件 (3个文件)
│   │   │   ├── ChatMessagesPanel.vue
│   │   │   ├── LLMInputWindow.vue
│   │   │   └── prompt/         # 提示词文件
│   │   ├── Charts/             # 图表组件 (17个文件)
│   │   │   ├── AgeDistributionChart.vue
│   │   │   ├── EducationLevelChart.vue
│   │   │   ├── GenderRatioChart.vue
│   │   │   ├── HospitalDistributionChart.vue
│   │   │   ├── WaterQualityChart1-4.vue
│   │   │   └── ...             # 其他统计图表
│   │   ├── Map/                # 地图组件 (14个文件)
│   │   │   ├── CoordinateDisplay.vue
│   │   │   ├── ScaleBar.vue
│   │   │   ├── OverviewMap.vue
│   │   │   ├── FeaturePopup.vue
│   │   │   ├── LayerAssistant.vue
│   │   │   ├── DistanceMeasurePanel.vue
│   │   │   ├── AreaMeasurePanel.vue
│   │   │   └── ...             # 图例和控件组件
│   │   └── UI/                 # UI组件 (25个文件)
│   │       ├── PrimaryButton.vue
│   │       ├── SecondaryButton.vue
│   │       ├── IconButton.vue
│   │       ├── PanelWindow.vue
│   │       ├── NotificationManager.vue
│   │       └── ...             # 其他UI组件
│   │
│   ├── composables/            # 组合式函数 (25个文件)
│   │   ├── useMap.ts           # 地图核心逻辑
│   │   ├── useLayerManager.ts  # 图层管理 (事件驱动)
│   │   ├── useBufferAnalysis.ts # 缓冲区分析
│   │   ├── useFeatureQuery.ts  # 要素查询
│   │   ├── useIntersectionAnalysis.ts # 相交分析
│   │   ├── useEraseAnalysis.ts # 擦除分析
│   │   ├── useShortestPathAnalysis.ts # 最短路径分析
│   │   ├── useRealTimeWaterQuality.ts # 实时水质监测
│   │   ├── useMonitoringDataLayers.ts # 监测数据图层
│   │   ├── useMonitoringThreshold.ts # 监测阈值管理
│   │   └── ...                 # 其他业务逻辑
│   │
│   ├── stores/                 # 状态管理 (21个 Pinia stores)
│   │   ├── mapStore.ts         # 地图状态
│   │   ├── userStore.ts        # 用户状态
│   │   ├── analysisStore.ts    # 分析工具状态
│   │   ├── modeStateStore.ts   # 模式切换状态
│   │   ├── bufferAnalysisStore.ts # 缓冲区分析状态
│   │   ├── featureQueryStore.ts # 要素查询状态
│   │   ├── intersectionAnalysisStore.ts # 相交分析状态
│   │   ├── eraseAnalysisStore.ts # 擦除分析状态
│   │   ├── shortestPathAnalysisStore.ts # 最短路径分析状态
│   │   ├── monitoringDataStore.ts # 监测数据状态
│   │   ├── layerDataStore.ts   # 图层数据状态
│   │   ├── layerUIStore.ts     # 图层UI状态
│   │   ├── pageStateStore.ts   # 页面状态
│   │   ├── persistenceStore.ts # 持久化状态
│   │   └── ...                 # 其他状态模块
│   │
│   ├── views/                  # 页面组件 (路由驱动)
│   │   ├── auth/               # 认证页面 (2个文件)
│   │   │   ├── Login.vue
│   │   │   └── Register.vue
│   │   ├── dashboard/          # 主工作台
│   │   │   ├── management-analysis/ # 管理分析模块
│   │   │   │   ├── layout/     # 布局组件 (2个文件)
│   │   │   │   │   ├── DashboardManageHeader.vue
│   │   │   │   │   └── DashboardManageLayout.vue
│   │   │   │   ├── LLM/        # EDA事件驱动LLM模式 (3个文件)
│   │   │   │   │   ├── LLMMode.vue
│   │   │   │   │   ├── ChatAssistant.vue # 事件监听器
│   │   │   │   │   └── ChatHistory.vue
│   │   │   │   ├── traditional/ # 传统 GIS 模式
│   │   │   │   │   ├── TraditionalMode.vue
│   │   │   │   │   └── tools/  # 分析工具面板 (8个文件)
│   │   │   │   │       ├── LayerManager.vue
│   │   │   │   │       ├── FeatureQueryPanel.vue
│   │   │   │   │       ├── AreaSelectionTools.vue
│   │   │   │   │       ├── BufferAnalysisPanel.vue
│   │   │   │   │       ├── IntersectionAnalysisPanel.vue
│   │   │   │   │       ├── EraseAnalysisPanel.vue
│   │   │   │   │       ├── ShortestPathAnalysisPanel.vue
│   │   │   │   │       └── DataUploadPanel.vue
│   │   │   │   ├── management/ # 系统管理 (1个文件)
│   │   │   │   │   └── AIManagement.vue
│   │   │   │   ├── profile/    # 用户管理 (1个文件)
│   │   │   │   │   └── UserProfile.vue
│   │   │   │   ├── ManagementAnalysis.vue
│   │   │   │   ├── RightPanel.vue
│   │   │   │   └── SuperMapViewer.vue
│   │   │   └── ViewPage/       # 视图页面
│   │   │       ├── layout/     # 视图布局 (1个文件)
│   │   │       │   └── DashboardViewHeader.vue
│   │   │       ├── data/       # 数据文件 (4个文件)
│   │   │       ├── monitordata/ # 监测数据 (6个GeoJSON文件)
│   │   │       ├── processed_data/ # 处理数据 (8个文件)
│   │   │       ├── ViewHome.vue
│   │   │       ├── ViewLayerManager.vue
│   │   │       ├── ViewSubPage1-3.vue
│   │   │       └── ...         # 长江数据文件
│   │   └── Dashboard.vue
│   │
│   ├── router/                 # 路由配置 (嵌套路由)
│   ├── styles/                 # 全局样式 (主题系统)
│   ├── types/                  # TypeScript 类型定义 (7个文件)
│   ├── utils/                  # 工具函数 (13个文件)
│   ├── data/                   # 数据文件
│   └── main.js                 # 应用入口
│
├── docs/                       # 前端架构文档 (21个文件)
│   ├── 0.路由页面管理方式.md    # 路由架构设计
│   ├── 1.页面布局及UI管理方式.md # 布局组件层级
│   ├── 2.UI组件设置.md          # UI组件详细说明
│   ├── 4.功能实现方法.md        # 组合式函数实现
│   ├── 5.状态管理设计.md        # 21个Pinia状态模块
│   ├── 9.图层管理与数据读取机制分析.md # 数据流转机制
│   ├── 20.事件驱动分析.md       # EDA事件驱动架构
│   └── ...                     # 其他架构文档
├── public/                     # 静态资源
└── package.json                # 依赖配置
```

### 后端结构 (Backend/)

#### EDA事件驱动Agent服务 (Backend/agent/)
```
agent/                          # FastAPI + LangChain + 通义千问
├── app.py                      # FastAPI 应用入口 (919行)
├── models/                     # 数据模型
│   ├── __init__.py
│   └── schemas.py              # Pydantic 模型定义
├── study_ali/                  # 阿里云大模型研究
│   ├── 1多轮对话.py            # 多轮对话示例
│   ├── 2工具调用.py            # 工具调用示例
│   ├── 3联网搜索.PY            # 联网搜索示例
│   ├── 4运行工具函数.PY        # 工具函数运行示例
│   ├── 5结构化输出.PY          # 结构化输出示例
│   ├── integrated_llm_agent.py # 集成LLM Agent
│   ├── 原理.md                 # 原理说明文档
│   └── Langchain/              # LangChain 学习案例
│       ├── 1.第一个LLM/        # 第一个LLM案例
│       │   ├── 1.对话翻译.Ipynb
│       │   ├── 2.工具调用.ipynb
│       │   └── 工具调用完整指南.md
│       └── readme.md
└── 17个工具函数 (在app.py中)   # 长江水域监测专业工具
    ├── toggle_layer_visibility # 图层可见性切换
    ├── query_features_by_attribute # 属性查询
    ├── execute_buffer_analysis # 缓冲区分析
    ├── execute_intersection_analysis # 相交分析
    ├── execute_erase_analysis  # 擦除分析
    ├── execute_shortest_path_analysis # 最短路径分析
    └── 保存/导出工具函数        # 结果保存和导出
```

#### 用户认证服务 (Backend/user/)
```
user/                           # FastAPI + PostgreSQL + DDD
├── api/                        # API 路由层
│   ├── __init__.py
│   ├── dependencies.py         # 依赖注入
│   └── v1/                     # API v1版本
│       ├── __init__.py
│       └── user/               # 用户相关API
│           ├── __init__.py
│           ├── auth.py         # 用户认证接口
│           └── user_dto.py     # 用户DTO定义
├── application/                # 应用层
│   ├── __init__.py
│   ├── dto/                    # 数据传输对象
│   │   ├── __init__.py
│   │   └── user_dto.py         # 用户DTO
│   └── use_cases/              # 用例实现
│       ├── __init__.py
│       └── user/               # 用户用例
│           ├── __init__.py
│           └── auth_use_case.py # 认证用例
├── domains/                    # 领域层
│   ├── __init__.py
│   ├── llm/                    # LLM领域
│   ├── spatial/                # 空间领域
│   └── user/                   # 用户领域模型
│       ├── __init__.py
│       ├── entities.py         # 用户实体
│       ├── repositories.py     # 仓储接口
│       ├── services.py         # 领域服务
│       └── value_objects.py    # 值对象
├── infrastructure/             # 基础设施层
│   ├── __init__.py
│   ├── database/               # 数据库实现
│   │   ├── __init__.py
│   │   ├── postgres/           # PostgreSQL实现
│   │   │   ├── __init__.py
│   │   │   ├── models.py       # SQLAlchemy模型
│   │   │   └── repositories.py # 仓储实现
│   │   └── redis/              # Redis缓存
│   │       ├── __init__.py
│   │       ├── cache_service.py
│   │       └── connection.py
│   ├── external/               # 外部服务
│   └── monitoring/             # 监控模块
│       ├── __init__.py
│       ├── health_check.py     # 健康检查
│       ├── metrics.py          # 指标监控
│       └── tracing.py          # 链路追踪
├── core/                       # 核心模块
│   ├── __init__.py
│   ├── cache.py                # 缓存配置
│   ├── config.py               # 配置管理
│   ├── container.py            # 依赖注入容器
│   ├── database.py             # 数据库连接
│   └── security.py             # 安全认证
├── docs/                       # 文档
│   ├── user-auth-api.md        # API文档
│   └── user-auth-quick-reference.md # 快速参考
├── utils/                      # 工具函数
│   └── test_userapi.py         # API测试
└── main.py                     # FastAPI 应用入口
```

#### 空间分析服务 (Backend/analysis/)
```
analysis/                       # Node.js + Express + DDD
├── src/
│   ├── api/                    # API 层
│   │   ├── controllers/        # 控制器 (4个文件)
│   │   │   ├── BufferAnalysisController.js
│   │   │   ├── EraseAnalysisController.js
│   │   │   ├── IntersectionAnalysisController.js
│   │   │   └── ShortestPathAnalysisController.js
│   │   ├── routes/             # 路由定义 (5个文件)
│   │   │   ├── buffer.js
│   │   │   ├── erase.js
│   │   │   ├── intersection.js
│   │   │   ├── shortestPath.js
│   │   │   └── download.js
│   │   └── geometryConverter.ts # 几何转换器
│   ├── application/            # 应用层
│   │   ├── dtos/               # 数据传输对象 (4个文件)
│   │   │   ├── BufferAnalysisDTO.js
│   │   │   ├── EraseAnalysisDTO.js
│   │   │   ├── IntersectionAnalysisDTO.js
│   │   │   └── ShortestPathAnalysisDTO.js
│   │   └── useCases/           # 用例实现 (4个文件)
│   │       ├── BufferAnalysisUseCase.js
│   │       ├── EraseAnalysisUseCase.js
│   │       ├── IntersectionAnalysisUseCase.js
│   │       └── ShortestPathAnalysisUseCase.js
│   ├── domain/                 # 领域层
│   │   ├── entities/           # 实体
│   │   │   └── Geometry.js
│   │   ├── valueObjects/       # 值对象
│   │   │   └── BufferSettings.js
│   │   └── services/           # 领域服务 (5个文件)
│   │       ├── BufferAnalysisService.js
│   │       ├── EraseAnalysisService.js
│   │       ├── GeometryProcessingService.js
│   │       ├── IntersectionAnalysisService.js
│   │       └── ShortestPathAnalysisService.js
│   ├── infrastructure/         # 基础设施层
│   │   ├── geometryConverter.js # 几何转换实现
│   │   └── repositories/       # 数据仓库
│   │       └── LayerRepository.js
│   ├── middleware/             # 中间件 (4个文件)
│   │   ├── errorHandler.js     # 错误处理
│   │   ├── llmResponseFormatter.js # LLM响应格式化
│   │   ├── requestLogger.js    # 请求日志
│   │   └── validation.js       # 请求验证
│   ├── config/                 # 配置
│   │   ├── dify-openapi-schema.json
│   │   └── swagger.js          # Swagger配置
│   ├── app.js                  # Express 应用入口
│   └── readme.md               # 服务说明文档
├── config/                     # 配置文件
│   └── index.js
├── downloads/                  # 下载文件 (136个JSON文件)
├── node_modules/               # Node.js依赖
├── package.json                # 依赖配置
├── package-lock.json           # 依赖锁定文件
└── README.md                   # 服务文档
```

### 架构设计原则

#### 前端架构
- **事件驱动设计**: 基于CustomEvent的前后端解耦通信机制
- **组件化设计**: 25个UI组件 + 14个地图组件 + 17个图表组件 + 3个Agent组件，高度可复用
- **状态管理**: 21个Pinia状态模块，模块化管理应用状态
- **组合式函数**: 25个composables承载业务逻辑，与组件解耦
- **路由驱动**: 每个功能面板独立路由，支持懒加载
- **主题系统**: CSS变量驱动的主题切换，支持明暗模式

#### 后端架构
- **EDA事件驱动**: Agent服务通过工具调用和事件反馈实现智能交互
- **微服务设计**: EDA Agent服务 + 用户服务 + 分析服务独立部署
- **DDD架构**: 领域驱动设计，清晰的分层结构
- **AI Agent集成**: LangChain + 通义千问，专业领域知识驱动
- **API优先**: RESTful API设计，完整的Swagger文档
- **类型安全**: TypeScript/Python类型检查，减少运行时错误

## 🚀 快速开始

### 环境要求

#### 基础环境
- **Node.js**: >= 20.19.0 或 >= 22.12.0
- **Python**: >= 3.11
- **PostgreSQL**: >= 15
- **Git**: 最新版本

#### 推荐工具
- **IDE**: VS Code + Vue Language Features 扩展
- **数据库工具**: pgAdmin 或 DBeaver
- **API测试**: Postman 或 Insomnia

### 一键启动（推荐）

系统需要同时启动三个服务，建议按以下顺序启动：

#### 1. 启动数据库服务
```bash
# 启动 PostgreSQL 数据库
# Windows (如果使用 PostgreSQL 服务)
net start postgresql-x64-15

# macOS (使用 Homebrew)
brew services start postgresql

# Linux (使用 systemctl)
sudo systemctl start postgresql
```

#### 2. 启动后端服务

**EDA事件驱动Agent服务 (端口: 8089)**
```bash
# 打开第一个 PowerShell 窗口
cd Backend/agent

# 激活 Python 环境 (如使用 conda)
conda activate pyside6

# 启动EDA Agent服务
python -m uvicorn app:app --reload --host 0.0.0.0 --port 8089
```

**用户认证服务 (端口: 8000)**
```bash
# 打开第二个 PowerShell 窗口
cd Backend/user

# 激活 Python 环境 (如使用 conda)
conda activate pyside6

# 启动用户服务
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**空间分析服务 (端口: 3001)**
```bash
# 打开第三个 PowerShell 窗口
cd Backend/analysis

# 安装依赖 (首次运行)
npm install

# 启动分析服务
npm run dev
```

#### 4. 启动前端应用 (端口: 5173)
```bash
# 打开第四个 PowerShell 窗口
cd Frontend

# 安装依赖 (首次运行)
npm install

# 启动前端开发服务器
npm run dev
```

### 服务访问地址

启动成功后，可通过以下地址访问各服务：

| 服务 | 地址 | 说明 |
|------|------|------|
| 🌐 前端应用 | http://localhost:5173 | 主应用界面 |
| 🤖 EDA Agent服务 | http://localhost:8089/docs | FastAPI Swagger 文档 |
| 👤 用户服务 API | http://localhost:8000/docs | FastAPI Swagger 文档 |
| 🗺️ 分析服务 API | http://localhost:3001/docs | 空间分析 API 文档 |
| ❤️ 健康检查 | http://localhost:8089/health | EDA Agent服务健康状态 |
| ❤️ 健康检查 | http://localhost:8000/health | 用户服务健康状态 |
| ❤️ 健康检查 | http://localhost:3001/health | 分析服务健康状态 |

### 环境配置

#### 数据库配置
在系统环境变量或 `.env` 文件中配置数据库连接：

```bash
# PostgreSQL 数据库配置
POSTGRES_USER=postgres
POSTGRES_PASSWORD=001117
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=supermap
```

#### JWT 安全配置
```bash
# JWT 配置
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

#### EDA Agent 配置
```bash
# 阿里云通义千问配置
DASHSCOPE_API_KEY=your-dashscope-api-key
DASHSCOPE_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
DASHSCOPE_MODEL=qwen-plus
DASHSCOPE_TEMPERATURE=0.7
DASHSCOPE_MAX_TOKENS=3000

# CORS 配置
CORS_ORIGINS=http://localhost:5173,http://localhost:3000
```

### 构建与部署

#### 前端构建
```bash
cd Frontend
npm run build
# 构建产物在 dist/ 目录
```

#### 后端部署
```bash
# EDA Agent服务
cd Backend/agent
python -m uvicorn app:app --host 0.0.0.0 --port 8089

# 用户服务
cd Backend/user
python -m uvicorn main:app --host 0.0.0.0 --port 8000

# 分析服务
cd Backend/analysis
npm start
```

## 🔧 开发指南

### API 文档

#### EDA事件驱动Agent服务 API
- **基础URL**: `http://localhost:8089/agent`
- **Swagger 文档**: http://localhost:8089/docs
- **主要接口**:
  - `POST /tool-chat` - LLM工具调用聊天接口
  - `GET /health` - 健康检查
- **17个工具函数**:
  - 图层管理: `toggle_layer_visibility`
  - 属性查询: `query_features_by_attribute`
  - 空间分析: `execute_buffer_analysis`, `execute_intersection_analysis`, `execute_erase_analysis`, `execute_shortest_path_analysis`
  - 结果保存: `save_*_results_as_layer`
  - 结果导出: `export_*_results_as_json`

#### 用户认证服务 API
- **基础URL**: `http://localhost:8000/api/v1/user`
- **Swagger 文档**: http://localhost:8000/docs
- **主要接口**:
  - `POST /register` - 用户注册
  - `POST /login` - 用户登录
  - `GET /profile` - 获取用户资料
  - `POST /update-profile` - 修改用户信息
  - `POST /change-password` - 修改密码
  - `POST /logout` - 用户登出

#### 空间分析服务 API
- **基础URL**: `http://localhost:3001/api/v1/spatial-analysis`
- **Swagger 文档**: http://localhost:3001/docs
- **主要接口**:
  - `POST /buffer` - 缓冲区分析
  - `POST /intersection` - 相交分析
  - `POST /erase` - 擦除分析
  - `POST /shortest-path` - 最短路径分析

### 开发规范

#### 前端开发规范
- **组件命名**: 使用 PascalCase (如: `MapViewer.vue`)
- **文件结构**: 使用 `<script setup lang="ts">` 语法糖
- **状态管理**: 使用 Composition API 风格的 Pinia stores
- **事件驱动**: 使用 CustomEvent 进行组件间通信
- **路由管理**: 支持懒加载和路由守卫
- **样式规范**: 使用 CSS 变量，支持主题切换

#### 后端开发规范
- **EDA Agent**: 使用 LangChain 工具调用和上下文记忆
- **API 设计**: RESTful API，统一响应格式
- **错误处理**: 完整的异常处理机制
- **数据验证**: 请求参数严格验证
- **文档规范**: 完整的 Swagger API 文档

### 核心组件库

#### UI 组件 (25个)
- **按钮类**: PrimaryButton, SecondaryButton, IconButton, ButtonGroup, BaseButton, DownloadButton, UploadButton
- **输入类**: TraditionalInputGroup, LLMInputGroup, DropdownSelect, QueryConditionRow
- **面板类**: PanelContainer, PanelWindow, SplitPanel
- **对话框类**: EditModal, ConfirmDialog, TipWindow, DataUploadModal, LayerNameModal
- **通知类**: NotificationToast, NotificationManager
- **容器类**: AutoScrollContainer, ThemeTransitionOverlay
- **图标类**: Icon
- **图层类**: LayerItem

#### 地图组件 (14个)
- **显示控件**: CoordinateDisplay, ScaleBar, OverviewMap
- **交互工具**: FeaturePopup, LayerAssistant
- **测量工具**: DistanceMeasurePanel, AreaMeasurePanel, DistanceMeasureButton
- **图例组件**: MapLegend, AdminLegend, TrafficLegend, TrafficWaterLegend, WaterLegend, YangtzeLegend

#### 状态管理 (21个 Pinia Stores)
- **核心状态**: mapStore, userStore, themeStore, modalStore, loadingStore
- **分析状态**: analysisStore, bufferAnalysisStore, intersectionAnalysisStore, eraseAnalysisStore, shortestPathAnalysisStore
- **交互状态**: selectionStore, areaSelectionStore, featureQueryStore, popupStore, interactionStore
- **模式状态**: modeStateStore (LLM模式 + 传统模式状态管理)
- **图层状态**: layerDataStore, layerUIStore (图层数据和UI状态管理)
- **监测状态**: monitoringDataStore (水质监测数据状态)
- **页面状态**: pageStateStore (页面状态管理)
- **持久化状态**: persistenceStore (状态持久化管理)

## 📖 文档与资源

### 项目文档

#### 前端文档 (Frontend/docs/)
- **[路由页面管理方式](Frontend/docs/0.路由页面管理方式.md)**: 详细的路由架构设计
- **[页面布局及UI管理方式](Frontend/docs/1.页面布局及UI管理方式.md)**: 布局组件层级结构
- **[UI组件设置](Frontend/docs/2.UI组件设置.md)**: 19个UI组件详细说明
- **[功能实现方法](Frontend/docs/4.功能实现方法.md)**: 12个组合式函数实现
- **[状态管理设计](Frontend/docs/5.状态管理设计.md)**: 17个Pinia状态模块设计
- **[图层管理与数据读取机制分析](Frontend/docs/9.图层管理与数据读取机制分析.md)**: 数据流转机制
- **[事件驱动分析](Frontend/docs/20.事件驱动分析.md)**: EDA事件驱动架构详解

#### 后端文档 (Backend/)
- **[EDA事件驱动Agent服务](Backend/agent/app.py)**: 17个工具函数的Agent服务
- **[用户认证API文档](Backend/user/docs/user-auth-api.md)**: 完整的用户服务API说明
- **[用户认证快速参考](Backend/user/docs/user-auth-quick-reference.md)**: API快速查询手册
- **[空间分析服务文档](Backend/analysis/README.md)**: DDD架构分析服务说明

#### 联调文档 (docs/)
- **[缓冲区分析前后端联调](docs/缓冲区分析前后端联调.md)**: 缓冲区分析完整流程
- **[相交分析前后端联调](docs/相交分析前后端联调.md)**: 相交分析实现细节
- **[擦除分析前后端联调](docs/擦除分析前后端联调.md)**: 擦除分析接口说明
- **[最短路径分析前后端联调](docs/最短路径分析前后端联调.md)**: 路径规划算法实现

### API 文档访问

| 服务 | Swagger 文档 | 说明 |
|------|-------------|------|
| EDA事件驱动Agent服务 | http://localhost:8089/docs | FastAPI + LangChain 文档 |
| 用户认证服务 | http://localhost:8000/docs | FastAPI 自动生成文档 |
| 空间分析服务 | http://localhost:3001/docs | Express + Swagger 文档 |
| 健康检查 | http://localhost:8089/health | EDA Agent服务健康状态 |
| 健康检查 | http://localhost:8000/health | 用户服务健康状态 |
| 健康检查 | http://localhost:3001/health | 分析服务健康状态 |

### 技术资源

#### 前端技术
- [Vue 3 文档](https://vuejs.org/) - Vue 3 官方文档
- [TypeScript 文档](https://www.typescriptlang.org/) - TypeScript 官方文档
- [Pinia 文档](https://pinia.vuejs.org/) - 状态管理库文档
- [Openlayers 文档](https://openlayers.org/) - 地图库文档
- [Ant Design Vue 文档](https://antdv.com/) - UI组件库文档

#### 后端技术
- [FastAPI 文档](https://fastapi.tiangolo.com/) - Python Web框架文档
- [LangChain 文档](https://python.langchain.com/) - AI Agent 框架文档
- [通义千问 文档](https://help.aliyun.com/zh/dashscope/) - 阿里云大语言模型文档
- [Node.js 文档](https://nodejs.org/) - Node.js 官方文档
- [Express 文档](https://expressjs.com/) - Express 框架文档
- [PostgreSQL 文档](https://www.postgresql.org/) - 数据库文档

#### 空间分析技术
- [SuperMap 文档](https://www.supermap.com/) - SuperMap 产品文档
- [Turf.js 文档](https://turfjs.org/) - JavaScript 空间分析库
- [GeoJSON 规范](https://geojson.org/) - GeoJSON 数据格式规范



## 🔧 故障排除

### 常见问题

#### 前端问题

1. **地图无法加载**
   - 检查 SuperMap 服务器连接状态
   - 确认网络连接正常
   - 查看浏览器控制台错误信息
   - 检查 Openlayers 版本兼容性

2. **分析功能异常**
   - 确认已选择正确的图层
   - 检查输入参数是否有效
   - 查看后端分析服务状态
   - 检查 Turf.js 版本兼容性

3. **主题切换问题**
   - 清除浏览器缓存
   - 检查 CSS 变量定义
   - 确认主题文件加载正常

4. **状态管理问题**
   - 检查 Pinia store 初始化
   - 确认状态持久化配置
   - 查看 localStorage 存储情况

#### 后端问题

1. **用户服务启动失败**
   - 检查 PostgreSQL 数据库连接
   - 确认数据库配置正确
   - 检查 Python 环境和依赖
   - 查看端口 8000 是否被占用

2. **分析服务启动失败**
   - 检查 Node.js 版本 (需要 18.0+)
   - 确认 npm 依赖安装完整
   - 查看端口 3001 是否被占用
   - 检查 DDD 架构模块加载

3. **API 请求失败**
   - 检查 CORS 配置
   - 确认请求格式正确
   - 查看 Swagger 文档
   - 检查认证令牌有效性

4. **数据库连接问题**
   - 确认 PostgreSQL 服务运行
   - 检查数据库连接参数
   - 验证用户权限
   - 查看数据库日志

### 调试模式

#### 前端调试
```bash
# 启用详细日志
npm run dev

# 查看网络请求
# 打开浏览器开发者工具 -> Network 标签

# Vue DevTools 调试
# 安装 Vue DevTools 浏览器扩展
```

#### 后端调试
```bash
# 用户服务调试模式
cd Backend/user
python -m uvicorn main:app --reload --log-level debug

# 分析服务调试模式
cd Backend/analysis
npm run dev
```

### 性能优化

#### 前端性能
- 使用 Vue 3 的 Composition API 减少重渲染
- 图层懒加载和按需渲染
- 大数据集使用虚拟滚动
- 地图要素聚类显示

#### 后端性能
- 数据库查询优化和索引
- API 响应缓存
- 空间分析算法优化
- 请求限流和防抖

### 日志查看

#### 应用日志位置
- **前端日志**: 浏览器开发者工具 Console
- **用户服务日志**: 终端输出和应用日志
- **分析服务日志**: Winston 日志文件
- **数据库日志**: PostgreSQL 日志文件

## 🧪 测试

### API 测试

#### 用户服务测试
```bash
# 健康检查
curl http://localhost:8000/health

# 用户注册测试
curl -X POST "http://localhost:8000/api/v1/user/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "phone": "13800138000",
    "password": "password123",
    "confirm_password": "password123"
  }'

# 用户登录测试
curl -X POST "http://localhost:8000/api/v1/user/login" \
  -H "Content-Type: application/json" \
  -d '{
    "login_identifier": "testuser",
    "password": "password123"
  }'
```

#### 空间分析服务测试
```bash
# 健康检查
curl http://localhost:3001/health

# 缓冲区分析测试
curl -X POST "http://localhost:3001/api/v1/spatial-analysis/buffer" \
  -H "Content-Type: application/json" \
  -d '{
    "sourcelayerId": "wuhan_schools",
    "bufferSettings": {
      "radius": 100,
      "semicircleLineSegment": 10
    }
  }'
```

### 前端测试

#### 路由测试
```bash
cd Frontend
npm run test:routing
```

#### 构建测试
```bash
cd Frontend
npm run test:build
```

#### 完整测试
```bash
cd Frontend
npm run test:all
```

## 🚀 部署

### 开发环境部署

按照[快速开始](#快速开始)部分的说明进行开发环境部署。

### 生产环境部署

#### 前端部署
```bash
cd Frontend
npm run build
# 构建产物在 dist/ 目录，部署到 Web 服务器
```

#### 后端部署

**用户服务部署**
```bash
cd Backend/user
# 生产环境启动
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

**空间分析服务部署**
```bash
cd Backend/analysis
# 生产环境启动
NODE_ENV=production npm start
```

### Docker 部署 (可选)

#### 前端 Docker 部署
```bash
cd Frontend
# 构建 Docker 镜像
docker build -t supermap-frontend .

# 运行容器
docker run -p 80:80 supermap-frontend
```

#### 后端 Docker 部署
```bash
# 用户服务 Docker 部署
cd Backend/user
docker build -t supermap-user-service .
docker run -p 8000:8000 supermap-user-service

# 分析服务 Docker 部署  
cd Backend/analysis
docker build -t supermap-analysis-service .
docker run -p 3001:3001 supermap-analysis-service
```

### 环境配置

#### 前端环境变量
- **开发环境**: `.env.development`
- **生产环境**: `.env.production`

```bash
# 前端环境配置
VITE_API_BASE_URL=http://localhost:8000
VITE_ANALYSIS_API_BASE_URL=http://localhost:3001
VITE_SUPERMAP_SERVER_URL=http://your-supermap-server
VITE_APP_TITLE=SuperMap 智能地理信息分析系统
```

#### 后端环境变量
```bash
# 用户服务环境配置
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your-password
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=supermap
SECRET_KEY=your-secret-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# 分析服务环境配置
NODE_ENV=production
PORT=3001
API_VERSION=v1
RATE_LIMIT_WINDOW_MS=60000
RATE_LIMIT_MAX_REQUESTS=100
```

## 📚 使用指南

### 快速上手

1. **启动应用**: 访问 `http://localhost:5173`
2. **选择模式**: 在顶部导航栏选择 LLM 模式或传统 GIS 模式
3. **地图操作**: 使用鼠标进行缩放、平移等基础操作
4. **图层管理**: 在传统模式下使用图层管理面板控制图层显示

### EDA事件驱动LLM智能模式

- 在聊天界面输入自然语言指令，支持长江水域监测专业术语
- 支持的地图操作：图层管理、属性查询、空间分析、结果导出
- 17个工具函数支持完整的地理空间分析工作流
- 示例指令：
  - "显示@学校图层"
  - "在@人口图层中查找人口>100万"
  - "对@污染源图层进行缓冲区分析，半径500米"
  - "保存缓冲区分析结果为图层"
  - "导出相交分析结果为JSON"

### 传统 GIS 模式

- **图层管理**: 控制图层的显示/隐藏、顺序调整
- **要素查询**: 按属性条件查询要素
- **空间分析**: 执行缓冲区分析、最短路径分析
- **编辑工具**: 创建、修改、删除地图要素

## 🔧 故障排除

### 常见问题

1. **地图无法加载**
   - 检查 SuperMap 服务器连接
   - 确认网络连接正常
   - 查看浏览器控制台错误信息

2. **分析功能异常**
   - 确认已选择正确的图层
   - 检查输入参数是否有效
   - 查看后端服务状态

3. **主题切换问题**
   - 清除浏览器缓存
   - 检查 CSS 变量定义

### 调试模式

```bash
# 启用详细日志
npm run dev -- --debug

# 查看网络请求
# 打开浏览器开发者工具 -> Network 标签
```


## 🤝 贡献指南

我们欢迎所有形式的贡献！

### 贡献流程

1. **Fork** 本仓库到你的 GitHub 账号
2. **Clone** 你的 fork 到本地开发环境
3. **创建** 特性分支 (`git checkout -b feature/AmazingFeature`)
4. **开发** 并测试你的功能
5. **提交** 你的修改 (`git commit -m 'Add some AmazingFeature'`)
6. **推送** 到分支 (`git push origin feature/AmazingFeature`)
7. **打开** Pull Request

### 贡献规范

#### 代码规范
- 遵循项目的代码风格和命名规范
- 添加必要的注释和文档
- 确保代码通过所有测试
- 提交前运行 ESLint 和 TypeScript 检查

#### 提交规范
- 使用清晰的提交信息描述变更
- 遵循 [Conventional Commits](https://conventionalcommits.org/) 规范
- 示例：`feat: add buffer analysis API`, `fix: resolve map rendering issue`

#### 文档规范
- 更新相关的 API 文档
- 添加新功能的使用说明
- 保持 README 和其他文档的同步

### 问题反馈

如果你发现 bug 或有功能建议：

1. 查看 [Issues](../../issues) 是否已有相关问题
2. 如果没有，请创建新的 Issue
3. 详细描述问题或建议
4. 提供复现步骤（如果是 bug）

### 开发环境设置

1. 确保满足[环境要求](#环境要求)
2. 按照[快速开始](#快速开始)设置开发环境
3. 运行测试确保环境正常
4. 开始你的贡献！

## 📜 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 🙏 致谢

感谢以下开源项目和技术的支持：

### 前端技术
- [Vue.js](https://vuejs.org/) - 渐进式 JavaScript 框架
- [TypeScript](https://www.typescriptlang.org/) - JavaScript 的超集
- [Vite](https://vitejs.dev/) - 下一代前端构建工具
- [Openlayers](https://openlayers.org/) - 开源地图库
- [Pinia](https://pinia.vuejs.org/) - Vue 状态管理库
- [Ant Design Vue](https://antdv.com/) - 企业级 UI 组件库

### 后端技术
- [FastAPI](https://fastapi.tiangolo.com/) - 现代高性能 Python Web 框架
- [LangChain](https://python.langchain.com/) - AI Agent 框架和工具调用
- [通义千问](https://help.aliyun.com/zh/dashscope/) - 阿里云大语言模型
- [Node.js](https://nodejs.org/) - JavaScript 运行时环境
- [Express](https://expressjs.com/) - Node.js Web 应用框架
- [PostgreSQL](https://www.postgresql.org/) - 开源关系型数据库

### 地理信息技术
- [SuperMap](https://www.supermap.com/) - 企业级 GIS 平台
- [Turf.js](https://turfjs.org/) - JavaScript 空间分析库
- [GeoJSON](https://geojson.org/) - 地理数据交换格式

### 开发工具
- [Git](https://git-scm.com/) - 版本控制系统
- [VS Code](https://code.visualstudio.com/) - 代码编辑器
- [Swagger](https://swagger.io/) - API 文档工具

---

## 📞 联系方式

- **项目地址**: [GitHub Repository](https://github.com/your-repo/supermap-gis)
- **问题反馈**: [GitHub Issues](https://github.com/your-repo/supermap-gis/issues)
- **文档**: 查看项目 `docs/` 目录获取详细文档

---

*本项目持续维护和更新中，欢迎关注和贡献！*

**最后更新**: 2024年1月
