/**
 * 前端状态监测脚本
 * 在浏览器控制台中运行，用于获取前端状态信息
 */

// 获取前端状态信息
function getFrontendState() {
  try {
    // 获取Vue应用实例
    const app = document.querySelector('#app').__vue_app__
    if (!app) {
      throw new Error('无法找到Vue应用实例')
    }
    
    // 获取Pinia store实例
    const mapStore = app.config.globalProperties.$pinia._s.get('map')
    const analysisStore = app.config.globalProperties.$pinia._s.get('analysis')
    
    if (!mapStore || !analysisStore) {
      throw new Error('无法找到Pinia store实例')
    }
    
    // 获取图层信息
    const layers = mapStore.vectorlayers.map(layer => ({
      name: layer.name,
      visible: layer.layer.getVisible(),
      type: layer.type,
      source: layer.source || 'unknown'
    }))
    
    // 添加自定义图层
    const customLayers = mapStore.customlayers.map(layer => ({
      name: layer.name,
      visible: layer.layer.getVisible(),
      type: layer.type,
      source: 'custom'
    }))
    
    const allLayers = [...layers, ...customLayers]
    
    const state = {
      map_ready: mapStore.isMapReady,
      layers: allLayers,
      analysis_status: analysisStore.analysisStatus,
      timestamp: Date.now(),
      map_center: mapStore.map ? mapStore.map.getView().getCenter() : null,
      map_zoom: mapStore.map ? mapStore.map.getView().getZoom() : null
    }
    
    console.log('前端状态:', state)
    return state
    
  } catch (error) {
    console.error('获取前端状态失败:', error)
    return {
      error: error.message,
      timestamp: Date.now()
    }
  }
}

// 监测状态变化
function monitorStateChanges(callback, interval = 2000) {
  let lastState = null
  
  const monitor = setInterval(() => {
    const currentState = getFrontendState()
    
    if (lastState && JSON.stringify(currentState) !== JSON.stringify(lastState)) {
      console.log('状态变化检测到:', {
        before: lastState,
        after: currentState,
        changes: findChanges(lastState, currentState)
      })
      
      if (callback) {
        callback(lastState, currentState)
      }
    }
    
    lastState = currentState
  }, interval)
  
  return monitor
}

// 查找状态变化
function findChanges(before, after) {
  const changes = {}
  
  // 检查图层变化
  if (before.layers && after.layers) {
    const beforeLayerNames = before.layers.map(l => l.name).sort()
    const afterLayerNames = after.layers.map(l => l.name).sort()
    
    if (JSON.stringify(beforeLayerNames) !== JSON.stringify(afterLayerNames)) {
      changes.layer_count = {
        before: before.layers.length,
        after: after.layers.length
      }
    }
  }
  
  // 检查分析状态变化
  if (before.analysis_status !== after.analysis_status) {
    changes.analysis_status = {
      before: before.analysis_status,
      after: after.analysis_status
    }
  }
  
  // 检查地图状态变化
  if (before.map_ready !== after.map_ready) {
    changes.map_ready = {
      before: before.map_ready,
      after: after.map_ready
    }
  }
  
  return changes
}

// 导出到全局作用域
window.getFrontendState = getFrontendState
window.monitorStateChanges = monitorStateChanges

console.log('前端状态监测脚本已加载')
console.log('使用方法:')
console.log('1. getFrontendState() - 获取当前状态')
console.log('2. monitorStateChanges(callback, interval) - 监测状态变化')
