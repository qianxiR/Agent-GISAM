import { useMapStore } from '@/stores/mapStore'
import { useLoadingStore } from '@/stores/loadingStore'
import { useLayerDataStore } from '@/stores/layerDataStore'
import { createAPIConfig } from '@/utils/config'
import { notificationManager } from '@/utils/notification'
import { useMapStyles } from './useMapStyles'
import { superMapClient } from '@/api/supermap'
import { uselayermanager } from './useLayerManager'

const ol = window.ol;

// 数据加载配置常量
const DATA_CONFIG = {
  PAGE_SIZE: 20, // 根据SuperMap API文档，每页20个要素
  PAGINATION_DELAY: 100,
  HIT_TOLERANCE: 5,
  DEFAULT_FEATURE_COUNT: 20,
  DEFAULT_START_INDEX: 0,
  Z_INDEX: {
    COUNTY_BOUNDARY: -500,
    CITY_BOUNDARY: -1000, // 武汉_市级图层使用更低的Z-index
    DEFAULT_OFFSET: 10
  }
} as const;

/**
 * 地图数据加载 Composable
 * 
 * 功能：管理SuperMap服务数据的加载，包括矢量图层和懒加载机制
 * 职责：连接SuperMap iServer、要素数据获取、分页加载、重复检查等
 * 
 * @returns {Object} 数据加载相关的方法
 */
export function useMapData() {
  const mapStore = useMapStore()
  const loadingStore = useLoadingStore()
  const layerDataStore = useLayerDataStore()
  const { createLayerStyle } = useMapStyles()
  const { saveFeaturesAslayer } = uselayermanager()

  /**
   * 加载矢量图层 - 使用SuperMap数据服务按属性方式加载
   * 调用者: useMapData() -> loadVectorLayers() -> loadVectorLayer()
   * 作用: 从SuperMap数据服务获取要素数据，转换为矢量图层并渲染到地图上
   * 
   * 入参:
   * - map (ol.Map): OpenLayers地图实例
   * - layerConfig (Object): 图层配置对象，包含图层名称、类型、可见性等
   * - visibleOverride (boolean, 可选): 覆盖配置中的可见性设置
   * 
   * 方法:
   * - 使用SuperMap数据服务API获取要素数据
   * - 将SuperMap要素数据转换为GeoJSON格式
   * - 使用OpenLayers GeoJSON格式器创建Feature对象
   * - 创建矢量图层并添加到地图
   * 
   * 出参:
   * - Promise<void>: 图层加载完成的Promise
   */
  /**
   * 修复GeoJSON坐标格式：将 {x, y} 对象转换为 [x, y] 数组
   */
  const fixGeoJSONCoordinates = (geojson: any): any => {
    if (!geojson || typeof geojson !== 'object') {
      return geojson
    }
    
    // 如果是坐标对象 {x, y}，转换为数组 [x, y]
    if (geojson.x !== undefined && geojson.y !== undefined) {
      return [geojson.x, geojson.y]
    }
    
    // 如果是数组，递归处理每个元素
    if (Array.isArray(geojson)) {
      return geojson.map(item => fixGeoJSONCoordinates(item))
    }
    
    // 如果是对象，递归处理每个属性
    if (geojson.type === 'FeatureCollection') {
      return {
        ...geojson,
        features: geojson.features?.map((feature: any) => fixGeoJSONCoordinates(feature)) || []
      }
    }
    
    if (geojson.type === 'Feature') {
      return {
        ...geojson,
        geometry: fixGeoJSONCoordinates(geojson.geometry),
        properties: geojson.properties
      }
    }
    
    if (geojson.type && ['Point', 'LineString', 'Polygon', 'MultiPoint', 'MultiLineString', 'MultiPolygon'].includes(geojson.type)) {
      return {
        ...geojson,
        coordinates: fixGeoJSONCoordinates(geojson.coordinates)
      }
    }
    
    return geojson
  }

  const loadVectorLayer = async (map: any, layerConfig: any, visibleOverride?: boolean): Promise<void> => {
    // 改进图层名称解析逻辑
    let layerName = layerConfig.name
    if (layerConfig.name.includes('@')) {
      // 处理标准化的数据源格式：图层名@数据源@@工作空间
      const parts = layerConfig.name.split('@')
      if (parts.length >= 1) {
        layerName = parts[0] // 取第一部分作为图层名称
      }
    } 
    
    // ===== 如果是武汉_县级图层，直接从本地文件加载 =====
    if (layerName === '武汉_县级') {
      console.log(`[${layerName}] 从本地GeoJSON文件加载图层`)
      
      try {
        loadingStore.updateLoading('map-init', `正在加载图层数据: ${layerName}...`)
        
        // 使用fetch加载本地GeoJSON文件（与长江面/长江线相同的方式）
        const response = await fetch('/src/views/dashboard/ViewPage/武汉_县级.geojson')
        if (!response.ok) {
          throw new Error(`加载GeoJSON文件失败: HTTP ${response.status}`)
        }
        
        let geojsonData = await response.json()
        
        // 修复坐标格式：将 {x, y} 转换为 [x, y]
        geojsonData = fixGeoJSONCoordinates(geojsonData)
        
        console.log(`[${layerName}] 成功加载GeoJSON文件，要素数量: ${geojsonData.features?.length || 0}`)
        
        // 使用OpenLayers GeoJSON格式器读取要素（与长江面/长江线相同的方式）
        const geoJsonFormat = new ol.format.GeoJSON()
        const features = geoJsonFormat.readFeatures(geojsonData, {
          featureProjection: map.getView().getProjection()
        })
        
        console.log(`[${layerName}] 成功创建 ${features.length} 个OpenLayers要素`)
        
        // 为每个要素设置属性
        features.forEach((feature: any, index: number) => {
          const properties = feature.getProperties()
          
          // 解析fieldNames和fieldValues数组，组合成实际的属性对象
          let parsedProperties: any = {}
          
          // 如果存在fieldNames和fieldValues数组，将它们组合成键值对
          if (properties.fieldNames && properties.fieldValues && 
              Array.isArray(properties.fieldNames) && Array.isArray(properties.fieldValues)) {
            properties.fieldNames.forEach((fieldName: string, i: number) => {
              if (i < properties.fieldValues.length) {
                parsedProperties[fieldName] = properties.fieldValues[i]
              }
            })
          } else {
            // 如果没有fieldNames/fieldValues，直接使用原始属性
            parsedProperties = { ...properties }
          }
          
          // 只保留指定的字段：NAME_1、PAC_FIRST_1、FIELD_SMPERIMETER
          const allowedFields = ['NAME_1', 'PAC_FIRST_1', 'FIELD_SMPERIMETER']
          const filteredProperties: any = {}
          allowedFields.forEach(field => {
            if (parsedProperties[field] !== undefined) {
              filteredProperties[field] = parsedProperties[field]
            }
          })
          
          // 调试：打印第一个要素的属性
          if (index === 0) {
            console.log(`[${layerName}] 第一个要素保留的属性:`, filteredProperties)
            console.log(`[${layerName}] NAME_1值:`, filteredProperties.NAME_1)
          }
          
          // 设置要素属性
          feature.set('id', `wuhan-county-${index}`)
          feature.set('layer_name', layerName)
          feature.set('geometry_type', feature.getGeometry()?.getType() || 'Polygon')
          feature.set('data_source', '本地文件')
          feature.set('last_update', new Date().toISOString())
          
          // 只设置过滤后的属性
          Object.keys(filteredProperties).forEach(key => {
            feature.set(key, filteredProperties[key])
          })
          
          // 清理不需要的属性（fieldNames、fieldValues等）
          const propertiesToRemove = ['fieldNames', 'fieldValues', 'stringID']
          propertiesToRemove.forEach(key => {
            if (feature.get(key) !== undefined) {
              feature.unset(key)
            }
          })
          
          // 保留ID（如果需要的话）
          if (properties.ID !== undefined) {
            feature.set('ID', properties.ID)
          }
        })
        
        // 创建武汉县级图层的样式函数（带动态注记显示NAME_1）
        const createWuhanCountyStyle = (feature: any) => {
          const css = getComputedStyle(document.documentElement)
          const strokeColor = css.getPropertyValue('--layer-stroke-武汉_县级').trim() || '#0078D4'
          const fillColor = css.getPropertyValue('--layer-fill-武汉_县级').trim() || 'rgba(0, 120, 212, 0.1)'
          
          // 获取NAME_1属性作为注记文本
          const nameText = feature.get('NAME_1') || ''
          
          return new ol.style.Style({
            fill: new ol.style.Fill({
              color: fillColor
            }),
            stroke: new ol.style.Stroke({
              color: strokeColor,
              width: 2
            }),
            text: new ol.style.Text({
              text: nameText, // 动态显示NAME_1
              font: 'bold 14px Arial', // 加粗字体，参考长江面样式
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
        
        // 直接创建图层并添加到地图（与长江面/长江线相同的方式）
        // 创建矢量源
        const vectorSource = new ol.source.Vector({
          features: features
        })
        
        // 创建矢量图层（使用样式函数以支持动态注记）
        const vectorLayer = new ol.layer.Vector({
          source: vectorSource,
          style: createWuhanCountyStyle, // 使用样式函数而不是固定样式
          visible: visibleOverride !== undefined ? visibleOverride : layerConfig.visible !== false,
          zIndex: 100
        })
        
        // 设置图层属性
        vectorLayer.set('layerName', layerName)
        vectorLayer.set('layerType', 'vector')
        vectorLayer.set('sourceType', 'upload') // 设置为upload类型，显示在上传图层分组中
        vectorLayer.set('description', `本地文件 - ${layerName}`)
        
        // 添加到地图
        map.addLayer(vectorLayer)
        
        // 添加到图层管理列表
        const layerInfo = {
          id: `wuhan-county-${Date.now()}`,
          name: layerName,
          layer: vectorLayer,
          visible: visibleOverride !== undefined ? visibleOverride : layerConfig.visible !== false,
          type: 'vector' as const,
          source: 'local' as const
        }
        
        mapStore.vectorlayers.push(layerInfo)
        mapStore.vectorlayers = [...mapStore.vectorlayers] // 强制触发响应式更新
        
        // 保存属性数据到layerDataStore（只保留指定字段）
        const allowedFields = ['NAME_1', 'PAC_FIRST_1', 'FIELD_SMPERIMETER']
        const featuresData = features.map((feature: any, index: number) => {
          const allProperties = feature.getProperties()
          const filteredProps: any = {}
          
          // 只保留允许的字段
          allowedFields.forEach(field => {
            if (allProperties[field] !== undefined) {
              filteredProps[field] = allProperties[field]
            }
          })
          
          return {
            id: feature.getId() || `${layerName}_${Date.now()}_${index}`,
            properties: filteredProps
          }
        })
        layerDataStore.setLayerAttributes(layerName, featuresData)
        
        console.log(`[${layerName}] 图层已加载完成`)
        notificationManager.info(
          `图层 ${layerName} 已加载`,
          `从本地GeoJSON文件加载\n✅ 共 ${features.length} 个要素`
        )
        
        return
      } catch (error) {
        console.error(`[${layerName}] 加载本地GeoJSON文件失败:`, error)
        notificationManager.error(
          `图层 ${layerName} 加载失败`,
          error instanceof Error ? error.message : '未知错误'
        )
        throw error
      }
    }
    
    // ===== 其他图层使用数据服务加载矢量图层 =====
    const apiConfig = createAPIConfig()
    console.log(`[${layerName}] 使用数据服务加载矢量图层`)
    
    try {
      // 获取数据集名称
      const datasetName = layerConfig.datasetName || layerName
      
      // 从SuperMap数据服务获取所有要素
      loadingStore.updateLoading('map-init', `正在加载图层数据: ${layerName}...`)
      const featuresResult = await superMapClient.getAllFeatures(
        datasetName,
        10000, // 批次大小
        (loaded: number, total: number) => {
          loadingStore.updateLoading('map-init', `正在加载图层数据: ${layerName}... (${loaded}/${total})`)
        }
      )
      
      if (!featuresResult.success || !featuresResult.data || featuresResult.data.length === 0) {
        throw new Error(featuresResult.error || `未获取到图层 ${layerName} 的数据`)
      }
      
      console.log(`[${layerName}] 获取到 ${featuresResult.data.length} 个要素`)
      
      // 将SuperMap要素数据转换为GeoJSON格式
      const geoJsonFeatures = featuresResult.data.map((feature: any, index: number) => {
        try {
          console.log(`[${layerName}] 处理要素 ${index}:`, feature)
          console.log(`[${layerName}] 要素 ${index} geometry对象:`, feature.geometry)
          
          // SuperMap返回的要素格式包含Point2D X和Y坐标
          // 需要提取这些坐标并转换为GeoJSON格式
          let geometry: any = null
          
          // 方法1: 如果已经有geometry字段，检查并转换
          if (feature.geometry && typeof feature.geometry === 'object') {
            const geomType = feature.geometry.type
            console.log(`[${layerName}] 要素 ${index} geometry类型: ${geomType}, geometry对象键:`, Object.keys(feature.geometry))
            
            // 如果geometry类型是REGION，需要转换为Polygon
            if (geomType === 'REGION' || geomType === 'POLYGON') {
              // 尝试从geometry对象中提取坐标
              if (feature.geometry.coordinates) {
                // 如果coordinates已经是数组格式，直接使用
                const coords = feature.geometry.coordinates
                // 确保coordinates格式正确（Polygon需要是三维数组）
                if (Array.isArray(coords) && coords.length > 0) {
                  if (Array.isArray(coords[0])) {
                    // 已经是正确的格式
                    geometry = {
                      type: 'Polygon',
                      coordinates: coords
                    }
                  } else {
                    // 需要包装一层
                    geometry = {
                      type: 'Polygon',
                      coordinates: [coords]
                    }
                  }
                } else {
                  console.log(`[${layerName}] geometry.coordinates格式不正确:`, coords)
                  geometry = null
                }
              } else if (feature.geometry.points) {
                // 如果有points数组，转换为coordinates
                const points = Array.isArray(feature.geometry.points) ? feature.geometry.points : []
                // 确保多边形闭合
                if (points.length > 0) {
                  const first = points[0]
                  const last = points[points.length - 1]
                  if (first[0] !== last[0] || first[1] !== last[1]) {
                    points.push([...first])
                  }
                }
                geometry = {
                  type: 'Polygon',
                  coordinates: [points]
                }
              } else {
                // 如果geometry中没有坐标，需要从feature的其他字段提取
                console.log(`[${layerName}] geometry是${geomType}但没有坐标，尝试从feature提取`)
                geometry = null // 继续到方法2
              }
            } 
            // 如果是标准GeoJSON类型，直接使用
            else if (['Point', 'LineString', 'Polygon', 'MultiPoint', 'MultiLineString', 'MultiPolygon'].includes(geomType)) {
              geometry = feature.geometry
            }
            // 其他情况，尝试转换或提取
            else {
              console.log(`[${layerName}] geometry类型 ${geomType} 不是标准GeoJSON类型，尝试提取坐标`)
              geometry = null // 继续到方法2
            }
          }
          
          // 方法2: 从SuperMap的Point2D格式提取坐标（如果方法1没有成功）
          if (!geometry) {
            // 提取所有Point2D X和Y坐标
            const coordinates: number[][] = []
            const keys = Object.keys(feature)
            
            // 查找所有Point2D X和Y字段，按顺序配对
            const xKeys: string[] = []
            const yKeys: string[] = []
            
            for (const key of keys) {
              if (key.trim() === 'Point2D X' || key.startsWith('Point2D X')) {
                xKeys.push(key)
              } else if (key.trim() === 'Point2D Y' || key.startsWith('Point2D Y')) {
                yKeys.push(key)
              }
            }
            
            // 按顺序配对X和Y坐标
            const maxPairs = Math.max(xKeys.length, yKeys.length)
            for (let i = 0; i < maxPairs; i++) {
              const xKey = xKeys[i]
              const yKey = yKeys[i]
              
              if (xKey && yKey) {
                const x = parseFloat(feature[xKey])
                const y = parseFloat(feature[yKey])
                
                if (!isNaN(x) && !isNaN(y)) {
                  coordinates.push([x, y])
                }
              }
            }
            
            console.log(`[${layerName}] 要素 ${index} 提取到 ${coordinates.length} 个坐标点 (X键: ${xKeys.length}, Y键: ${yKeys.length})`)
            
            // 如果提取到了坐标，构建GeoJSON几何
            if (coordinates.length > 0) {
              const geometryType = feature.geometryType || 'REGION'
              
              if (geometryType === 'REGION' || geometryType === 'POLYGON') {
                // 确保多边形是闭合的（首尾坐标相同）
                if (coordinates.length > 0) {
                  const first = coordinates[0]
                  const last = coordinates[coordinates.length - 1]
                  if (first[0] !== last[0] || first[1] !== last[1]) {
                    coordinates.push([...first])
                  }
                }
                geometry = {
                  type: 'Polygon',
                  coordinates: [coordinates]
                }
              } else if (geometryType === 'LINE' || geometryType === 'POLYLINE') {
                geometry = {
                  type: 'LineString',
                  coordinates: coordinates
                }
              } else if (geometryType === 'POINT') {
                geometry = {
                  type: 'Point',
                  coordinates: coordinates[0] || [0, 0]
                }
              }
              
              console.log(`[${layerName}] 要素 ${index} 提取到 ${coordinates.length} 个坐标点，几何类型: ${geometryType}`)
            }
          }
          
          if (!geometry) {
            console.warn(`[${layerName}] 要素${index}无法提取几何信息`)
            return null
          }
          
          // 获取属性数据（排除几何相关字段）
          const properties: any = {}
          const excludeKeys = ['geometry', 'geometryType', 'geometryID', 'PartIndex']
          for (const key of Object.keys(feature)) {
            if (!excludeKeys.includes(key) && !key.startsWith('Point2D')) {
              properties[key] = feature[key]
            }
          }
          
          // 构建GeoJSON Feature格式
          return {
            type: 'Feature',
            geometry: geometry,
            properties: properties
          }
        } catch (error) {
          console.warn(`[${layerName}] 处理要素${index}失败:`, error)
          return null
        }
      }).filter((f: any) => f !== null && f.geometry) // 过滤掉解析失败或没有geometry的要素
      
      if (geoJsonFeatures.length === 0) {
        throw new Error(`图层 ${layerName} 没有有效的要素数据`)
      }
      
      // 创建GeoJSON FeatureCollection
      const geoJsonData = {
        type: 'FeatureCollection',
        features: geoJsonFeatures
      }
      
      console.log(`[${layerName}] GeoJSON数据已准备，要素数量: ${geoJsonData.features.length}`)
      
      // ===== 保存GeoJSON数据到本地文件 =====
      const saveGeoJSONToFile = (data: any, fileName: string) => {
        try {
          const jsonString = JSON.stringify(data, null, 2)
          const blob = new Blob([jsonString], { type: 'application/json' })
          const url = URL.createObjectURL(blob)
          const link = document.createElement('a')
          link.href = url
          link.download = fileName
          document.body.appendChild(link)
          link.click()
          document.body.removeChild(link)
          URL.revokeObjectURL(url)
          console.log(`[${layerName}] GeoJSON文件已保存: ${fileName}`)
        } catch (error) {
          console.error(`[${layerName}] 保存GeoJSON文件失败:`, error)
        }
      }
      
      // 保存GeoJSON数据
      const fileName = `${layerName}_${new Date().getTime()}.geojson`
      saveGeoJSONToFile(geoJsonData, fileName)
      
      // ===== 使用和本地上传数据相同的方式加载图层 =====
      // 使用OpenLayers GeoJSON格式器读取要素
      const geoJsonFormat = new ol.format.GeoJSON()
      const features = geoJsonFormat.readFeatures(geoJsonData, {
        featureProjection: map.getView().getProjection()
      })
      
      console.log(`[${layerName}] 成功创建 ${features.length} 个OpenLayers要素`)
      
      // 验证要素是否有几何信息
      features.forEach((feature: any, index: number) => {
        const geometry = feature.getGeometry()
        if (!geometry) {
          console.warn(`[${layerName}] 要素 ${index} 没有几何信息`)
        } else {
          const geomType = geometry.getType()
          const coords = geometry.getCoordinates()
          console.log(`[${layerName}] 要素 ${index} 几何类型: ${geomType}, 坐标维度: ${Array.isArray(coords[0]) ? (Array.isArray(coords[0][0]) ? '3D' : '2D') : '1D'}`)
        }
      })
      
      // 使用saveFeaturesAslayer加载图层（和本地上传数据相同的方式）
      if (!mapStore.map) {
        throw new Error('地图实例未初始化')
      }
      
      const success = await saveFeaturesAslayer(features, layerName, 'upload')
      
      if (!success) {
        throw new Error('保存图层失败')
      }
      
      // 保存属性数据到layerDataStore
      const featuresData = features.map((feature: any, index: number) => ({
        id: feature.getId() || `${layerName}_${Date.now()}_${index}`,
        properties: feature.getProperties()
      }))
      layerDataStore.setLayerAttributes(layerName, featuresData)
      
      console.log(`[${layerName}] 图层已使用saveFeaturesAslayer加载完成`)
      notificationManager.info(
        `图层 ${layerName} 已加载`,
        `使用数据服务加载: ${datasetName}\n数据来源: SuperMap iServer 数据服务\n✅ 共 ${features.length} 个要素\n已保存为GeoJSON文件: ${fileName}`
      )
      
    } catch (error) {
      console.error(`[${layerName}] 加载矢量图层失败:`, error)
      notificationManager.error(
        `图层 ${layerName} 加载失败`,
        error instanceof Error ? error.message : '未知错误'
      )
      throw error
    }
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
   * 仅加载武汉县级图层，使用矢量数据服务方式加载
   * @param map 地图实例
   * @param visibleLayers 指定要显示的图层名称数组，如果不提供则只加载武汉县级图层
   */
  const loadVectorLayers = async (map: any, visibleLayers?: string[]): Promise<void> => {
    // ===== 首先清空所有现有图层 =====
    clearAllLayersBeforeInit()
    
    const apiConfig = createAPIConfig()
    
    // ===== 只加载武汉县级图层 =====
    const targetLayerName = '武汉_县级'
    const loadTasks: Promise<void>[] = []
    
    // 查找武汉县级图层配置
    const countyLayerConfig = apiConfig.wuhanlayers.find(layer => {
      const layerName = layer.name.split('@')[0] || layer.name
      return layerName === targetLayerName
    })
    
    if (!countyLayerConfig) {
      console.warn(`未找到图层配置: ${targetLayerName}`)
      return
    }
    
    // 只加载武汉县级图层
    loadingStore.updateLoading('map-init', `正在加载图层: ${targetLayerName}`)
    loadTasks.push(loadVectorLayer(map, countyLayerConfig, true))
    
    await Promise.allSettled(loadTasks)
  }

  return {
    loadVectorLayer,
    loadVectorLayers,
    clearAllLayersBeforeInit
  }
}
