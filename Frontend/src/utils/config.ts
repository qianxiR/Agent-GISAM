import type { APIConfig, Wuhanlayer } from '@/types/map'

/**
 * GeoServer API 配置管理器
 * 
 * 功能：集中管理GeoServer的所有服务配置
 * 包括：服务器地址、服务路径、图层定义、底图配置等
 * 
 * @returns {APIConfig} 完整的API配置对象
 */
export const createAPIConfig = (): APIConfig => {
  // ===== 基础服务配置 =====
  
  /** GeoServer 服务器基础地址 */
  const baseUrl = import.meta.env.VITE_GEOSERVER_BASE_URL || ''
  
  /** WMS服务路径 - 用于瓦片地图服务 */
  const wmsService = import.meta.env.VITE_GEOSERVER_WMS_SERVICE || 'geoserver/wms'
  
  /** WFS服务路径 - 用于矢量要素数据获取 */
  const wfsService = import.meta.env.VITE_GEOSERVER_WFS_SERVICE || 'geoserver/wfs'
  
  /** 工作空间名称 */
  const workspace = import.meta.env.VITE_GEOSERVER_WORKSPACE || 'czh'
  
  // ===== 地图显示配置 =====
  
  /** 地图边界和显示参数配置 */
  const mapBounds = {
    /** 成都地区边界范围 [minLon, minLat, maxLon, maxLat] */
    extent: [103.9, 30.4, 104.5, 31.0] as [number, number, number, number],
    /** 地图中心点坐标 [lon, lat] */
    center: [104.06, 30.67] as [number, number],
    /** 初始缩放级别 */
    zoom: 8
  }
  
  return {
    baseUrl: baseUrl.replace(/\/$/, ''), // 移除末尾斜杠
    mapService: wmsService,
    dataService: wfsService,
    datasetName: workspace,
    
    // ===== 底图服务配置 =====
    // 调用者: useMap.ts -> updateBaseMap() -> getCurrentBaseMapUrl()
    // 服务器地址: GeoServer WMS服务
    // 作用: 提供浅色和深色主题的底图瓦片服务，根据主题自动切换
    baseMaps: {
      light: `${baseUrl}/${wmsService}`,
      dark: `${baseUrl}/${wmsService}`
    },
    
    // ===== 备用底图服务配置 =====
    // 调用者: useMap.ts -> updateBaseMap() -> getCurrentBaseMapUrl()
    // 服务器地址: GeoServer WMS服务
    // 作用: 当主底图服务不可用时，提供备用的底图瓦片服务
    fallbackBaseMaps: {
      light: `${baseUrl}/${wmsService}`,
      dark: `${baseUrl}/${wmsService}`
    },
    
    // ===== 矢量图层配置 =====
    // 调用者: useMap.ts -> loadVectorlayers() -> loadVectorlayer()
    // 服务器地址: GeoServer WMS/WFS服务
    // 作用: 定义所有矢量图层，包括行政区边界、地貌类型、水文站点等
    wuhanlayers: [
      // ===== 地貌类型图层 =====
      // 调用者: useMap.ts -> loadVectorlayer()
      // 服务器地址: GeoServer WMS/WFS服务
      // 作用: 提供地貌类型分类数据，用于地形分析
      { 
        name: `${workspace}:成都市地貌类型_`, 
        type: 'raster', 
        visible: false, 
        group: '地形数据',
        datasetName: '成都市地貌类型_',
        dataService: `${baseUrl}/${wmsService}`,
        lazyLoad: true // 懒加载，点击显示时才加载
      },
      
      // ===== 区县图层 =====
      // 调用者: useMap.ts -> loadVectorlayer()
      // 服务器地址: GeoServer WMS/WFS服务
      // 作用: 提供区县级行政区边界数据
      { 
        name: `${workspace}:成都区`, 
        type: 'polygon', 
        visible: true, 
        group: '行政区划',
        datasetName: '成都区划',
        dataService: `${baseUrl}/${wmsService}`,
        lazyLoad: true // 懒加载，点击显示时才加载
      },
      
      // ===== 水文站点图层 =====
      // 调用者: useMap.ts -> loadVectorlayer()
      // 服务器地址: GeoServer WMS/WFS服务
      // 作用: 提供水文监测站点数据，用于水资源分析
      { 
        name: `${workspace}:水文站点`, 
        type: 'point', 
        visible: true, 
        group: '基础设施',
        datasetName: '水文站点',
        dataService: `${baseUrl}/${wmsService}`,
        lazyLoad: true // 懒加载，点击显示时才加载
      }
    ],
    timeout: Number(import.meta.env.VITE_API_TIMEOUT),
    retryCount: Number(import.meta.env.VITE_API_RETRY_COUNT),
    devMode: import.meta.env.VITE_DEV_MODE === 'true' || import.meta.env.DEV,
    mapBounds: mapBounds
  }
}

/**
 * 获取完整的SuperMap服务URL
 * 调用者: mapStore.ts -> createMapConfig() -> getFullUrl()
 * 作用: 根据服务类型构建完整的SuperMap iServer服务访问地址
 */
export const getFullUrl = (endpoint: 'map' | 'data'): string => {
  // ===== 获取API配置 =====
  // 调用者: getFullUrl() -> createAPIConfig()
  // 作用: 获取SuperMap服务器的基础配置信息
  const config = createAPIConfig()
  
  // ===== 选择服务类型 =====
  // 调用者: getFullUrl()
  // 作用: 根据endpoint参数选择对应的服务路径
  const service = endpoint === 'map' ? config.mapService : config.dataService
  
  // ===== 构建完整URL =====
  // 调用者: mapStore.ts -> createMapConfig()
  // 服务器地址: ${baseUrl}/${service}
  // 作用: 返回完整的SuperMap服务访问地址
  return `${config.baseUrl}/${service}`
}

export const isDevelopment = (): boolean => {
  return createAPIConfig().devMode
}

// 获取按组分类的图层
export const getLayersByGroup = () => {
  const config = createAPIConfig()
  const groupedlayers: Record<string, Wuhanlayer[]> = {}
  
  config.wuhanlayers.forEach(layer => {
    const group = layer.group || '其他'
    if (!groupedlayers[group]) {
      groupedlayers[group] = []
    }
    groupedlayers[group].push(layer)
  })
  
  return groupedlayers
}

// 获取指定组的图层
export const getLayersByGroupName = (groupName: string): Wuhanlayer[] => {
  const config = createAPIConfig()
  return config.wuhanlayers.filter(layer => layer.group === groupName)
}

// 获取所有图层组名称
export const getlayerGroupNames = (): string[] => {
  const config = createAPIConfig()
  const groups = new Set(config.wuhanlayers.map(layer => layer.group).filter((group): group is string => Boolean(group)))
  return Array.from(groups)
}

// 获取指定图层的完整地图服务URL
export const getlayerMapServiceUrl = (layerName: string): string | null => {
  const config = createAPIConfig()
  const layer = config.wuhanlayers.find(l => l.name === layerName)
  
  if (layer && layer.dataService) {
    return `${config.baseUrl}/${layer.dataService}/${layer.name}`
  }
  
  return null
}

// 获取指定图层的完整数据服务URL（包含数据集）
export const getlayerDatasetUrl = (layerName: string): string | null => {
  const config = createAPIConfig()
  const layer = config.wuhanlayers.find(l => l.name === layerName)
  
  if (layer && layer.dataService && layer.datasetName) {
    return `${config.baseUrl}/${layer.dataService}/${layer.datasetName}`
  }
  
  return null
}

// 获取所有地图服务URL
export const getAllMapServiceUrls = (): Record<string, string> => {
  const config = createAPIConfig()
  const urls: Record<string, string> = {}
  
  config.wuhanlayers.forEach(layer => {
    if (layer.dataService) {
      urls[layer.name] = `${config.baseUrl}/${layer.dataService}/${layer.name}`
    }
  })
  
  return urls
}

// 测试函数：验证图层配置
export const testlayerConfig = () => {
  const config = createAPIConfig()
  config.wuhanlayers.forEach((layer, index) => {
  })
  
  return config
}

// 获取当前主题对应的底图URL
export const getCurrentBaseMapUrl = (theme: 'light' | 'dark'): string => {
  const config = createAPIConfig()
  return config.baseMaps[theme]
}

// 获取所有底图配置
export const getBaseMapConfig = () => {
  const config = createAPIConfig()
  return config.baseMaps
}

// ===== LLM 接入配置 =====
export interface LLMApiConfig {
  apiKey: string
  baseUrl: string
  model: string
  temperature: number
  maxTokens: number
}

export const getLLMApiConfig = (): LLMApiConfig => {
  const env = import.meta.env as any
  const apiKey = (env.VITE_LLM_API_KEY as string)
    || (env.VITE_DASHSCOPE_API_KEY as string)
    || (env.DASHSCOPE_API_KEY as string)
    || ''
  const baseUrlRaw = (env.VITE_LLM_BASE_URL as string)
    || (env.VITE_DASHSCOPE_BASE_URL as string)
    || (env.DASHSCOPE_BASE_URL as string)
    || 'https://dashscope.aliyuncs.com/compatible-mode/v1'
  const baseUrl = String(baseUrlRaw).replace(/\/$/, '')
  const model = (env.VITE_LLM_MODEL as string)
    || (env.VITE_DASHSCOPE_MODEL as string)
    || (env.DASHSCOPE_MODEL as string)
    || 'qwen-plus'
  const temperature = Number(
    env.VITE_LLM_TEMPERATURE ?? env.VITE_DASHSCOPE_TEMPERATURE ?? env.DASHSCOPE_TEMPERATURE ?? 0.7
  )
  const maxTokens = Number(
    env.VITE_LLM_MAX_TOKENS ?? env.VITE_DASHSCOPE_MAX_TOKENS ?? env.DASHSCOPE_MAX_TOKENS ?? 3000
  )
  return { apiKey, baseUrl, model, temperature, maxTokens }
}

// ===== Agent Service Base URL =====
export const getAgentApiBaseUrl = (): string => {
  const env = import.meta.env as any
  const base = env.VITE_AGENT_BASE_URL || env.VITE_AGENT_API_BASE_URL || env.AGENT_API_BASE_URL || 'http://localhost:8089'
  return String(base).replace(/\/$/, '')
}

export default createAPIConfig