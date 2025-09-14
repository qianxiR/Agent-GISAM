import { ref, computed } from 'vue'
import { useMapStore } from '@/stores/mapStore'
import { useMonitoringPlatformStore } from '@/stores/monitoringPlatformStore'
import { useThemeStore } from '@/stores/themeStore'
import { useLayerDataStore } from '@/stores/layerDataStore'
import { useMapStyles } from '@/composables/useMapStyles'
import { uselayermanager } from '@/composables/useLayerManager'

const ol = window.ol

/**
 * 监测数据图层管理 Composable
 * 
 * 功能：管理四个监测点的图层显示，使用与管理分析平台相同的颜色和注记方式
 * 职责：图层加载、样式设置、事件处理等
 */
export function useMonitoringDataLayers() {
  const mapStore = useMapStore()
  const monitoringPlatformStore = useMonitoringPlatformStore()
  const themeStore = useThemeStore()
  const layerDataStore = useLayerDataStore()
  const { createLocalLayerStyle } = useMapStyles()

  // 监测点图层存储
  const monitoringLayers = ref<Map<string, any>>(new Map())

  /**
   * 创建监测点样式
   * 使用与监测预警可视化平台相同的样式系统，包括注记样式
   * @param waterQualityClass 水质类别（保留参数以保持接口一致性）
   * @param siteName 监测点名称
   * @returns OpenLayers样式对象
   */
  const createMonitoringPointStyle = (waterQualityClass: string, siteName: string) => {
    // 获取基础样式
    const baseStyle = createLocalLayerStyle('upload')
    
    // 创建与监测预警可视化平台完全相同的注记样式
    const monitoringPointStyle = new ol.style.Style({
      image: new ol.style.Circle({
        radius: 12, // 与监测预警平台相同的大小
        fill: new ol.style.Fill({
          color: '#1976d2' // 更深的蓝色填充
        }),
        stroke: new ol.style.Stroke({
          color: '#0d47a1', // 更深的蓝色描边
          width: 3 // 与监测预警平台相同的描边宽度
        })
      }),
      text: new ol.style.Text({
        text: siteName,
        font: 'bold 12px Arial', // 与监测预警平台相同的字体
        fill: new ol.style.Fill({
          color: '#000000' // 黑色文字，与监测预警平台相同
        }),
        stroke: new ol.style.Stroke({
          color: '#ffffff', // 白色描边，与监测预警平台相同
          width: 2 // 与监测预警平台相同的描边宽度
        }),
        offsetY: -20, // 与监测预警平台相同的位置偏移
        textAlign: 'center'
      })
    })
    
    return monitoringPointStyle
  }

  /**
   * 加载单个监测点图层
   * @param siteInfo 监测点信息
   */
  const loadMonitoringSiteLayer = (siteInfo: any) => {
    if (!mapStore.map) {
      console.warn('地图未初始化，无法加载监测点图层')
      return
    }

    try {
      // 检查是否已存在懒加载图层容器
      const existingLayerInfo = mapStore.vectorlayers.find(l => 
        l.name === siteInfo.layerName && 
        l.source === 'local' && 
        l.layer.get('sourceType') === 'upload'
      )
      
      if (existingLayerInfo && existingLayerInfo.layer) {
        // 图层已存在，直接返回
        return
      }

      // 创建GeoJSON要素
      const feature = new ol.Feature({
        geometry: new ol.geom.Point(siteInfo.coordinates)
      })
      
      // 设置要素属性（直接设置在要素对象上，而不是properties字段中）
      feature.set('id', siteInfo.id)
      feature.set('site_name', siteInfo.name)
      feature.set('location', siteInfo.location)
      feature.set('water_quality_class', siteInfo.waterQualityClass)
      feature.set('coordinates', siteInfo.coordinates)
      feature.set('monitor_type', '水质监测')
      feature.set('data_source', '监测预警平台')
      feature.set('last_update', new Date().toISOString())

      // 创建矢量源
      const vectorSource = new ol.source.Vector({
        features: [feature]
      })

      // 创建矢量图层
      const vectorLayer = new ol.layer.Vector({
        source: vectorSource,
        style: createMonitoringPointStyle(siteInfo.waterQualityClass, siteInfo.layerName),
        visible: true,
        zIndex: 1000 // 确保监测点图层在最上层
      })

      // 设置图层属性 - 关键：设置为upload类型以便在图层管理面板中显示
      vectorLayer.set('layerName', siteInfo.layerName)
      vectorLayer.set('layerType', 'monitoring')
      vectorLayer.set('sourceType', 'upload') // 设置为upload类型，显示在上传图层分组中
      vectorLayer.set('siteId', siteInfo.id)
      vectorLayer.set('description', `监测预警平台 - ${siteInfo.location}`)

      // 添加到地图
      mapStore.map.addLayer(vectorLayer)

      // 添加到mapStore的vectorlayers中，使其在图层管理面板中显示
      const layerInfo = {
        id: siteInfo.id,
        name: siteInfo.layerName,
        layer: vectorLayer,
        visible: true,
        type: 'vector' as const,
        source: 'local' as const
      }
      
      // 添加到图层管理列表
      mapStore.vectorlayers.push(layerInfo)
      
      // 强制触发响应式更新
      mapStore.vectorlayers = [...mapStore.vectorlayers]

      // 存储图层引用
      monitoringLayers.value.set(siteInfo.id, vectorLayer)
      
      // 同步到监测平台store
      monitoringPlatformStore.setMonitoringLayer(siteInfo.id, vectorLayer)
      monitoringPlatformStore.setLayerVisibility(siteInfo.id, true)

      // 保存属性数据到layerDataStore，用于管理分析平台的要素信息显示
      const featureData = {
        id: siteInfo.id,
        properties: {
          id: siteInfo.id,
          site_name: siteInfo.name,
          location: siteInfo.location,
          water_quality_class: siteInfo.waterQualityClass,
          coordinates: siteInfo.coordinates,
          monitor_type: '水质监测',
          data_source: '监测预警平台',
          last_update: new Date().toISOString()
        }
      }
      
      layerDataStore.setLayerAttributes(siteInfo.layerName, [featureData])

    } catch (error) {
      console.error(`加载监测点图层失败: ${siteInfo.layerName}`, error)
    }
  }


  /**
   * 加载所有监测点图层
   */
  const loadAllMonitoringLayers = () => {
    // 先清理已存在的监测点图层，避免重复加载
    unloadAllMonitoringLayers()
    
    const sites = monitoringPlatformStore.getAllSites
    
    sites.forEach(site => {
      loadMonitoringSiteLayer(site)
    })
  }

  /**
   * 卸载监测点图层
   * @param siteId 监测点ID
   */
  const unloadMonitoringLayer = (siteId: string) => {
    const layer = monitoringLayers.value.get(siteId)
    if (layer && mapStore.map) {
      // 从mapStore的vectorlayers中移除
      const layerIndex = mapStore.vectorlayers.findIndex(l => l.id === siteId)
      if (layerIndex > -1) {
        mapStore.vectorlayers.splice(layerIndex, 1)
        // 强制触发响应式更新
        mapStore.vectorlayers = [...mapStore.vectorlayers]
      }
      
      // 从地图中移除
      mapStore.map.removeLayer(layer)
      
      // 从layerDataStore中清理属性数据
      const layerName = layer.get('layerName')
      if (layerName) {
        layerDataStore.clearLayerData(layerName)
      }
      
      monitoringLayers.value.delete(siteId)
      
      // 同步到监测平台store
      monitoringPlatformStore.removeMonitoringLayer(siteId)
    }
  }

  /**
   * 卸载所有监测点图层
   */
  const unloadAllMonitoringLayers = () => {
    if (mapStore.map) {
      monitoringLayers.value.forEach((layer, siteId) => {
        // 从mapStore的vectorlayers中移除
        const layerIndex = mapStore.vectorlayers.findIndex(l => l.id === siteId)
        if (layerIndex > -1) {
          mapStore.vectorlayers.splice(layerIndex, 1)
        }
        
        // 从layerDataStore中清理属性数据
        const layerName = layer.get('layerName')
        if (layerName) {
          layerDataStore.clearLayerData(layerName)
        }
        
        // 从地图中移除
        mapStore.map.removeLayer(layer)
      })
      
      // 强制触发响应式更新
      mapStore.vectorlayers = [...mapStore.vectorlayers]
      monitoringLayers.value.clear()
      
      // 同步到监测平台store
      monitoringPlatformStore.clearAllMonitoringLayers()
    }
  }

  /**
   * 切换监测点图层可见性
   * @param siteId 监测点ID
   * @param visible 是否可见
   */
  const toggleMonitoringLayerVisibility = (siteId: string, visible: boolean) => {
    const layer = monitoringLayers.value.get(siteId)
    if (layer) {
      layer.setVisible(visible)
      // 同步到监测平台store
      monitoringPlatformStore.setLayerVisibility(siteId, visible)
    }
  }

  /**
   * 更新监测点样式（当水质类别变化时）
   * @param siteId 监测点ID
   * @param newWaterQualityClass 新的水质类别
   */
  const updateMonitoringLayerStyle = (siteId: string, newWaterQualityClass: string) => {
    const layer = monitoringLayers.value.get(siteId)
    const siteInfo = monitoringPlatformStore.getSiteById(siteId)
    
    if (layer && siteInfo) {
      const newStyle = createMonitoringPointStyle(newWaterQualityClass, siteInfo.location)
      layer.setStyle(newStyle)
    }
  }

  /**
   * 获取监测点图层状态
   */
  const getMonitoringLayersStatus = computed(() => {
    return monitoringPlatformStore.getLayersStatus
  })

  return {
    // 状态
    monitoringLayers: computed(() => monitoringLayers.value),
    getMonitoringLayersStatus,
    
    // 方法
    loadMonitoringSiteLayer,
    loadAllMonitoringLayers,
    unloadMonitoringLayer,
    unloadAllMonitoringLayers,
    toggleMonitoringLayerVisibility,
    updateMonitoringLayerStyle,
    createMonitoringPointStyle
  }
}
