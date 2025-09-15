<template>
  <!-- 聊天助手主容器 -->
  <div class="chat-assistant">
    <!-- 顶部头部区域：包含功能按钮，为按钮预留高度，避免遮挡内容 -->
    <div class="chat-header">
      <!-- 新对话按钮：清空当前对话，开始新的对话会话 -->
      <SecondaryButton
        class="new-chat-button"
        variant="secondary"
        @click="startNewConversation"
      >
        <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <path d="M12 5v14M5 12h14"/>
        </svg>
        <span class="button-text">新对话</span>
      </SecondaryButton>
      
      <!-- 服务状态按钮：显示Agent服务的运行状态和功能信息 -->
      <SecondaryButton
        class="status-button"
        variant="secondary"
        @click="toggleApiStatus"
      >
        <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <circle cx="12" cy="12" r="10"/>
          <path d="M8 12l2 2 4-4"/>
        </svg>
        <span class="button-text">服务状态</span>
      </SecondaryButton>

      <!-- 历史记录按钮：查看和管理历史对话记录 -->
      <SecondaryButton
        class="history-button"
        variant="secondary"
        @click="toggleChatHistory"
      >
        <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <path d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"/>
        </svg>
        <span class="button-text">历史记录</span>
      </SecondaryButton>
    
      <!-- 工具记录按钮：查看Agent工具调用的历史记录和状态 -->
      <SecondaryButton
        class="tool-records-button"
        variant="secondary"
        @click="toggleToolRecords"
      >
        <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <path d="M12 20h9"/>
          <path d="M16.5 3.5a2.121 2.121 0 1 1 3 3L7 19l-4 1 1-4Z"/>
        </svg>
        <span class="button-text">工具记录</span>
      </SecondaryButton>
      
      
    </div>
    
    <!-- API状态弹窗：显示Agent服务的详细状态信息 -->
    <div v-if="showApiStatus" class="api-status-modal-overlay" @click="toggleApiStatus">
      <div class="api-status-modal" @click.stop>
        <div class="modal-header">
          <h3>服务状态</h3>
          <button class="close-button" @click="toggleApiStatus">
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M18 6L6 18M6 6l12 12"/>
            </svg>
          </button>
        </div>
        <div class="modal-content" v-if="apiStatus">
          <!-- 服务基本状态 -->
          <div class="status-item">
            <div class="status-label">服务状态</div>
            <div class="status-value">{{ apiStatus.service }}</div>
          </div>
          <!-- RAG知识库系统状态 -->
          <div class="status-item" v-if="apiStatus.rag_system_status">
            <div class="status-label">RAG系统</div>
            <div class="status-value">
              {{ getRAGStatusText(apiStatus.rag_system_status) }}
              <span v-if="apiStatus.rag_details?.document_count" class="doc-count">
                ({{ apiStatus.rag_details.document_count }}个文档)
              </span>
            </div>
          </div>
          <!-- 可用工具数量 -->
          <div class="status-item" v-if="apiStatus.tools_count">
            <div class="status-label">可用工具</div>
            <div class="status-value">{{ apiStatus.tools_count }}个</div>
          </div>
          <!-- 服务版本信息 -->
          <div class="status-item" v-if="apiStatus.version">
            <div class="status-label">版本</div>
            <div class="status-value">v{{ apiStatus.version }}</div>
          </div>
          
          <!-- 异常值提醒控制 -->
          <div class="status-item monitoring-control">
            <div class="status-label">异常值提醒</div>
            <div class="monitoring-control-content">
              <div class="monitoring-status">
                <span class="status-indicator" :class="{ active: isAutoPushEnabled }"></span>
                <span class="status-text">{{ isAutoPushEnabled ? '已启用' : '已禁用' }}</span>
              </div>
              <div class="monitoring-buttons">
                <button 
                  class="monitoring-toggle-btn"
                  :class="{ active: isAutoPushEnabled }"
                  @click="toggleAutoPush"
                >
                  {{ isAutoPushEnabled ? '停止提醒' : '启动提醒' }}
                </button>
                <button 
                  class="test-anomaly-btn"
                  @click="testAnomalyDetection"
                  :disabled="isLLMResponding"
                >
                  {{ isLLMResponding ? '测试中...' : '立即测试' }}
                </button>
              </div>
            </div>
            <div class="monitoring-description">
              检测到水质异常值时自动提醒AI进行深度分析
            </div>
          </div>
        </div>
        <div class="modal-content" v-else>
          <div class="loading-status">正在获取服务状态...</div>
        </div>
      </div>
    </div>

    <!-- 工具记录弹窗：显示Agent工具调用的历史记录和状态 -->
    <div v-if="showToolRecords" class="tool-records-modal-overlay" @click="toggleToolRecords">
      <div class="tool-records-modal" @click.stop>
        <div class="modal-header">
          <h3>工具调用记录</h3>
          <button class="close-button" @click="toggleToolRecords">
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M18 6L6 18M6 6l12 12"/>
            </svg>
          </button>
        </div>
        <div class="modal-content">
          <!-- 工具记录头部：显示记录数量和清空按钮 -->
          <div class="tool-records-header">
            <span class="record-count">共 {{ toolRecords.length }} 条记录</span>
            <button class="clear-records-button" @click="clearToolRecords" v-if="toolRecords.length > 0">
              清空记录
            </button>
          </div>
          <!-- 工具记录表格：显示工具名称和执行状态 -->
          <div class="tool-records-info">
            <div class="records-header">
              <span class="record-tool-name">工具名称</span>
              <span class="record-status">状态</span>
            </div>
            <div class="records-list">
              <!-- 工具记录列表：遍历显示每条工具调用记录 -->
              <div v-for="(record, index) in toolRecords" :key="index" class="record-item">
                <span class="record-tool-name">{{ record.name }}</span>
                <span class="record-status" :class="getStatusClass(record.resultStr)">
                  {{ getStatusText(record.resultStr) }}
                </span>
              </div>
              <!-- 空状态提示 -->
              <div v-if="toolRecords.length === 0" class="no-records">
                暂无工具调用记录
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 聊天历史弹窗：管理历史对话记录 -->
    <ChatHistory
      :visible="showChatHistory"
      @close="showChatHistory = false"
    />

    <!-- 工具调用提示区域：当AI调用了工具时显示工具调用信息（当前已禁用显示） -->
    <div v-if="toolCallInfo" class="tool-call-banner">
      <div class="tool-call-left">
        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <path d="M12 20h9"/>
          <path d="M16.5 3.5a2.121 2.121 0 1 1 3 3L7 19l-4 1 1-4Z"/>
        </svg>
        <div class="tool-meta">
          <div class="tool-name">工具调用：{{ toolCallInfo.name }}</div>
          <div class="tool-args" v-if="toolCallInfo.argsStr">参数：{{ toolCallInfo.argsStr }}</div>
        </div>
      </div>
      <div class="tool-result" v-if="toolCallInfo.resultStr">结果：{{ toolCallInfo.resultStr }}</div>
    </div>

    <!-- 聊天记录显示区域：显示用户和AI的对话消息 -->
    <ChatMessagesPanel
      ref="messagesPanelRef"
      :messages="messages"
      :auto-scroll="true"
      :scroll-threshold="100"
    />
    
    <!-- 输入区域：用户输入消息的界面 -->
    <LLMInputWindow
      v-model="newMessage"
      placeholder="请输入您的需求..."
      :rows="3"
      :disabled="false"
      :send-disabled="isLLMResponding"
      :send-button-title="isLLMResponding ? '请等待上一次对话完成！' : '发送消息'"
      @send="sendMessage"
    />
  </div>
</template>//

<script setup lang="ts">
// Vue 3 Composition API 相关导入
import { ref, watch, onMounted, nextTick, onUnmounted, computed } from 'vue';
import { useRouter } from 'vue-router';

// 状态管理相关导入
import { useThemeStore } from '@/stores/themeStore';
import { useModeStateStore } from '@/stores/modeStateStore';
import { useMonitoringPlatformStore } from '@/stores/monitoringPlatformStore';

// 组件导入
import LLMInputWindow from '@/components/Agent/LLMInputWindow.vue';
import ChatMessagesPanel from '@/components/Agent/ChatMessagesPanel.vue';
import SecondaryButton from '@/components/UI/SecondaryButton.vue';
import ChatHistory from './ChatHistory.vue';

// 工具函数导入
import { getAgentApiBaseUrl, getLLMApiConfig } from '@/utils/config'
import { getEnvironmentalBackground, getUseCases } from '@/utils/domainBackground'
import { getMonitoringSiteData } from '@/data/waterQualityMockData'

// 空间分析功能组合式函数导入
import { useBufferAnalysis } from '@/composables/useBufferAnalysis'
import { useIntersectionAnalysis } from '@/composables/useIntersectionAnalysis'
import { useEraseAnalysis } from '@/composables/useEraseAnalysis'
import { useShortestPathAnalysis } from '@/composables/useShortestPathAnalysis'

// HTTP 请求库
import axios from 'axios'

// 消息接口定义
interface Message {
  id: number;
  text: string;
  sender: 'user' | 'system';
}

// 初始化状态管理
useThemeStore();
const modeStateStore = useModeStateStore();
const monitoringPlatformStore = useMonitoringPlatformStore();
const router = useRouter();

// 初始化空间分析功能组合式函数
const { saveBufferResultsAsLayer } = useBufferAnalysis();
const { saveIntersectionResultsAsLayer } = useIntersectionAnalysis();
const { saveEraseResultsAsLayer } = useEraseAnalysis();
const { savePathResultsAsLayer } = useShortestPathAnalysis();

// 组件属性定义
const props = defineProps<{
  mapReady: boolean;
}>();

// 响应式状态定义
const messages = ref<Message[]>([]); // 聊天消息列表
const newMessage = ref(''); // 当前输入的消息
const hasAnnounced = ref(false); // 是否已显示欢迎消息
const messagesPanelRef = ref<InstanceType<typeof ChatMessagesPanel> | null>(null); // 消息面板引用
const toolCallInfo = ref<{ name: string; argsStr: string; resultStr: string } | null>(null); // 工具调用信息
const nextAssistantOverride = ref<string | null>(null); // 下一个助手回复覆盖
const currentTaskId = ref<string | null>(null); // 当前任务ID
const isLLMResponding = ref<boolean>(false); // LLM是否正在响应
const apiStatus = ref<any>(null); // API状态信息
const showApiStatus = ref<boolean>(false); // 是否显示API状态弹窗
const showToolRecords = ref<boolean>(false); // 是否显示工具记录弹窗

// 监测数据自动推送相关状态
const autoPushInterval = ref<number | null>(null); // 自动推送定时器
const currentSiteIndex = ref(0); // 当前推送的监测点索引
const isAutoPushEnabled = ref(true); // 是否启用自动推送
const showChatHistory = ref<boolean>(false); // 是否显示聊天历史弹窗
const toolRecords = ref<Array<{name: string, argsStr: string, resultStr: string, timestamp: number}>>([]); // 工具调用记录
let statusInterval: number | null = null; // 状态更新定时器


// 智能滚动相关状态现在由ChatMessagesPanel组件内部处理

// ==================== API状态管理函数 ====================

/**
 * 获取Agent服务的健康状态信息
 * 包括服务状态、RAG系统状态、工具数量等
 */
const fetchApiStatus = async () => {
  try {
    const apiBase = getAgentApiBaseUrl()
    const resp = await axios.get(`${apiBase}/health`)
    apiStatus.value = resp.data
    console.log('[ChatAssistant] API状态更新:', resp.data)
  } catch (error) {
    console.error('获取API状态失败:', error)
    apiStatus.value = {
      status: 'error',
      service: 'Agent Service',
      error: '连接失败'
    }
  }
}

/**
 * RAG状态文本转换函数
 * 将英文状态转换为中文显示
 */
const getRAGStatusText = (status: string) => {
  const statusMap: Record<string, string> = {
    'ready': '就绪',
    'not_initialized': '未初始化',
    'error': '错误',
    'unknown': '未知'
  }
  return statusMap[status] || status
}

/**
 * 切换API状态弹窗显示
 * 显示时自动获取最新状态信息
 */
const toggleApiStatus = () => {
  showApiStatus.value = !showApiStatus.value
  // 如果显示状态，立即获取最新状态
  if (showApiStatus.value) {
    fetchApiStatus()
  }
}

/**
 * 切换工具记录弹窗显示
 * 显示时自动从localStorage加载记录
 */
const toggleToolRecords = () => {
  showToolRecords.value = !showToolRecords.value
  // 如果显示记录，从localStorage加载
  if (showToolRecords.value) {
    loadToolRecords()
  }
}

/**
 * 切换聊天历史弹窗显示
 */
const toggleChatHistory = () => {
  showChatHistory.value = !showChatHistory.value
}

// ==================== 工具记录管理函数 ====================

/**
 * 从localStorage加载工具调用记录
 */
const loadToolRecords = () => {
  try {
    const saved = localStorage.getItem('toolRecords')
    if (saved) {
      toolRecords.value = JSON.parse(saved)
    }
  } catch (error) {
    console.error('加载工具记录失败:', error)
    toolRecords.value = []
  }
}

/**
 * 保存工具调用记录到localStorage
 * @param name 工具名称
 * @param argsStr 工具参数
 * @param resultStr 工具执行结果
 */
const saveToolRecord = (name: string, argsStr: string, resultStr: string) => {
  const record = {
    name,
    argsStr,
    resultStr,
    timestamp: Date.now()
  }
  
  toolRecords.value.unshift(record) // 添加到开头
  
  // 限制记录数量，最多保存50条
  if (toolRecords.value.length > 50) {
    toolRecords.value = toolRecords.value.slice(0, 50)
  }
  
  // 保存到localStorage
  try {
    localStorage.setItem('toolRecords', JSON.stringify(toolRecords.value))
  } catch (error) {
    console.error('保存工具记录失败:', error)
  }
}

/**
 * 清空所有工具调用记录
 */
const clearToolRecords = () => {
  toolRecords.value = []
  localStorage.removeItem('toolRecords')
}

// ==================== 工具函数 ====================

/**
 * 格式化时间戳为中文格式
 * @param timestamp 时间戳
 * @returns 格式化的时间字符串
 */
const formatTime = (timestamp: number) => {
  const date = new Date(timestamp)
  return date.toLocaleString('zh-CN', {
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  })
}

/**
 * 根据工具执行结果获取状态文本
 * @param resultStr 工具执行结果字符串
 * @returns 状态文本
 */
const getStatusText = (resultStr: string) => {
  if (!resultStr || resultStr.trim() === '') {
    return '执行中'
  }
  try {
    const result = JSON.parse(resultStr)
    if (result.action && result.params) {
      return '已完成'
    }
  } catch (e) {
    // 不是JSON格式，检查是否包含成功标识
    if (resultStr.includes('成功') || resultStr.includes('完成')) {
      return '已完成'
    }
  }
  return '已完成'
}

/**
 * 根据工具执行结果获取状态样式类
 * @param resultStr 工具执行结果字符串
 * @returns 状态样式类对象
 */
const getStatusClass = (resultStr: string) => {
  const status = getStatusText(resultStr)
  return {
    'status-completed': status === '已完成',
    'status-executing': status === '执行中'
  }
}

// ==================== 事件处理函数 ====================

/**
 * 键盘事件处理函数
 * ESC键关闭所有弹窗
 */
const handleKeydown = (event: KeyboardEvent) => {
  if (event.key === 'Escape') {
    if (showApiStatus.value) {
      showApiStatus.value = false
    }
    if (showToolRecords.value) {
      showToolRecords.value = false
    }
    if (showChatHistory.value) {
      showChatHistory.value = false
    }
  }
}

// ==================== 任务管理函数 ====================

/**
 * 检查任务状态
 * @param taskId 任务ID
 * @returns 任务状态信息
 */
const checkTaskStatus = async (taskId: string) => {
  try {
    const apiBase = getAgentApiBaseUrl()
    const resp = await axios.get(`${apiBase}/agent/task/${taskId}/status`)
    return resp.data
  } catch (error) {
    console.error('检查任务状态失败:', error)
  }
  return null
}




// ==================== 初始化函数 ====================

/**
 * 显示初始欢迎消息
 * 只在首次加载时显示，避免重复显示
 */
const maybeAnnounceInitiallayers = () => {
  // 显示初始欢迎语
  if (!hasAnnounced.value) {
    hasAnnounced.value = true;
    
    // 添加欢迎消息
    const welcomeMessage = `您好，我是您的武汉市长江水域与水资源管理的自主智能体助手。我能够自主完成感知、决策、分析、执行工作，可以帮助您进行城市空间分析、水资源管理、数据可视化以及多源信息整合等工作。

您可以进行以下功能，我将为您执行具体任务。

## 主要功能
- **知识库查询**：武汉市基本概况、水文资源条件概况、长江流域
- **缓冲区分析**：对图层@图层名称进行影响范围分析
- **相交分析**：@图层名称与@图层名称叠加，计算**人口数量、重要设施与土地类型**
- **擦除分析**：剔除限制区，得到**真实可治理与可取水区域**
- **最短路径分析**：规划**应急送水、物资运输、无人机航测**等最优路线以规避限制区

请告诉我您需要进行的具体任务或分析，我会为您提供支持！`
    
    messages.value.push({
      id: Date.now(),
      text: welcomeMessage,
      sender: 'system'
    })
    
    // 滚动到底部显示欢迎消息
    nextTick(() => {
      messagesPanelRef.value?.scrollToBottom()
    })
  }
}

/**
 * 恢复历史对话消息
 * @param historyMessages 历史消息数组
 */
const restoreHistoryMessages = (historyMessages: any[]) => {
  if (historyMessages && historyMessages.length > 0) {
    messages.value = [...historyMessages]
    hasAnnounced.value = true
    
    // 清空输入框
    newMessage.value = ''
    
    // 重置状态
    currentTaskId.value = null
    isLLMResponding.value = false
    
    // 滚动到底部
    nextTick(() => {
      messagesPanelRef.value?.scrollToBottom()
    })
  }
}

/**
 * 监听历史记录恢复事件
 * 从ChatHistory组件接收历史消息并恢复
 */
const handleChatHistoryRestored = (event: CustomEvent) => {
  const { messages: historyMessages } = event.detail
  restoreHistoryMessages(historyMessages)
}

// ==================== 事件监听器函数 ====================

/**
 * 监听属性查询结果事件
 * 处理属性查询完成后的结果反馈和上下文记忆
 */
const handleQueryResult = (event: CustomEvent) => {
  const { success, message, layerName, field, operator, value, count, error } = event.detail
  
  // 构造查询结果消息
  let resultMessage = ''
  if (success) {
    resultMessage = `[属性查询] 查询完成：${message}

🌊 长江水域分析概况：
当前属性查询已成功完成，为武汉市长江段水资源管理提供了重要的要素筛选结果。该查询结果可用于快速定位关键区域、筛选重要设施等水资源管理决策。

💡 后续操作建议：
您可以选择以下操作来进一步处理查询结果：
- 导出为图层：保存查询结果为新的地图图层，便于后续叠加分析
请告诉我您希望进行哪种操作？`
  } else {
    resultMessage = `[属性查询] 查询失败：${error || '未知错误'}`
  }
  
  // 将结果添加到聊天记录中
  messages.value.push({ 
    id: Date.now(), 
    text: resultMessage, 
    sender: 'system' 
  })
  
  // 滚动到底部显示新消息
  nextTick(() => {
    messagesPanelRef.value?.scrollToBottom()
  })
  
  // 发送查询结果上下文给AI，让AI记住刚才的查询类型
  if (success) {
    const contextMessage = `[属性查询完成] 刚才执行了属性查询，图层"${layerName}"，字段"${field}"，操作符"${operator}"，值"${value}"。现在AI需要记住这个查询类型，当用户说"导出为json"、"导出为图层"、"保存为图层"等操作时，必须基于这个属性查询结果调用对应的工具。`
    sendImplicitMessageToLLM(contextMessage, false)
  }
}

// 监听保存结果事件
const handleSaveResult = async (event: CustomEvent) => {
  const { success, message, layerName, count, error } = event.detail
  
  console.log('[ChatAssistant] 收到保存结果事件:', { success, message, layerName, count, error })
  
  // 保存失败时不向聊天面板发送消息，只记录日志
  if (!success) {
    console.log('[ChatAssistant] 保存失败，不显示到聊天面板:', message || '未知错误')
  }
  // 如果保存成功，不显示消息，等待系统弹窗确认
}

// 监听系统弹窗事件，确认保存操作完成
const handleSystemNotification = (event: CustomEvent) => {
  const { title, message, type } = event.detail
  
  // 检查是否是保存成功的弹窗
  if (type === 'success' && title && title.includes('保存成功')) {
    console.log('[ChatAssistant] 检测到保存成功弹窗:', { title, message })
    
    // 显示保存成功消息
    const successMessage = `✅ ${title}${message ? ` - ${message}` : ''}`
    messages.value.push({ 
      id: Date.now(), 
      text: successMessage, 
      sender: 'system' 
    })
    
    // 滚动到底部显示新消息
    nextTick(() => {
      messagesPanelRef.value?.scrollToBottom()
    })
    
    // 任务完成，重置状态
    currentTaskId.value = null
    isLLMResponding.value = false
    console.log('[ChatAssistant] 保存操作完成，任务状态已重置')
  }
}

// 监听导出结果事件
const handleExportResult = async (event: CustomEvent) => {
  const { success, message, fileName, count, error } = event.detail
  
  console.log('[ChatAssistant] 收到导出结果事件:', { success, message, fileName, count, error })
  
  // 移除回调消息显示逻辑，不再显示导出完成消息
}

// 具体的事件处理器函数
const handleSaveBufferResultsAsLayer = async (event: CustomEvent) => {
  const { layerName } = event.detail
  console.log('[ChatAssistant] 处理保存缓冲区分析结果事件:', { layerName })
  
  try {
    const result = await saveBufferResultsAsLayer(layerName)
    console.log('[ChatAssistant] 缓冲区分析结果保存完成:', result)
    
    // 保存成功后清空缓冲区分析状态
    if (result) {
      const { clearState } = useBufferAnalysis()
      clearState()
      console.log('[ChatAssistant] 缓冲区分析状态已清空')
    }
    
    // 发送保存结果事件
    const saveEvent = new CustomEvent('agent:saveResult', {
      detail: { 
        success: result, 
        message: result ? '缓冲区分析结果保存成功' : '缓冲区分析结果保存失败',
        layerName,
        count: 0
      }
    })
    window.dispatchEvent(saveEvent)
  } catch (error) {
    console.error('[ChatAssistant] 保存缓冲区分析结果失败:', error)
    const saveEvent = new CustomEvent('agent:saveResult', {
      detail: { 
        success: false, 
        message: '缓冲区分析结果保存失败',
        layerName,
        error: error instanceof Error ? error.message : '未知错误'
      }
    })
    window.dispatchEvent(saveEvent)
  }
}


const handleSaveIntersectionResultsAsLayer = async (event: CustomEvent) => {
  const { layerName } = event.detail
  console.log('[ChatAssistant] 处理保存相交分析结果事件:', { layerName })
  
  try {
    const result = await saveIntersectionResultsAsLayer(layerName)
    console.log('[ChatAssistant] 相交分析结果保存完成:', result)
    
    // 保存成功后清空相交分析状态
    if (result) {
      const { clearState } = useIntersectionAnalysis()
      clearState()
      console.log('[ChatAssistant] 相交分析状态已清空')
    }
    
    const saveEvent = new CustomEvent('agent:saveResult', {
      detail: { 
        success: result, 
        message: result ? '相交分析结果保存成功' : '相交分析结果保存失败',
        layerName,
        count: 0
      }
    })
    window.dispatchEvent(saveEvent)
  } catch (error) {
    console.error('[ChatAssistant] 保存相交分析结果失败:', error)
    const saveEvent = new CustomEvent('agent:saveResult', {
      detail: { 
        success: false, 
        message: '相交分析结果保存失败',
        layerName,
        error: error instanceof Error ? error.message : '未知错误'
      }
    })
    window.dispatchEvent(saveEvent)
  }
}


const handleSaveEraseResultsAsLayer = async (event: CustomEvent) => {
  const { layerName } = event.detail
  console.log('[ChatAssistant] 处理保存擦除分析结果事件:', { layerName })
  
  try {
    const result = await saveEraseResultsAsLayer(layerName)
    console.log('[ChatAssistant] 擦除分析结果保存完成:', result)
    
    // 保存成功后清空擦除分析状态
    if (result) {
      const { clearState } = useEraseAnalysis()
      clearState()
      console.log('[ChatAssistant] 擦除分析状态已清空')
    }
    
    const saveEvent = new CustomEvent('agent:saveResult', {
      detail: { 
        success: result, 
        message: result ? '擦除分析结果保存成功' : '擦除分析结果保存失败',
        layerName,
        count: 0
      }
    })
    window.dispatchEvent(saveEvent)
  } catch (error) {
    console.error('[ChatAssistant] 保存擦除分析结果失败:', error)
    const saveEvent = new CustomEvent('agent:saveResult', {
      detail: { 
        success: false, 
        message: '擦除分析结果保存失败',
        layerName,
        error: error instanceof Error ? error.message : '未知错误'
      }
    })
    window.dispatchEvent(saveEvent)
  }
}


const handleSavePathResultsAsLayer = async (event: CustomEvent) => {
  const { layerName } = event.detail
  console.log('[ChatAssistant] 处理保存最短路径分析结果事件:', { layerName })
  
  try {
    const result = await savePathResultsAsLayer(layerName)
    console.log('[ChatAssistant] 最短路径分析结果保存完成:', result)
    
    // 保存成功后清空最短路径分析状态
    if (result) {
      const { clearState } = useShortestPathAnalysis()
      clearState()
      console.log('[ChatAssistant] 最短路径分析状态已清空')
    }
    
    const saveEvent = new CustomEvent('agent:saveResult', {
      detail: { 
        success: result, 
        message: result ? '最短路径分析结果保存成功' : '最短路径分析结果保存失败',
        layerName,
        count: 0
      }
    })
    window.dispatchEvent(saveEvent)
  } catch (error) {
    console.error('[ChatAssistant] 保存最短路径分析结果失败:', error)
    const saveEvent = new CustomEvent('agent:saveResult', {
      detail: { 
        success: false, 
        message: '最短路径分析结果保存失败',
        layerName,
        error: error instanceof Error ? error.message : '未知错误'
      }
    })
    window.dispatchEvent(saveEvent)
  }
}


// 监听缓冲区分析结果事件
const handleBufferAnalysisResult = (event: CustomEvent) => {
  const { success, message, layerName, radius, unit, error } = event.detail
  
  // 移除回调消息显示逻辑，不再显示详细的分析完成消息
  
  // 任务完成，重置状态
  currentTaskId.value = null
  isLLMResponding.value = false
  console.log('缓冲区分析完成，任务状态已重置')
  
    sendImplicitMessageToLLM( '', false)
  
}

// 监听相交分析结果事件
const handleIntersectionAnalysisResult = (event: CustomEvent) => {
  const { success, message, targetLayerName, maskLayerName, error } = event.detail
  
  // 移除回调消息显示逻辑，不再显示详细的分析完成消息
  
  // 任务完成，重置状态
  currentTaskId.value = null
  isLLMResponding.value = false
  console.log('相交分析完成，任务状态已重置')
  
  sendImplicitMessageToLLM( '', false)
}

// 监听擦除分析结果事件
const handleEraseAnalysisResult = (event: CustomEvent) => {
  const { success, message, targetLayerName, eraseLayerName, error } = event.detail
  
  // 移除回调消息显示逻辑，不再显示详细的分析完成消息
  
  // 任务完成，重置状态
  currentTaskId.value = null
  isLLMResponding.value = false
  console.log('擦除分析完成，任务状态已重置')
  
  sendImplicitMessageToLLM( '', false)
}

// 监听最短路径分析结果事件
const handlePathAnalysisResult = (event: CustomEvent) => {
  const { success, message, startLayerName, endLayerName, error } = event.detail
  
  // 移除回调消息显示逻辑，不再显示详细的分析完成消息
  
  // 任务完成，重置状态
  currentTaskId.value = null
  isLLMResponding.value = false
  console.log('最短路径分析完成，任务状态已重置')
  
  sendImplicitMessageToLLM( '', false)
}

// 监听获取打开图层结果事件
const handleGetOpenLayersResult = (event: CustomEvent) => {
  const { success, message, layerCount, layers, layerNames, error } = event.detail
  
  // 移除回调消息显示逻辑，不再显示图层查询完成消息
  
  // 任务完成，重置状态
  currentTaskId.value = null
  isLLMResponding.value = false
  console.log('图层查询完成，任务状态已重置')
}

// 监听LLM分析结果接收事件
const handleLLMAnalysisResultReceived = (event: CustomEvent) => {
  const { analysisType, resultMessage, llmResponse, additionalData } = event.detail
  
  console.log('[ChatAssistant] 收到LLM分析结果:', {
    analysisType,
    resultMessage,
    llmResponse: llmResponse?.substring(0, 100) + '...',
    additionalData
  })
  
  // 将LLM响应添加到聊天记录中
  if (llmResponse) {
    messages.value.push({ 
      id: Date.now(), 
      text: llmResponse, 
      sender: 'system' 
    })
    
    // 滚动到底部显示新消息
    nextTick(() => {
      messagesPanelRef.value?.scrollToBottom()
    })
  }
}

// 监听LLM分析结果错误事件
const handleLLMAnalysisResultError = (event: CustomEvent) => {
  const { analysisType, error } = event.detail
  
  console.error('[ChatAssistant] LLM分析结果处理错误:', {
    analysisType,
    error
  })
  
  // 将错误消息添加到聊天记录中
  const errorMessage = `[${analysisType}] LLM处理失败：${error}`
  messages.value.push({ 
    id: Date.now(), 
    text: errorMessage, 
    sender: 'system' 
  })
  
  // 滚动到底部显示新消息
  nextTick(() => {
    messagesPanelRef.value?.scrollToBottom()
  })
}





onMounted(() => {
  // 恢复LLM模式状态
  const llmState = modeStateStore.getLLMState()
  if (llmState.messages.length > 0) {
    messages.value = [...llmState.messages]
    hasAnnounced.value = true
  }
  if (llmState.inputText) {
    newMessage.value = llmState.inputText
  }
  
  // 初始化监测平台store
  monitoringPlatformStore.initializeStore()
  
  // 启动监测数据自动推送
  if (isAutoPushEnabled.value) {
    startAutoPush()
  }
  
  // 重置任务状态
  currentTaskId.value = null
  isLLMResponding.value = false
  
  // 设置定期更新API状态（每30秒，但不自动显示）
  statusInterval = setInterval(() => {
    if (showApiStatus.value) {
      fetchApiStatus()
    }
  }, 30000)
  
  // 如果没有恢复的状态，则显示初始消息
  if (messages.value.length === 0) {
    maybeAnnounceInitiallayers();
  }
  
  // 使用nextTick处理DOM更新
  nextTick(() => {
    // 初始化滚动位置检测
    // 滚动位置检测现在由ChatMessagesPanel组件内部处理
    
    // 恢复滚动位置
    if (llmState.scrollPosition > 0) {
      setTimeout(() => {
        messagesPanelRef.value?.scrollToPosition(llmState.scrollPosition);
      }, 100);
    } else {
      // 如果没有保存的滚动位置，滚动到底部
      messagesPanelRef.value?.scrollToBottom();
    }
  });

  
  // 监听查询结果事件 - 只注册一次
  if (!(window as any).__queryResultListenerRegistered) {
    (window as any).__queryResultListenerRegistered = true
    window.addEventListener('agent:queryResult', handleQueryResult as EventListener)
    window.addEventListener('agent:saveResult', handleSaveResult as unknown as EventListener)
    window.addEventListener('agent:exportResult', handleExportResult as unknown as EventListener)
    window.addEventListener('agent:bufferAnalysisResult', handleBufferAnalysisResult as EventListener)
    window.addEventListener('agent:intersectionAnalysisResult', handleIntersectionAnalysisResult as EventListener)
    window.addEventListener('llm:analysisResultReceived', handleLLMAnalysisResultReceived as EventListener)
    window.addEventListener('llm:analysisResultError', handleLLMAnalysisResultError as EventListener)
    window.addEventListener('agent:eraseAnalysisResult', handleEraseAnalysisResult as EventListener)
    window.addEventListener('agent:pathAnalysisResult', handlePathAnalysisResult as EventListener)
    window.addEventListener('agent:getOpenLayersResult', handleGetOpenLayersResult as EventListener)
    // 监听保存和导出结果事件
    window.addEventListener('agent:saveBufferResultsAsLayer', handleSaveBufferResultsAsLayer as unknown as EventListener)
    window.addEventListener('agent:saveIntersectionResultsAsLayer', handleSaveIntersectionResultsAsLayer as unknown as EventListener)
    window.addEventListener('agent:saveEraseResultsAsLayer', handleSaveEraseResultsAsLayer as unknown as EventListener)
    window.addEventListener('agent:savePathResultsAsLayer', handleSavePathResultsAsLayer as unknown as EventListener)
    // 监听图层可见性变化事件，只记录日志不显示消息
    window.addEventListener('agent:layerVisibilityChanged', ((e: any) => {
      const { layerName, visible } = e.detail || {}
      const msg = visible ? `打开图层：${layerName}` : `关闭图层：${layerName}`
      console.log('[ChatAssistant] 图层可见性变化，不显示到聊天面板:', msg)
      // 不发送给AI，避免占据端口
    }) as EventListener)
  }
  
    // 监听系统弹窗事件，确认保存操作完成
    window.addEventListener('showNotification', handleSystemNotification as unknown as EventListener)
    
    // 监听监测点选择事件，自动发送监测点信息
    window.addEventListener('monitoring:siteSelected', ((e: any) => {
      const { site } = e.detail || {}
      if (site) {
        console.log('[ChatAssistant] 收到监测点选择事件:', site.name)
        // 自动发送监测点信息给AI
        sendMonitoringSiteInfo(site, false)
      }
    }) as EventListener)
    
    // 监听阈值超限警告事件
    window.addEventListener('system:thresholdAlert', ((e: any) => {
      const { siteName, layerName, violations } = e.detail || {}
      if (siteName && violations) {
        console.log('[ChatAssistant] 收到阈值超限警告:', siteName)
        
        // 构造阈值超限消息
        const violationMessages = violations.map((v: any) => {
          const paramName = v.parameter === 'water_temperature' ? '水温' :
                           v.parameter === 'ph_value' ? 'pH值' :
                           v.parameter === 'dissolved_oxygen' ? '溶解氧' :
                           v.parameter === 'turbidity' ? '浊度' :
                           v.parameter === 'permanganate_index' ? '高锰酸盐指数' :
                           v.parameter === 'ammonia_nitrogen' ? '氨氮' :
                           v.parameter === 'total_phosphorus' ? '总磷' :
                           v.parameter === 'total_nitrogen' ? '总氮' :
                           v.parameter === 'chlorophyll_a' ? '叶绿素a' :
                           v.parameter === 'algae_density' ? '藻类密度' : v.parameter
          
          const unit = v.parameter === 'water_temperature' ? '°C' :
                      v.parameter === 'ph_value' ? '' :
                      v.parameter === 'dissolved_oxygen' ? 'mg/L' :
                      v.parameter === 'turbidity' ? 'NTU' :
                      v.parameter === 'permanganate_index' ? 'mg/L' :
                      v.parameter === 'ammonia_nitrogen' ? 'mg/L' :
                      v.parameter === 'total_phosphorus' ? 'mg/L' :
                      v.parameter === 'total_nitrogen' ? 'mg/L' :
                      v.parameter === 'chlorophyll_a' ? 'mg/L' :
                      v.parameter === 'algae_density' ? '个/L' : ''
          
          const currentValue = v.parameter === 'algae_density' 
            ? v.value.toLocaleString() 
            : v.value.toFixed(3)
          
          let status = ''
          if (v.value < v.threshold.min) {
            status = `低于最小值 ${v.threshold.min}${unit}`
          } else if (v.value > v.threshold.max) {
            status = `超过最大值 ${v.threshold.max}${unit}`
          }
          
          return `${paramName}: ${currentValue}${unit} (${status})`
        }).join('\n')
        
        const alertMessage = `[水质预警] 监测点 ${siteName} 的以下参数超过阈值：
${violationMessages}

请立即关注这些异常指标，建议进行进一步的水质分析和处理。`
        
        // 发送预警消息给AI
        sendQuickMessageToLLM(alertMessage)
        
        // 显示系统通知
        showSystemNotification(
          '水质参数超限预警',
          `监测点 ${siteName} 有 ${violations.length} 个参数超过阈值`,
          'error'
        )
      }
    }) as EventListener)
  });

// 保存LLM模式状态
const saveLLMState = () => {
  const scrollPosition = messagesPanelRef.value?.getScrollPosition() || 0;
  modeStateStore.saveLLMState({
    messages: messages.value,
    inputText: newMessage.value,
    scrollPosition
  });
};

// 组件卸载时保存状态和清理事件监听器
onUnmounted(() => {
  saveLLMState();
  
  // 清理定时器
  if (statusInterval) {
    clearInterval(statusInterval)
  }
  
  // 清理自动推送定时器
  if (autoPushInterval.value) {
    clearInterval(autoPushInterval.value)
    autoPushInterval.value = null
  }
  
  // 清理事件监听器
  window.removeEventListener('chatHistoryRestored', handleChatHistoryRestored as EventListener)
  window.removeEventListener('keydown', handleKeydown)
  
  
  
  if ((window as any).__queryResultListenerRegistered) {
    window.removeEventListener('agent:queryResult', handleQueryResult as EventListener)
    window.removeEventListener('agent:saveResult', handleSaveResult as unknown as EventListener)
    window.removeEventListener('agent:exportResult', handleExportResult as unknown as EventListener)
    window.removeEventListener('agent:bufferAnalysisResult', handleBufferAnalysisResult as EventListener)
    window.removeEventListener('agent:intersectionAnalysisResult', handleIntersectionAnalysisResult as EventListener)
    window.removeEventListener('agent:eraseAnalysisResult', handleEraseAnalysisResult as EventListener)
    window.removeEventListener('agent:pathAnalysisResult', handlePathAnalysisResult as EventListener)
    window.removeEventListener('agent:getOpenLayersResult', handleGetOpenLayersResult as EventListener)
    // 清理保存结果事件监听器
    window.removeEventListener('agent:saveBufferResultsAsLayer', handleSaveBufferResultsAsLayer as unknown as EventListener)
    window.removeEventListener('agent:saveIntersectionResultsAsLayer', handleSaveIntersectionResultsAsLayer as unknown as EventListener)
    window.removeEventListener('agent:saveEraseResultsAsLayer', handleSaveEraseResultsAsLayer as unknown as EventListener)
    window.removeEventListener('agent:savePathResultsAsLayer', handleSavePathResultsAsLayer as unknown as EventListener)
    window.removeEventListener('agent:layerVisibilityChanged', (() => {}) as EventListener)
    window.removeEventListener('llm:analysisResultReceived', handleLLMAnalysisResultReceived as EventListener)
    window.removeEventListener('llm:analysisResultError', handleLLMAnalysisResultError as EventListener)
    ;(window as any).__queryResultListenerRegistered = false
  }
});

// 监听状态变化，自动保存
watch([messages, newMessage], () => {
  saveLLMState();
}, { deep: true });

// 地图就绪与否均可发送消息，保留监听但不做限制
watch(() => props.mapReady, () => {
  maybeAnnounceInitiallayers();
});

watch(messages, async () => {
  await nextTick();
  // 智能滚动逻辑现在由ChatMessagesPanel组件内部处理
}, { deep: true });

// 隐式发送消息到LLM（用于分析结果反馈）
const sendImplicitMessageToLLM = async (resultMessage: string, showResponse: boolean = false) => {
  try {
    const apiBase = getAgentApiBaseUrl()
    // 使用相同的会话ID
    const convId = sessionStorage.getItem('agent_conv_id') || (() => {
      const v = `conv-${Date.now()}`
      sessionStorage.setItem('agent_conv_id', v)
      return v
    })()
    
    // 构造完整的prompt
    const fullPrompt = resultMessage
    
    const llm = getLLMApiConfig()
    const payload = {
      model: 'qwen-plus',
      temperature: typeof llm.temperature === 'number' ? llm.temperature : 0.7,
      prompt: fullPrompt,
      stream: false,
      conversation_id: convId
    }
    
    const resp = await axios.post(`${apiBase}/agent/tool-chat`, payload)
    const content = resp.data?.data?.final_answer || '[空响应]'
      
      // 根据showResponse参数决定是否将LLM的回应添加到聊天记录中
      if (showResponse) {
        messages.value.push({ 
          id: Date.now() + 1, 
          text: content, 
          sender: 'system' 
        })
        
        // 滚动到底部显示新消息
        nextTick(() => {
          messagesPanelRef.value?.scrollToBottom()
        })
      }
  } catch (e: any) {
    console.error('隐式LLM请求异常:', e?.response?.data?.message || e?.message || e)
  }
}

// 快速发送消息到LLM（显示发送消息和AI回复）
const sendQuickMessageToLLM = async (resultMessage: string) => {
  // 设置LLM响应状态
  isLLMResponding.value = true
  
  try {
    // 先将发送的消息添加到聊天记录中
    messages.value.push({
      id: Date.now(),
      text: resultMessage,
      sender: 'user'
    })
    
    // 滚动到底部显示发送的消息
    nextTick(() => {
      messagesPanelRef.value?.scrollToBottom()
    })
    
    const apiBase = getAgentApiBaseUrl()
    // 使用相同的会话ID
    const convId = sessionStorage.getItem('agent_conv_id') || (() => {
      const v = `conv-${Date.now()}`
      sessionStorage.setItem('agent_conv_id', v)
      return v
    })()
    
    // 构造完整的prompt
    
    const llm = getLLMApiConfig()
    const payload = {
      model: 'qwen-plus',
      temperature: typeof llm.temperature === 'number' ? llm.temperature : 0.7,
      stream: false,
      conversation_id: convId
    }
    
    const resp = await axios.post(`${apiBase}/agent/tool-chat`, payload)
    const content = resp.data?.data?.final_answer || '未得到结果。'
      
      // 添加AI回复到消息列表
      messages.value.push({
        id: Date.now() + 1,
        text: content,
        sender: 'user'
      })
      
      // 滚动到底部
      nextTick(() => {
        messagesPanelRef.value?.scrollToBottom()
      })
      
      // 保存状态
      saveLLMState()
      
      // 重置响应状态
      isLLMResponding.value = false
  } catch (error: any) {
    console.error('快速发送消息到LLM失败:', error)
    const errorMessage = error?.response?.data?.message || error?.message || error
    messages.value.push({ 
      id: Date.now() + 1, 
      text: `LLM请求失败: ${errorMessage}`, 
      sender: 'system' 
    })
    // 重置响应状态
    isLLMResponding.value = false
  }
}

// ==================== 监测数据自动推送功能 ====================

/**
 * 发送监测点信息到AI
 * @param siteInfo 监测点信息
 * @param isAutoPush 是否为自动推送
 */
const sendMonitoringSiteInfo = async (siteInfo: any, isAutoPush: boolean = false) => {
  try {
    // 获取监测点的最新数据
    const siteData = getMonitoringSiteData(siteInfo.name)
    if (!siteData || !siteData.data || siteData.data.length === 0) {
      console.warn(`[ChatAssistant] 监测点 ${siteInfo.name} 没有数据`)
      return
    }

    const latestData = siteData.data[siteData.data.length - 1]
    
    // 随机生成异常指标名称
    const anomalyIndicators = ['溶解氧', '氨氮', '总磷', '浊度', 'pH值', '水温', '高锰酸盐指数', '总氮', '叶绿素a', '藻类密度']
    const randomAnomaly = anomalyIndicators[Math.floor(Math.random() * anomalyIndicators.length)]
    
    // 构造异常值检测消息
    const monitoringMessage = `🚨 [异常值检测] 监测点：${siteInfo.name} (${siteInfo.location})
坐标：${siteInfo.coordinates[0]}, ${siteInfo.coordinates[1]}
图层名称：${siteInfo.layerName}
水质类别：${siteInfo.waterQualityClass}

⚠️ 检测到异常指标：${randomAnomaly}指标异常！

📊 完整监测数据：
- 时间：${latestData.time}
- 水温：${latestData.water_temperature}°C
- pH值：${latestData.ph_value}
- 溶解氧：${latestData.dissolved_oxygen} mg/L
- 浊度：${latestData.turbidity} NTU
- 高锰酸盐指数：${latestData.permanganate_index} mg/L
- 氨氮：${latestData.ammonia_nitrogen} mg/L
- 总磷：${latestData.total_phosphorus} mg/L
- 总氮：${latestData.total_nitrogen} mg/L
- 叶绿素a：${latestData.chlorophyll_a} mg/L
- 藻类密度：${latestData.algae_density.toLocaleString()} 个/L

🔍 请立即分析这些异常数据，结合监测点坐标信息(${siteInfo.coordinates[0]}, ${siteInfo.coordinates[1]})和图层名称"${siteInfo.layerName}"，作为武汉市长江水域与水资源管理的自主智能体，给出针对性的治理意见和下一步建议！`

    // 发送给AI
    await sendQuickMessageToLLM(monitoringMessage)
    
    // 显示系统通知
    showSystemNotification(
      '水质异常值检测',
      `${siteInfo.location}站点${randomAnomaly}指标异常！我将为您自主定位并分析`,
      'error'
    )
    
    console.log(`[ChatAssistant] ${isAutoPush ? '自动检测' : '手动检测'}异常值: ${siteInfo.name}, 异常指标: ${randomAnomaly}`)
    
  } catch (error) {
    console.error('[ChatAssistant] 异常值检测失败:', error)
    showSystemNotification(
      '检测失败',
      `检测监测点"${siteInfo.location}"异常值时发生错误`,
      'error'
    )
  }
}

/**
 * 自动检测监测点异常值（每5分钟检测一次）
 */
const autoPushMonitoringData = () => {
  if (!isAutoPushEnabled.value) return
  
  const sites = monitoringPlatformStore.getAllSites
  if (sites.length === 0) return
  
  // 获取当前要检测的监测点
  const currentSite = sites[currentSiteIndex.value]
  if (currentSite) {
    sendMonitoringSiteInfo(currentSite, true)
    
    // 更新索引，循环检测
    currentSiteIndex.value = (currentSiteIndex.value + 1) % sites.length
  }
}

/**
 * 启动异常值检测定时器
 */
const startAutoPush = () => {
  if (autoPushInterval.value) return
  
  // 每5分钟检测一次
  autoPushInterval.value = setInterval(autoPushMonitoringData, 5 * 60 * 1000)
  console.log('[ChatAssistant] 异常值检测已启动，每5分钟检测一次')
  
  showSystemNotification(
    '异常值检测已启动',
    'Agent将自动检测监测点异常值并为您给出针对性意见并执行后续分析任务',
    'success'
  )
}

/**
 * 停止异常值检测定时器
 */
const stopAutoPush = () => {
  if (autoPushInterval.value) {
    clearInterval(autoPushInterval.value)
    autoPushInterval.value = null
    console.log('[ChatAssistant] 异常值检测已停止')
    
    showSystemNotification(
      '异常值检测已停止',
      '系统不再自动检测监测点异常值',
      'info'
    )
  }
}

/**
 * 显示系统通知
 */
const showSystemNotification = (title: string, message: string, type: 'success' | 'error' | 'info' = 'info') => {
  const notificationEvent = new CustomEvent('showNotification', {
    detail: {
      title,
      message,
      type,
      duration: 4000
    }
  })
  window.dispatchEvent(notificationEvent)
}

/**
 * 切换自动推送状态
 */
const toggleAutoPush = () => {
  isAutoPushEnabled.value = !isAutoPushEnabled.value
  
  if (isAutoPushEnabled.value) {
    startAutoPush()
  } else {
    stopAutoPush()
  }
}

/**
 * 立即测试异常值检测
 */
const testAnomalyDetection = async () => {
  if (isLLMResponding.value) return
  
  const sites = monitoringPlatformStore.getAllSites
  if (sites.length === 0) {
    showSystemNotification(
      '测试失败',
      '没有可用的监测点进行测试',
      'error'
    )
    return
  }
  
  // 获取当前要测试的监测点
  const currentSite = sites[currentSiteIndex.value]
  if (currentSite) {
    try {
      // 立即触发异常值检测
      await sendMonitoringSiteInfo(currentSite, true)
      
      // 显示测试成功通知
      showSystemNotification(
        '测试已触发',
        `已向AI发送${currentSite.location}站点的异常值检测请求`,
        'success'
      )
      
      // 随机生成异常指标名称并显示异常值提醒
      const anomalyIndicators = ['溶解氧', '氨氮', '总磷', '浊度', 'pH值', '水温', '高锰酸盐指数', '总氮', '叶绿素a', '藻类密度']
      const randomAnomaly = anomalyIndicators[Math.floor(Math.random() * anomalyIndicators.length)]
      
      // 显示异常值提醒通知
      showSystemNotification(
        '水质异常值检测',
        `${currentSite.location}站点${randomAnomaly}指标异常！我将为您自主定位并分析`,
        'error'
      )
      
      // 关闭服务状态弹窗
      showApiStatus.value = false
      
      console.log(`[ChatAssistant] 手动测试异常值检测: ${currentSite.name}`)
    } catch (error) {
      console.error('[ChatAssistant] 测试异常值检测失败:', error)
      showSystemNotification(
        '测试失败',
        `测试${currentSite.location}站点异常值检测时发生错误`,
        'error'
      )
    }
  }
}

// ==================== 核心消息发送函数 ====================

/**
 * 发送消息到Agent服务
 * 这是整个聊天系统的核心函数，处理用户输入并调用Agent工具
 */
const sendMessage = async () => {
  const message = newMessage.value.trim()
  
  // 如果LLM正在响应中，不允许发送新消息
  if (isLLMResponding.value) {
    console.log('[ChatAssistant] LLM正在响应中，禁止发送新消息')
    return
  }
  
  // 获取要发送的消息内容：优先使用输入框内容，否则使用最后一条用户消息
  const messageToSend = message || (() => {
    const lastUserMessage = messages.value.filter(msg => msg.sender === 'user').pop()
    return lastUserMessage ? lastUserMessage.text : ''
  })()
  
  if (!messageToSend) return

  // 设置LLM响应状态
  isLLMResponding.value = true

  // 只有在输入框有内容时才添加用户消息（避免重复添加）
  if (message) {
    const userMessage = { id: Date.now(), text: message, sender: 'user' as const }
    messages.value.push(userMessage)
    
    console.log('[ChatAssistant] 用户消息已发送')
  }
  

  // 获取Agent API基础URL
  const apiBase = getAgentApiBaseUrl()
  // 使用路由路径+时间戳派生一个稳定会话ID（同页会话期间不变）
  const convId = sessionStorage.getItem('agent_conv_id') || (() => {
    const v = `conv-${Date.now()}`
    sessionStorage.setItem('agent_conv_id', v)
    return v
  })()
  
  const userMsg = { role: 'user', content: messageToSend }

  try {
    // 构建请求参数
    const llm = getLLMApiConfig()
    const payload = {
      model: 'qwen-plus',
      temperature: typeof llm.temperature === 'number' ? llm.temperature : 0.7,
      prompt: messageToSend,
      stream: false,
      conversation_id: convId
    }
    
    // 发送请求到Agent服务
    const resp = await axios.post(`${apiBase}/agent/tool-chat`, payload)
    const data = resp.data
      
    // 保存任务ID
    if (data.task_id) {
      currentTaskId.value = data.task_id
      console.log('任务已创建:', data.task_id)
    }
      
    // 解析工具调用信息
    const firstCall = data?.data?.first_call
    const toolCalls = firstCall?.tool_calls || []
    if (Array.isArray(toolCalls) && toolCalls.length > 0) {
      const call = toolCalls[0]
      const name = call?.name || 'unknown'
      const argsStr = call?.args ? JSON.stringify(call.args) : ''
      const resultStr = data?.data?.tool_result != null ? 
        (typeof data.data.tool_result === 'object' ? 
          JSON.stringify(data.data.tool_result, null, 2) : 
          String(data.data.tool_result)) : ''
      
      // 所有工具调用都不显示工具调用结果框
      toolCallInfo.value = null
      // 保存工具调用记录
      saveToolRecord(name, argsStr, resultStr)
        
      // 对于知识库相关工具，不显示工具调用信息，直接等待AI回复
      if (name === 'query_knowledge_base' || name === 'update_knowledge_base') {
        console.log(`[Agent] ${name}工具调用，等待AI回复，不显示工具调用信息`)
        // 知识库工具不需要前端处理，直接等待AI的最终回复
      }
        
      // ==================== 工具调用分发处理 ====================
      // 根据不同的工具名称，分发对应的自定义事件到前端处理
      
      // 如果是切换图层可见性的工具，则在前端本地执行具体动作
      if (name === 'toggle_layer_visibility') {
          try {
            const parsed = call?.args || {}
            // 仅使用 layer_name 参数
            const layerName = parsed.layer_name || parsed.layerName
            const action = parsed.action
            if (layerName && action) {
              const ev = new CustomEvent('agent:toggleLayerVisibility', { detail: { layerName, action } })
              window.dispatchEvent(ev)
              console.log('[Agent] dispatched event: agent:toggleLayerVisibility', { layerName, action })
            }
          } catch {}
        }
        
        // 如果是按属性查询要素的工具，则在前端本地执行具体动作
        if (name === 'query_features_by_attribute') {
          try {
            const parsed = call?.args || {}
            const layerName = parsed.layer_name || parsed.layerName
            const field = parsed.field
            const operator = parsed.operator
            const value = parsed.value
            
            if (layerName && field && operator && value !== undefined) {
              const eventDetail = { layerName, field, operator, value }
              const ev = new CustomEvent('agent:queryFeaturesByAttribute', { 
                detail: eventDetail 
              })
              window.dispatchEvent(ev)
              console.log('[Agent] dispatched event: agent:queryFeaturesByAttribute', eventDetail)
            }
          } catch (error) {
            console.error('[Agent] 处理属性查询工具调用时出错:', error)
          }
        }
        
        // 如果是保存查询结果为图层的工具
        if (name === 'save_query_results_as_layer') {
          try {
            const parsed = call?.args || {}
            const layerName = parsed.layer_name || parsed.layerName
            
            if (layerName) {
              const ev = new CustomEvent('agent:saveQueryResultsAsLayer', { 
                detail: { layerName } 
              })
              window.dispatchEvent(ev)
              console.log('[Agent] dispatched event: agent:saveQueryResultsAsLayer', { layerName })
            }
          } catch (error) {
            console.error('[Agent] 处理保存查询结果工具调用时出错:', error)
          }
        }
        
        
        // 如果是获取当前打开图层的工具
        if (name === 'get_open_layers') {
          try {
            const ev = new CustomEvent('agent:getOpenLayers', { 
              detail: {} 
            })
            window.dispatchEvent(ev)
            console.log('[Agent] dispatched event: agent:getOpenLayers')
          } catch (error) {
            console.error('[Agent] 处理获取打开图层工具调用时出错:', error)
          }
        }
        
        // 如果是缓冲区分析工具
        if (name === 'execute_buffer_analysis') {
          try {
            const parsed = call?.args || {}
            const layerName = parsed.layer_name || parsed.layerName
            const radius = parsed.radius
            const unit = parsed.unit || 'meters'
            
            if (layerName && radius !== undefined) {
              const ev = new CustomEvent('agent:executeBufferAnalysis', { 
                detail: { layerName, radius, unit } 
              })
              window.dispatchEvent(ev)
              console.log('[Agent] dispatched event: agent:executeBufferAnalysis', { layerName, radius, unit })
            }
          } catch (error) {
            console.error('[Agent] 处理缓冲区分析工具调用时出错:', error)
          }
        }
        
        // 如果是相交分析工具
        if (name === 'execute_intersection_analysis') {
          try {
            const parsed = call?.args || {}
            const targetLayerName = parsed.target_layer_name || parsed.targetLayerName
            const maskLayerName = parsed.mask_layer_name || parsed.maskLayerName
            
            if (targetLayerName && maskLayerName) {
              const ev = new CustomEvent('agent:executeIntersectionAnalysis', { 
                detail: { targetLayerName, maskLayerName } 
              })
              window.dispatchEvent(ev)
              console.log('[Agent] dispatched event: agent:executeIntersectionAnalysis', { targetLayerName, maskLayerName })
            }
          } catch (error) {
            console.error('[Agent] 处理相交分析工具调用时出错:', error)
          }
        }
        
        // 如果是保存相交分析结果为图层的工具
        if (name === 'save_intersection_results_as_layer') {
          try {
            const parsed = call?.args || {}
            const layerName = parsed.layer_name || parsed.layerName
            
            if (layerName) {
              const ev = new CustomEvent('agent:saveIntersectionResultsAsLayer', { 
                detail: { layerName } 
              })
              window.dispatchEvent(ev)
              console.log('[Agent] dispatched event: agent:saveIntersectionResultsAsLayer', { layerName })
            }
          } catch (error) {
            console.error('[Agent] 处理保存相交分析结果工具调用时出错:', error)
          }
        }
        
        
        // 如果是擦除分析工具
        if (name === 'execute_erase_analysis') {
          try {
            const parsed = call?.args || {}
            const targetLayerName = parsed.target_layer_name || parsed.targetLayerName
            const eraseLayerName = parsed.erase_layer_name || parsed.eraseLayerName
            
            if (targetLayerName && eraseLayerName) {
              const ev = new CustomEvent('agent:executeEraseAnalysis', { 
                detail: { targetLayerName, eraseLayerName } 
              })
              window.dispatchEvent(ev)
              console.log('[Agent] dispatched event: agent:executeEraseAnalysis', { targetLayerName, eraseLayerName })
            }
          } catch (error) {
            console.error('[Agent] 处理擦除分析工具调用时出错:', error)
          }
        }
        
        // 如果是最短路径分析工具
        if (name === 'execute_shortest_path_analysis') {
          try {
            const parsed = call?.args || {}
            const startLayerName = parsed.start_layer_name || parsed.startLayerName
            const endLayerName = parsed.end_layer_name || parsed.endLayerName
            const obstacleLayerName = parsed.obstacle_layer_name || parsed.obstacleLayerName || ''
            
            if (startLayerName && endLayerName) {
              const ev = new CustomEvent('agent:executeShortestPathAnalysis', { 
                detail: { startLayerName, endLayerName, obstacleLayerName } 
              })
              window.dispatchEvent(ev)
              console.log('[Agent] dispatched event: agent:executeShortestPathAnalysis', { startLayerName, endLayerName, obstacleLayerName })
            }
          } catch (error) {
            console.error('[Agent] 处理最短路径分析工具调用时出错:', error)
          }
        }
        
        // 如果是保存缓冲区分析结果为图层的工具
        if (name === 'save_buffer_results_as_layer') {
          try {
            const parsed = call?.args || {}
            const layerName = parsed.layer_name || parsed.layerName
            
            console.log('[Agent] 准备分发保存缓冲区分析结果事件:', { layerName, parsed })
            
            if (layerName) {
              const ev = new CustomEvent('agent:saveBufferResultsAsLayer', { 
                detail: { layerName } 
              })
              window.dispatchEvent(ev)
              console.log('[Agent] dispatched event: agent:saveBufferResultsAsLayer', { layerName })
              
              // 测试事件是否被正确分发
              setTimeout(() => {
                console.log('[Agent] 事件分发后检查 - 3秒后')
              }, 3000)
            } else {
              console.warn('[Agent] 保存缓冲区分析结果事件分发失败 - 缺少layerName:', { layerName, parsed })
            }
          } catch (error) {
            console.error('[Agent] 处理保存缓冲区分析结果工具调用时出错:', error)
          }
        }
        
        
        // 如果是保存擦除分析结果为图层的工具
        if (name === 'save_erase_results_as_layer') {
          try {
            const parsed = call?.args || {}
            const layerName = parsed.layer_name || parsed.layerName
            
            if (layerName) {
              const ev = new CustomEvent('agent:saveEraseResultsAsLayer', { 
                detail: { layerName } 
              })
              window.dispatchEvent(ev)
              console.log('[Agent] dispatched event: agent:saveEraseResultsAsLayer', { layerName })
            }
          } catch (error) {
            console.error('[Agent] 处理保存擦除分析结果工具调用时出错:', error)
          }
        }
        
        
        // 如果是保存最短路径分析结果为图层的工具
        if (name === 'save_path_results_as_layer') {
          try {
            const parsed = call?.args || {}
            const layerName = parsed.layer_name || parsed.layerName
            
            if (layerName) {
              const ev = new CustomEvent('agent:savePathResultsAsLayer', { 
                detail: { layerName } 
              })
              window.dispatchEvent(ev)
              console.log('[Agent] dispatched event: agent:savePathResultsAsLayer', { layerName })
            }
          } catch (error) {
            console.error('[Agent] 处理保存最短路径分析结果工具调用时出错:', error)
          }
        }
        
        // 如果是导出最短路径分析结果为JSON的工具
        if (name === 'export_path_results_as_json') {
          try {
            const parsed = call?.args || {}
            const fileName = parsed.file_name || parsed.fileName
            
            if (fileName) {
              const ev = new CustomEvent('agent:exportPathResultsAsJson', { 
                detail: { fileName } 
              })
              window.dispatchEvent(ev)
              console.log('[Agent] dispatched event: agent:exportPathResultsAsJson', { fileName })
            }
          } catch (error) {
            console.error('[Agent] 处理导出最短路径分析结果工具调用时出错:', error)
          }
        }
        
        
        // ==================== 处理AI最终回复 ====================
        // 处理AI的最终回复（无论是否有工具调用）
        const finalAnswer = data?.data?.final_answer
        if (finalAnswer && finalAnswer.trim()) {
          const systemMessage = { id: Date.now() + 1, text: finalAnswer, sender: 'system' as const }
          messages.value.push(systemMessage)
          console.log('[ChatAssistant] AI最终回复已添加到聊天记录:', finalAnswer.substring(0, 100) + '...')
          
          // 滚动到底部显示AI回复
          nextTick(() => {
            messagesPanelRef.value?.scrollToBottom()
          })
        } else {
          console.warn('[ChatAssistant] AI没有生成最终回复或回复为空')
        }
        
        // 重置任务状态（有工具调用时也需要重置）
        currentTaskId.value = null
        isLLMResponding.value = false
        console.log('[ChatAssistant] 工具调用完成，任务状态已重置')
      } else {
        // ==================== 无工具调用处理 ====================
        toolCallInfo.value = null
        // 没有工具调用，直接重置任务状态
        currentTaskId.value = null
        isLLMResponding.value = false
        console.log('LLM响应完成（无工具调用），任务状态已重置')
        
        // 只有在没有工具调用时才添加AI的final_answer响应
        const content = nextAssistantOverride.value || data?.data?.final_answer || '[空响应]'
        const systemMessage = { id: Date.now() + 1, text: content, sender: 'system' as const }
        messages.value.push(systemMessage)
      }
      
      // 更新系统消息状态到Pinia

      nextAssistantOverride.value = null
    
    // 注意：有工具调用时不在这里重置任务状态，让工具调用结果事件来重置
    // 没有工具调用时在上面已经重置了任务状态
  } catch (e: any) {
    const errorMessage = e?.response?.data?.message || e?.message || e
    console.log('[ChatAssistant] LLM请求异常，不显示到聊天面板:', errorMessage)
    // 任务失败，重置状态
    currentTaskId.value = null
    isLLMResponding.value = false
    // 重置消息监控状态
  }

  newMessage.value = ''
}



// ==================== 对话管理函数 ====================

/**
 * 开启新对话功能
 * 保存当前对话到历史记录，清空当前状态，重新初始化
 */
const startNewConversation = () => {
  // 保存当前对话到历史记录（只要有消息就保存，包括欢迎消息）
  if (messages.value.length > 0) {
    const savedChatHistory = localStorage.getItem('chatHistory') || '[]';
    const chatHistory = JSON.parse(savedChatHistory);
    
    const currentChat = {
      id: Date.now(),
      timestamp: new Date().toISOString(),
      messages: [...messages.value],
      messageCount: messages.value.length
    };
    
    chatHistory.push(currentChat);
    
    // 限制历史记录数量，最多保存20条
    if (chatHistory.length > 20) {
      chatHistory.splice(0, chatHistory.length - 20);
    }
    
    localStorage.setItem('chatHistory', JSON.stringify(chatHistory));
    
    // 显示保存成功通知
    window.dispatchEvent(new CustomEvent('showNotification', {
      detail: {
        title: '对话已保存',
        message: '当前对话已保存到历史记录',
        type: 'success',
        duration: 2000
      }
    }));
  }
  
  // 清空消息历史
  messages.value = [];
  // 清空输入框
  newMessage.value = '';
  // 重置状态
  hasAnnounced.value = false;
  currentTaskId.value = null;
  isLLMResponding.value = false;
  
  // 重新初始化状态
  maybeAnnounceInitiallayers();
  
  // 清空保存的状态
  modeStateStore.saveLLMState({
    messages: [],
    inputText: '',
    scrollPosition: 0
  });
  
  // 滚动到顶部
  nextTick(() => {
    messagesPanelRef.value?.scrollToBottom();
  });
};

// ==================== 组件暴露方法 ====================

// 暴露方法给父组件
defineExpose({
  startNewConversation,
  toggleChatHistory
});
</script>



<style scoped>
.chat-assistant {
  height: 100%;
  width: 100%;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  min-height: 0;
  flex: 1;
  background: var(--bg);
}

.chat-header {
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: flex-start;
  gap: 8px;
  padding: 2px 6px;
  min-height: 26px;
  border-bottom: 1px solid var(--border);
  background: var(--panel);
}

/* API状态弹窗样式 */
.api-status-modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  backdrop-filter: blur(4px);
}

.api-status-modal {
  background: var(--panel);
  border: 1px solid var(--border);
  border-radius: 12px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
  max-width: 50vw;
  width: 90%;
  max-height: 85vh;
  overflow: hidden;
  animation: modalSlideIn 0.3s ease-out;
}

@keyframes modalSlideIn {
  from {
    opacity: 0;
    transform: scale(0.9) translateY(-20px);
  }
  to {
    opacity: 1;
    transform: scale(1) translateY(0);
  }
}

.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 20px;
  border-bottom: 1px solid var(--border);
  background: var(--surface);
}

.modal-header h3 {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: var(--text);
}

.close-button {
  background: none;
  border: none;
  padding: 4px;
  cursor: pointer;
  border-radius: 6px;
  color: var(--sub);
  transition: all 0.2s ease;
}

.close-button:hover {
  background: var(--surface-hover);
  color: var(--text);
}

/* 统一图标颜色 */
.status-button svg,
.close-button svg {
  color: var(--accent);
  transition: color 0.2s ease;
}

.status-button:hover svg,
.close-button:hover svg {
  color: var(--text);
}

.modal-content {
  padding: 20px;
  max-height: 75vh;
  overflow-y: auto;
}

.status-item {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  padding: 12px 0;
  border-bottom: 1px solid var(--border);
}

.status-item:last-child {
  border-bottom: none;
}

.status-label {
  font-size: 14px;
  font-weight: 500;
  color: var(--text);
  min-width: 80px;
}

/* 监测数据推送控制样式 */
.monitoring-control {
  flex-direction: column;
  align-items: flex-start;
  gap: 8px;
}

.monitoring-control-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 100%;
  gap: 12px;
}

.monitoring-buttons {
  display: flex;
  gap: 8px;
  align-items: center;
}

.monitoring-status {
  display: flex;
  align-items: center;
  gap: 8px;
}

.status-indicator {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--sub);
  transition: all 0.3s ease;
}

.status-indicator.active {
  background: var(--accent);
  box-shadow: 0 0 8px rgba(var(--accent-rgb), 0.4);
}

.status-text {
  font-size: 13px;
  color: var(--text);
  font-weight: 500;
}

.monitoring-toggle-btn {
  padding: 6px 12px;
  border: 1px solid var(--border);
  border-radius: 6px;
  background: var(--surface);
  color: var(--text);
  font-size: 12px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  min-width: 80px;
}

.monitoring-toggle-btn:hover {
  background: var(--surface-hover);
  border-color: var(--accent);
}

.monitoring-toggle-btn.active {
  background: var(--accent);
  color: white;
  border-color: var(--accent);
}

.monitoring-toggle-btn.active:hover {
  background: var(--accent-hover);
}

.test-anomaly-btn {
  padding: 8px 16px;
  border: 1px solid var(--border);
  border-radius: 8px;
  background: var(--surface);
  color: var(--text);
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  min-width: 100px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.test-anomaly-btn:hover:not(:disabled) {
  background: var(--surface-hover);
  border-color: var(--accent);
  color: var(--accent);
  transform: translateY(-1px);
}

.test-anomaly-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  background: var(--surface);
  color: var(--sub);
  transform: none;
}

.monitoring-description {
  font-size: 12px;
  color: var(--sub);
  line-height: 1.4;
  margin-top: 4px;
}

.status-value {
  font-size: 14px;
  color: var(--sub);
  text-align: right;
  flex: 1;
}

.doc-count {
  color: var(--accent);
  font-weight: 500;
}


.loading-status {
  text-align: center;
  color: var(--sub);
  font-size: 14px;
  padding: 20px;
}

/* 工具记录弹窗样式 */
.tool-records-modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  backdrop-filter: blur(4px);
}

.tool-records-modal {
  background: var(--panel);
  border: 1px solid var(--border);
  border-radius: 12px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
  max-width: 60vw;
  width: 85%;
  max-height: 85vh;
  overflow: hidden;
  animation: modalSlideIn 0.3s ease-out;
}

.tool-records-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 0;
  border-bottom: 1px solid var(--border);
}

.record-count {
  font-size: 14px;
  color: var(--text);
  font-weight: 500;
}

.clear-records-button {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 6px;
  padding: 6px 12px;
  font-size: 12px;
  color: var(--text);
  cursor: pointer;
  transition: all 0.2s ease;
}

.clear-records-button:hover {
  background: var(--surface-hover);
  border-color: var(--accent);
}

/* 使用与FeatureQueryPanel相同的表格样式 */
.tool-records-info {
  background: var(--panel);
  border: 1px solid var(--border);
  border-radius: 12px;
  overflow: hidden;
  box-shadow: var(--glow);
}

.records-header {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 12px;
  padding: 12px 16px;
  background: var(--surface);
  border-bottom: 1px solid var(--border);
  font-size: 12px;
  font-weight: 600;
  color: var(--text);
}

.records-list {
  max-height: 55vh;
  overflow-y: auto;
}

.record-item {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 12px;
  padding: 10px 16px;
  border-bottom: 1px solid var(--divider);
  font-size: 12px;
  background: var(--panel);
  transition: none !important;
}

.record-item:hover {
  background: var(--surface-hover);
}

.record-item:last-child {
  border-bottom: none;
}

.record-tool-name {
  font-weight: 500;
  color: var(--text);
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
}

.record-status {
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 11px;
  font-weight: 500;
  text-align: center;
  min-width: 60px;
}

.status-completed {
  background: var(--field-type-text-bg);
  color: var(--field-type-text-color);
}

.status-executing {
  background: var(--field-type-number-bg);
  color: var(--field-type-number-color);
}

.no-records {
  text-align: center;
  color: var(--sub);
  font-size: 14px;
  padding: 40px 20px;
}

/* 滚动条样式 */
.records-list::-webkit-scrollbar {
  width: 3px;
}

.records-list::-webkit-scrollbar-track {
  background: var(--scrollbar-track, rgba(200, 200, 200, 0.1));
  border-radius: 1.5px;
}

.records-list::-webkit-scrollbar-thumb {
  background: var(--scrollbar-thumb, rgba(150, 150, 150, 0.3));
  border-radius: 1.5px;
}

.records-list::-webkit-scrollbar-thumb:hover {
  background: var(--scrollbar-thumb-hover, rgba(150, 150, 150, 0.5));
}

/* 工具调用提示样式 */
.tool-call-banner {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
  padding: 8px 10px;
  border-bottom: 1px dashed var(--border);
  background: var(--surface);
}
.tool-call-left {
  display: flex;
  align-items: center;
  gap: 8px;
  color: var(--text);
}
.tool-meta {
  display: flex;
  flex-direction: column;
  gap: 2px;
}
.tool-name {
  font-size: 12px;
  font-weight: 600;
  color: var(--text);
}
.tool-args,
.tool-result {
  font-size: 12px;
  color: var(--sub);
  word-break: break-all;
}


.history-button,
.new-chat-button,
.status-button,
.tool-records-button {
  display: flex !important;
  align-items: center !important;
  gap: 6px !important;
  padding: 4px 10px !important;
  width: auto !important;
  height: auto !important;
  box-shadow: none !important;
  backdrop-filter: none !important;
  background: var(--surface) !important;
  border: 1px solid var(--border) !important;
  border-radius: 12px !important;
  transition: all 0.2s ease !important;
  animation: none !important;
}

.history-button:hover,
.new-chat-button:hover,
.status-button:hover,
.tool-records-button:hover {
  transform: none !important;
  box-shadow: none !important;
  background: var(--surface-hover) !important;
  border-color: var(--accent) !important;
}

.history-button:active,
.new-chat-button:active,
.status-button:active,
.tool-records-button:active {
  transform: translateY(0) !important;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.15) !important;
}

.history-button .button-text,
.new-chat-button .button-text,
.status-button .button-text,
.tool-records-button .button-text {
  font-size: 12px !important;
  font-weight: 500 !important;
  color: var(--text) !important;
  margin-left: 2px !important;
  white-space: nowrap !important;
}

.history-button svg,
.new-chat-button svg,
.status-button svg,
.tool-records-button svg {
  flex-shrink: 0 !important;
  width: 14px !important;
  height: 14px !important;
  color: var(--text) !important;
  stroke-width: 2 !important;
}




/* 保留fadeIn动画定义但不使用 */
@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.chat-message {
  margin-bottom: 16px;
  padding: 12px;
  border-radius: 8px;
  /* 禁用动画，防止主题切换闪烁 */
  animation: none !important;
}

.user-message {
  background: var(--surface);
  color: var(--text);
  border: 1px solid var(--border);
  margin-left: 20%;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  /* 禁用动画，防止主题切换闪烁 */
  animation: none !important;
}

.assistant-message {
  background: var(--surface);
  border: 1px solid var(--border);
  margin-right: 20%;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  /* 禁用动画，防止主题切换闪烁 */
  animation: none !important;
}


</style>

