<template>
  <PanelContainer class="llm-panel">
    <div class="chat-container">
      <!-- 使用router-view渲染子路由 -->
      <router-view :map-ready="mapStore.isMapReady" />
    </div>
    
  </PanelContainer>
</template>

<script setup lang="ts">
import { onMounted, onUnmounted } from 'vue'
import { useMapStore } from '@/stores/mapStore'
import { useModeStateStore } from '@/stores/modeStateStore'
import { useMonitoringDataLayers } from '@/composables/useMonitoringDataLayers'
import { useYangtzeWaterLayers } from '@/composables/useYangtzeWaterLayers'
import { useMonitoringThreshold } from '@/composables/useMonitoringThreshold'
import PanelContainer from '@/components/UI/PanelContainer.vue'

const mapStore = useMapStore()
const modeStateStore = useModeStateStore()
const monitoringLayers = useMonitoringDataLayers()
const yangtzeLayers = useYangtzeWaterLayers()
const thresholdMonitoring = useMonitoringThreshold()

// 组件生命周期管理
onMounted(() => {
  // 激活LLM模式，恢复状态
  modeStateStore.restoreModeState('llm')
  
  // 加载监测点图层 - 添加延迟确保地图完全初始化
  const loadMonitoringLayers = () => {
    if (mapStore.isMapReady) {
      // 延迟加载，确保地图组件完全渲染
      setTimeout(() => {
        monitoringLayers.loadAllMonitoringLayers()
        yangtzeLayers.loadAllYangtzeLayers()
        console.log('LLM模式：监测点图层和长江水系图层已加载')
      }, 500)
    } else {
      // 监听地图就绪状态
      const unwatch = mapStore.$subscribe((mutation, state) => {
        if (state.isMapReady) {
          // 延迟加载，确保地图组件完全渲染
          setTimeout(() => {
            monitoringLayers.loadAllMonitoringLayers()
            yangtzeLayers.loadAllYangtzeLayers()
            console.log('LLM模式：监测点图层和长江水系图层已加载（延迟）')
          }, 500)
          unwatch() // 取消监听
        }
      })
    }
  }
  
  loadMonitoringLayers()
  
  
})

onUnmounted(() => {
  // 停止水质阈值监测
  thresholdMonitoring.stopMonitoring()
})
</script>

<style scoped>
.llm-panel {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
}

.chat-container {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  min-height: 0;
}
</style>