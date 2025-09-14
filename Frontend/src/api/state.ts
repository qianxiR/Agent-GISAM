import axios from 'axios'
import { useMapStore } from '@/stores/mapStore'
import { useAnalysisStore } from '@/stores/analysisStore'

/**
 * 前端状态API接口
 * 用于测试脚本获取前端状态信息
 */

export interface FrontendState {
  map_ready: boolean
  layers: Array<{
    name: string
    visible: boolean
    type: string
    source: string
  }>
  analysis_status: string
  timestamp: number
}

/**
 * 获取前端状态信息
 * @returns 前端状态数据
 */
export function getFrontendState(): FrontendState {
  const mapStore = useMapStore()
  const analysisStore = useAnalysisStore()
  
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
  
  return {
    map_ready: mapStore.isMapReady,
    layers: allLayers,
    analysis_status: analysisStore.analysisStatus,
    timestamp: Date.now()
  }
}

/**
 * 创建状态API路由处理器
 * 用于在开发环境中提供状态查询接口
 */
export function createStateAPIHandler() {
  return {
    method: 'GET',
    path: '/api/state',
    handler: (req: any, res: any) => {
      try {
        const state = getFrontendState()
        res.json(state)
      } catch (error) {
        console.error('获取前端状态失败:', error)
        res.status(500).json({ error: '获取前端状态失败' })
      }
    }
  }
}

/**
 * 在开发环境中注册状态API
 */
export function registerStateAPI() {
  if (import.meta.env.DEV) {
    // 在开发环境中，可以通过Vite的代理功能或直接暴露到window对象
    (window as any).getFrontendState = getFrontendState
    console.log('前端状态API已注册到 window.getFrontendState')
  }
}
