<template>
  <PanelWindow 
    :visible="analysisStore.toolPanel.visible && analysisStore.toolPanel.activeTool === 'buffer'"
    :embed="true"
    :width="'100%'"
    :height="'100%'"
    class="buffer-analysis-panel"
  >
    <!-- 选择分析及绘制图层 -->
    <div class="analysis-section">
      <div class="section-title">选择分析及绘制图层</div>
      <div class="layer-selector">
        <DropdownSelect 
          :model-value="selectedAnalysislayerId"
          :options="layerOptionsWithNone"
          placeholder="请选择分析及绘制图层"
          @update:model-value="onlayerSelectionChange"
        />
      </div>
      
      <!-- 显示选中图层信息 -->
      <div v-if="selectedAnalysislayerInfo" class="layer-info">
        <div class="info-item">
          <span class="info-label">图层名称:</span>
          <span class="info-value">{{ selectedAnalysislayerInfo?.name }}</span>
        </div>
        <div class="info-item">
          <span class="info-label">图层类型:</span>
          <span class="info-value">{{ selectedAnalysislayerInfo?.type }}</span>
        </div>
        <div class="info-item">
          <span class="info-label">要素数量:</span>
          <span class="info-value">{{ selectedAnalysislayerInfo?.featureCount }} 个</span>
        </div>
      </div>
      
    </div>
    
    <!-- 参数设置 -->
    <div class="analysis-section">
      <div class="section-title">参数设置</div>
      <div class="form-row">
        <div class="form-item">
          <label class="form-label">圆弧精度</label>
          <TraditionalInputGroup
            :model-value="bufferSettings.semicircleLineSegment"
            type="number"
            :min="4"
            :max="50"
            :step="2"
            placeholder="圆弧精度 (步数)"
            @update:model-value="(value) => updateBufferSettings({ semicircleLineSegment: value })"
          />
        </div>

      </div>
      <div class="form-row">
        <div class="form-item">
          <label class="form-label">缓冲距离 (米)</label>
          <TraditionalInputGroup
            :model-value="bufferSettings.radius"
            type="number"
            :min="0"
            :step="10"
            placeholder="缓冲距离"
            @update:model-value="(value) => updateBufferSettings({ radius: value })"
          />
        </div>
      </div>
    </div>

    <!-- 分析操作 -->
    <div class="analysis-section">
      <div class="button-group">
        <PrimaryButton 
          text="执行缓冲区分析"
          :loading="isAnalyzing"
          @click="executeBufferAnalysis"
        />
        <PrimaryButton 
          text="保存为图层"
          @click="onSaveAsLayer"
        />
        <SecondaryButton 
          text="清除结果"
          @click="clearResults"
        />
      </div>
      
      <!-- 运行时提示 -->
      <TipWindow 
        v-if="isAnalyzing"
        :visible="isAnalyzing"
        variant="info"
        :show-icon="true"
      >
        <template #icon>🔄</template>
        <div>
          <div style="font-weight: 600; margin-bottom: 4px;">正在执行缓冲区分析...</div>
          <div style="font-size: 11px; opacity: 0.8;">
            正在对图层 "{{ selectedAnalysislayerInfo?.name }}" 进行缓冲区分析，请稍候
          </div>
        </div>
      </TipWindow>
    </div>

    <!-- 分析结果 -->
    <div v-if="bufferResults && bufferResults.length > 0" class="analysis-section">
      <div class="section-title">分析结果</div>
      <div class="result-info">
        <div class="info-item">
          <span class="info-label">生成缓冲区:</span>
          <span class="info-value">{{ bufferResults.length }} 个</span>
        </div>
        <div class="info-item">
          <span class="info-label">缓冲距离:</span>
          <span class="info-value">{{ bufferSettings.radius }} 米</span>
        </div>
        <div class="info-item">
          <span class="info-label">圆弧精度:</span>
          <span class="info-value">{{ bufferSettings.semicircleLineSegment }} 步</span>
        </div>
      </div>
        
        <!-- 结果操作 -->
    </div>
  </PanelWindow>
  
  <!-- 图层名称输入弹窗 -->
  <LayerNameModal
    :visible="showLayerNameModalRef"
    title="保存缓冲区分析结果"
    placeholder="请输入图层名称"
    hint="图层名称将用于在图层管理器中识别此缓冲区分析结果"
    :default-name="defaultlayerName"
    @confirm="handlelayerNameConfirm"
    @close="handlelayerNameClose"
  />
  
</template>

<script setup lang="ts">
import { watch, computed, ref, onMounted, onUnmounted } from 'vue'
import { useAnalysisStore } from '@/stores/analysisStore'
import { useMapStore } from '@/stores/mapStore'
import { useBufferAnalysis } from '@/composables/useBufferAnalysis'
import PrimaryButton from '@/components/UI/PrimaryButton.vue'
import SecondaryButton from '@/components/UI/SecondaryButton.vue'
import TraditionalInputGroup from '@/components/UI/TraditionalInputGroup.vue'
import DropdownSelect from '@/components/UI/DropdownSelect.vue'
import PanelWindow from '@/components/UI/PanelWindow.vue'
import TipWindow from '@/components/UI/TipWindow.vue'
import LayerNameModal from '@/components/UI/LayerNameModal.vue'

const analysisStore = useAnalysisStore()
const mapStore = useMapStore()

const {
  selectedAnalysislayerId,
  selectedAnalysislayerInfo,
  layerOptions,
  bufferSettings,
  bufferResults,
  currentResult,
  isAnalyzing,
  setSelectedAnalysislayer,
  updateBufferSettings,
  executeBufferAnalysis,
  saveBufferResultsAsLayer,
  clearState,
  lastFeatureCollection,
} = useBufferAnalysis()

// 使用图层管理 hook

// 包含"无"选项的图层选项
const layerOptionsWithNone = computed(() => {
  return [
    { value: '', label: '无', disabled: false },
    ...layerOptions.value
  ]
})

// 图层选择变化处理
const onlayerSelectionChange = (layerId: string) => {
  if (layerId) {
    setSelectedAnalysislayer(layerId)
  }
}

// 图层名称弹窗状态
const showLayerNameModalRef = ref<boolean>(false)
const defaultlayerName = ref<string>('')

// 显示图层名称输入弹窗
const showLayerNameModal = () => {
  if (!lastFeatureCollection.value || !lastFeatureCollection.value.features || lastFeatureCollection.value.features.length === 0) {
    return
  }
  defaultlayerName.value = generatelayerNameFromBuffer()
  showLayerNameModalRef.value = true
}

// 处理图层名称确认
const handlelayerNameConfirm = async (layerName: string) => {
  showLayerNameModalRef.value = false
  await saveBufferResultsAsLayer(layerName)
}

// 处理图层名称弹窗关闭
const handlelayerNameClose = () => {
  showLayerNameModalRef.value = false
}

// 保存为图层
const onSaveAsLayer = async () => {
  showLayerNameModal()
}


// 距离变化时的处理
const onDistanceChange = () => {
  const radius = bufferSettings.value.radius
  
  if (radius <= 0) {
    analysisStore.setAnalysisStatus('缓冲距离必须大于0')
  } else {
    analysisStore.setAnalysisStatus(`缓冲距离: ${radius}米`)
  }
}

// 清除结果
const clearResults = () => {
  clearState()
  analysisStore.setAnalysisStatus('已清除缓冲区分析结果')
}


// 生成基于分析参数的图层名称
const generatelayerNameFromBuffer = () => {
  if (!selectedAnalysislayerInfo.value) {
    return `缓冲区分析`
  }

  const sourcelayerName = selectedAnalysislayerInfo.value.name
  const distanceText = `${bufferSettings.value.radius}米`
  
  
  return `缓冲区_${sourcelayerName}_${distanceText}`
}


// 工具状态管理（已移除持久化）

// 清理缓冲区分析状态（工具切换时调用）
const clearBufferAnalysisState = () => {
  clearState()
  
  analysisStore.setAnalysisStatus('缓冲区分析状态已清理')
}

// 已移除持久化保存/恢复逻辑

// 组件生命周期管理
onMounted(() => {
  analysisStore.setAnalysisStatus('请选择分析及绘制图层')
})

onUnmounted(() => {})

// 监听状态变化，自动保存（防抖）
watch([
  selectedAnalysislayerId,
  () => bufferSettings.value.radius,
  () => bufferSettings.value.semicircleLineSegment
], () => {
  // 持久化已移除：此处仅更新状态提示
})

// 监听工具面板变化
watch(() => analysisStore.toolPanel?.activeTool, (tool, prevTool) => {
  if (tool === 'buffer' && prevTool !== 'buffer') {
    // 当进入缓冲区分析时，只更新状态提示，不重复恢复状态
    if (bufferResults.value && bufferResults.value.length > 0) {
      analysisStore.setAnalysisStatus(`缓冲区分析结果已加载（${bufferResults.value.length}个结果），点击"执行分析"重新显示`)
    } else {
      analysisStore.setAnalysisStatus('请选择分析及绘制图层')
    }
  } else if (prevTool === 'buffer' && tool !== 'buffer') {
    // 当从缓冲区分析切换到其他工具时，清理分析结果和地图显示
    clearBufferAnalysisState()
  }
}, { immediate: true })

// 监听图层选择变化
watch(selectedAnalysislayerId, (newlayerId) => {
  if (newlayerId) {
    setSelectedAnalysislayer(newlayerId)
  }
})



</script>

<style scoped>
.buffer-analysis-panel {
  height: 100%;
  overflow-y: auto;
  padding: 8px;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.analysis-section {
  background: var(--panel);
  border: 1px solid var(--border);
  border-radius: 16px;
  padding: 16px;
  animation: none !important;
  margin-bottom: 16px;
}

.section-title {
  font-size: 13px;
  color: var(--text);
  margin-bottom: 12px;
  font-weight: 600;
  letter-spacing: 0.5px;
}

.layer-selector {
  margin-bottom: 12px;
}

.form-item {
  display: flex;
  flex-direction: column;
  gap: 8px;
  flex: 1;
}

.form-row {
  display: flex;
  gap: 12px;
  margin-bottom: 12px;
}

.form-row:last-child {
  margin-bottom: 0;
}

.form-label {
  font-size: 12px;
  color: var(--sub);
  font-weight: 500;
}

.layer-info {
  margin-top: 12px;
  padding: 16px;
  background: var(--panel);
  border: 1px solid var(--border);
  border-radius: 12px;
  transition: all 0.2s ease;
  box-shadow: var(--glow);
}

.layer-info:hover {
  background: var(--surface-hover);
  border-color: var(--accent);
  box-shadow: 0 2px 6px rgba(var(--accent-rgb), 0.15);
}


.info-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 6px;
}

.info-item:last-child {
  margin-bottom: 0;
}

.info-label {
  font-size: 11px;
  color: var(--sub);
  font-weight: 500;
}

.info-value {
  font-size: 11px;
  color: var(--text);
  font-weight: 600;
}

.button-group {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

.button-group > * {
  flex: 1 1 0;
  min-width: 120px;
}

.button-group :deep(.btn) {
  width: 100%;
  justify-content: center;
}

.result-info {
  margin-bottom: 16px;
  padding: 12px;
  background: rgba(var(--accent-rgb), 0.1);
  border: 1px solid rgba(var(--accent-rgb), 0.2);
  border-radius: 8px;
}

.result-actions {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.result-actions .button-group {
  justify-content: stretch;
}

.result-actions .button-group .primary-button,
.result-actions .button-group .secondary-button {
  flex: 1;
}
</style>