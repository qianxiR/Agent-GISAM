import { ref, onMounted, onUnmounted } from 'vue'
import { WaterQualityData } from '@/data/waterQualityMockData'

// 全局异常数据管理：每5分钟随机选择一个监测点生成异常数据
class GlobalAnomalyManager {
  private static instance: GlobalAnomalyManager
  private currentAnomalySite: string | null = null
  private lastSwitchTime: Date | null = null
  private readonly SWITCH_INTERVAL = 5 * 60 * 1000 // 5分钟切换间隔
  private switchTimer: number | null = null
  private allSites: string[] = []

  static getInstance(): GlobalAnomalyManager {
    if (!GlobalAnomalyManager.instance) {
      GlobalAnomalyManager.instance = new GlobalAnomalyManager()
    }
    return GlobalAnomalyManager.instance
  }

  // 初始化所有监测点列表
  initializeSites(sites: string[]): void {
    this.allSites = sites
    console.log(`[GlobalAnomalyManager] 初始化监测点列表: ${sites.join(', ')}`)
  }

  // 检查指定监测点是否应该生成异常数据
  isCurrentAnomalySite(siteName: string): boolean {
    return this.currentAnomalySite === siteName
  }

  // 随机选择下一个异常监测点
  private selectRandomAnomalySite(): string {
    if (this.allSites.length === 0) return ''
    const randomIndex = Math.floor(Math.random() * this.allSites.length)
    return this.allSites[randomIndex]
  }

  // 切换到下一个异常监测点
  switchToNextAnomalySite(): void {
    const previousSite = this.currentAnomalySite
    this.currentAnomalySite = this.selectRandomAnomalySite()
    this.lastSwitchTime = new Date()
    
    console.log(`[GlobalAnomalyManager] 切换异常监测点: ${previousSite || '无'} → ${this.currentAnomalySite}`)
    
    // 设置下次切换定时器
    this.scheduleNextSwitch()
  }

  // 安排下次切换
  private scheduleNextSwitch(): void {
    if (this.switchTimer) {
      clearTimeout(this.switchTimer)
    }
    
    this.switchTimer = window.setTimeout(() => {
      this.switchToNextAnomalySite()
    }, this.SWITCH_INTERVAL)
  }

  // 启动随机异常切换机制
  startRandomAnomalySwitching(): void {
    if (this.allSites.length === 0) {
      console.warn('[GlobalAnomalyManager] 监测点列表为空，无法启动随机异常切换')
      return
    }
    
    // 立即选择第一个异常监测点
    this.switchToNextAnomalySite()
    console.log('[GlobalAnomalyManager] 启动随机异常切换机制，每5分钟切换一次')
  }

  // 停止随机异常切换机制
  stopRandomAnomalySwitching(): void {
    if (this.switchTimer) {
      clearTimeout(this.switchTimer)
      this.switchTimer = null
    }
    this.currentAnomalySite = null
    this.lastSwitchTime = null
    console.log('[GlobalAnomalyManager] 停止随机异常切换机制')
  }

  // 获取当前异常监测点
  getCurrentAnomalySite(): string | null {
    return this.currentAnomalySite
  }

  // 获取下次切换时间
  getNextSwitchTime(): Date | null {
    if (!this.lastSwitchTime) return null
    return new Date(this.lastSwitchTime.getTime() + this.SWITCH_INTERVAL)
  }
}

// 实时水质数据管理
export function useRealTimeWaterQuality(siteName: string) {
  const data = ref<WaterQualityData[]>([])
  const isLoading = ref(false)
  const lastUpdateTime = ref<Date>(new Date())
  
  let updateInterval: number | null = null
  
  // 获取全局异常管理器实例
  const anomalyManager = GlobalAnomalyManager.getInstance()
  
  // 基础数据值（每个站点的基准值，都在正常范围内）
  const baseValues: Record<string, Partial<WaterQualityData>> = {
    '湖北省新洲县阳逻镇武湖泵站': {
      water_quality_class: 'Ⅱ',
      water_temperature: 15.2,
      ph_value: 7.6,
      dissolved_oxygen: 8.8,
      turbidity: 4.2, // 正常范围
      permanganate_index: 2.8, // 正常范围
      ammonia_nitrogen: 0.022,
      total_phosphorus: 0.012,
      total_nitrogen: 1.1,
      chlorophyll_a: 0.0028,
      algae_density: 1200000 // 正常范围
    },
    '湖北省武汉市南望山': {
      water_quality_class: 'Ⅰ',
      water_temperature: 13.8,
      ph_value: 7.85,
      dissolved_oxygen: 10.5,
      turbidity: 2.1, // 正常范围
      permanganate_index: 2.8, // 正常范围
      ammonia_nitrogen: 0.015,
      total_phosphorus: 0.008,
      total_nitrogen: 0.95,
      chlorophyll_a: 0.002,
      algae_density: 850000 // 正常范围
    },
    '湖北省武汉市东西湖区吴家山': {
      water_quality_class: 'Ⅱ',
      water_temperature: 15.8,
      ph_value: 7.45,
      dissolved_oxygen: 8.2,
      turbidity: 4.5, // 正常范围（但可能在实时生成时异常）
      permanganate_index: 2.8, // 正常范围（但可能在实时生成时异常）
      ammonia_nitrogen: 0.025,
      total_phosphorus: 0.018,
      total_nitrogen: 1.45,
      chlorophyll_a: 0.004,
      algae_density: 1200000 // 正常范围（但可能在实时生成时异常）
    },
    '湖北省武昌县金口镇金水闸': {
      water_quality_class: 'Ⅱ',
      water_temperature: 15.3,
      ph_value: 7.72,
      dissolved_oxygen: 8.9,
      turbidity: 4.2, // 正常范围
      permanganate_index: 2.8, // 正常范围
      ammonia_nitrogen: 0.022,
      total_phosphorus: 0.012,
      total_nitrogen: 1.18,
      chlorophyll_a: 0.003,
      algae_density: 1200000 // 正常范围
    }
  }
  
  // 生成新的数据点
  const generateNewDataPoint = (): WaterQualityData => {
    const now = new Date()
    const base = baseValues[siteName] || baseValues['湖北省新洲县阳逻镇武湖泵站']
    
    // 检查当前监测点是否被选为异常监测点
    const isCurrentAnomalySite = anomalyManager.isCurrentAnomalySite(siteName)
    
    let dataPoint: WaterQualityData
    
    if (isCurrentAnomalySite) {
      // 生成异常数据（当前被选中的异常监测点）
      console.log(`[RealTimeWaterQuality] 生成异常数据: ${siteName}`)
      
      dataPoint = {
        time: now.toISOString().slice(11, 16),
        water_quality_class: 'Ⅲ',
        water_temperature: (base.water_temperature || 15) + (Math.random() - 0.5) * 2,
        ph_value: (base.ph_value || 7.5) + (Math.random() - 0.5) * 0.3,
        dissolved_oxygen: (base.dissolved_oxygen || 8.5) + (Math.random() - 0.5) * 1.5,
        turbidity: 8.2 + (Math.random() - 0.5) * 3, // 超过阈值5
        permanganate_index: 4.1 + (Math.random() - 0.5) * 1, // 超过阈值3
        ammonia_nitrogen: (base.ammonia_nitrogen || 0.025) + (Math.random() - 0.5) * 0.01,
        total_phosphorus: (base.total_phosphorus || 0.015) + (Math.random() - 0.5) * 0.008,
        total_nitrogen: (base.total_nitrogen || 1.2) + (Math.random() - 0.5) * 0.5,
        chlorophyll_a: (base.chlorophyll_a || 0.003) + (Math.random() - 0.5) * 0.002,
        algae_density: 2200000 + (Math.random() - 0.5) * 500000 // 超过阈值150万
      }
    } else {
      // 生成正常数据
      dataPoint = {
        time: now.toISOString().slice(11, 16),
        water_quality_class: base.water_quality_class || 'Ⅱ',
        water_temperature: (base.water_temperature || 15) + (Math.random() - 0.5) * 2,
        ph_value: (base.ph_value || 7.5) + (Math.random() - 0.5) * 0.3,
        dissolved_oxygen: (base.dissolved_oxygen || 8.5) + (Math.random() - 0.5) * 1.5,
        turbidity: (base.turbidity || 5) + (Math.random() - 0.5) * 3,
        permanganate_index: (base.permanganate_index || 3.5) + (Math.random() - 0.5) * 1,
        ammonia_nitrogen: (base.ammonia_nitrogen || 0.025) + (Math.random() - 0.5) * 0.01,
        total_phosphorus: (base.total_phosphorus || 0.015) + (Math.random() - 0.5) * 0.008,
        total_nitrogen: (base.total_nitrogen || 1.2) + (Math.random() - 0.5) * 0.5,
        chlorophyll_a: (base.chlorophyll_a || 0.003) + (Math.random() - 0.5) * 0.002,
        algae_density: (base.algae_density || 1500000) + (Math.random() - 0.5) * 500000
      }
    }
    
    return dataPoint
  }
  
  // 初始化数据（生成最近15分钟的数据）
  const initializeData = () => {
    const initialData: WaterQualityData[] = []
    const now = new Date()
    
    for (let i = 14; i >= 0; i--) {
      const time = new Date(now.getTime() - i * 60000) // 每分钟一个数据点
      const base = baseValues[siteName] || baseValues['湖北省新洲县阳逻镇武湖泵站']
      
      initialData.push({
        time: time.toISOString().slice(11, 16),
        water_quality_class: base.water_quality_class || 'Ⅱ',
        water_temperature: (base.water_temperature || 15) + (Math.random() - 0.5) * 2,
        ph_value: (base.ph_value || 7.5) + (Math.random() - 0.5) * 0.3,
        dissolved_oxygen: (base.dissolved_oxygen || 8.5) + (Math.random() - 0.5) * 1.5,
        turbidity: (base.turbidity || 5) + (Math.random() - 0.5) * 3,
        permanganate_index: (base.permanganate_index || 3.5) + (Math.random() - 0.5) * 1,
        ammonia_nitrogen: (base.ammonia_nitrogen || 0.025) + (Math.random() - 0.5) * 0.01,
        total_phosphorus: (base.total_phosphorus || 0.015) + (Math.random() - 0.5) * 0.008,
        total_nitrogen: (base.total_nitrogen || 1.2) + (Math.random() - 0.5) * 0.5,
        chlorophyll_a: (base.chlorophyll_a || 0.003) + (Math.random() - 0.5) * 0.002,
        algae_density: (base.algae_density || 1500000) + (Math.random() - 0.5) * 500000
      })
    }
    
    data.value = initialData
  }
  
  // 更新数据
  const updateData = () => {
    isLoading.value = true
    
    // 模拟网络延迟
    setTimeout(() => {
      const newDataPoint = generateNewDataPoint()
      
      // 添加新数据点，逐步增长数据
      data.value = [...data.value, newDataPoint]
      
      // 如果数据超过60个点，移除最旧的数据点（保持60个数据点）
      if (data.value.length > 60) {
        data.value = data.value.slice(-60)
      }
      
      lastUpdateTime.value = new Date()
      isLoading.value = false
      
      // 注意：不再需要检查数据恢复，因为异常监测点会每5分钟自动切换
      
      // 触发阈值检测事件
      const thresholdEvent = new CustomEvent('waterQuality:newData', {
        detail: {
          siteName,
          newDataPoint,
          timestamp: lastUpdateTime.value
        }
      })
      window.dispatchEvent(thresholdEvent)
    }, 200)
  }
  
  // 初始化监测点列表并启动随机异常切换
  const initializeAnomalyManager = () => {
    const allSites = Object.keys(baseValues)
    anomalyManager.initializeSites(allSites)
    anomalyManager.startRandomAnomalySwitching()
  }
  
  // 启动实时更新
  const startRealTimeUpdate = () => {
    // 计算到下一分钟的剩余时间
    const now = new Date()
    const nextMinute = new Date(now.getFullYear(), now.getMonth(), now.getDate(), now.getHours(), now.getMinutes() + 1, 0, 0)
    const timeToNextMinute = nextMinute.getTime() - now.getTime()
    
    // 先等待到下一分钟
    setTimeout(() => {
      updateData() // 立即更新一次
      
      // 然后每分钟更新一次
      updateInterval = setInterval(updateData, 60000) // 60秒 = 60000毫秒
    }, timeToNextMinute)
  }
  
  // 停止实时更新
  const stopRealTimeUpdate = () => {
    if (updateInterval) {
      clearInterval(updateInterval)
      updateInterval = null
    }
  }
  
  // 手动刷新数据
  const refreshData = () => {
    updateData()
  }
  
  // 更新特定时间点的数据（双向绑定）
  const updateDataPoint = (time: string, newData: Partial<WaterQualityData>) => {
    const index = data.value.findIndex(item => item.time === time)
    if (index !== -1) {
      // 更新现有数据点
      data.value[index] = { ...data.value[index], ...newData }
    } else {
      // 如果时间点不存在，创建新的数据点
      const base = baseValues[siteName] || baseValues['湖北省新洲县阳逻镇武湖泵站']
      const newDataPoint: WaterQualityData = {
        time,
        water_quality_class: newData.water_quality_class || base.water_quality_class || 'Ⅱ',
        water_temperature: newData.water_temperature || (base.water_temperature || 15) + (Math.random() - 0.5) * 2,
        ph_value: newData.ph_value || (base.ph_value || 7.5) + (Math.random() - 0.5) * 0.3,
        dissolved_oxygen: newData.dissolved_oxygen || (base.dissolved_oxygen || 8.5) + (Math.random() - 0.5) * 1.5,
        turbidity: newData.turbidity || (base.turbidity || 5) + (Math.random() - 0.5) * 3,
        permanganate_index: newData.permanganate_index || (base.permanganate_index || 3.5) + (Math.random() - 0.5) * 1,
        ammonia_nitrogen: newData.ammonia_nitrogen || (base.ammonia_nitrogen || 0.025) + (Math.random() - 0.5) * 0.01,
        total_phosphorus: newData.total_phosphorus || (base.total_phosphorus || 0.015) + (Math.random() - 0.5) * 0.008,
        total_nitrogen: newData.total_nitrogen || (base.total_nitrogen || 1.2) + (Math.random() - 0.5) * 0.5,
        chlorophyll_a: newData.chlorophyll_a || (base.chlorophyll_a || 0.003) + (Math.random() - 0.5) * 0.002,
        algae_density: newData.algae_density || (base.algae_density || 1500000) + (Math.random() - 0.5) * 500000
      }
      data.value.push(newDataPoint)
    }
  }
  
  // 获取特定时间点的数据
  const getDataPoint = (time: string): WaterQualityData | undefined => {
    return data.value.find(item => item.time === time)
  }
  
  // 删除特定时间点的数据
  const removeDataPoint = (time: string) => {
    const index = data.value.findIndex(item => item.time === time)
    if (index !== -1) {
      data.value.splice(index, 1)
    }
  }
  
  onMounted(() => {
    initializeData()
    initializeAnomalyManager()
    startRealTimeUpdate()
  })
  
  onUnmounted(() => {
    stopRealTimeUpdate()
    // 注意：不停止全局异常管理器，因为其他监测点可能还在使用
  })
  
  return {
    data,
    isLoading,
    lastUpdateTime,
    refreshData,
    startRealTimeUpdate,
    stopRealTimeUpdate,
    // 双向绑定方法
    updateDataPoint,
    getDataPoint,
    removeDataPoint
  }
}
