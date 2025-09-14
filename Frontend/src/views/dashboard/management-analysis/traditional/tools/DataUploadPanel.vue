<template>
  <PanelWindow 
    :visible="analysisStore.toolPanel.visible && analysisStore.toolPanel.activeTool === 'upload'"
    :embed="true"
    :width="'100%'"
    :height="'100%'"
    class="data-upload-panel"
  >
    <!-- 数据上传说明 -->
    <div class="upload-section">
      <div class="section-title">数据上传</div>
      <div class="upload-description">
        <p>支持上传GeoJSON格式的地理数据文件，系统将自动解析并在地图上显示。</p>
        <div class="supported-formats">
          <span class="format-label">支持格式：</span>
          <span class="format-item">GeoJSON (.geojson, .json)</span>
        </div>
      </div>
    </div>

    <!-- 文件上传区域 -->
    <div class="upload-section">
      <div class="section-title">选择文件</div>
      
      <div class="upload-area" @click="openUploadModal">
        <div class="upload-content">
          <div class="upload-icon">📁</div>
          <div class="upload-text">
            <p class="upload-title">点击选择文件</p>
            <p class="upload-subtitle">或拖拽文件到此区域</p>
          </div>
        </div>
      </div>
      
      <div class="upload-actions">
        <SecondaryButton 
          text="选择文件"
          @click="openUploadModal"
          :disabled="isUploading"
        />
        
        <SecondaryButton 
          v-if="uploadedFiles.length > 0"
          text="清除所有"
          @click="clearAllFiles"
          variant="outline"
          style="margin-left: 8px;"
        />
      </div>
    </div>

    <!-- 已上传文件列表 -->
    <div class="upload-section" v-if="uploadedFiles.length > 0">
      <div class="section-title">已上传文件</div>
      
      <div class="file-list">
        <div 
          v-for="(file, index) in uploadedFiles" 
          :key="file.id"
          class="file-item"
        >
          <div class="file-info">
            <div class="file-name">{{ file.name }}</div>
            <div class="file-details">
              <span class="file-size">{{ formatFileSize(file.size) }}</span>
              <span class="file-status" :class="file.status">
                {{ getStatusText(file.status) }}
              </span>
            </div>
          </div>
          
          <div class="file-actions">
            <SecondaryButton 
              v-if="file.status === 'success'"
              text="预览"
              @click="previewFile(file)"
              size="small"
            />
            
            <SecondaryButton 
              v-if="file.status === 'success'"
              text="添加到地图"
              @click="addToMap(file)"
              size="small"
              style="margin-left: 4px;"
            />
            
            <SecondaryButton 
              text="删除"
              @click="removeFile(index)"
              variant="outline"
              size="small"
              style="margin-left: 4px;"
            />
          </div>
        </div>
      </div>
    </div>

    <!-- 上传进度 -->
    <div class="upload-section" v-if="isUploading">
      <div class="section-title">上传进度</div>
      <div class="upload-progress">
        <div class="progress-bar">
          <div class="progress-fill" :style="{ width: uploadProgress + '%' }"></div>
        </div>
        <div class="progress-text">{{ uploadProgress }}%</div>
      </div>
    </div>

    <!-- 数据上传模态窗口 -->
    <DataUploadModal 
      :visible="showUploadModal"
      :externalUploading="isUploading"
      @close="closeUploadModal"
      @upload="handleFileUpload"
    />

    <!-- 图层名称弹窗 -->
    <LayerNameModal
      :visible="showLayerNameModal"
      :defaultName="defaultlayerName"
      title="设置图层名称"
      placeholder="请输入图层名称"
      hint="为上传的数据设置一个图层名称"
      @confirm="handlelayerNameConfirm"
      @close="handlelayerNameClose"
    />
  </PanelWindow>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import { useAnalysisStore } from '@/stores/analysisStore'
import { useDataUpload } from '@/composables/useDataUpload'
import SecondaryButton from '@/components/UI/SecondaryButton.vue'
import PanelWindow from '@/components/UI/PanelWindow.vue'
import DataUploadModal from '@/components/UI/DataUploadModal.vue'
import LayerNameModal from '@/components/UI/LayerNameModal.vue'

const analysisStore = useAnalysisStore()

const {
  uploadedFiles,
  isUploading,
  uploadProgress,
  showUploadModal,
  showLayerNameModal,
  defaultlayerName,
  openUploadModal,
  closeUploadModal,
  handleFileUpload,
  handlelayerNameConfirm,
  handlelayerNameClose,
  clearAllFiles,
  removeFile,
  previewFile,
  addToMap
} = useDataUpload()

// 格式化文件大小
function formatFileSize(bytes: number): string {
  if (bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

// 获取状态文本
function getStatusText(status: string): string {
  const statusMap: { [key: string]: string } = {
    'uploading': '上传中',
    'success': '上传成功',
    'error': '上传失败',
    'parsing': '解析中',
    'parsed': '解析完成'
  }
  return statusMap[status] || status
}
</script>

<style scoped>
.data-upload-panel {
  height: 100%;
  overflow-y: auto;
  padding: 8px;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.upload-section {
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

.upload-description {
  margin-bottom: 16px;
}

.upload-description p {
  font-size: 12px;
  color: var(--sub);
  margin: 0 0 8px 0;
  line-height: 1.4;
}

.supported-formats {
  display: flex;
  align-items: center;
  gap: 8px;
}

.format-label {
  font-size: 11px;
  color: var(--sub);
  font-weight: 500;
}

.format-item {
  font-size: 11px;
  color: var(--accent);
  font-weight: 600;
  background: var(--surface);
  padding: 2px 6px;
  border-radius: 4px;
  border: 1px solid var(--accent);
}

.upload-area {
  border: 2px dashed var(--accent);
  border-radius: 12px;
  padding: 32px 16px;
  text-align: center;
  cursor: pointer;
  transition: all 0.2s ease;
  margin-bottom: 16px;
}

.upload-area:hover {
  border-color: var(--accent);
  background: rgba(var(--accent-rgb), 0.05);
}

.upload-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
}

.upload-icon {
  font-size: 32px;
  opacity: 0.6;
}

.upload-text {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.upload-title {
  font-size: 14px;
  color: var(--text);
  font-weight: 600;
  margin: 0;
}

.upload-subtitle {
  font-size: 12px;
  color: var(--sub);
  margin: 0;
}

.upload-actions {
  display: flex;
  gap: 8px;
  align-items: center;
}

.upload-actions .btn:first-child {
  flex: 1 !important;
  width: 100% !important;
  flex-shrink: 1 !important;
}

.file-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.file-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px;
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 8px;
}

.file-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.file-name {
  font-size: 13px;
  color: var(--text);
  font-weight: 600;
}

.file-details {
  display: flex;
  gap: 12px;
  align-items: center;
}

.file-size {
  font-size: 11px;
  color: var(--sub);
}

.file-status {
  font-size: 11px;
  font-weight: 500;
  padding: 2px 6px;
  border-radius: 4px;
}

.file-status.uploading {
  color: var(--accent);
  background: rgba(var(--accent-rgb), 0.1);
}

.file-status.success {
  color: #10b981;
  background: rgba(16, 185, 129, 0.1);
}

.file-status.error {
  color: #ef4444;
  background: rgba(239, 68, 68, 0.1);
}

.file-status.parsing {
  color: #f59e0b;
  background: rgba(245, 158, 11, 0.1);
}

.file-status.parsed {
  color: #10b981;
  background: rgba(16, 185, 129, 0.1);
}

.file-actions {
  display: flex;
  gap: 4px;
  align-items: center;
}

.upload-progress {
  display: flex;
  align-items: center;
  gap: 12px;
}

.progress-bar {
  flex: 1;
  height: 8px;
  background: var(--surface);
  border-radius: 4px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: var(--accent);
  transition: width 0.3s ease;
}

.progress-text {
  font-size: 12px;
  color: var(--text);
  font-weight: 600;
  min-width: 40px;
  text-align: right;
}
</style>
