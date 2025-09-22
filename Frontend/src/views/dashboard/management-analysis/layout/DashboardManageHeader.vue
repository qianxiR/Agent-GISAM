<template>
  <div class="screen-header">
    <div class="header-left">
      <img 
        src="/logoContent.png" 
        alt="Logo" 
        class="header-logo" 
      />
      <div class="screen-title">基于EDA-Agent的多模态实时态势感知地理空间智能决策分析平台</div>
    </div>
    
          <div class="header-right">
        <ButtonGroup
          :buttons="modeButtons"
          :active-button="activeMode"
          @select="setMode"
        />
        
        <div class="right-controls">
          <!-- 地球按钮 -->
          <div class="earth-toggle">
            <button 
              class="earth-logo" 
              @click="goToView"
              title="切换到可视化平台页面"
            >
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <circle cx="12" cy="12" r="10"/>
                <path d="M2 12h20"/>
                <path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"/>
              </svg>
            </button>
          </div>
          
          <div class="theme-toggle">
            <IconButton 
              @click="toggleTheme" 
              :title="theme === 'light' ? '切换到暗色主题' : '切换到浅色主题'"
            >
              <!-- 浅色主题图标 (太阳) -->
              <svg v-if="theme === 'light'" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <circle cx="12" cy="12" r="5"/>
                <path d="M12 1v2M12 21v2M4.22 4.22l1.42 1.42M18.36 18.36l1.42 1.42M1 12h2M21 12h2M4.22 19.78l1.42-1.42M18.36 5.64l1.42-1.42"/>
              </svg>
              <!-- 暗色主题图标 (月亮) -->
              <svg v-else viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/>
              </svg>
            </IconButton>
          </div>
          
        </div>
      </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed, watch } from 'vue'
import { storeToRefs } from 'pinia'
import { useRouter } from 'vue-router'
import ButtonGroup from '@/components/UI/ButtonGroup.vue'
import IconButton from '@/components/UI/IconButton.vue'
import { useThemeStore } from '@/stores/themeStore'
import { useModeStateStore } from '@/stores/modeStateStore'

// 主题管理
const themeStore = useThemeStore()
const { theme } = storeToRefs(themeStore)
const { toggleTheme, applySystemTheme, setupSystemThemeListener } = themeStore

// 路由管理
const router = useRouter()

// 模式状态管理
const modeStateStore = useModeStateStore()

// 模态框管理
import { useGlobalModalStore } from '@/stores/modalStore'
const globalModal = useGlobalModalStore()

const goToView = () => {
  router.push('/dashboard/view/home').then(() => {
    // 路由切换后刷新页面
    window.location.reload()
  })
}


// 模式管理 - 集成状态管理
const activeMode = computed(() => {
  return modeStateStore.currentMode
})

const modeButtons = [
  { id: 'llm', text: '对话模式' },
  { id: 'traditional', text: '手动模式' },
];

const setMode = (modeId: 'traditional' | 'llm') => {
  // 使用状态管理进行模式切换
  modeStateStore.switchMode(modeId)
  
  // 路由导航到对应模式
  if (modeId === 'traditional') {
    // 获取传统模式的当前工具状态
    const traditionalState = modeStateStore.getTraditionalState()
    const toolPathMap: { [key: string]: string } = {
      'layer': 'layer',
      'query': 'attribute-selection',
      'bianji': 'area-selection',
      'buffer': 'buffer',
      'distance': 'distance',
      'intersect': 'intersect',
      'erase': 'erase',
      'upload': 'upload'
    }
    const path = toolPathMap[traditionalState.activeTool] || 'layer'
    router.push(`/dashboard/management-analysis/traditional/${path}`)
  } else {
    router.push('/dashboard/management-analysis/llm')
  }
};

// 初始化主题和模式状态
onMounted(() => {
  applySystemTheme()
  setupSystemThemeListener()
  
  // 确保模式状态与当前路由同步
  const currentPath = router.currentRoute.value.path
  if (currentPath.includes('/dashboard/management-analysis/llm')) {
    if (modeStateStore.currentMode !== 'llm') {
      modeStateStore.switchMode('llm')
    }
  } else if (currentPath.includes('/dashboard/management-analysis/traditional')) {
    if (modeStateStore.currentMode !== 'traditional') {
      modeStateStore.switchMode('traditional')
    }
  }

  setTimeout(() => {
    void Promise.all([
      import('@/views/dashboard/management-analysis/traditional/TraditionalMode.vue'),
      import('@/views/dashboard/management-analysis/traditional/tools/LayerManager.vue'),
      import('@/views/dashboard/management-analysis/traditional/tools/FeatureQueryPanel.vue'),
      import('@/views/dashboard/management-analysis/traditional/tools/AreaSelectionTools.vue'),
      import('@/views/dashboard/management-analysis/traditional/tools/BufferAnalysisPanel.vue'),
      import('@/views/dashboard/management-analysis/traditional/tools/ShortestPathAnalysisPanel.vue'),
      import('@/views/dashboard/management-analysis/traditional/tools/DataUploadPanel.vue'),
      import('ol')
    ]).catch(() => {})
  }, 0)
})

// 监听路由变化，同步模式状态
watch(() => router.currentRoute.value.path, (newPath: string) => {
  if (newPath.includes('/dashboard/management-analysis/llm')) {
    if (modeStateStore.currentMode !== 'llm') {
      modeStateStore.switchMode('llm')
    }
  } else if (newPath.includes('/dashboard/management-analysis/traditional')) {
    if (modeStateStore.currentMode !== 'traditional') {
      modeStateStore.switchMode('traditional')
    }
  }
})

</script>

<style scoped>
.screen-header {
  height: clamp(48px, 6vh, 64px);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 clamp(12px, 2vw, 24px);
  letter-spacing: 0.5px;
  background: var(--panel);
  border-bottom: 1px solid var(--border);
  box-shadow: var(--glow);
}

.header-left {
  flex: 1;
}

.screen-title {
  font-size: clamp(16px, 1.6vw, 20px);
  font-weight: 700;
  color: var(--accent);
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
  font-family: "Segoe UI", PingFang SC, Microsoft YaHei, Arial, sans-serif;
  transition: color 0.2s ease;
}

.header-left {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: flex-start;
  gap: 12px;
}

.header-logo {
  height: 32px;
  width: auto;
  object-fit: contain;
  flex-shrink: 0;
  border-radius: 4px;
  padding: 2px;
}

.earth-toggle {
  display: flex;
  align-items: center;
}

.earth-logo {
  width: 36px;
  height: 36px;
  border: none;
  background: transparent;
  color: var(--text);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 8px;
  transition: all 0.2s ease;
  flex-shrink: 0;
  padding: 0;
}

.earth-logo:hover {
  background: var(--surface-hover, var(--btn-secondary-bg));
  transform: translateY(-1px);
  box-shadow: var(--glow);
}

.earth-logo:active {
  transform: translateY(0);
}

.earth-logo svg {
  width: 18px;
  height: 18px;
  stroke: currentColor;
  fill: none;
  stroke-width: 2;
}


.header-right {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 16px;
}

.right-controls {
  display: flex;
  align-items: center;
  gap: 12px;
  padding-left: 16px;
  border-left: 1px solid var(--border);
}

.theme-toggle {
  display: flex;
  align-items: center;
}

.user-dropdown {
  position: relative;
}


.user-menu {
  position: absolute;
  top: 100%;
  right: 0;
  margin-top: 8px;
  background: var(--panel);
  border: 1px solid var(--border);
  border-radius: 12px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
  min-width: 240px;
  z-index: 2000;
  animation: slideDown 0.2s ease-out;
  overflow: hidden;
}

@keyframes slideDown {
  from {
    opacity: 0;
    transform: translateY(-8px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.user-info {
  padding: 16px;
  background: var(--surface);
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
}

.user-details {
  flex: 1;
}

.username {
  font-size: 16px;
  font-weight: 600;
  color: var(--text);
  margin-bottom: 4px;
  line-height: 1.2;
}

.user-email {
  font-size: 13px;
  color: var(--sub);
  line-height: 1.2;
}

.user-phone {
  font-size: 13px;
  color: var(--sub);
  line-height: 1.2;
}

.copy-btn {
  width: 28px;
  height: 28px;
  border: none;
  background: transparent;
  color: var(--sub);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 6px;
  transition: all 0.2s ease;
  flex-shrink: 0;
}

.copy-btn:hover {
  background: var(--surface-hover);
  color: var(--text);
}

.menu-divider {
  height: 1px;
  background: var(--border);
  margin: 0;
}

.menu-item {
  width: 100%;
  padding: 12px 16px;
  border: none;
  background: transparent;
  color: var(--text);
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 14px;
  transition: all 0.2s ease;
  text-align: left;
}

.menu-item:hover {
  background: var(--surface-hover);
}

.menu-item span {
  flex: 1;
}

.logout-item {
  color: var(--text);
}

.logout-item:hover {
  background: var(--surface-hover);
}

.menu-item svg {
  width: 16px;
  height: 16px;
  stroke: currentColor;
  flex-shrink: 0;
}

@media (max-width: 1200px) {
  .screen-header {
    padding: 0 16px;
  }
  
  .screen-title {
    font-size: 18px;
  }
}

@media (max-width: 768px) {
  .right-controls {
    gap: 8px;
    padding-left: 12px;
  }
  
  .user-menu {
    min-width: 200px;
  }
  
  .user-info {
    padding: 12px;
  }
  
  .username {
    font-size: 14px;
  }
  
  .user-email {
    font-size: 12px;
  }
  
  .menu-item {
    padding: 10px 12px;
    font-size: 13px;
  }
}
</style>
