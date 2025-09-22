import { createRouter, createWebHistory } from 'vue-router'
import Dashboard from '@/views/Dashboard.vue'

/**
 * Vue Router 配置
 * 使用 History API 模式，支持更友好的URL结构
 */
const router = createRouter({
  history: createWebHistory(),
  routes: [
    // 根路径重定向到仪表板（会自动重定向到视图页面）
    {
      path: '/',
      redirect: '/dashboard'
    },
    // 仪表板页面，包含模式子路由
    {
      path: '/dashboard',
      name: 'dashboard',
      component: Dashboard,
      meta: { 
        title: '地图系统'
      },
      children: [
        // 默认子路由 - 重定向到图层管理
        {
          path: '',
          name: 'dashboard-default',
          redirect: '/dashboard/management-analysis/traditional/layer'
        },
        // 视图首页（带地图功能）
        {
          path: 'view/home',
          name: 'view-home',
          component: () => import('@/views/dashboard/ViewPage/ViewHome.vue'),
          meta: { 
            title: '地图视图'
          },
          children: [
            // 图层管理子路由
            {
              path: 'layermanage',
              name: 'view-layer-manage',
              component: () => import('@/views/dashboard/ViewPage/ViewLayerManager.vue'),
              meta: {
                title: '图层管理'
              }
            }
          ]
        },
        // 视图页面重定向
        {
          path: 'view',
          name: 'view-page',
          redirect: '/dashboard/view/home'
        },
        // 管理分析模块
        {
          path: 'management-analysis',
          name: 'management-analysis',
          component: () => import('@/views/dashboard/management-analysis/ManagementAnalysis.vue'),
          meta: {
            title: '管理分析'
          },
          children: [
            // 管理分析默认子路由 - 直接重定向到图层管理
            {
              path: '',
              name: 'management-analysis-default',
              redirect: '/dashboard/management-analysis/traditional/layer'
            },
            // LLM模式
            {
              path: 'llm',
              name: 'llm-mode',
              component: () => import('@/views/dashboard/management-analysis/LLM/LLMMode.vue'),
              meta: {
                title: 'AI助手',
                mode: 'llm'
              },
              children: [
                // LLM模式默认子路由
                {
                  path: '',
                  name: 'llm-mode-default',
                  redirect: '/dashboard/management-analysis/llm/chat'
                },
                // 聊天界面
                {
                  path: 'chat',
                  name: 'llm-chat',
                  component: () => import('@/views/dashboard/management-analysis/LLM/ChatAssistant.vue'),
                  meta: {
                    title: 'AI聊天'
                  }
                },
                // 历史聊天记录
                {
                  path: 'chat-history',
                  name: 'chat-history',
                  component: () => import('@/views/dashboard/management-analysis/LLM/ChatHistory.vue'),
                  meta: {
                    title: '历史聊天记录',
                    mode: 'llm'
                  }
                }
              ]
            },
            // 传统模式
            {
              path: 'traditional',
              name: 'traditional-mode',
              component: () => import('@/views/dashboard/management-analysis/traditional/TraditionalMode.vue'),
              meta: {
                title: '传统模式',
                mode: 'traditional'
              },
              children: [
                // 传统模式默认子路由 - 直接重定向到图层管理
                {
                  path: '',
                  name: 'traditional-mode-default',
                  redirect: '/dashboard/management-analysis/traditional/layer'
                },
                // 图层管理
                {
                  path: 'layer',
                  name: 'layer-management',
                  component: () => import('@/views/dashboard/management-analysis/traditional/tools/LayerManager.vue'),
                  meta: {
                    title: '图层管理',
                    tool: 'layer'
                  }
                },
                // 按属性选择要素
                {
                  path: 'attribute-selection',
                  name: 'attribute-selection',
                  component: () => import('@/views/dashboard/management-analysis/traditional/tools/FeatureQueryPanel.vue'),
                  meta: {
                    title: '按属性选择要素',
                    tool: 'query'
                  }
                },
                // 按区域选择要素
                {
                  path: 'area-selection',
                  name: 'area-selection',
                  component: () => import('@/views/dashboard/management-analysis/traditional/tools/AreaSelectionTools.vue'),
                  meta: {
                    title: '按区域选择要素',
                    tool: 'bianji'
                  }
                },
                // 缓冲区分析
                {
                  path: 'buffer',
                  name: 'buffer-analysis',
                  component: () => import('@/views/dashboard/management-analysis/traditional/tools/BufferAnalysisPanel.vue'),
                  meta: {
                    title: '缓冲区分析',
                    tool: 'buffer'
                  }
                },
                // 最短路径分析
                {
                  path: 'distance',
                  name: 'shortest-path-analysis',
                  component: () => import('@/views/dashboard/management-analysis/traditional/tools/ShortestPathAnalysisPanel.vue'),
                  meta: {
                    title: '最短路径分析',
                    tool: 'distance'
                  }
                },
                // 相交分析
                {
                  path: 'intersect',
                  name: 'intersection-analysis',
                  component: () => import('@/views/dashboard/management-analysis/traditional/tools/IntersectionAnalysisPanel.vue'),
                  meta: {
                    title: '相交分析',
                    tool: 'intersect'
                  }
                },
                // 擦除分析
                {
                  path: 'erase',
                  name: 'erase-analysis',
                  component: () => import('@/views/dashboard/management-analysis/traditional/tools/EraseAnalysisPanel.vue'),
                  meta: {
                    title: '擦除分析',
                    tool: 'erase'
                  }
                },
                // 数据上传
                {
                  path: 'upload',
                  name: 'data-upload',
                  component: () => import('@/views/dashboard/management-analysis/traditional/tools/DataUploadPanel.vue'),
                  meta: {
                    title: '数据上传',
                    tool: 'upload'
                  }
                }
              ]
            }
      ]
    }
  ]
},]
})

/**
 * 全局路由守卫
 * 在每次路由跳转前执行
 */
router.beforeEach((to, _from, next) => {
  // 直接跳转，无需认证检查
  next()
})

export default router
