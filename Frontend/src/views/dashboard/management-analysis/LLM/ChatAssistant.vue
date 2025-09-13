<template>
  <div class="chat-assistant">
    <!-- 顶部头部区域：为按钮预留高度，避免遮挡内容 -->
    <div class="chat-header">
      <!-- 新对话按钮 -->
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
      

            <!-- 服务状态按钮 -->
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

      
      <!-- 历史记录按钮 -->
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
    
      
      <!-- 工具记录按钮 -->
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
    
    <!-- API状态弹窗 -->
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
          <div class="status-item">
            <div class="status-label">服务状态</div>
            <div class="status-value">{{ apiStatus.service }}</div>
          </div>
          <div class="status-item" v-if="apiStatus.rag_system_status">
            <div class="status-label">RAG系统</div>
            <div class="status-value">
              {{ getRAGStatusText(apiStatus.rag_system_status) }}
              <span v-if="apiStatus.rag_details?.document_count" class="doc-count">
                ({{ apiStatus.rag_details.document_count }}个文档)
              </span>
            </div>
          </div>
          <div class="status-item" v-if="apiStatus.tools_count">
            <div class="status-label">可用工具</div>
            <div class="status-value">{{ apiStatus.tools_count }}个</div>
          </div>
          <div class="status-item" v-if="apiStatus.version">
            <div class="status-label">版本</div>
            <div class="status-value">v{{ apiStatus.version }}</div>
          </div>
          <div class="status-item">
            <div class="status-label">功能特性</div>
            <div class="status-features">
              <div class="feature-tag primary">GIS工具箱</div>
              <div class="feature-tag secondary">知识库系统</div>
              <div class="feature-tag accent">空间分析</div>
              <div class="feature-tag info">智能对话</div>
            </div>
          </div>
        </div>
        <div class="modal-content" v-else>
          <div class="loading-status">正在获取服务状态...</div>
        </div>
      </div>
    </div>

    <!-- 工具记录弹窗 -->
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
          <div class="tool-records-header">
            <span class="record-count">共 {{ toolRecords.length }} 条记录</span>
            <button class="clear-records-button" @click="clearToolRecords" v-if="toolRecords.length > 0">
              清空记录
            </button>
          </div>
        <div class="tool-records-info">
          <div class="records-header">
            <span class="record-tool-name">工具名称</span>
            <span class="record-status">状态</span>
          </div>
          <div class="records-list">
            <div v-for="(record, index) in toolRecords" :key="index" class="record-item">
              <span class="record-tool-name">{{ record.name }}</span>
              <span class="record-status" :class="getStatusClass(record.resultStr)">
                {{ getStatusText(record.resultStr) }}
              </span>
            </div>
            <div v-if="toolRecords.length === 0" class="no-records">
              暂无工具调用记录
            </div>
          </div>
        </div>
        </div>
      </div>
    </div>

    <!-- 聊天历史弹窗 -->
    <ChatHistory
      :visible="showChatHistory"
      @close="showChatHistory = false"
    />

    <!-- 工具调用提示区域（当AI调用了工具时显示） -->
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

    <!-- 聊天记录显示区域 -->
    <ChatMessagesPanel
      ref="messagesPanelRef"
      :messages="messages"
      :auto-scroll="true"
      :scroll-threshold="100"
    />
    
    <!-- 输入区域 -->
    <LLMInputWindow
      v-model="newMessage"
      placeholder="请输入您的需求..."
      :rows="3"
      :disabled="isLLMResponding"
      @send="sendMessage"
    />
  </div>
</template>//

<script setup lang="ts">
import { ref, watch, onMounted, nextTick, onUnmounted, computed } from 'vue';
import { useRouter } from 'vue-router';
import { useThemeStore } from '@/stores/themeStore';
import { useModeStateStore } from '@/stores/modeStateStore';
import { useMonitoringDataStore } from '@/stores/monitoringDataStore';
import LLMInputWindow from '@/components/Agent/LLMInputWindow.vue';
import ChatMessagesPanel from '@/components/Agent/ChatMessagesPanel.vue';
import SecondaryButton from '@/components/UI/SecondaryButton.vue';
import ChatHistory from './ChatHistory.vue';
import { getAgentApiBaseUrl, getLLMApiConfig } from '@/utils/config'
import { getEnvironmentalBackground, getUseCases } from '@/utils/domainBackground'

interface Message {
  id: number;
  text: string;
  sender: 'user' | 'system';
}

useThemeStore();
const modeStateStore = useModeStateStore();
const monitoringDataStore = useMonitoringDataStore();
const router = useRouter();

const props = defineProps<{
  mapReady: boolean;
}>();
const messages = ref<Message[]>([]);
const newMessage = ref('');
const hasAnnounced = ref(false);
const messagesPanelRef = ref<InstanceType<typeof ChatMessagesPanel> | null>(null);
const toolCallInfo = ref<{ name: string; argsStr: string; resultStr: string } | null>(null);
const nextAssistantOverride = ref<string | null>(null);
const currentTaskId = ref<string | null>(null);
const isLLMResponding = ref<boolean>(false);
const apiStatus = ref<any>(null);
const showApiStatus = ref<boolean>(false);
const showToolRecords = ref<boolean>(false);
const showChatHistory = ref<boolean>(false);
const toolRecords = ref<Array<{name: string, argsStr: string, resultStr: string, timestamp: number}>>([]);
let statusInterval: number | null = null;


// 智能滚动相关状态现在由ChatMessagesPanel组件内部处理

// API状态管理函数
const fetchApiStatus = async () => {
  try {
    const apiBase = getAgentApiBaseUrl()
    const resp = await fetch(`${apiBase}/health`)
    if (resp.ok) {
      const status = await resp.json()
      apiStatus.value = status
      console.log('[ChatAssistant] API状态更新:', status)
    }
  } catch (error) {
    console.error('获取API状态失败:', error)
    apiStatus.value = {
      status: 'error',
      service: 'Agent Service',
      error: '连接失败'
    }
  }
}

// RAG状态文本转换
const getRAGStatusText = (status: string) => {
  const statusMap: Record<string, string> = {
    'ready': '就绪',
    'not_initialized': '未初始化',
    'error': '错误',
    'unknown': '未知'
  }
  return statusMap[status] || status
}

// 切换API状态显示
const toggleApiStatus = () => {
  showApiStatus.value = !showApiStatus.value
  // 如果显示状态，立即获取最新状态
  if (showApiStatus.value) {
    fetchApiStatus()
  }
}

// 切换工具记录显示
const toggleToolRecords = () => {
  showToolRecords.value = !showToolRecords.value
  // 如果显示记录，从localStorage加载
  if (showToolRecords.value) {
    loadToolRecords()
  }
}

// 切换聊天历史显示
const toggleChatHistory = () => {
  showChatHistory.value = !showChatHistory.value
}

// 加载工具记录
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

// 保存工具记录
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

// 清空工具记录
const clearToolRecords = () => {
  toolRecords.value = []
  localStorage.removeItem('toolRecords')
}

// 格式化时间
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

// 获取状态文本
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

// 获取状态样式类
const getStatusClass = (resultStr: string) => {
  const status = getStatusText(resultStr)
  return {
    'status-completed': status === '已完成',
    'status-executing': status === '执行中'
  }
}

// 键盘事件处理
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

// 任务管理相关函数
const checkTaskStatus = async (taskId: string) => {
  try {
    const apiBase = getAgentApiBaseUrl()
    const resp = await fetch(`${apiBase}/agent/task/${taskId}/status`)
    if (resp.ok) {
      const taskStatus = await resp.json()
      return taskStatus
    }
  } catch (error) {
    console.error('检查任务状态失败:', error)
  }
  return null
}




const maybeAnnounceInitiallayers = () => {
  // 显示初始欢迎语
  if (!hasAnnounced.value) {
    hasAnnounced.value = true;
    
    // 添加欢迎消息
    const welcomeMessage = "您好，我是您的武汉市长江水域与水资源监测管理的自主智能助手。我能够帮助您进行城市空间分析、水资源监测与综合管理、环境监测预警、数据可视化以及多源信息整合等工作。请告诉我您需要进行的具体任务或分析，我会为您提供支持。"
    
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

// 恢复历史对话的方法
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

// 监听历史记录恢复事件
const handleChatHistoryRestored = (event: CustomEvent) => {
  const { messages: historyMessages } = event.detail
  restoreHistoryMessages(historyMessages)
}

// 监听查询结果事件
const handleQueryResult = (event: CustomEvent) => {
  const { success, message, layerName, field, operator, value, count, error } = event.detail
  
  // 构造查询结果消息
  let resultMessage = ''
  if (success) {
    resultMessage = `查询完成：${message}`
  } else {
    resultMessage = `查询失败：${error || '未知错误'}`
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
}

// 监听保存结果事件
const handleSaveResult = (event: CustomEvent) => {
  const { success, message, layerName, count, error } = event.detail
  
  // 构造保存结果消息
  let resultMessage = ''
  if (success) {
    resultMessage = `保存完成：${message}`
  } else {
    resultMessage = `保存失败：${error || '未知错误'}`
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
}

// 监听导出结果事件
const handleExportResult = (event: CustomEvent) => {
  const { success, message, fileName, count, error } = event.detail
  
  // 构造导出结果消息
  let resultMessage = ''
  if (success) {
    resultMessage = `导出完成：${message}`
  } else {
    resultMessage = `导出失败：${error || '未知错误'}`
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
}

// 监听缓冲区分析结果事件
const handleBufferAnalysisResult = (event: CustomEvent) => {
  const { success, message, layerName, radius, unit, error } = event.detail
  
  // 构造缓冲区分析结果消息
  let resultMessage = ''
  if (success) {
    resultMessage = `缓冲区分析完成：${message}`
  } else {
    resultMessage = `缓冲区分析失败：${error || '未知错误'}`
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
  
  // 任务完成，重置状态
  currentTaskId.value = null
  isLLMResponding.value = false
  console.log('缓冲区分析完成，任务状态已重置')
  
  // 更新系统消息状态到Pinia（分析结果作为系统消息）
  const analysisResultMessage = { 
    id: Date.now(), 
    text: resultMessage, 
    sender: 'system' as const 
  }
  
  // 注意：不再发送隐式LLM请求，避免重复发送
}

// 监听相交分析结果事件
const handleIntersectionAnalysisResult = (event: CustomEvent) => {
  const { success, message, targetLayerName, maskLayerName, error } = event.detail
  
  // 构造相交分析结果消息
  let resultMessage = ''
  if (success) {
    resultMessage = `相交分析完成：${message}`
  } else {
    resultMessage = `相交分析失败：${error || '未知错误'}`
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
  
  // 任务完成，重置状态
  currentTaskId.value = null
  isLLMResponding.value = false
  console.log('相交分析完成，任务状态已重置')
  
  // 更新系统消息状态到Pinia（分析结果作为系统消息）
  const analysisResultMessage = { 
    id: Date.now(), 
    text: resultMessage, 
    sender: 'system' as const 
  }
  
  // 注意：不再发送隐式LLM请求，避免重复发送
}

// 监听擦除分析结果事件
const handleEraseAnalysisResult = (event: CustomEvent) => {
  const { success, message, targetLayerName, eraseLayerName, error } = event.detail
  
  // 构造擦除分析结果消息
  let resultMessage = ''
  if (success) {
    resultMessage = `擦除分析完成：${message}`
  } else {
    resultMessage = `擦除分析失败：${error || '未知错误'}`
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
  
  // 任务完成，重置状态
  currentTaskId.value = null
  isLLMResponding.value = false
  console.log('擦除分析完成，任务状态已重置')
  
  // 更新系统消息状态到Pinia（分析结果作为系统消息）
  const analysisResultMessage = { 
    id: Date.now(), 
    text: resultMessage, 
    sender: 'system' as const 
  }
  
  // 注意：不再发送隐式LLM请求，避免重复发送
}

// 监听最短路径分析结果事件
const handlePathAnalysisResult = (event: CustomEvent) => {
  const { success, message, startLayerName, endLayerName, error } = event.detail
  
  // 构造最短路径分析结果消息
  let resultMessage = ''
  if (success) {
    resultMessage = `最短路径分析完成：${message}`
  } else {
    resultMessage = `最短路径分析失败：${error || '未知错误'}`
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
  
  // 任务完成，重置状态
  currentTaskId.value = null
  isLLMResponding.value = false
  console.log('最短路径分析完成，任务状态已重置')
  
  // 更新系统消息状态到Pinia（分析结果作为系统消息）
  const analysisResultMessage = { 
    id: Date.now(), 
    text: resultMessage, 
    sender: 'system' as const 
  }
  
  // 注意：不再发送隐式LLM请求，避免重复发送
}

// 监听获取打开图层结果事件
const handleGetOpenLayersResult = (event: CustomEvent) => {
  const { success, message, layerCount, layers, layerNames, error } = event.detail
  
  // 构造图层查询结果消息
  let resultMessage = ''
  if (success) {
    resultMessage = `图层查询完成：${message}`
  } else {
    resultMessage = `图层查询失败：${error || '未知错误'}`
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

// 监听监测点选择事件
const handleMonitoringSiteSelected: (event: CustomEvent) => Promise<void> = async (event: CustomEvent) => {
  const { site, coordinates, layerName, timestamp } = event.detail
  
  console.log('[ChatAssistant] 监测点被选择:', {
    site: site.name,
    location: site.location,
    coordinates,
    layerName,
    timestamp
  })
  
  // 获取监测点的mock数据
  let mockDataInfo = ''
  try {
    const { getMonitoringSiteData } = await import('@/data/waterQualityMockData')
    const siteData = getMonitoringSiteData(site.name)
    
    if (siteData && siteData.data && siteData.data.length > 0) {
      const latestData = siteData.data[siteData.data.length - 1] // 获取最新数据
      mockDataInfo = `
最新水质数据：
- 水温：${latestData.water_temperature.toFixed(1)}°C
- pH值：${latestData.ph_value.toFixed(2)}
- 溶解氧：${latestData.dissolved_oxygen.toFixed(1)} mg/L
- 浊度：${latestData.turbidity.toFixed(1)} NTU
- 高锰酸盐指数：${latestData.permanganate_index.toFixed(1)} mg/L
- 氨氮：${latestData.ammonia_nitrogen.toFixed(3)} mg/L
- 总磷：${latestData.total_phosphorus.toFixed(3)} mg/L
- 总氮：${latestData.total_nitrogen.toFixed(2)} mg/L
- 叶绿素a：${latestData.chlorophyll_a.toFixed(3)} mg/L
- 藻类密度：${latestData.algae_density.toLocaleString()} 个/L
- 数据时间：${latestData.time}
- 数据点数：${siteData.data.length}个（60分钟历史数据）`
    }
  } catch (error) {
    console.warn('获取监测点mock数据失败:', error)
    mockDataInfo = '（无法获取详细水质数据）'
  }
  
  // 构造监测点选择消息
  const selectionMessage = `${site.location} (${site.name})，坐标：${coordinates[0].toFixed(4)}, ${coordinates[1].toFixed(4)}，图层：${layerName}，水质类别：${site.waterQualityClass}类${mockDataInfo}

请稍等，我将为您分析该结果并且给您相应的执行建议！`
  
  // 将选择消息添加到聊天记录中
  messages.value.push({ 
    id: Date.now(), 
    text: selectionMessage, 
    sender: 'system' 
  })
  
  // 滚动到底部显示新消息
  nextTick(() => {
    messagesPanelRef.value?.scrollToBottom()
  })
  
  // 立即发送消息到LLM，提供监测点上下文和详细数据
  const contextMessage = `用户选择了监测点：${site.location}，该监测点位于坐标(${coordinates[0].toFixed(4)}, ${coordinates[1].toFixed(4)})，水质类别为${site.waterQualityClass}类。${mockDataInfo}请根据这个监测点的水质数据提供专业的分析建议和改善建议。`
  
  // 立即发送，不延迟
  sendQuickMessageToLLM(contextMessage)
}

// 监听自动分析事件（模拟用户发送正常请求）
const handleAutoAnalysis = async (event: CustomEvent) => {
  const { siteName, layerName, violations, analysisRequest } = event.detail
  
  console.log('[ChatAssistant] 收到自动分析请求:', {
    siteName,
    layerName,
    violations: violations.length,
    analysisRequest
  })
  
  
  // 构造自动分析系统消息
  const autoAnalysisMessage = `🚨 自动分析触发：监测点 ${siteName} 水质参数超限，正在执行1000米缓冲区分析...`
  
  // 将自动分析系统消息添加到聊天记录中
  messages.value.push({ 
    id: Date.now(), 
    text: autoAnalysisMessage, 
    sender: 'system' 
  })
  
  // 模拟用户发送缓冲区分析请求
  if (analysisRequest) {
    // 将分析请求作为用户消息添加到聊天记录中
    messages.value.push({
      id: Date.now() + 1,
      text: analysisRequest,
      sender: 'user'
    })
    
    // 滚动到底部显示新消息
    nextTick(() => {
      messagesPanelRef.value?.scrollToBottom()
    })
    
    // 调用正常的发送消息流程（会自动获取最后一条用户消息）
    await sendMessage()
  }
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
  
  // 监听历史记录恢复事件
  window.addEventListener('chatHistoryRestored', handleChatHistoryRestored as EventListener)
  
  // 监听键盘事件
  window.addEventListener('keydown', handleKeydown)
  
  // 监听监测点选择事件 - 只注册一次
  if (!(window as any).__monitoringSiteSelectedListenerRegistered) {
    (window as any).__monitoringSiteSelectedListenerRegistered = true
    window.addEventListener('monitoring:siteSelected', handleMonitoringSiteSelected as unknown as EventListener)
  }
  
  // 监听自动分析事件 - 只注册一次
  if (!(window as any).__autoAnalysisListenerRegistered) {
    (window as any).__autoAnalysisListenerRegistered = true
    window.addEventListener('llm:autoAnalysis', handleAutoAnalysis as unknown as EventListener)
  }
  
  // 监听查询结果事件 - 只注册一次
  if (!(window as any).__queryResultListenerRegistered) {
    (window as any).__queryResultListenerRegistered = true
    window.addEventListener('agent:queryResult', handleQueryResult as EventListener)
    window.addEventListener('agent:saveResult', handleSaveResult as EventListener)
    window.addEventListener('agent:exportResult', handleExportResult as EventListener)
    window.addEventListener('agent:bufferAnalysisResult', handleBufferAnalysisResult as EventListener)
    window.addEventListener('agent:intersectionAnalysisResult', handleIntersectionAnalysisResult as EventListener)
    window.addEventListener('llm:analysisResultReceived', handleLLMAnalysisResultReceived as EventListener)
    window.addEventListener('llm:analysisResultError', handleLLMAnalysisResultError as EventListener)
    window.addEventListener('agent:eraseAnalysisResult', handleEraseAnalysisResult as EventListener)
    window.addEventListener('agent:pathAnalysisResult', handlePathAnalysisResult as EventListener)
    window.addEventListener('agent:getOpenLayersResult', handleGetOpenLayersResult as EventListener)
    // 新增：监听图层可见性变化事件
    window.addEventListener('agent:layerVisibilityChanged', ((e: any) => {
      const { layerName, visible } = e.detail || {}
      const msg = visible ? `打开图层：${layerName}` : `关闭图层：${layerName}`
      messages.value.push({ id: Date.now(), text: msg, sender: 'system' })
      nextTick(() => {
        messagesPanelRef.value?.scrollToBottom()
      })
      // 移除自动发送LLM请求，避免频繁API调用
    }) as EventListener)
  }
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
  
  // 清理事件监听器
  window.removeEventListener('chatHistoryRestored', handleChatHistoryRestored as EventListener)
  window.removeEventListener('keydown', handleKeydown)
  
  if ((window as any).__monitoringSiteSelectedListenerRegistered) {
    window.removeEventListener('monitoring:siteSelected', handleMonitoringSiteSelected as unknown as EventListener)
    ;(window as any).__monitoringSiteSelectedListenerRegistered = false
  }
  
  if ((window as any).__autoAnalysisListenerRegistered) {
    window.removeEventListener('llm:autoAnalysis', handleAutoAnalysis as unknown as EventListener)
    ;(window as any).__autoAnalysisListenerRegistered = false
  }
  
  if ((window as any).__queryResultListenerRegistered) {
    window.removeEventListener('agent:queryResult', handleQueryResult as EventListener)
    window.removeEventListener('agent:saveResult', handleSaveResult as EventListener)
    window.removeEventListener('agent:exportResult', handleExportResult as EventListener)
    window.removeEventListener('agent:bufferAnalysisResult', handleBufferAnalysisResult as EventListener)
    window.removeEventListener('agent:intersectionAnalysisResult', handleIntersectionAnalysisResult as EventListener)
    window.removeEventListener('agent:eraseAnalysisResult', handleEraseAnalysisResult as EventListener)
    window.removeEventListener('agent:pathAnalysisResult', handlePathAnalysisResult as EventListener)
    window.removeEventListener('agent:getOpenLayersResult', handleGetOpenLayersResult as EventListener)
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
const sendImplicitMessageToLLM = async (resultMessage: string, showResponse: boolean = true) => {
  try {
    const apiBase = getAgentApiBaseUrl()
    // 使用相同的会话ID
    const convId = sessionStorage.getItem('agent_conv_id') || (() => {
      const v = `conv-${Date.now()}`
      sessionStorage.setItem('agent_conv_id', v)
      return v
    })()
    
    // 构造包含历史记录的完整prompt
    let conversationContext = ''
    if (messages.value.length > 0) {
      conversationContext = '对话历史：\n'
      messages.value.forEach(msg => {
        const role = msg.sender === 'user' ? '用户' : '助手'
        conversationContext += `${role}: ${msg.text}\n`
      })
      conversationContext += '\n'
    }
    
    // 构造完整的prompt
    const fullPrompt = `${conversationContext}分析结果反馈：${resultMessage}。请根据这个结果给出适当的回应或建议。`
    
    const llm = getLLMApiConfig()
    const payload = {
      model: 'qwen-plus',
      temperature: typeof llm.temperature === 'number' ? llm.temperature : 0.7,
      prompt: fullPrompt,
      stream: false,
      conversation_id: convId
    }
    
    const resp = await fetch(`${apiBase}/agent/tool-chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(payload)
    })

    if (resp.ok) {
      const data = await resp.json()
      const content = data?.data?.final_answer || '[空响应]'
      
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
    } else {
      console.error('隐式LLM请求失败:', resp.status, await resp.text())
    }
  } catch (e: any) {
    console.error('隐式LLM请求异常:', e?.message || e)
  }
}

// 快速发送消息到LLM（不显示发送状态，直接发送）
const sendQuickMessageToLLM = async (resultMessage: string) => {
  // 设置LLM响应状态
  isLLMResponding.value = true
  
  try {
    const apiBase = getAgentApiBaseUrl()
    // 使用相同的会话ID
    const convId = sessionStorage.getItem('agent_conv_id') || (() => {
      const v = `conv-${Date.now()}`
      sessionStorage.setItem('agent_conv_id', v)
      return v
    })()
    
    // 构造包含历史记录的完整prompt
    let conversationContext = ''
    if (messages.value.length > 0) {
      conversationContext = '对话历史：\n'
      messages.value.forEach(msg => {
        const role = msg.sender === 'user' ? '用户' : '助手'
        conversationContext += `${role}: ${msg.text}\n`
      })
      conversationContext += '\n'
    }
    
    // 构造完整的prompt
    const fullPrompt = `${conversationContext}${resultMessage}`
    
    const llm = getLLMApiConfig()
    const payload = {
      model: 'qwen-plus',
      temperature: typeof llm.temperature === 'number' ? llm.temperature : 0.7,
      prompt: fullPrompt,
      stream: false,
      conversation_id: convId
    }
    
    const resp = await fetch(`${apiBase}/agent/tool-chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(payload)
    })

    if (resp.ok) {
      const data = await resp.json()
      const content = data?.data?.final_answer || '未得到结果。'
      
      // 直接添加AI回复到消息列表
      messages.value.push({
        id: Date.now() + 1,
        text: content,
        sender: 'system'
      })
      
      // 滚动到底部
      nextTick(() => {
        messagesPanelRef.value?.scrollToBottom()
      })
      
      // 保存状态
      saveLLMState()
      
      // 重置响应状态
      isLLMResponding.value = false
    } else {
      console.error('LLM API请求失败:', resp.status, resp.statusText)
      // 重置响应状态
      isLLMResponding.value = false
    }
  } catch (error) {
    console.error('快速发送消息到LLM失败:', error)
    // 重置响应状态
    isLLMResponding.value = false
  }
}

// 发送消息
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
  

  const apiBase = getAgentApiBaseUrl()
  // 使用路由路径+时间戳派生一个稳定会话ID（同页会话期间不变）
  const convId = sessionStorage.getItem('agent_conv_id') || (() => {
    const v = `conv-${Date.now()}`
    sessionStorage.setItem('agent_conv_id', v)
    return v
  })()
  
  const userMsg = { role: 'user', content: messageToSend }

  try {
    const llm = getLLMApiConfig()
    const payload = {
      model: 'qwen-plus',
      temperature: typeof llm.temperature === 'number' ? llm.temperature : 0.7,
      prompt: messageToSend,
      stream: false,
      conversation_id: convId
    }
    const resp = await fetch(`${apiBase}/agent/tool-chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(payload)
    })

    // 更新API状态
    if (resp.ok) {
      fetchApiStatus()
    }

    if (!resp.ok) {
      const errText = await resp.text()
      messages.value.push({ id: Date.now() + 1, text: `LLM请求失败(${resp.status}): ${errText}`, sender: 'system' })
      currentTaskId.value = null
      isLLMResponding.value = false
      // 重置消息监控状态
    } else {
      const data = await resp.json()
      
      // 保存任务ID
      if (data.task_id) {
        currentTaskId.value = data.task_id
        console.log('任务已创建:', data.task_id)
      }
      
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
        
        // 知识库工具调用不显示工具调用结果
        if (name === 'query_knowledge_base' || name === 'update_knowledge_base') {
          toolCallInfo.value = null
        } else {
          toolCallInfo.value = { name, argsStr, resultStr }
          // 保存工具调用记录
          saveToolRecord(name, argsStr, resultStr)
        }
        
        // 调试：打印AI实际调用的工具名称
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
        
        // 如果是导出查询结果为JSON的工具
        if (name === 'export_query_results_as_json') {
          try {
            const parsed = call?.args || {}
            const fileName = parsed.file_name || parsed.fileName
            
            if (fileName) {
              const ev = new CustomEvent('agent:exportQueryResultsAsJson', { 
                detail: { fileName } 
              })
              window.dispatchEvent(ev)
              console.log('[Agent] dispatched event: agent:exportQueryResultsAsJson', { fileName })
            }
          } catch (error) {
            console.error('[Agent] 处理导出查询结果工具调用时出错:', error)
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
        
        // 如果是导出相交分析结果为JSON的工具
        if (name === 'export_intersection_results_as_json') {
          try {
            const parsed = call?.args || {}
            const fileName = parsed.file_name || parsed.fileName
            
            if (fileName) {
              const ev = new CustomEvent('agent:exportIntersectionResultsAsJson', { 
                detail: { fileName } 
              })
              window.dispatchEvent(ev)
              console.log('[Agent] dispatched event: agent:exportIntersectionResultsAsJson', { fileName })
            }
          } catch (error) {
            console.error('[Agent] 处理导出相交分析结果工具调用时出错:', error)
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
        
        // 如果是导出缓冲区分析结果为JSON的工具
        if (name === 'export_buffer_results_as_json') {
          try {
            const parsed = call?.args || {}
            const fileName = parsed.file_name || parsed.fileName
            
            if (fileName) {
              const ev = new CustomEvent('agent:exportBufferResultsAsJson', { 
                detail: { fileName } 
              })
              window.dispatchEvent(ev)
              console.log('[Agent] dispatched event: agent:exportBufferResultsAsJson', { fileName })
            }
          } catch (error) {
            console.error('[Agent] 处理导出缓冲区分析结果工具调用时出错:', error)
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
        
        // 如果是导出擦除分析结果为JSON的工具
        if (name === 'export_erase_results_as_json') {
          try {
            const parsed = call?.args || {}
            const fileName = parsed.file_name || parsed.fileName
            
            if (fileName) {
              const ev = new CustomEvent('agent:exportEraseResultsAsJson', { 
                detail: { fileName } 
              })
              window.dispatchEvent(ev)
              console.log('[Agent] dispatched event: agent:exportEraseResultsAsJson', { fileName })
            }
          } catch (error) {
            console.error('[Agent] 处理导出擦除分析结果工具调用时出错:', error)
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
      } else {
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
    }
    
    // 注意：有工具调用时不在这里重置任务状态，让工具调用结果事件来重置
    // 没有工具调用时在上面已经重置了任务状态
  } catch (e: any) {
    messages.value.push({ id: Date.now() + 2, text: `LLM请求异常: ${e?.message || e}`, sender: 'system' })
    // 任务失败，重置状态
    currentTaskId.value = null
    isLLMResponding.value = false
    // 重置消息监控状态
  }

  newMessage.value = ''
}



// 新增：开启新对话功能
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
  max-width: 40vw;
  width: 90%;
  max-height: 70vh;
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
  max-height: 60vh;
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

.status-features {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  flex: 1;
  justify-content: flex-end;
}

.feature-tag {
  border-radius: 6px;
  padding: 6px 10px;
  font-size: 12px;
  font-weight: 500;
  border: 1px solid;
  transition: all 0.2s ease;
}

.feature-tag.primary,
.feature-tag.secondary,
.feature-tag.accent,
.feature-tag.info {
  background: var(--accent);
  color: white;
  border-color: var(--accent);
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
  max-width: 50vw;
  width: 80%;
  max-height: 70vh;
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
  max-height: 40vh;
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

