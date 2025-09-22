import { useMapStore } from '@/stores/mapStore'
import { useLoadingStore } from '@/stores/loadingStore'
import { createAPIConfig } from '@/utils/config'
import { notificationManager } from '@/utils/notification'
import { useMapStyles } from './useMapStyles'

const ol = window.ol;

// 数据加载配置常量
const DATA_CONFIG = {
  PAGE_SIZE: 10000,
  PAGINATION_DELAY: 100,
  HIT_TOLERANCE: 5,
  DEFAULT_FEATURE_COUNT: 20,
  DEFAULT_START_INDEX: 0,
  Z_INDEX: {
    COUNTY_BOUNDARY: -500,
    DEFAULT_OFFSET: 10
  }
} as const;

/**
 * 地图数据加载 Composable
 * 
 * 功能：管理GeoServer服务数据的加载，包括矢量图层和懒加载机制
 * 职责：连接GeoServer WMS/WFS、要素数据获取、图层管理、重复检查等
 * 
 * @returns {Object} 数据加载相关的方法
 */
export function useMapData() {
  const mapStore = useMapStore()
  const loadingStore = useLoadingStore()
  const { createLayerStyle } = useMapStyles()

  /**
   * 加载矢量图层 - 连接GeoServer WMS/WFS服务获取地理要素数据
   * 调用者: useMapData() -> loadVectorLayers() -> loadVectorLayer()
   * 作用: 从GeoServer服务器加载指定图层的矢量要素数据并渲染到地图上
   */
  const loadVectorLayer = async (map: any, layerConfig: any, visibleOverride?: boolean): Promise<void> => {
    // 解析图层名称（GeoServer格式：workspace:layerName）
    const layerName = layerConfig.name
    
    // 检查是否已存在懒加载图层容器
    const existingLayerInfo = mapStore.vectorlayers.find(l => l.name === layerName && l.isLazyLoaded)
    let wfsLayer: any
    
    if (existingLayerInfo && existingLayerInfo.layer) {
      // 使用已存在的图层容器（仅矢量层）
      wfsLayer = existingLayerInfo.layer
    } else {
      // 创建新的图层容器
      const style = createLayerStyle(layerConfig, layerName);

      // 创建WFS图层（矢量交互）
      const params = new URLSearchParams()
      params.set('service', 'WFS')
      params.set('request', 'GetFeature')
      params.set('version', '1.1.0')
      params.set('typeName', layerName)
      params.set('outputFormat', 'application/json')
      params.set('srsName', 'EPSG:4326')

      const wfsSource = new ol.source.Vector({
        url: mapStore.mapConfig.dataUrl + '?' + params.toString(),
        format: new ol.format.GeoJSON({ 
          dataProjection: 'EPSG:4326', 
          featureProjection: 'EPSG:4326' 
        })
      })

      wfsLayer = new ol.layer.Vector({ 
        source: wfsSource, 
        style: style 
      })
    }
    
    // ===== 添加图层到地图 =====
    // 调用者: loadVectorLayer()
    // 作用: 根据类型添加图层到地图：raster 用 WMS，vector 用 WFS
    if (!existingLayerInfo) {
      if (layerConfig.type === 'raster') {
        const wmsSource = new ol.source.TileWMS({
          url: layerConfig.dataService,
          params: {
            'LAYERS': layerName,
            'STYLES': '',
            'FORMAT': 'image/png',
            'TRANSPARENT': 'true',
            'TILED': true
          },
          serverType: 'geoserver',
          transition: 0
        })
        const wmsLayer = new ol.layer.Tile({ source: wmsSource })
        map.addLayer(wmsLayer)
        mapStore.vectorlayers.push({
          id: layerConfig.name,
          name: layerName,
          layer: wmsLayer,
          wfsLayer: undefined,
          visible: typeof visibleOverride === 'boolean' ? visibleOverride : !!layerConfig.visible,
          type: 'tile',
          source: 'geoserver'
        })
      } else {
        map.addLayer(wfsLayer)
        mapStore.vectorlayers.push({
          id: layerConfig.name,
          name: layerName,
          layer: wfsLayer,
          wfsLayer: wfsLayer,
          visible: typeof visibleOverride === 'boolean' ? visibleOverride : !!layerConfig.visible,
          type: 'vector',
          source: 'geoserver'
        })
      }
    }
    
    // ===== 设置图层可见性和样式 =====
    const resolvedVisible = typeof visibleOverride === 'boolean' ? visibleOverride : !!layerConfig.visible
    if (layerConfig.type === 'raster') {
      // visible handled on layer creation; nothing for wfsLayer here
    } else {
      wfsLayer.setVisible(resolvedVisible)
    }
    
    const zIndex = layerName.includes('县级') ? DATA_CONFIG.Z_INDEX.COUNTY_BOUNDARY : DATA_CONFIG.Z_INDEX.DEFAULT_OFFSET + mapStore.vectorlayers.length
    if (layerConfig.type !== 'raster') {
      wfsLayer.setZIndex(zIndex)
    }
    
    // ===== 加载完成通知 =====
    // 调用者: loadVectorLayer()
    // 作用: 显示图层加载完成的统计信息
    notificationManager.info(
      `图层 ${layerName} 加载完成`,
      `数据来源: GeoServer WMS/WFS\n服务器地址: ${layerConfig.dataService}\n图层类型: ${layerConfig.type}\n✅ 使用GeoServer服务`
    )
  }

  /**
   * 创建懒加载图层容器 - 创建空的图层容器，等待用户点击显示时再加载数据
   * 调用者: loadVectorLayers() -> createLazyLayerContainer()
   * 作用: 为懒加载图层创建空的OpenLayers图层容器，设置初始样式但不加载数据
   */
  /* removed lazy loading: createLazyLayerContainer no longer used */
  const createLazyLayerContainer = (map: any, layerConfig: any): void => {
    return
  }

  /**
   * 加载懒加载图层数据 - 当用户点击显示懒加载图层时调用
   * 调用者: useLayerManager.ts -> toggleLayerVisibility() -> loadLazyLayer()
   * 作用: 为已创建的懒加载图层容器加载实际的矢量数据
   */
  const loadLazyLayer = async (_layerName: string): Promise<boolean> => {
    return false
  }

  /**
   * 卸载懒加载图层数据 - 当用户点击隐藏懒加载图层时调用
   * 调用者: useLayerManager.ts -> toggleLayerVisibility() -> unloadLazyLayer()
   * 作用: 完全移除懒加载图层的数据，释放内存，但保留图层容器
   */
  const unloadLazyLayer = async (_layerName: string): Promise<boolean> => {
    return false
  }

  /**
   * 清空所有图层数据
   * 在页面刷新或重新初始化时调用，彻底清理所有图层避免重复
   */
  const clearAllLayersBeforeInit = (): void => {
    
    // 1. 清空SuperMap服务图层
    const supermapLayersCount = mapStore.vectorlayers.filter(l => l.source === 'supermap').length
    
    // 2. 清空本地图层（分析、绘制、查询、上传等）
    const localLayersCount = mapStore.vectorlayers.filter(l => l.source === 'local').length
    
    // 3. 清空自定义图层
    const customLayersCount = mapStore.customlayers.length
    
    // 4. 从地图中移除所有图层
    if (mapStore.map) {
      // 移除矢量图层
      mapStore.vectorlayers.forEach(item => {
        try { 
          mapStore.map.removeLayer(item.layer)
        } catch (_) { /* 静默处理 */ }
      })
      
      // 移除自定义图层
      mapStore.customlayers.forEach(item => {
        try { 
          mapStore.map.removeLayer(item.layer)
        } catch (_) { /* 静默处理 */ }
      })
    }
    
    // 5. 清空数组
    const totalBefore = mapStore.vectorlayers.length + mapStore.customlayers.length
    mapStore.vectorlayers.length = 0  // 清空矢量图层数组
    mapStore.customlayers.length = 0  // 清空自定义图层数组
    
    // 6. 清空选择图层的数据源
    if (mapStore.selectlayer?.getSource) {
      try {
        mapStore.selectlayer.getSource().clear()
      } catch (_) { /* 静默处理 */ }
    }
    
  }

  /**
   * 加载所有矢量图层
   * 在加载前彻底清空所有图层，避免重复添加
   */
  const loadVectorLayers = async (map: any): Promise<void> => {
    // ===== 首先清空所有现有图层 =====
    clearAllLayersBeforeInit()
    
    const apiConfig = createAPIConfig()
    
    for (const layerConfig of apiConfig.wuhanlayers) {
      const layerName = layerConfig.name
      if (layerConfig.type === 'raster') {
        continue
      }
      loadingStore.updateLoading('map-init', `正在加载图层: ${layerName}`)
      // 使用配置中的 visible 作为初始可见性
      await loadVectorLayer(map, layerConfig)
    }
  }

  return {
    loadVectorLayer,
    loadVectorLayers,
    createLazyLayerContainer,
    loadLazyLayer,
    unloadLazyLayer,
    clearAllLayersBeforeInit
  }
}
