/**
 * 全局自动分析事件处理器
 * 用于在多个组件中响应阈值超限的自动分析请求
 */

interface AutoAnalysisEventDetail {
  siteName: string
  layerName: string
  violations: Array<{
    parameter: string
    value: number
    threshold: { min: number; max: number }
  }>
  analysisRequest: string
}

/**
 * 全局自动分析事件处理器
 * 当检测到阈值超限时，会触发此处理器
 */
export const handleGlobalAutoAnalysis = (event: CustomEvent<AutoAnalysisEventDetail>) => {
  const { siteName, layerName, violations, analysisRequest } = event.detail
  
  console.log('[GlobalAutoAnalysis] 收到自动分析请求:', {
    siteName,
    layerName,
    violations: violations.length,
    analysisRequest
  })
  
  // 检查当前路由是否包含management-analysis（LLM模式）
  const currentPath = window.location.pathname
  if (currentPath.includes('management-analysis')) {
    // 在LLM模式下，发送到ChatAssistant处理
    const llmEvent = new CustomEvent('llm:autoAnalysis', {
      detail: { siteName, layerName, violations, analysisRequest }
    })
    window.dispatchEvent(llmEvent)
    console.log('[GlobalAutoAnalysis] 已转发到LLM模式处理')
  }
  
  // 在所有路由下都显示系统通知弹窗
  const violationMessages = violations.map(v => {
    const paramName = getParameterName(v.parameter)
    const unit = getParameterUnit(v.parameter)
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
  
  const notificationMessage = `监测点 ${siteName} 的以下参数超过阈值：\n${violationMessages}\n\n建议进行缓冲区分析`
  
  // 创建系统通知（全局显示）
  const notificationEvent = new CustomEvent('system:thresholdAlert', {
    detail: {
      type: 'warning',
      title: '水质参数超限警告',
      message: notificationMessage,
      siteName,
      layerName,
      violations
    }
  })
  window.dispatchEvent(notificationEvent)
  
  console.log('[GlobalAutoAnalysis] 全局系统通知已发送:', {
    message: notificationMessage,
    violations: violations.map(v => `${v.parameter}: ${v.value}`)
  })
}

/**
 * 获取参数名称
 */
const getParameterName = (parameter: string): string => {
  const names: Record<string, string> = {
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
  return names[parameter] || parameter
}

/**
 * 获取参数单位
 */
const getParameterUnit = (parameter: string): string => {
  const units: Record<string, string> = {
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
  return units[parameter] || ''
}

/**
 * 注册全局自动分析事件监听器
 */
export const registerGlobalAutoAnalysisListener = () => {
  if (!(window as any).__globalAutoAnalysisListenerRegistered) {
    (window as any).__globalAutoAnalysisListenerRegistered = true
    window.addEventListener('llm:autoAnalysis', handleGlobalAutoAnalysis as unknown as EventListener)
    console.log('[GlobalAutoAnalysis] 全局自动分析监听器已注册')
  }
}

/**
 * 注销全局自动分析事件监听器
 */
export const unregisterGlobalAutoAnalysisListener = () => {
  if ((window as any).__globalAutoAnalysisListenerRegistered) {
    window.removeEventListener('llm:autoAnalysis', handleGlobalAutoAnalysis as unknown as EventListener)
    ;(window as any).__globalAutoAnalysisListenerRegistered = false
    console.log('[GlobalAutoAnalysis] 全局自动分析监听器已注销')
  }
}
