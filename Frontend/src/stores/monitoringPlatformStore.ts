import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { monitoringSites, getMonitoringSiteData, getAllMonitoringSitesData, type WaterQualityData, type MonitoringSite } from '@/data/waterQualityMockData'

export interface MonitoringSiteInfo {
  id: string
  name: string
  location: string
  coordinates: [number, number]
  layerName: string
  waterQualityClass: string
}

export interface MonitoringPlatformState {
  // 监测点基础信息
  sites: MonitoringSiteInfo[]
  selectedSite: MonitoringSiteInfo | null
  
  // 实时数据状态
  realTimeData: Map<string, WaterQualityData[]>
  lastUpdateTime: Map<string, Date>
  
  // 阈值检测状态
  thresholdViolations: Array<{
    siteName: string
    parameter: string
    value: number
    threshold: { min: number; max: number }
    timestamp: Date
  }>
  
  // 监测状态
  isMonitoring: boolean
  lastCheckTime: Date | null
  
  // 图层状态
  monitoringLayers: Map<string, any>
  layersVisible: Map<string, boolean>
}

const useMonitoringPlatformStore = defineStore('monitoringPlatform', () => {
  // 监测点基础信息
  const sites = ref<MonitoringSiteInfo[]>([
    {
      id: 'wuhu-pump-station',
      name: '湖北省新洲县阳逻镇武湖泵站',
      location: '武湖泵站',
      coordinates: [114.7856, 30.8456],
      layerName: '阳逻',
      waterQualityClass: 'Ⅱ'
    },
    {
      id: 'nanwangshan',
      name: '湖北省武汉市南望山',
      location: '南望山',
      coordinates: [114.3125, 30.5268],
      layerName: '东湖',
      waterQualityClass: 'Ⅰ'
    },
    {
      id: 'wujiashan',
      name: '湖北省武汉市东西湖区吴家山',
      location: '吴家山',
      coordinates: [114.1456, 30.6234],
      layerName: '汉口(吴家山)',
      waterQualityClass: 'Ⅲ'
    },
    {
      id: 'jinshuizha',
      name: '湖北省武昌县金口镇金水闸',
      location: '金水闸',
      coordinates: [114.2678, 30.4567],
      layerName: '金口',
      waterQualityClass: 'Ⅱ'
    }
  ])

  // 当前选中的监测点
  const selectedSite = ref<MonitoringSiteInfo | null>(null)
  
  // 实时数据存储
  const realTimeData = ref<Map<string, WaterQualityData[]>>(new Map())
  
  // 最后更新时间
  const lastUpdateTime = ref<Map<string, Date>>(new Map())
  
  // 阈值违规记录
  const thresholdViolations = ref<Array<{
    siteName: string
    parameter: string
    value: number
    threshold: { min: number; max: number }
    timestamp: Date
  }>>([])
  
  // 监测状态
  const isMonitoring = ref(false)
  const lastCheckTime = ref<Date | null>(null)
  
  // 图层状态
  const monitoringLayers = ref<Map<string, any>>(new Map())
  const layersVisible = ref<Map<string, boolean>>(new Map())

  // 计算属性：根据ID获取监测点信息
  const getSiteById = computed(() => {
    return (id: string) => sites.value.find(site => site.id === id)
  })

  // 计算属性：根据名称获取监测点信息
  const getSiteByName = computed(() => {
    return (name: string) => sites.value.find(site => site.name === name)
  })

  // 计算属性：根据图层名称获取监测点信息
  const getSiteByLayerName = computed(() => {
    return (layerName: string) => sites.value.find(site => site.layerName === layerName)
  })

  // 计算属性：根据坐标获取监测点信息
  const getSiteByCoordinates = computed(() => {
    return (coordinates: [number, number]) => {
      return sites.value.find(site => 
        Math.abs(site.coordinates[0] - coordinates[0]) < 0.0001 &&
        Math.abs(site.coordinates[1] - coordinates[1]) < 0.0001
      )
    }
  })

  // 计算属性：获取所有监测点
  const getAllSites = computed(() => {
    return sites.value
  })

  // 计算属性：获取违规历史记录
  const getViolationHistory = computed(() => {
    return thresholdViolations.value.sort((a, b) => b.timestamp.getTime() - a.timestamp.getTime())
  })

  // 计算属性：获取实时数据状态
  const getRealTimeDataStatus = computed(() => {
    const status: Record<string, any> = {}
    realTimeData.value.forEach((data, siteName) => {
      const lastUpdate = lastUpdateTime.value.get(siteName)
      status[siteName] = {
        dataCount: data.length,
        lastUpdate: lastUpdate,
        hasData: data.length > 0
      }
    })
    return status
  })

  // 计算属性：获取图层状态
  const getLayersStatus = computed(() => {
    const status: Record<string, any> = {}
    monitoringLayers.value.forEach((layer, siteId) => {
      const siteInfo = getSiteById.value(siteId)
      const visible = layersVisible.value.get(siteId) || false
      status[siteId] = {
        visible,
        layerName: siteInfo?.layerName,
        siteInfo
      }
    })
    return status
  })

  // Actions - 监测点管理
  function setSelectedSite(site: MonitoringSiteInfo | null) {
    selectedSite.value = site
    lastCheckTime.value = new Date()
    
    // 触发自定义事件，通知ChatAssistant
    if (site) {
      const event = new CustomEvent('monitoring:siteSelected', {
        detail: {
          site,
          coordinates: site.coordinates,
          layerName: site.layerName,
          timestamp: lastCheckTime.value
        }
      })
      window.dispatchEvent(event)
    }
  }

  function selectSiteById(id: string) {
    const site = getSiteById.value(id)
    if (site) {
      setSelectedSite(site)
    }
  }

  function selectSiteByName(name: string) {
    const site = getSiteByName.value(name)
    if (site) {
      setSelectedSite(site)
    }
  }

  function selectSiteByLayerName(layerName: string) {
    const site = getSiteByLayerName.value(layerName)
    if (site) {
      setSelectedSite(site)
    }
  }

  function selectSiteByCoordinates(coordinates: [number, number]) {
    const site = getSiteByCoordinates.value(coordinates)
    if (site) {
      setSelectedSite(site)
    }
  }

  function clearSelectedSite() {
    setSelectedSite(null)
  }

  function updateSiteWaterQuality(id: string, waterQualityClass: string) {
    const site = sites.value.find(s => s.id === id)
    if (site) {
      site.waterQualityClass = waterQualityClass
      lastCheckTime.value = new Date()
    }
  }

  // Actions - 实时数据管理
  function setRealTimeData(siteName: string, data: WaterQualityData[]) {
    realTimeData.value.set(siteName, data)
    lastUpdateTime.value.set(siteName, new Date())
  }

  function getRealTimeData(siteName: string): WaterQualityData[] {
    return realTimeData.value.get(siteName) || []
  }

  function addRealTimeDataPoint(siteName: string, dataPoint: WaterQualityData) {
    const currentData = realTimeData.value.get(siteName) || []
    const newData = [...currentData, dataPoint]
    
    // 保持最近60个数据点
    if (newData.length > 60) {
      newData.splice(0, newData.length - 60)
    }
    
    realTimeData.value.set(siteName, newData)
    lastUpdateTime.value.set(siteName, new Date())
  }

  function clearRealTimeData(siteName?: string) {
    if (siteName) {
      realTimeData.value.delete(siteName)
      lastUpdateTime.value.delete(siteName)
    } else {
      realTimeData.value.clear()
      lastUpdateTime.value.clear()
    }
  }

  // 别名方法，用于兼容useRealTimeWaterQuality
  function getRealTimeDataBySite(siteName: string): WaterQualityData[] {
    return getRealTimeData(siteName)
  }

  function setRealTimeDataForSite(siteName: string, data: WaterQualityData[]) {
    setRealTimeData(siteName, data)
  }

  // Actions - 阈值检测管理
  function addThresholdViolation(violation: {
    siteName: string
    parameter: string
    value: number
    threshold: { min: number; max: number }
    timestamp: Date
  }) {
    thresholdViolations.value.push(violation)
  }

  function clearViolationHistory() {
    thresholdViolations.value = []
  }

  function getViolationsBySite(siteName: string) {
    return thresholdViolations.value.filter(v => v.siteName === siteName)
  }

  // Actions - 监测状态管理
  function startMonitoring() {
    isMonitoring.value = true
    lastCheckTime.value = new Date()
  }

  function stopMonitoring() {
    isMonitoring.value = false
  }

  // Actions - 图层管理
  function setMonitoringLayer(siteId: string, layer: any) {
    monitoringLayers.value.set(siteId, layer)
  }

  function getMonitoringLayer(siteId: string) {
    return monitoringLayers.value.get(siteId)
  }

  function removeMonitoringLayer(siteId: string) {
    monitoringLayers.value.delete(siteId)
    layersVisible.value.delete(siteId)
  }

  function setLayerVisibility(siteId: string, visible: boolean) {
    layersVisible.value.set(siteId, visible)
    const layer = monitoringLayers.value.get(siteId)
    if (layer) {
      layer.setVisible(visible)
    }
  }

  function getLayerVisibility(siteId: string): boolean {
    return layersVisible.value.get(siteId) || false
  }

  function clearAllMonitoringLayers() {
    monitoringLayers.value.clear()
    layersVisible.value.clear()
  }

  // Actions - 数据同步（与现有mock数据同步）
  function syncWithMockData() {
    // 同步静态mock数据到实时数据存储
    const mockSites = getAllMonitoringSitesData()
    mockSites.forEach(mockSite => {
      const siteInfo = getSiteByName.value(mockSite.name)
      if (siteInfo) {
        setRealTimeData(mockSite.name, mockSite.data)
      }
    })
  }

  function getMockDataForSite(siteName: string): MonitoringSite | undefined {
    return getMonitoringSiteData(siteName)
  }

  // 初始化时同步mock数据
  function initializeStore() {
    syncWithMockData()
    lastCheckTime.value = new Date()
  }

  return {
    // State
    sites,
    selectedSite,
    realTimeData,
    lastUpdateTime,
    thresholdViolations,
    isMonitoring,
    lastCheckTime,
    monitoringLayers,
    layersVisible,
    
    // Computed
    getSiteById,
    getSiteByName,
    getSiteByLayerName,
    getSiteByCoordinates,
    getAllSites,
    getViolationHistory,
    getRealTimeDataStatus,
    getLayersStatus,
    
    // Actions - 监测点管理
    setSelectedSite,
    selectSiteById,
    selectSiteByName,
    selectSiteByLayerName,
    selectSiteByCoordinates,
    clearSelectedSite,
    updateSiteWaterQuality,
    
    // Actions - 实时数据管理
    setRealTimeData,
    getRealTimeData,
    addRealTimeDataPoint,
    clearRealTimeData,
    getRealTimeDataBySite,
    setRealTimeDataForSite,
    
    // Actions - 阈值检测管理
    addThresholdViolation,
    clearViolationHistory,
    getViolationsBySite,
    
    // Actions - 监测状态管理
    startMonitoring,
    stopMonitoring,
    
    // Actions - 图层管理
    setMonitoringLayer,
    getMonitoringLayer,
    removeMonitoringLayer,
    setLayerVisibility,
    getLayerVisibility,
    clearAllMonitoringLayers,
    
    // Actions - 数据同步
    syncWithMockData,
    getMockDataForSite,
    initializeStore
  }
})

export { useMonitoringPlatformStore }
export default useMonitoringPlatformStore

