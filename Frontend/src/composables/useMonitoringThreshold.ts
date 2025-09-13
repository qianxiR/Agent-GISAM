import { ref, computed } from 'vue'
import { useMonitoringDataStore } from '@/stores/monitoringDataStore'
import { getMonitoringSiteData } from '@/data/waterQualityMockData'

// 水质参数阈值配置
interface WaterQualityThresholds {
  water_temperature: { min: number; max: number }
  ph_value: { min: number; max: number }
  dissolved_oxygen: { min: number; max: number }
  turbidity: { min: number; max: number }
  permanganate_index: { min: number; max: number }
  ammonia_nitrogen: { min: number; max: number }
  total_phosphorus: { min: number; max: number }
  total_nitrogen: { min: number; max: number }
  chlorophyll_a: { min: number; max: number }
  algae_density: { min: number; max: number }
}

// 水质参数阈值定义（基于国家地表水环境质量标准，设置严格阈值用于测试）
const WATER_QUALITY_THRESHOLDS: WaterQualityThresholds = {
  water_temperature: { min: 10, max: 25 }, // 水温适宜范围
  ph_value: { min: 6.5, max: 8.5 }, // pH值标准范围
  dissolved_oxygen: { min: 5, max: 15 }, // 溶解氧标准范围
  turbidity: { min: 0, max: 5 }, // 浊度标准范围（严格设置为5，确保触发预警）
  permanganate_index: { min: 0, max: 3 }, // 高锰酸盐指数标准范围（严格设置为3）
  ammonia_nitrogen: { min: 0, max: 0.5 }, // 氨氮标准范围
  total_phosphorus: { min: 0, max: 0.1 }, // 总磷标准范围
  total_nitrogen: { min: 0, max: 2.0 }, // 总氮标准范围
  chlorophyll_a: { min: 0, max: 0.01 }, // 叶绿素a标准范围
  algae_density: { min: 0, max: 1500000 } // 藻类密度标准范围（严格设置为150万）
}

// 参数名称映射
const PARAMETER_NAMES: Record<string, string> = {
  water_temperature: '水温',
  ph_value: 'pH值',
  dissolved_oxygen: '溶解氧',
  turbidity: '浊度',
  permanganate_index: '高锰酸盐指数',
  ammonia_nitrogen: '氨氮',
  total_phosphorus: '总磷',
  total_nitrogen: '总氮',
  chlorophyll_a: '叶绿素a',
  algae_density: '藻类密度'
}

// 单位映射
const PARAMETER_UNITS: Record<string, string> = {
  water_temperature: '°C',
  ph_value: '',
  dissolved_oxygen: 'mg/L',
  turbidity: 'NTU',
  permanganate_index: 'mg/L',
  ammonia_nitrogen: 'mg/L',
  total_phosphorus: 'mg/L',
  total_nitrogen: 'mg/L',
  chlorophyll_a: 'mg/L',
  algae_density: '个/L'
}

export function useMonitoringThreshold() {
  const monitoringStore = useMonitoringDataStore()
  const isMonitoring = ref(false)
  const lastCheckTime = ref<Date | null>(null)
  const thresholdViolations = ref<Array<{
    siteName: string
    parameter: string
    value: number
    threshold: { min: number; max: number }
    timestamp: Date
  }>>([])
  
  // 防重复触发机制：记录每个监测点最后一次发送通知的时间
  const lastNotificationTime = ref<Map<string, Date>>(new Map())
  const NOTIFICATION_COOLDOWN = 10 * 60 * 1000 // 10分钟冷却时间，防止频繁触发
  
  // 防止同一数据更新周期内重复发送通知
  const processingNotifications = ref<Set<string>>(new Set())

  /**
   * 检查单个参数是否超过阈值
   */
  const checkParameterThreshold = (parameter: string, value: number, thresholds: { min: number; max: number }): boolean => {
    return value < thresholds.min || value > thresholds.max
  }

  /**
   * 检查监测点数据是否超过阈值
   */
  const checkSiteThresholds = (siteName: string, data: any): Array<{
    parameter: string
    value: number
    threshold: { min: number; max: number }
  }> => {
    const violations: Array<{
      parameter: string
      value: number
      threshold: { min: number; max: number }
    }> = []

    Object.keys(WATER_QUALITY_THRESHOLDS).forEach(param => {
      const value = data[param]
      const threshold = WATER_QUALITY_THRESHOLDS[param as keyof WaterQualityThresholds]
      
      if (value !== undefined && checkParameterThreshold(param, value, threshold)) {
        violations.push({
          parameter: param,
          value,
          threshold
        })
      }
    })

    return violations
  }

  /**
   * 获取监测点对应的图层名称
   */
  const getLayerNameBySiteName = (siteName: string): string | null => {
    const sites = monitoringStore.getAllSites()
    const site = sites.find(s => s.name === siteName)
    return site ? site.layerName : null
  }

  /**
   * 发送阈值超限通知
   */
  const sendThresholdNotification = (siteName: string, violations: Array<{
    parameter: string
    value: number
    threshold: { min: number; max: number }
  }>) => {
    const layerName = getLayerNameBySiteName(siteName)
    if (!layerName) return

    // 检查是否正在处理该监测点的通知，防止同一数据更新周期内重复发送
    if (processingNotifications.value.has(siteName)) {
      console.log(`[MonitoringThreshold] 监测点 ${siteName} 正在处理通知中，跳过重复发送`)
      return
    }

    // 检查是否在冷却时间内，防止重复发送
    const now = new Date()
    const lastTime = lastNotificationTime.value.get(siteName)
    if (lastTime && (now.getTime() - lastTime.getTime()) < NOTIFICATION_COOLDOWN) {
      console.log(`[MonitoringThreshold] 监测点 ${siteName} 在冷却时间内，跳过重复通知`, {
        lastNotification: lastTime,
        cooldownRemaining: Math.ceil((NOTIFICATION_COOLDOWN - (now.getTime() - lastTime.getTime())) / 1000 / 60),
        unit: 'minutes'
      })
      return
    }

    // 标记正在处理该监测点的通知
    processingNotifications.value.add(siteName)

    // 更新最后通知时间
    lastNotificationTime.value.set(siteName, now)

    // 构造通知消息
    const violationMessages = violations.map(v => {
      const paramName = PARAMETER_NAMES[v.parameter] || v.parameter
      const unit = PARAMETER_UNITS[v.parameter] || ''
      const currentValue = v.parameter === 'algae_density' 
        ? v.value.toLocaleString() 
        : v.value.toFixed(3)
      
      let status = ''
      if (v.value < v.threshold.min) {
        status = `低于最小值 ${v.threshold.min}${unit}`
      } else if (v.value > v.threshold.max) {
        status = `超过最大值 ${v.threshold.max}${unit}`
      }
      
      return `${paramName}: ${currentValue}${unit} (${status})`
    }).join('\n')

    // 发送系统通知
    const notificationEvent = new CustomEvent('system:thresholdAlert', {
      detail: {
        type: 'warning',
        title: '水质参数超限警告',
        message: `监测点 ${siteName} 的以下参数超过阈值：\n${violationMessages}\n\n将自动进行缓冲区分析...`,
        siteName,
        layerName,
        violations
      }
    })
    window.dispatchEvent(notificationEvent)

    // 直接向ChatAssistant发送缓冲区分析请求
    const bufferAnalysisRequest = `对@${layerName} 执行1000米缓冲区分析`
    
    // 发送自动分析请求到ChatAssistant
    const autoAnalysisEvent = new CustomEvent('llm:autoAnalysis', {
      detail: {
        siteName,
        layerName,
        violations,
        analysisRequest: bufferAnalysisRequest
      }
    })
    window.dispatchEvent(autoAnalysisEvent)
    
    console.log('[MonitoringThreshold] 自动触发缓冲区分析:', {
      siteName,
      layerName,
      radius: 1000,
      unit: 'meters',
      violations: violations.length,
      cooldownSet: true
    })
    
    // 延迟清除处理标志，确保通知完全发送
    setTimeout(() => {
      processingNotifications.value.delete(siteName)
    }, 1000)
  }

  /**
   * 检查所有监测点的阈值
   */
  const checkAllThresholds = async () => {
    try {
      const sites = monitoringStore.getAllSites()
      
      for (const site of sites) {
        const siteData = getMonitoringSiteData(site.name)
        if (siteData && siteData.data && siteData.data.length > 0) {
          const latestData = siteData.data[siteData.data.length - 1]
          const violations = checkSiteThresholds(site.name, latestData)
          
          if (violations.length > 0) {
            // 记录违规情况
            violations.forEach(violation => {
              thresholdViolations.value.push({
                siteName: site.name,
                parameter: violation.parameter,
                value: violation.value,
                threshold: violation.threshold,
                timestamp: new Date()
              })
            })
            
            // 发送通知
            sendThresholdNotification(site.name, violations)
          }
        }
      }
      
      lastCheckTime.value = new Date()
    } catch (error) {
      console.error('阈值检查失败:', error)
    }
  }

  /**
   * 监听新水质数据事件
   */
  const handleNewWaterQualityData = (event: CustomEvent) => {
    const { siteName, newDataPoint } = event.detail
    
    console.log(`[MonitoringThreshold] 收到新数据，开始检测阈值: ${siteName}`)
    
    // 检查该站点的最新数据是否超限
    const violations = checkSiteThresholds(siteName, newDataPoint)
    
    if (violations.length > 0) {
      // 记录违规情况
      violations.forEach(violation => {
        thresholdViolations.value.push({
          siteName,
          parameter: violation.parameter,
          value: violation.value,
          threshold: violation.threshold,
          timestamp: new Date()
        })
      })
      
      // 发送通知
      sendThresholdNotification(siteName, violations)
    }
    
    lastCheckTime.value = new Date()
  }

  /**
   * 开始自动监测（基于实时数据更新）
   */
  const startMonitoring = () => { 
    if (isMonitoring.value) return
    
    isMonitoring.value = true
    console.log('开始水质阈值自动监测（基于实时数据更新）...')
    
    // 监听新水质数据事件
    window.addEventListener('waterQuality:newData', handleNewWaterQualityData as EventListener)
  }



  /**
   * 停止自动监测
   */
  const stopMonitoring = () => {
    isMonitoring.value = false
    console.log('停止水质阈值自动监测')
    
    // 移除事件监听器
    window.removeEventListener('waterQuality:newData', handleNewWaterQualityData as EventListener)
    
    // 清理通知时间记录
    lastNotificationTime.value.clear()
  }

  /**
   * 获取违规历史记录
   */
  const getViolationHistory = computed(() => {
    return thresholdViolations.value.sort((a, b) => b.timestamp.getTime() - a.timestamp.getTime())
  })

  /**
   * 清除违规历史记录
   */
  const clearViolationHistory = () => {
    thresholdViolations.value = []
  }

  return {
    // 状态
    isMonitoring,
    lastCheckTime,
    thresholdViolations,
    getViolationHistory,
    
    // 方法
    checkAllThresholds,
    startMonitoring,
    stopMonitoring,
    clearViolationHistory,
    getLayerNameBySiteName,
    
    // 配置
    WATER_QUALITY_THRESHOLDS,
    PARAMETER_NAMES,
    PARAMETER_UNITS
  }
}
