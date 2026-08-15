# 🗺️ 基于EDA-Agent的武汉市长江流域地理空间实时势态感知的智能决策分析监测预警一体化平台
> 基于微服务架构的现代化 WebGIS 全栈应用，集成 EDA 事件驱动 AI Agent 与传统 GIS 分析功能
*所有开发工作仅由本人自主研发设计，若引用项目理念及相关内容请发送邮箱至qianxi_x@163.com*


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

基于EDA-Agent的武汉市长江流域地理空间实时势态感知的智能决策分析监测预警一体化平台（Agent-GISAM）是一个基于微服务架构的现代化 WebGIS 全栈应用，采用前后端分离设计，集成了传统 GIS 分析功能与 AI 智能助手。系统提供完整的用户管理、空间分析和智能交互功能。

### 系统架构

```
┌─────────────────────────────────────────────────────────────────┐
│                        前端应用层                                │
│  Vue 3 + TypeScript + Openlayers + Pinia + Ant Design Vue     │
│  ├── 事件驱动架构 (CustomEvent)                                │
│  ├── 22个Pinia状态管理模块                                     │
│  ├── 25个UI组件 + 14个地图组件 + 17个图表组件 + 2个Agent组件     │
│  └── 24个组合式函数 (Composables)                              │
└─────────────────┬───────────────────────────────────────────────┘
                  │ HTTP/REST API + 事件驱动通信
┌─────────────────┴───────────────────────────────────────────────┐
│                       后端服务层                                │
├─────────────────────────────────────────────────────────────────┤
│  EDA事件驱动Agent服务 (FastAPI + LangChain)                    │
│  - 长江水域监测专业背景知识 (13个专业文档，涵盖武汉概况、长江流域、水质监测等) │
│  - 18个工具函数 (知识库查询+图层管理+空间分析+结果导出)         │
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
- **智能AI助手**: 长江水域监测专业背景的AI Agent，支持18个工具函数
- **事件驱动通信**: 前端事件监听器 + 后端工具调用 + 结果反馈机制
- **用户管理系统**: 完整的用户认证、授权和资料管理
- **响应式界面**: 现代化 UI 设计，支持主题切换
- **状态持久化**: 22个Pinia状态模块的完整应用状态管理

## ✨ 功能特性

### 🔐 用户管理系统
- **用户认证**: 注册、登录、JWT 令牌管理
- **资料管理**: 用户信息修改、密码变更
- **权限控制**: 基于角色的访问控制
- **会话管理**: 安全的用户会话和登出

### 🧠 EDA事件驱动LLM智能模式
- **自然语言交互**: 通过聊天界面操作地图，支持长江水域监测专业术语
- **18个工具函数**: 知识库查询、图层管理、空间分析、结果导出的完整工具链
- **事件驱动通信**: 前端CustomEvent监听 + 后端LangChain工具调用
- **上下文记忆**: 会话历史管理和操作上下文自动识别
- **专业背景知识**: 长江水系特征、水质监测标准、监测点布局等专业知识，包含13个专业文档的知识库
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
- **状态管理**: 22个Pinia状态模块的完整应用状态持久化
- **模块化组件**: 25个UI组件 + 14个地图组件 + 17个图表组件 + 2个Agent组件
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
- **18个工具函数**: 知识库查询、图层管理、空间分析、结果导出

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
│   ├── src/                    # 源代码目录
│   │   ├── api/                # API接口层 (6个文件)
│   │   ├── components/         # 组件库 (58个组件)
│   │   │   ├── Agent/          # AI Agent组件 (2个文件)
│   │   │   │   ├── ChatMessagesPanel.vue    # 聊天消息面板
│   │   │   │   └── LLMInputWindow.vue       # LLM输入窗口
│   │   │   ├── Charts/         # 图表组件 (17个文件)
│   │   │   │   ├── AgeDistributionChart.vue      # 年龄分布图表
│   │   │   │   ├── EducationLevelChart.vue       # 教育水平图表
│   │   │   │   ├── GenderRatioChart.vue          # 性别比例图表
│   │   │   │   ├── HospitalDistributionChart.vue # 医院分布图表
│   │   │   │   ├── LivelihoodSummaryChart.vue    # 民生资源汇总图表
│   │   │   │   ├── RailwayTypeChart.vue          # 铁路类型图表
│   │   │   │   ├── RegionAreaChart.vue           # 区域面积图表
│   │   │   │   ├── RegionPopulationChart.vue     # 区域人口图表
│   │   │   │   ├── ResidentDistributionChart.vue # 居民分布图表
│   │   │   │   ├── RoadLevelChart.vue            # 道路等级图表
│   │   │   │   ├── SchoolDistributionChart.vue   # 学校分布图表
│   │   │   │   ├── WaterLineChart.vue            # 水系线图表
│   │   │   │   ├── WaterQualityChart1.vue        # 水质图表1
│   │   │   │   ├── WaterQualityChart2.vue        # 水质图表2
│   │   │   │   ├── WaterQualityChart3.vue        # 水质图表3
│   │   │   │   ├── WaterQualityChart4.vue        # 水质图表4
│   │   │   │   └── WaterSurfaceChart.vue         # 水面图表
│   │   │   ├── Map/            # 地图组件 (14个文件)
│   │   │   │   ├── AdminLegend.vue               # 行政区图例
│   │   │   │   ├── AreaMeasurePanel.vue          # 面积测量面板
│   │   │   │   ├── CoordinateDisplay.vue         # 坐标显示
│   │   │   │   ├── DistanceMeasureButton.vue     # 距离测量按钮
│   │   │   │   ├── DistanceMeasurePanel.vue      # 距离测量面板
│   │   │   │   ├── FeaturePopup.vue              # 要素弹窗
│   │   │   │   ├── LayerAssistant.vue            # 图层助手
│   │   │   │   ├── MapLegend.vue                 # 地图图例
│   │   │   │   ├── OverviewMap.vue               # 鹰眼地图
│   │   │   │   ├── ScaleBar.vue                  # 比例尺
│   │   │   │   ├── TrafficLegend.vue             # 交通图例
│   │   │   │   ├── TrafficWaterLegend.vue        # 交通水系图例
│   │   │   │   ├── WaterLegend.vue               # 水系图例
│   │   │   │   └── YangtzeLegend.vue             # 长江图例
│   │   │   └── UI/              # UI组件 (25个文件)
│   │   │       ├── AutoScrollContainer.vue       # 自动滚动容器
│   │   │       ├── BaseButton.vue                # 基础按钮
│   │   │       ├── ButtonGroup.vue               # 按钮组
│   │   │       ├── ConfirmDialog.vue             # 确认对话框
│   │   │       ├── DataUploadModal.vue           # 数据上传模态框
│   │   │       ├── DownloadButton.vue            # 下载按钮
│   │   │       ├── DropdownSelect.vue            # 下拉选择器
│   │   │       ├── EditModal.vue                 # 编辑模态框
│   │   │       ├── Icon.vue                      # 图标组件
│   │   │       ├── IconButton.vue                # 图标按钮
│   │   │       ├── LayerItem.vue                 # 图层项
│   │   │       ├── LayerNameModal.vue            # 图层名称模态框
│   │   │       ├── LLMInputGroup.vue             # LLM输入组
│   │   │       ├── NotificationManager.vue       # 通知管理器
│   │   │       ├── NotificationToast.vue         # 通知提示
│   │   │       ├── PanelContainer.vue            # 面板容器
│   │   │       ├── PanelWindow.vue               # 面板窗口
│   │   │       ├── PrimaryButton.vue             # 主要按钮
│   │   │       ├── QueryConditionRow.vue         # 查询条件行
│   │   │       ├── SecondaryButton.vue           # 次要按钮
│   │   │       ├── SplitPanel.vue                # 分割面板
│   │   │       ├── ThemeTransitionOverlay.vue    # 主题过渡覆盖层
│   │   │       ├── TipWindow.vue                 # 提示窗口
│   │   │       ├── TraditionalInputGroup.vue     # 传统输入组
│   │   │       └── UploadButton.vue              # 上传按钮
│   │   ├── composables/        # 组合式函数 (24个文件)
│   │   │   ├── useBufferAnalysis.ts              # 缓冲区分析
│   │   │   ├── useBuildingExtrusion.ts           # 建筑拉伸
│   │   │   ├── useDataUpload.ts                  # 数据上传
│   │   │   ├── useEraseAnalysis.ts               # 擦除分析
│   │   │   ├── useFeatureQuery.ts                # 要素查询
│   │   │   ├── useFeatureSelection.ts            # 要素选择
│   │   │   ├── useIntersectionAnalysis.ts        # 相交分析
│   │   │   ├── useLayerExport.ts                 # 图层导出
│   │   │   ├── useLayerManager.ts                # 图层管理 (事件驱动)
│   │   │   ├── useLayerMentions.ts               # 图层提及
│   │   │   ├── useLogin.ts                       # 登录逻辑
│   │   │   ├── useMap.ts                         # 地图核心逻辑
│   │   │   ├── useMapData.ts                     # 地图数据
│   │   │   ├── useMapInteraction.ts              # 地图交互
│   │   │   ├── useMapLifecycle.ts                # 地图生命周期
│   │   │   ├── useMapStyles.ts                   # 地图样式
│   │   │   ├── useMonitoringDataLayers.ts        # 监测数据图层
│   │   │   ├── useMonitoringThreshold.ts         # 监测阈值管理
│   │   │   ├── useRealTimeWaterQuality.ts        # 实时水质监测
│   │   │   ├── useRegister.ts                    # 注册逻辑
│   │   │   ├── useShortestPathAnalysis.ts        # 最短路径分析
│   │   │   ├── useThemeOptimization.ts           # 主题优化
│   │   │   ├── useUserProfile.ts                 # 用户资料
│   │   │   └── useYangtzeWaterLayers.ts          # 长江水图层
│   │   ├── stores/             # 状态管理 (22个 Pinia stores)
│   │   │   ├── analysisStore.ts                  # 分析工具状态
│   │   │   ├── areaSelectionStore.ts             # 区域选择状态
│   │   │   ├── bufferAnalysisStore.ts            # 缓冲区分析状态
│   │   │   ├── eraseAnalysisStore.ts             # 擦除分析状态
│   │   │   ├── featureQueryStore.ts              # 要素查询状态
│   │   │   ├── interactionStore.ts               # 交互状态
│   │   │   ├── intersectionAnalysisStore.ts      # 相交分析状态
│   │   │   ├── layerDataStore.ts                 # 图层数据状态
│   │   │   ├── layerUIStore.ts                   # 图层UI状态
│   │   │   ├── loadingStore.ts                   # 加载状态
│   │   │   ├── mapStore.ts                       # 地图状态
│   │   │   ├── modalStore.ts                     # 模态框状态
│   │   │   ├── modeStateStore.ts                 # 模式切换状态
│   │   │   ├── monitoringDataStore.ts            # 监测数据状态
│   │   │   ├── monitoringPlatformStore.ts        # 监测平台状态
│   │   │   ├── pageStateStore.ts                 # 页面状态
│   │   │   ├── persistenceStore.ts               # 持久化状态
│   │   │   ├── popupStore.ts                     # 弹窗状态
│   │   │   ├── selectionStore.ts                 # 选择状态
│   │   │   ├── shortestPathAnalysisStore.ts      # 最短路径分析状态
│   │   │   ├── themeStore.ts                     # 主题状态
│   │   │   └── userStore.ts                      # 用户状态
│   │   ├── views/              # 页面组件 (路由驱动)
│   │   │   ├── auth/            # 认证页面 (2个文件)
│   │   │   │   ├── Login.vue                     # 登录页面
│   │   │   │   └── Register.vue                  # 注册页面
│   │   │   ├── dashboard/       # 主工作台
│   │   │   │   ├── management-analysis/          # 管理分析模块
│   │   │   │   │   ├── layout/                   # 布局组件 (2个文件)
│   │   │   │   │   │   ├── DashboardManageHeader.vue    # 管理头部
│   │   │   │   │   │   └── DashboardManageLayout.vue    # 管理布局
│   │   │   │   │   ├── LLM/                      # EDA事件驱动LLM模式 (3个文件)
│   │   │   │   │   │   ├── LLMMode.vue           # LLM模式主页面
│   │   │   │   │   │   ├── ChatAssistant.vue     # 聊天助手 (事件监听器)
│   │   │   │   │   │   └── ChatHistory.vue       # 聊天历史
│   │   │   │   │   ├── traditional/              # 传统 GIS 模式 (9个文件)
│   │   │   │   │   │   ├── TraditionalMode.vue   # 传统模式主页面
│   │   │   │   │   │   ├── LayerManager.vue      # 图层管理器
│   │   │   │   │   │   ├── FeatureQueryPanel.vue # 要素查询面板
│   │   │   │   │   │   ├── AreaSelectionTools.vue # 区域选择工具
│   │   │   │   │   │   ├── BufferAnalysisPanel.vue # 缓冲区分析面板
│   │   │   │   │   │   ├── IntersectionAnalysisPanel.vue # 相交分析面板
│   │   │   │   │   │   ├── EraseAnalysisPanel.vue # 擦除分析面板
│   │   │   │   │   │   ├── ShortestPathAnalysisPanel.vue # 最短路径分析面板
│   │   │   │   │   │   └── DataUploadPanel.vue   # 数据上传面板
│   │   │   │   │   ├── management/               # 系统管理 (1个文件)
│   │   │   │   │   │   └── AIManagement.vue      # AI管理
│   │   │   │   │   ├── profile/                  # 用户管理 (1个文件)
│   │   │   │   │   │   └── UserProfile.vue       # 用户资料
│   │   │   │   │   ├── ManagementAnalysis.vue    # 管理分析主页面
│   │   │   │   │   ├── RightPanel.vue            # 右侧面板
│   │   │   │   │   └── SuperMapViewer.vue        # SuperMap查看器
│   │   │   │   └── ViewPage/                     # 视图页面
│   │   │   │       ├── layout/                   # 视图布局 (1个文件)
│   │   │   │       │   └── DashboardViewHeader.vue # 视图头部
│   │   │   │       ├── data/                     # 数据文件 (4个文件)
│   │   │   │       ├── monitordata/              # 监测数据 (6个GeoJSON文件)
│   │   │   │       ├── processed_data/           # 处理数据 (8个文件)
│   │   │   │       ├── ViewHome.vue              # 视图首页
│   │   │   │       ├── ViewLayerManager.vue      # 视图图层管理
│   │   │   │       ├── ViewSubPage1.vue          # 视图子页面1
│   │   │   │       ├── ViewSubPage2.vue          # 视图子页面2
│   │   │   │       ├── ViewSubPage3.vue          # 视图子页面3
│   │   │   │       ├── 水文监测点_GeoJSON.json   # 水文监测点数据
│   │   │   │       ├── 长江线.geojson            # 长江线数据
│   │   │   │       └── 长江面.geojson            # 长江面数据
│   │   │   └── Dashboard.vue                     # 主仪表板
│   │   ├── types/              # TypeScript 类型定义 (7个文件)
│   │   │   ├── geojson.d.ts                     # GeoJSON类型定义
│   │   │   ├── jsx-global.d.ts                  # JSX全局类型
│   │   │   ├── map.ts                           # 地图相关类型
│   │   │   ├── query.ts                         # 查询相关类型
│   │   │   ├── splitpanes.d.ts                  # 分割面板类型
│   │   │   ├── supermap.d.ts                    # SuperMap类型定义
│   │   │   └── vue-shims.d.ts                   # Vue类型声明
│   │   ├── utils/              # 工具函数 (12个文件)
│   │   │   ├── __tests__/                       # 测试文件目录
│   │   │   ├── config.ts                        # 配置工具
│   │   │   ├── domainBackground.ts              # 领域背景
│   │   │   ├── eventUtils.ts                    # 事件工具
│   │   │   ├── featureUtils.ts                  # 要素工具
│   │   │   ├── geometryConverter.ts             # 几何转换
│   │   │   ├── layerUtils.ts                    # 图层工具
│   │   │   ├── layerValidation.ts               # 图层验证
│   │   │   ├── legendColorUtils.ts              # 图例颜色工具
│   │   │   ├── llmNotification.ts               # LLM通知
│   │   │   ├── notification.ts                  # 通知工具
│   │   │   ├── styleUtils.ts                    # 样式工具
│   │   │   └── themeUtils.ts                    # 主题工具
│   │   ├── styles/            # 全局样式
│   │   ├── router/            # 路由配置
│   │   └── data/              # 数据文件
│   ├── docs/                  # 前端架构文档 (21个文件)
│   ├── public/                # 静态资源
│   └── dist/                  # 构建产物
├── Backend/                    # 后端服务
│   ├── agent/                  # EDA事件驱动Agent服务 (FastAPI + LangChain)
│   ├── user/                   # 用户认证服务 (FastAPI + PostgreSQL + DDD)
│   ├── analysis/               # 空间分析服务 (Node.js + Express + DDD)
│   ├── rag/                    # RAG知识库系统
│   └── vector_db/              # 向量数据库存储
├── docs/                       # 项目文档
└── README.md                   # 项目说明文档
```

### 前端结构 (Frontend/)

```
Frontend/
├── src/
│   ├── api/                    # API 接口层 (6个文件)
│   │   ├── config.ts           # Axios 配置和拦截器
│   │   ├── state.ts            # 状态管理API
│   │   ├── supermap.ts         # SuperMap iServer 接口
│   │   ├── hydrologyData.ts    # 水文数据接口
│   │   ├── waterQualityData.ts # 水质数据接口
│   │   └── yangtzeData.ts      # 长江数据接口
│   │
│   ├── components/             # 组件库 (4个分类，共58个文件)
│   │   ├── Agent/              # AI Agent组件 (2个文件)
│   │   │   ├── ChatMessagesPanel.vue    # 聊天消息面板
│   │   │   └── LLMInputWindow.vue       # LLM输入窗口
│   │   ├── Charts/             # 图表组件 (17个文件)
│   │   │   ├── AgeDistributionChart.vue      # 年龄分布图表
│   │   │   ├── EducationLevelChart.vue       # 教育水平图表
│   │   │   ├── GenderRatioChart.vue          # 性别比例图表
│   │   │   ├── HospitalDistributionChart.vue # 医院分布图表
│   │   │   ├── LivelihoodSummaryChart.vue    # 民生资源汇总图表
│   │   │   ├── RailwayTypeChart.vue          # 铁路类型图表
│   │   │   ├── RegionAreaChart.vue           # 区域面积图表
│   │   │   ├── RegionPopulationChart.vue     # 区域人口图表
│   │   │   ├── ResidentDistributionChart.vue # 居民分布图表
│   │   │   ├── RoadLevelChart.vue            # 道路等级图表
│   │   │   ├── SchoolDistributionChart.vue   # 学校分布图表
│   │   │   ├── WaterLineChart.vue            # 水系线图表
│   │   │   ├── WaterQualityChart1.vue        # 水质图表1
│   │   │   ├── WaterQualityChart2.vue        # 水质图表2
│   │   │   ├── WaterQualityChart3.vue        # 水质图表3
│   │   │   ├── WaterQualityChart4.vue        # 水质图表4
│   │   │   └── WaterSurfaceChart.vue         # 水面图表
│   │   ├── Map/                # 地图组件 (14个文件)
│   │   │   ├── AdminLegend.vue               # 行政区图例
│   │   │   ├── AreaMeasurePanel.vue          # 面积测量面板
│   │   │   ├── CoordinateDisplay.vue         # 坐标显示
│   │   │   ├── DistanceMeasureButton.vue     # 距离测量按钮
│   │   │   ├── DistanceMeasurePanel.vue      # 距离测量面板
│   │   │   ├── FeaturePopup.vue              # 要素弹窗
│   │   │   ├── LayerAssistant.vue            # 图层助手
│   │   │   ├── MapLegend.vue                 # 地图图例
│   │   │   ├── OverviewMap.vue               # 鹰眼地图
│   │   │   ├── ScaleBar.vue                  # 比例尺
│   │   │   ├── TrafficLegend.vue             # 交通图例
│   │   │   ├── TrafficWaterLegend.vue        # 交通水系图例
│   │   │   ├── WaterLegend.vue               # 水系图例
│   │   │   └── YangtzeLegend.vue             # 长江图例
│   │   └── UI/                 # UI组件 (25个文件)
│   │       ├── AutoScrollContainer.vue       # 自动滚动容器
│   │       ├── BaseButton.vue                # 基础按钮
│   │       ├── ButtonGroup.vue               # 按钮组
│   │       ├── ConfirmDialog.vue             # 确认对话框
│   │       ├── DataUploadModal.vue           # 数据上传模态框
│   │       ├── DownloadButton.vue            # 下载按钮
│   │       ├── DropdownSelect.vue            # 下拉选择器
│   │       ├── EditModal.vue                 # 编辑模态框
│   │       ├── Icon.vue                      # 图标组件
│   │       ├── IconButton.vue                # 图标按钮
│   │       ├── LayerItem.vue                 # 图层项
│   │       ├── LayerNameModal.vue            # 图层名称模态框
│   │       ├── LLMInputGroup.vue             # LLM输入组
│   │       ├── NotificationManager.vue       # 通知管理器
│   │       ├── NotificationToast.vue         # 通知提示
│   │       ├── PanelContainer.vue            # 面板容器
│   │       ├── PanelWindow.vue               # 面板窗口
│   │       ├── PrimaryButton.vue             # 主要按钮
│   │       ├── QueryConditionRow.vue         # 查询条件行
│   │       ├── SecondaryButton.vue           # 次要按钮
│   │       ├── SplitPanel.vue                # 分割面板
│   │       ├── ThemeTransitionOverlay.vue    # 主题过渡覆盖层
│   │       ├── TipWindow.vue                 # 提示窗口
│   │       ├── TraditionalInputGroup.vue     # 传统输入组
│   │       └── UploadButton.vue              # 上传按钮
│   │
│   ├── composables/            # 组合式函数 (24个文件)
│   │   ├── useBufferAnalysis.ts # 缓冲区分析
│   │   ├── useBuildingExtrusion.ts # 建筑拉伸
│   │   ├── useDataUpload.ts    # 数据上传
│   │   ├── useEraseAnalysis.ts # 擦除分析
│   │   ├── useFeatureQuery.ts  # 要素查询
│   │   ├── useFeatureSelection.ts # 要素选择
│   │   ├── useIntersectionAnalysis.ts # 相交分析
│   │   ├── useLayerExport.ts   # 图层导出
│   │   ├── useLayerManager.ts  # 图层管理 (事件驱动)
│   │   ├── useLayerMentions.ts # 图层提及
│   │   ├── useLogin.ts         # 登录逻辑
│   │   ├── useMap.ts           # 地图核心逻辑
│   │   ├── useMapData.ts       # 地图数据
│   │   ├── useMapInteraction.ts # 地图交互
│   │   ├── useMapLifecycle.ts  # 地图生命周期
│   │   ├── useMapStyles.ts     # 地图样式
│   │   ├── useMonitoringDataLayers.ts # 监测数据图层
│   │   ├── useMonitoringThreshold.ts # 监测阈值管理
│   │   ├── useRealTimeWaterQuality.ts # 实时水质监测
│   │   ├── useRegister.ts      # 注册逻辑
│   │   ├── useShortestPathAnalysis.ts # 最短路径分析
│   │   ├── useThemeOptimization.ts # 主题优化
│   │   ├── useUserProfile.ts   # 用户资料
│   │   └── useYangtzeWaterLayers.ts # 长江水图层
│   │
│   ├── stores/                 # 状态管理 (22个 Pinia stores)
│   │   ├── analysisStore.ts    # 分析工具状态
│   │   ├── areaSelectionStore.ts # 区域选择状态
│   │   ├── bufferAnalysisStore.ts # 缓冲区分析状态
│   │   ├── eraseAnalysisStore.ts # 擦除分析状态
│   │   ├── featureQueryStore.ts # 要素查询状态
│   │   ├── interactionStore.ts # 交互状态
│   │   ├── intersectionAnalysisStore.ts # 相交分析状态
│   │   ├── layerDataStore.ts   # 图层数据状态
│   │   ├── layerUIStore.ts     # 图层UI状态
│   │   ├── loadingStore.ts     # 加载状态
│   │   ├── mapStore.ts         # 地图状态
│   │   ├── modalStore.ts       # 模态框状态
│   │   ├── modeStateStore.ts   # 模式切换状态
│   │   ├── monitoringDataStore.ts # 监测数据状态
│   │   ├── monitoringPlatformStore.ts # 监测平台状态
│   │   ├── pageStateStore.ts   # 页面状态
│   │   ├── persistenceStore.ts # 持久化状态
│   │   ├── popupStore.ts       # 弹窗状态
│   │   ├── selectionStore.ts   # 选择状态
│   │   ├── shortestPathAnalysisStore.ts # 最短路径分析状态
│   │   ├── themeStore.ts       # 主题状态
│   │   └── userStore.ts        # 用户状态
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
│   │   │   │   ├── traditional/ # 传统 GIS 模式 (9个文件)
│   │   │   │   │   ├── TraditionalMode.vue
│   │   │   │   │   ├── LayerManager.vue
│   │   │   │   │   ├── FeatureQueryPanel.vue
│   │   │   │   │   ├── AreaSelectionTools.vue
│   │   │   │   │   ├── BufferAnalysisPanel.vue
│   │   │   │   │   ├── IntersectionAnalysisPanel.vue
│   │   │   │   │   ├── EraseAnalysisPanel.vue
│   │   │   │   │   ├── ShortestPathAnalysisPanel.vue
│   │   │   │   │   └── DataUploadPanel.vue
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
│   │   │       ├── ViewSubPage1.vue
│   │   │       ├── ViewSubPage2.vue
│   │   │       ├── ViewSubPage3.vue
│   │   │       ├── 水文监测点_GeoJSON.json
│   │   │       ├── 长江线.geojson
│   │   │       └── 长江面.geojson
│   │   └── Dashboard.vue
│   │
│   ├── types/                  # TypeScript 类型定义 (7个文件)
│   │   ├── geojson.d.ts
│   │   ├── jsx-global.d.ts
│   │   ├── map.ts
│   │   ├── query.ts
│   │   ├── splitpanes.d.ts
│   │   ├── supermap.d.ts
│   │   └── vue-shims.d.ts
│   ├── utils/                  # 工具函数 (12个文件)
│   │   ├── __tests__/          # 测试文件
│   │   ├── config.ts           # 配置工具
│   │   ├── domainBackground.ts # 领域背景
│   │   ├── eventUtils.ts       # 事件工具
│   │   ├── featureUtils.ts     # 要素工具
│   │   ├── geometryConverter.ts # 几何转换
│   │   ├── layerUtils.ts       # 图层工具
│   │   ├── layerValidation.ts  # 图层验证
│   │   ├── legendColorUtils.ts # 图例颜色工具
│   │   ├── llmNotification.ts  # LLM通知
│   │   ├── notification.ts     # 通知工具
│   │   ├── styleUtils.ts       # 样式工具
│   │   └── themeUtils.ts       # 主题工具
│   ├── router/                 # 路由配置 (嵌套路由)
│   │   └── index.ts
│   ├── styles/                 # 全局样式 (主题系统)
│   │   └── theme.css
│   ├── data/                   # 数据文件
│   │   └── waterQualityMockData.ts
│   ├── App.vue                 # 根组件
│   ├── main.js                 # 应用入口
│   └── vite-env.d.ts           # Vite环境类型
│
├── docs/                       # 前端架构文档 (21个文件)
│   ├── 0.路由页面管理方式.md    # 路由架构设计
│   ├── 1.页面布局及UI管理方式.md # 布局组件层级
│   ├── 2.UI组件设置.md          # UI组件详细说明
│   ├── 3.前端四大分析功能接口调用文档.md # 分析功能接口
│   ├── 4.功能实现方法.md        # 组合式函数实现
│   ├── 5.状态管理设计.md        # 22个Pinia状态模块
│   ├── 6.openlayer使用情况.md   # OpenLayers使用
│   ├── 7.主题切换机制说明.md    # 主题系统
│   ├── 8.读取数据流程.md        # 数据读取流程
│   ├── 9.图层管理与数据读取机制分析.md # 数据流转机制
│   ├── 10.Pinia状态管理重构总结.md # 状态管理重构
│   ├── 10.配置设置.md          # 配置设置
│   ├── 11.LLMmodelUI.md        # LLM模型UI
│   ├── 11.UI组件库介绍.md       # UI组件库介绍
│   ├── 13.图层保存方式.md       # 图层保存
│   ├── 14.显示图层.md          # 图层显示
│   ├── 15.属性数据处理优化.md   # 属性数据处理
│   ├── 16.注记添加方法.md       # 注记添加
│   ├── 17.属性数据管理方式.md   # 属性数据管理
│   ├── 18.view页面路由设计方案整理.md # 视图页面路由
│   ├── 19.持久化上传图层.md     # 持久化上传图层
│   └── 20.事件驱动分析.md       # EDA事件驱动架构
├── public/                     # 静态资源
│   ├── dist/                   # 第三方库
│   ├── libs/                   # 库文件
│   ├── favicon.ico
│   ├── logo.jpg
│   └── logoContent.png
├── dist/                       # 构建产物
├── package.json                # 依赖配置
├── tsconfig.json               # TypeScript配置
└── vite.config.js              # Vite配置
```

### 后端结构 (Backend/)

#### EDA事件驱动Agent服务 (Backend/agent/)
```
agent/                          # FastAPI + LangChain + 通义千问
├── app.py                      # FastAPI 应用入口 (919行)
│       └── readme.md
├── rag/                        # RAG知识库系统
│   ├── 知识库/                 # 专业领域知识文档 (13个文件)
│   │   ├── wuhan.md            # 武汉基础信息
│   │   ├── 人工智能+.md        # 人工智能发展
│   │   ├── 发展方向.md         # 发展方向
│   │   ├── 地理空间人工智能发展概况.md # GeoAI发展研究
│   │   ├── 地表水环境标准GB3838-2002.pdf # 水质标准PDF
│   │   ├── 武汉市介绍.md       # 武汉市综合调研报告
│   │   ├── 武汉市基本情况_武汉年鉴.md # 武汉年鉴数据
│   │   ├── 武汉市基础情况_百度百科.md # 百度百科武汉
│   │   ├── 武汉市水文条件.md   # 武汉水文条件
│   │   ├── 武汉市统计数据.md   # 武汉统计数据
│   │   ├── 水质监测指标概念与标准.md # 水质监测专业标准
│   │   ├── 长江流域概况_百度百科.md # 长江流域百度百科
│   │   └── 长江流域概况.md     # 长江流域水资源管理报告
│   ├── 查询脚本/               # SQL查询脚本 (7个文件)
│   │   ├── 公路等级统计.sql
│   │   ├── 医院区域统计.sql
│   │   ├── 学校区域统计.sql
│   │   ├── 居民地地点名区域统计.sql
│   │   ├── 水文站点区域统计.sql
│   │   ├── 水系数据统计统计.sql
│   │   └── 铁路类型统计.sql
│   ├── 源表/                   # 数据源表 (6个文件)
│   │   ├── 医院.sql
│   │   ├── 学校.sql
│   │   ├── 居民地地点名.sql
│   │   ├── 水文站点.sql
│   │   ├── 水系线.sql
│   │   └── 水系面.sql
│   ├── 统计结果/               # 统计结果 (17个文件)
│   │   ├── 一到七普.sql
│   │   ├── 公路等级统计结果.sql
│   │   ├── 区域人口数量.sql
│   │   ├── 医院.sql
│   │   ├── 土地利用2000.sql
│   │   ├── 土地利用2010.sql
│   │   ├── 土地利用2020.sql
│   │   ├── 居民点.sql
│   │   ├── 年龄人口分布.sql
│   │   ├── 教育程度.sql
│   │   ├── 水文监测点.sql
│   │   ├── 水文站点.sql
│   │   ├── 水系线分类统计表.sql
│   │   ├── 水系面分类统计表.sql
│   │   ├── 男女比重.sql
│   │   ├── 行政区面积.sql
│   │   └── 铁路类型统计结果.sql
│   ├── 课件&代码/              # 学习课件 (3个文件)
│   │   ├── 1.RAG入门与从零到一搭建RAG系统.ipynb
│   │   ├── 2.基于LangChain的RAG系统开发.ipynb
│   │   └── 3.手动搭建RAG系统实战.ipynb
│   ├── vector_db/              # 向量数据库存储
│   │   ├── index.faiss
│   │   └── index.pkl
│   ├── rag_system.py           # RAG系统核心实现
│   ├── interactive_test.py     # 交互测试
│   ├── start_rag.py           # RAG启动脚本
│   ├── requirements.txt        # RAG依赖
│   └── README.md              # RAG说明文档
└── 18个工具函数 (在app.py中)   # 长江水域监测专业工具
    ├── query_knowledge_base    # 知识库查询 (武汉市概况、长江流域、水质监测标准等)
    ├── update_knowledge_base   # 知识库更新
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
├── downloads/                  # 下载文件 (526个JSON文件)
├── node_modules/               # Node.js依赖
├── package.json                # 依赖配置
├── package-lock.json           # 依赖锁定文件
└── README.md                   # 服务文档
```

### 架构设计原则

#### 前端架构
- **事件驱动设计**: 基于CustomEvent的前后端解耦通信机制
- **组件化设计**: 25个UI组件 + 14个地图组件 + 17个图表组件 + 2个Agent组件，高度可复用
- **状态管理**: 22个Pinia状态模块，模块化管理应用状态
- **组合式函数**: 24个composables承载业务逻辑，与组件解耦
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
- **Python**: >= 3.10（推荐使用 conda `py310` 环境）
- **PostgreSQL**: >= 15
- **Git**: 最新版本

#### 推荐工具
- **IDE**: VS Code + Vue Language Features 扩展
- **数据库工具**: pgAdmin 或 DBeaver
- **API测试**: Postman 或 Insomnia

### 一键启动（推荐）

#### 1. 安装依赖

在仓库根目录创建并激活 conda 环境（环境名称必须是 `py310`），安装 Python 依赖：

```powershell
conda create -n py310 python=3.10
conda activate py310
pip install -r requirements.txt
```

或者使用仓库内虚拟环境 `.venv_tmp`：

```powershell
.\.venv_tmp\Scripts\Activate.ps1
```

安装前端与分析服务依赖：

```powershell
cd Frontend
npm install
cd ..\Backend\analysis
npm install
```

#### 2. 启动所有服务

在仓库根目录双击或执行启动脚本：

| 脚本 | Python 环境 | 启动的服务 |
|------|------------|-----------|
| `start_services.bat`（推荐） | conda `py310` | Analysis + Agent + Frontend（不启动 User） |
| `start_services_venv_tmp.bat` | `.venv_tmp` | Analysis + User + Agent + Frontend（全部四个） |

脚本会先自动释放 5173/8087/8088/8089 端口，再依次拉起各服务。

### 服务访问地址

启动成功后，可通过以下地址访问各服务：

| 服务 | 地址 | 说明 |
|------|------|------|
| 🌐 前端应用 | http://localhost:5173 | 主应用界面 |
| 🤖 EDA Agent服务 | http://localhost:8089/docs | FastAPI Swagger 文档 |
| 👤 用户服务 API | http://localhost:8088/docs | FastAPI Swagger 文档 |
| 🗺️ 分析服务 API | http://localhost:8087/docs | 空间分析 API 文档 |
| 🗺️ SuperMap iServer | http://localhost:8090 | 独立部署的地图服务 |



#### EDA Agent 配置
```bash
# 阿里云通义千问配置
DASHSCOPE_API_KEY=your-dashscope-api-key#项目保留了自己的key位于后端服务的.env文件中
DASHSCOPE_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
DASHSCOPE_MODEL=qwen-plus
DASHSCOPE_TEMPERATURE=0.5
DASHSCOPE_MAX_TOKENS=3000
```



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
   - 查看端口 8088 是否被占用

2. **分析服务启动失败**
   - 检查 Node.js 版本 (需要 18.0+)
   - 确认 npm 依赖安装完整
   - 查看端口 8087 是否被占用
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

### 调试模式

```powershell
# 启用详细日志
npm run dev -- --debug
```

查看网络请求：打开浏览器开发者工具 -> Network 标签

## 🧪 测试

```powershell
# Frontend：路由测试 + 构建测试
cd Frontend
npm run test:all

# Analysis：单元测试（jest）
cd ..\Backend\analysis
npm test
```

## 📚 使用指南

### 快速上手
0. **启动服务**：双击启动仓库根目录的 `start_services.bat`
1. **启动应用**: 访问 `http://localhost:5173`
2. **选择模式**: 在顶部导航栏选择 LLM 模式或传统 GIS 模式
3. **地图操作**: 执行各类功能的实现（基础地图查看、查询、分析、知识库查询、查看可视化大屏等等）
4. **图层管理**: 在传统模式下使用图层管理面板控制图层显示

### EDA事件驱动LLM智能模式

- 在聊天界面输入自然语言指令，支持长江水域监测专业术语
- 支持的地图操作：知识库查询、图层管理、属性查询、空间分析、结果导出
- 18个工具函数支持完整的地理空间分析工作流
- 示例指令：
  - "查询武汉市的基本概况"
  - "长江流域的水质监测标准是什么？"
  - "武汉市的水文条件如何？"
  - "地理空间人工智能的发展概况"
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

- **项目地址**: [GitHub Repository](https://github.com/qianxiR/Agent-GISAM)
- **问题反馈**: [GitHub Issues](https://github.com/qianxiR/Agent-GISAM/issues)
- **文档**: 查看项目 `docs/` 目录获取详细文档

---

*本项目持续维护和更新中，欢迎关注和贡献！*

**最后更新**: 2026.8.16
