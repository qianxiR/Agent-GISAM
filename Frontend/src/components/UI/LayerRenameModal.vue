<template>
  <div v-if="visible" class="modal-intersect" @click="handleModalClick">
    <div class="modal-container" @click.stop>
      <div class="modal-header">
        <h3 class="modal-title">重命名图层</h3>
        <button class="close-btn" @click="handleClose" title="关闭">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
            <path d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z"/>
          </svg>
        </button>
      </div>
      
      <div class="modal-body">
        <div class="form-group">
          <label class="form-label">图层名称</label>
          <input
            ref="nameInput"
            v-model="layerName"
            type="text"
            class="form-input"
            placeholder="请输入新的图层名称"
            @keyup.enter="handleConfirm"
            @keyup.escape="handleClose"
          />
          <div class="form-hint">图层名称不能为空</div>
        </div>
        
        <div class="modal-actions">
          <SecondaryButton text="取消" @click="handleClose" />
          <PrimaryButton 
            text="保存" 
            @click="handleConfirm"
            :disabled="!layerName.trim()"
          />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, nextTick } from 'vue'
import PrimaryButton from './PrimaryButton.vue'
import SecondaryButton from './SecondaryButton.vue'

interface Props {
  visible: boolean
  currentName?: string
}

interface Emits {
  (e: 'confirm', name: string): void
  (e: 'close'): void
}

const props = withDefaults(defineProps<Props>(), {
  currentName: ''
})

const emit = defineEmits<Emits>()

const nameInput = ref<HTMLInputElement>()
const layerName = ref(props.currentName)

// 监听visible变化，自动聚焦输入框
watch(() => props.visible, (newVisible) => {
  if (newVisible) {
    layerName.value = props.currentName
    nextTick(() => {
      nameInput.value?.focus()
      nameInput.value?.select()
    })
  }
})

// 监听currentName变化
watch(() => props.currentName, (newName) => {
  layerName.value = newName
})

const handleModalClick = () => {
  handleClose()
}

const handleClose = () => {
  emit('close')
}

const handleConfirm = () => {
  if (layerName.value.trim()) {
    emit('confirm', layerName.value.trim())
  }
}
</script>

<style scoped>
.modal-intersect {
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
}

.modal-container {
  background: var(--panel);
  border: 1px solid var(--border);
  border-radius: 12px;
  min-width: 400px;
  max-width: 500px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
}

.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 20px 24px 16px;
  border-bottom: 1px solid var(--border);
}

.modal-title {
  font-size: 16px;
  font-weight: 600;
  color: var(--text);
  margin: 0;
}

.close-btn {
  background: none;
  border: none;
  color: var(--text-secondary);
  cursor: pointer;
  padding: 4px;
  border-radius: 4px;
  transition: background-color 0.2s;
}

.close-btn:hover {
  background: var(--btn-secondary-bg);
  color: var(--text);
}

.modal-body {
  padding: 24px;
}

.form-group {
  margin-bottom: 24px;
}

.form-label {
  display: block;
  font-size: 14px;
  font-weight: 500;
  color: var(--text);
  margin-bottom: 8px;
}

.form-input {
  width: 100%;
  padding: 12px 16px;
  border: 1px solid var(--border);
  border-radius: 8px;
  background: var(--input-bg);
  color: var(--text);
  font-size: 14px;
  transition: border-color 0.2s;
  box-sizing: border-box;
}

.form-input:focus {
  outline: none;
  border-color: var(--accent);
}

.form-hint {
  font-size: 12px;
  color: var(--text-secondary);
  margin-top: 6px;
}

.modal-actions {
  display: flex;
  gap: 12px;
  justify-content: flex-end;
}
</style>
