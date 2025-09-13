import { ref, computed } from 'vue'
import { useMapStore } from '@/stores/mapStore'
import { useLayerDataStore } from '@/stores/layerDataStore'
import { useMapStyles } from '@/composables/useMapStyles'

const ol = window.ol

/**
 * 长江水系图层管理 Composable
 * 
 * 功能：管理长江水系线和长江面图层的显示，使用与管理分析平台相同的颜色和注记方式
 * 职责：图层加载、样式设置、事件处理等
 */
export function useYangtzeWaterLayers() {
  const mapStore = useMapStore()
  const layerDataStore = useLayerDataStore()
  const { createLocalLayerStyle } = useMapStyles()

  // 长江图层存储
  const yangtzeLayers = ref<Map<string, any>>(new Map())

  /**
   * 创建长江水系线样式
   * 使用与监测预警可视化平台相同的样式系统，包括注记样式
   * @param layerName 图层名称
   * @returns OpenLayers样式对象
   */
  const createYangtzeLineStyle = (layerName: string) => {
    return new ol.style.Style({
      stroke: new ol.style.Stroke({
        color: '#1976d2', // 深蓝色线条
        width: 4 // 加粗线条
      }),
      text: new ol.style.Text({
        text: '长江',
        font: 'bold 14px Arial', // 加粗字体
        fill: new ol.style.Fill({
          color: '#000000' // 黑色文字
        }),
        stroke: new ol.style.Stroke({
          color: '#ffffff', // 白色描边
          width: 3 // 加粗描边
        }),
        offsetY: -15,
        textAlign: 'center'
      })
    })
  }

  /**
   * 创建长江水系面样式
   * 使用与监测预警可视化平台相同的样式系统，包括注记样式
   * @param layerName 图层名称
   * @returns OpenLayers样式对象
   */
  const createYangtzePolygonStyle = (layerName: string) => {
    return new ol.style.Style({
      fill: new ol.style.Fill({
        color: 'rgba(25, 118, 210, 0.3)' // 深蓝色半透明填充
      }),
      stroke: new ol.style.Stroke({
        color: '#1976d2', // 深蓝色描边
        width: 3 // 加粗描边
      }),
      text: new ol.style.Text({
        text: '长江',
        font: 'bold 14px Arial', // 加粗字体
        fill: new ol.style.Fill({
          color: '#000000' // 黑色文字
        }),
        stroke: new ol.style.Stroke({
          color: '#ffffff', // 白色描边
          width: 3 // 加粗描边
        }),
        offsetY: 0,
        textAlign: 'center'
      })
    })
  }

  /**
   * 加载长江水系线图层
   */
  const loadYangtzeLineLayer = async () => {
    if (!mapStore.map) {
      console.warn('地图未初始化，无法加载长江水系线图层')
      return
    }

    try {
      // 检查是否已存在懒加载图层容器
      const existingLayerInfo = mapStore.vectorlayers.find(l => 
        l.name === '长江水系线' && 
        l.source === 'local' && 
        l.layer.get('sourceType') === 'upload'
      )
      
      if (existingLayerInfo && existingLayerInfo.layer) {
        // 图层已存在，直接返回
        return
      }

      // 获取长江线数据
      const response = await fetch('/src/views/dashboard/ViewPage/monitordata/长江线.geojson')
      const geojsonData = await response.json()

      // 创建OpenLayers要素
      const features = new ol.format.GeoJSON().readFeatures(geojsonData, {
        featureProjection: mapStore.map.getView().getProjection()
      })

      // 为每个要素设置属性
      features.forEach((feature: any, index: number) => {
        const properties = feature.getProperties()
        
        // 设置要素属性（直接设置在要素对象上）
        feature.set('id', `yangtze-line-${index}`)
        feature.set('layer_name', '长江水系线')
        feature.set('water_system', '长江')
        feature.set('geometry_type', 'LineString')
        feature.set('feature_type', '水系线')
        feature.set('data_source', '监测预警平台')
        feature.set('last_update', new Date().toISOString())
        
        // 保留原始属性
        Object.keys(properties).forEach(key => {
          if (key !== 'geometry') {
            feature.set(key, properties[key])
          }
        })
      })

      // 创建矢量源
      const vectorSource = new ol.source.Vector({
        features: features
      })

      // 创建矢量图层
      const vectorLayer = new ol.layer.Vector({
        source: vectorSource,
        style: createYangtzeLineStyle('长江水系线'),
        visible: true,
        zIndex: 900 // 确保在水系面之上
      })

      // 设置图层属性
      vectorLayer.set('layerName', '长江水系线')
      vectorLayer.set('layerType', 'yangtze')
      vectorLayer.set('sourceType', 'upload') // 设置为upload类型，显示在上传图层分组中
      vectorLayer.set('waterSystem', '长江')
      vectorLayer.set('description', '监测预警平台 - 长江水系线')

      // 添加到地图
      mapStore.map.addLayer(vectorLayer)

      // 添加到图层管理列表
      const layerInfo = {
        id: 'yangtze-line',
        name: '长江水系线',
        layer: vectorLayer,
        visible: true,
        type: 'vector' as const,
        source: 'local' as const
      }
      
      mapStore.vectorlayers.push(layerInfo)
      mapStore.vectorlayers = [...mapStore.vectorlayers] // 强制触发响应式更新

      // 存储图层引用
      yangtzeLayers.value.set('yangtze-line', vectorLayer)

      // 保存属性数据到layerDataStore
      const featureDataArray = features.map((feature: any, index: number) => ({
        id: `yangtze-line-${index}`,
        properties: {
          id: `yangtze-line-${index}`,
          layer_name: '长江水系线',
          water_system: '长江',
          geometry_type: 'LineString',
          feature_type: '水系线',
          data_source: '监测预警平台',
          last_update: new Date().toISOString(),
          ...feature.getProperties()
        }
      }))
      
      layerDataStore.setLayerAttributes('长江水系线', featureDataArray)

    } catch (error) {
      console.error('加载长江水系线图层失败:', error)
    }
  }

  /**
   * 加载长江水系面图层
   */
  const loadYangtzePolygonLayer = async () => {
    if (!mapStore.map) {
      console.warn('地图未初始化，无法加载长江水系面图层')
      return
    }

    try {
      // 检查是否已存在懒加载图层容器
      const existingLayerInfo = mapStore.vectorlayers.find(l => 
        l.name === '长江水系面' && 
        l.source === 'local' && 
        l.layer.get('sourceType') === 'upload'
      )
      
      if (existingLayerInfo && existingLayerInfo.layer) {
        // 图层已存在，直接返回
        return
      }

      // 获取长江面数据
      const response = await fetch('/src/views/dashboard/ViewPage/monitordata/长江面.geojson')
      const geojsonData = await response.json()

      // 创建OpenLayers要素
      const features = new ol.format.GeoJSON().readFeatures(geojsonData, {
        featureProjection: mapStore.map.getView().getProjection()
      })

      // 为每个要素设置属性
      features.forEach((feature: any, index: number) => {
        const properties = feature.getProperties()
        
        // 设置要素属性（直接设置在要素对象上）
        feature.set('id', `yangtze-polygon-${index}`)
        feature.set('layer_name', '长江水系面')
        feature.set('water_system', '长江')
        feature.set('geometry_type', 'MultiPolygon')
        feature.set('feature_type', '水系面')
        feature.set('data_source', '监测预警平台')
        feature.set('last_update', new Date().toISOString())
        
        // 保留原始属性
        Object.keys(properties).forEach(key => {
          if (key !== 'geometry') {
            feature.set(key, properties[key])
          }
        })
      })

      // 创建矢量源
      const vectorSource = new ol.source.Vector({
        features: features
      })

      // 创建矢量图层
      const vectorLayer = new ol.layer.Vector({
        source: vectorSource,
        style: createYangtzePolygonStyle('长江水系面'),
        visible: true,
        zIndex: 800 // 确保在水系线之下
      })

      // 设置图层属性
      vectorLayer.set('layerName', '长江水系面')
      vectorLayer.set('layerType', 'yangtze')
      vectorLayer.set('sourceType', 'upload') // 设置为upload类型，显示在上传图层分组中
      vectorLayer.set('waterSystem', '长江')
      vectorLayer.set('description', '监测预警平台 - 长江水系面')

      // 添加到地图
      mapStore.map.addLayer(vectorLayer)

      // 添加到图层管理列表
      const layerInfo = {
        id: 'yangtze-polygon',
        name: '长江水系面',
        layer: vectorLayer,
        visible: true,
        type: 'vector' as const,
        source: 'local' as const
      }
      
      mapStore.vectorlayers.push(layerInfo)
      mapStore.vectorlayers = [...mapStore.vectorlayers] // 强制触发响应式更新

      // 存储图层引用
      yangtzeLayers.value.set('yangtze-polygon', vectorLayer)

      // 保存属性数据到layerDataStore
      const featureDataArray = features.map((feature: any, index: number) => ({
        id: `yangtze-polygon-${index}`,
        properties: {
          id: `yangtze-polygon-${index}`,
          layer_name: '长江水系面',
          water_system: '长江',
          geometry_type: 'MultiPolygon',
          feature_type: '水系面',
          data_source: '监测预警平台',
          last_update: new Date().toISOString(),
          ...feature.getProperties()
        }
      }))
      
      layerDataStore.setLayerAttributes('长江水系面', featureDataArray)

    } catch (error) {
      console.error('加载长江水系面图层失败:', error)
    }
  }

  /**
   * 加载所有长江水系图层
   */
  const loadAllYangtzeLayers = async () => {
    await loadYangtzePolygonLayer() // 先加载面图层（底层）
    await loadYangtzeLineLayer()    // 再加载线图层（上层）
  }

  /**
   * 卸载长江水系图层
   * @param layerId 图层ID
   */
  const unloadYangtzeLayer = (layerId: string) => {
    const layer = yangtzeLayers.value.get(layerId)
    if (layer && mapStore.map) {
      // 从mapStore的vectorlayers中移除
      const layerIndex = mapStore.vectorlayers.findIndex(l => l.id === layerId)
      if (layerIndex > -1) {
        mapStore.vectorlayers.splice(layerIndex, 1)
        mapStore.vectorlayers = [...mapStore.vectorlayers]
      }
      
      // 从layerDataStore中清理属性数据
      const layerName = layer.get('layerName')
      if (layerName) {
        layerDataStore.clearLayerData(layerName)
      }
      
      // 从地图中移除
      mapStore.map.removeLayer(layer)
      yangtzeLayers.value.delete(layerId)
    }
  }

  /**
   * 卸载所有长江水系图层
   */
  const unloadAllYangtzeLayers = () => {
    if (mapStore.map) {
      yangtzeLayers.value.forEach((layer, layerId) => {
        // 从mapStore的vectorlayers中移除
        const layerIndex = mapStore.vectorlayers.findIndex(l => l.id === layerId)
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
      
      mapStore.vectorlayers = [...mapStore.vectorlayers]
      yangtzeLayers.value.clear()
    }
  }

  /**
   * 切换长江水系图层可见性
   * @param layerId 图层ID
   * @param visible 是否可见
   */
  const toggleYangtzeLayerVisibility = (layerId: string, visible: boolean) => {
    const layer = yangtzeLayers.value.get(layerId)
    if (layer) {
      layer.setVisible(visible)
    }
  }

  /**
   * 获取长江水系图层状态
   */
  const getYangtzeLayersStatus = computed(() => {
    const status: Record<string, any> = {}
    
    yangtzeLayers.value.forEach((layer, layerId) => {
      status[layerId] = {
        visible: layer.getVisible(),
        layerName: layer.get('layerName'),
        waterSystem: layer.get('waterSystem')
      }
    })
    
    return status
  })

  return {
    // 状态
    yangtzeLayers: computed(() => yangtzeLayers.value),
    getYangtzeLayersStatus,
    
    // 方法
    loadYangtzeLineLayer,
    loadYangtzePolygonLayer,
    loadAllYangtzeLayers,
    unloadYangtzeLayer,
    unloadAllYangtzeLayers,
    toggleYangtzeLayerVisibility,
    createYangtzeLineStyle,
    createYangtzePolygonStyle
  }
}
