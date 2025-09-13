<template>
  <div class="notification-manager">
    <TransitionGroup name="toast" tag="div" class="notification-container">
      <NotificationToast
        v-for="notification in notifications"
        :key="notification.id"
        :title="notification.title"
        :message="notification.message"
        :type="notification.type"
        :duration="notification.duration"
        @close="removeNotification(notification.id)"
      />
    </TransitionGroup>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import NotificationToast from './NotificationToast.vue'

interface Notification {
  id: string
  title: string
  message?: string
  type: 'success' | 'error' | 'info' | 'warning'
  duration?: number
}

const notifications = ref<Notification[]>([])

const addNotification = (notification: Omit<Notification, 'id'>) => {
  // 清除所有现有通知
  notifications.value = []
  
  const id = Date.now().toString() + Math.random().toString(36).substr(2, 9)
  notifications.value.push({
    ...notification,
    id
  })
}

const removeNotification = (id: string) => {
  const index = notifications.value.findIndex(n => n.id === id)
  if (index > -1) {
    notifications.value.splice(index, 1)
  }
}

// 处理系统阈值警告事件
const handleThresholdAlert = (event: CustomEvent) => {
  const { type, title, message } = event.detail
  
  addNotification({
    title,
    message,
    type: type || 'warning',
    duration: 8000 // 阈值警告显示8秒
  })
}

onMounted(() => {
  // 监听系统阈值警告事件
  window.addEventListener('system:thresholdAlert', handleThresholdAlert as unknown as EventListener)
})

onUnmounted(() => {
  // 清理事件监听器
  window.removeEventListener('system:thresholdAlert', handleThresholdAlert as unknown as EventListener)
})

// 暴露方法给全局使用
defineExpose({
  addNotification,
  removeNotification
})
</script>

<style scoped>
.notification-manager {
  position: fixed;
  bottom: 24px;
  left: 24px;
  z-index: 9999;
  pointer-events: none;
}

.notification-container {
  display: flex;
  flex-direction: column;
  gap: 12px;
  pointer-events: auto;
}

/* 动画效果 */
.toast-enter-active,
.toast-leave-active {
   
}

.toast-enter-from {
  opacity: 0;
  transform: translateY(100%);
}

.toast-leave-to {
  opacity: 0;
  transform: translateY(100%);
}

.toast-move {
  transition: transform 0.3s ease;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .notification-manager {
    bottom: 16px;
    left: 16px;
    right: 16px;
  }
  
  .notification-container {
    gap: 8px;
  }
}
</style>
