import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { monitoringSites } from '@/data/waterQualityMockData'

export interface MonitoringSiteInfo {
  id: string
  name: string
  location: string
  coordinates: [number, number]
  layerName: string
  waterQualityClass: string
}

export interface MonitoringDataState {
  sites: MonitoringSiteInfo[]
  selectedSite: MonitoringSiteInfo | null
  lastUpdateTime: Date | null
}

const useMonitoringDataStore = defineStore('monitoringData', () => {
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
  
  // 最后更新时间
  const lastUpdateTime = ref<Date | null>(null)

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

  // Actions
  function setSelectedSite(site: MonitoringSiteInfo | null) {
    selectedSite.value = site
    lastUpdateTime.value = new Date()
    
    // 触发自定义事件，通知ChatAssistant
    if (site) {
      const event = new CustomEvent('monitoring:siteSelected', {
        detail: {
          site,
          coordinates: site.coordinates,
          layerName: site.layerName,
          timestamp: lastUpdateTime.value
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
      lastUpdateTime.value = new Date()
    }
  }

  function getAllSites() {
    return sites.value
  }

  function getSelectedSiteCoordinates() {
    return selectedSite.value?.coordinates || null
  }

  function getSelectedSiteLayerName() {
    return selectedSite.value?.layerName || null
  }

  return {
    // State
    sites,
    selectedSite,
    lastUpdateTime,
    
    // Computed
    getSiteById,
    getSiteByName,
    getSiteByLayerName,
    getSiteByCoordinates,
    
    // Actions
    setSelectedSite,
    selectSiteById,
    selectSiteByName,
    selectSiteByLayerName,
    selectSiteByCoordinates,
    clearSelectedSite,
    updateSiteWaterQuality,
    getAllSites,
    getSelectedSiteCoordinates,
    getSelectedSiteLayerName
  }
})

export { useMonitoringDataStore }
export default useMonitoringDataStore
