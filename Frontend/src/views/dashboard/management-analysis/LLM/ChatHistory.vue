<template>
  <!-- 聊天历史弹窗 -->
  <div v-if="visible" class="chat-history-modal-overlay" @click="closeModal">
    <div class="chat-history-modal" @click.stop>
      <div class="modal-header">
        <h3>聊天历史记录</h3>
        <button class="close-button" @click="closeModal">
          <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M18 6L6 18M6 6l12 12"/>
          </svg>
        </button>
      </div>
      <div class="modal-content">
        <div class="chat-history-header">
          <span class="record-count">共 {{ chatHistory.length }} 条记录</span>
          <button class="clear-records-button" @click="clearAllHistory" v-if="chatHistory.length > 0">
            清空记录
          </button>
        </div>
        
        <!-- 加载状态 -->
        <div v-if="isLoading" class="loading-container">
          <div class="loading-spinner"></div>
          <p>加载中...</p>
        </div>

        <!-- 空状态 -->
        <div v-else-if="chatHistory.length === 0" class="no-records">
          暂无历史聊天记录
        </div>

        <!-- 聊天记录列表 -->
        <div v-else class="chat-records-list">
          <div 
            v-for="(record, index) in sortedHistory" 
            :key="record.id"
            class="chat-record-item"
            :class="{ 'active': selectedRecordId === record.id }"
            @click="selectRecord(record.id)"
          >
            <div class="record-header">
              <div class="record-time">{{ formatDate(record.timestamp) }}</div>
              <div class="record-tool-name">第{{ sortedHistory.length - index }}次对话</div>
            </div>
            <div class="record-details">
              <div class="record-message-count">
                <strong>消息数量：</strong>{{ record.messages ? record.messages.length : 0 }}条
              </div>
              <div class="record-operations">
                <button class="record-action-btn" @click.stop="toggleRecord(record.id)" title="切换到该对话">
                  切换对话
                </button>
                <button class="record-action-btn danger" @click.stop="deleteRecord(record.id)" title="删除该记录">
                  删除
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
  
  <!-- 确认对话框 -->
  <ConfirmDialog
    :visible="confirmDialogVisible"
    :title="confirmDialogConfig.title"
    :message="confirmDialogConfig.message"
    confirm-text="确定"
    cancel-text="取消"
    @confirm="handleConfirmDialog"
    @cancel="handleCancelDialog"
    @close="handleCancelDialog"
  />
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import ConfirmDialog from '@/components/UI/ConfirmDialog.vue'
import { useModeStateStore } from '@/stores/modeStateStore'

// Props
const props = defineProps<{
  visible: boolean
}>()

// Emits
const emit = defineEmits<{
  close: []
}>()

const router = useRouter()
const modeStateStore = useModeStateStore()

// 响应式数据
const chatHistory = ref<any[]>([])
const selectedRecordId = ref<string | null>(null)
const isLoading = ref(false)

// 确认对话框状态
const confirmDialogVisible = ref(false)
const confirmDialogConfig = ref({
  title: '',
  message: '',
  action: '',
  recordId: ''
})

// 计算属性
const sortedHistory = computed(() => {
  return chatHistory.value
    .sort((a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime())
})

// 方法
const loadChatHistory = () => {
  isLoading.value = true
  try {
    const savedChatHistory = localStorage.getItem('chatHistory') || '[]'
    chatHistory.value = JSON.parse(savedChatHistory)
  } catch (error) {
    console.error('加载聊天历史失败:', error)
    chatHistory.value = []
  } finally {
    isLoading.value = false
  }
}

const refreshHistory = () => {
  loadChatHistory()
}

const clearAllHistory = () => {
  confirmDialogConfig.value = {
    title: '清空历史记录',
    message: '确定要清空所有聊天历史记录吗？此操作不可恢复。',
    action: 'clearAll',
    recordId: ''
  }
  confirmDialogVisible.value = true
}

const selectRecord = (recordId: string) => {
  selectedRecordId.value = recordId
}

const toggleRecord = (recordId: string) => {
  const record = chatHistory.value.find(r => r.id === recordId)
  if (!record) return

  // 将所选历史对话写入 LLM 模式状态
  const historyMessages = Array.isArray(record.messages) ? record.messages : []
  modeStateStore.saveLLMState({
    messages: historyMessages,
    inputText: '',
    scrollPosition: 0
  })

  // 发送自定义事件通知ChatAssistant组件状态已更新
  window.dispatchEvent(new CustomEvent('chatHistoryRestored', {
    detail: {
      messages: historyMessages,
      recordId: recordId
    }
  }))

  // 提示已切换
  window.dispatchEvent(new CustomEvent('showNotification', {
    detail: {
      title: '已切换对话',
      message: '已加载所选历史对话',
      type: 'success',
      duration: 2000
    }
  }))

  // 关闭弹窗
  closeModal()
}

const deleteRecord = (recordId: string) => {
  confirmDialogConfig.value = {
    title: '删除记录',
    message: '确定要删除这条聊天记录吗？',
    action: 'delete',
    recordId: recordId
  }
  confirmDialogVisible.value = true
}

const handleConfirmDialog = () => {
  const { action, recordId } = confirmDialogConfig.value
  
  if (action === 'clearAll') {
    localStorage.removeItem('chatHistory')
    chatHistory.value = []
    selectedRecordId.value = null
    
    // 显示通知
    window.dispatchEvent(new CustomEvent('showNotification', {
      detail: {
        title: '清空成功',
        message: '所有聊天历史记录已清空',
        type: 'success',
        duration: 3000
      }
    }))
  } else if (action === 'delete') {
    const index = chatHistory.value.findIndex(r => r.id === recordId)
    if (index !== -1) {
      chatHistory.value.splice(index, 1)
      localStorage.setItem('chatHistory', JSON.stringify(chatHistory.value))
      
      if (selectedRecordId.value === recordId) {
        selectedRecordId.value = null
      }
      
      // 显示通知
      window.dispatchEvent(new CustomEvent('showNotification', {
        detail: {
          title: '删除成功',
          message: '聊天记录已删除',
          type: 'success',
          duration: 3000
        }
      }))
    }
  }
  
  confirmDialogVisible.value = false
}

const handleCancelDialog = () => {
  confirmDialogVisible.value = false
}

const formatDate = (timestamp: string) => {
  return new Date(timestamp).toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const closeModal = () => {
  emit('close')
}



// 生命周期
onMounted(() => {
  loadChatHistory()
})
</script>

<style scoped>
/* 聊天历史弹窗样式 */
.chat-history-modal-overlay {
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

.chat-history-modal {
  background: var(--panel);
  border: 1px solid var(--border);
  border-radius: 12px;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.16);
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
  padding: 12px 16px;
  border-bottom: 1px solid var(--border);
  background: var(--surface);
}

.modal-header h3 {
  margin: 0;
  font-size: 13px;
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

.close-button svg {
  color: var(--accent);
  transition: color 0.2s ease;
}

.close-button:hover svg {
  color: var(--text);
}

.modal-content {
  padding: 12px;
  max-height: 60vh;
  overflow-y: auto;
}

.chat-history-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 0;
  border-bottom: 1px solid var(--border);
}

.record-count {
  font-size: 12px;
  color: var(--text);
  font-weight: 500;
}

.clear-records-button {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 6px;
  padding: 6px 8px;
  font-size: 12px;
  color: var(--text);
  cursor: pointer;
  transition: all 0.2s ease;
  min-height: 32px;
}

.clear-records-button:hover {
  background: var(--surface-hover);
  border-color: var(--accent);
}

.chat-records-list {
  max-height: 50vh;
  overflow-y: auto;
  padding: 8px 0;
}

.chat-record-item {
  border: 1px solid var(--border);
  border-radius: 8px;
  margin-bottom: 10px;
  padding: 10px;
  background: var(--surface);
  transition: all 0.2s ease;
  cursor: pointer;
}

.chat-record-item:hover {
  border-color: var(--accent);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.chat-record-item.active {
  border-color: var(--accent);
  background: var(--accent);
  color: white;
}

.record-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 6px;
  padding-bottom: 6px;
  border-bottom: 1px solid var(--border);
}

.chat-record-item.active .record-header {
  border-bottom-color: rgba(255, 255, 255, 0.3);
}

.record-time {
  font-size: 12px;
  color: var(--sub);
}

.chat-record-item.active .record-time {
  color: rgba(255, 255, 255, 0.9);
}

.record-tool-name {
  font-size: 13px;
  font-weight: 600;
  color: var(--accent);
}

.chat-record-item.active .record-tool-name {
  color: white;
}

.record-details {
  font-size: 12px;
  color: var(--text);
}

.chat-record-item.active .record-details {
  color: white;
}

.record-message-count {
  margin-bottom: 8px;
}

.record-message-count strong {
  color: var(--text);
  font-weight: 600;
}

.chat-record-item.active .record-message-count strong {
  color: white;
}

.record-operations {
  display: flex;
  gap: 8px;
  margin-top: 8px;
}

.record-action-btn {
  background: var(--btn-secondary-bg);
  border: 1px solid var(--border);
  border-radius: 6px;
  padding: 6px 8px;
  font-size: 12px;
  color: var(--text);
  cursor: pointer;
  transition: all 0.2s ease;
  min-height: 32px;
}

.record-action-btn:hover {
  background: var(--surface-hover);
  border-color: var(--accent);
}

.record-action-btn.danger {
  background: var(--btn-danger-bg);
  color: var(--btn-danger-color);
  border-color: var(--btn-danger-bg);
}

.record-action-btn.danger:hover {
  background: var(--btn-danger-hover-bg);
  border-color: var(--btn-danger-hover-bg);
  color: var(--btn-danger-hover-color);
}

.chat-record-item.active .record-action-btn {
  background: rgba(255, 255, 255, 0.2);
  border-color: rgba(255, 255, 255, 0.3);
  color: white;
}

.chat-record-item.active .record-action-btn:hover {
  background: rgba(255, 255, 255, 0.3);
}

.chat-record-item.active .record-action-btn.danger {
  background: rgba(255, 107, 107, 0.8);
  border-color: rgba(255, 107, 107, 0.8);
}

.chat-record-item.active .record-action-btn.danger:hover {
  background: rgba(255, 107, 107, 1);
}

/* 加载状态样式 */
.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px 20px;
  color: var(--sub);
}

.loading-spinner {
  width: 32px;
  height: 32px;
  border: 3px solid var(--border);
  border-top: 3px solid var(--accent);
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 16px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* 空状态样式 */
.no-records {
  text-align: center;
  color: var(--sub);
  font-size: 12px;
  padding: 40px 20px;
}

/* 滚动条样式 */
.chat-records-list::-webkit-scrollbar {
  width: 3px;
}

.chat-records-list::-webkit-scrollbar-track {
  background: var(--scrollbar-track, rgba(200, 200, 200, 0.1));
  border-radius: 1.5px;
}

.chat-records-list::-webkit-scrollbar-thumb {
  background: var(--scrollbar-thumb, rgba(150, 150, 150, 0.3));
  border-radius: 1.5px;
}

.chat-records-list::-webkit-scrollbar-thumb:hover {
  background: var(--scrollbar-thumb-hover, rgba(150, 150, 150, 0.5));
}

.modal-content::-webkit-scrollbar {
  width: 3px;
}

.modal-content::-webkit-scrollbar-track {
  background: var(--scrollbar-track, rgba(200, 200, 200, 0.1));
  border-radius: 1.5px;
}

.modal-content::-webkit-scrollbar-thumb {
  background: var(--scrollbar-thumb, rgba(150, 150, 150, 0.3));
  border-radius: 1.5px;
}

.modal-content::-webkit-scrollbar-thumb:hover {
  background: var(--scrollbar-thumb-hover, rgba(150, 150, 150, 0.5));
}
</style>
