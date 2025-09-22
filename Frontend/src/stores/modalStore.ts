import { defineStore } from 'pinia'
import { ref } from 'vue'

export type GlobalModalType = 'none'

export const useGlobalModalStore = defineStore('globalModal', () => {
  const visible = ref<boolean>(false)
  const type = ref<GlobalModalType>('none')

  const open = (modalType: Exclude<GlobalModalType, 'none'>) => {
    type.value = modalType
    visible.value = true
  }

  const close = () => {
    visible.value = false
    type.value = 'none'
  }

  return { visible, type, open, close }
})

export default useGlobalModalStore





