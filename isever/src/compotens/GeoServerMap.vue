<template>
  <div class="geoserver-map-container">
    <div ref="mapElement" class="geoserver-map"></div>
    
    <!-- 图层管理面板 -->
    <div class="layer-panel">
      <div class="panel-header">
        <h3>图层管理</h3>
        <button @click="toggleLayerPanel" class="toggle-btn">
          {{ showLayerPanel ? '▼' : '▲' }}
        </button>
      </div>
      <div v-if="showLayerPanel" class="panel-content">
        <div v-for="layer in layerList" :key="layer.name" class="layer-item">
          <div class="layer-info">
            <input 
              type="checkbox" 
              :id="layer.name"
              :checked="layer.visible"
              @change="toggleLayer(layer.name, ($event.target as HTMLInputElement).checked)"
              class="layer-checkbox"
            >
            <label :for="layer.name" class="layer-label">{{ layer.displayName }}</label>
          </div>
          <div class="layer-controls">
            <button 
              @click="setLayerOpacity(layer.name, Math.max(0, layer.opacity - 0.1))"
              class="opacity-btn"
              title="降低透明度"
            >-</button>
            <span class="opacity-value">{{ Math.round(layer.opacity * 100) }}%</span>
            <button 
              @click="setLayerOpacity(layer.name, Math.min(1, layer.opacity + 0.1))"
              class="opacity-btn"
              title="提高透明度"
            >+</button>
          </div>
        </div>
      </div>
    </div>

    <!-- 属性信息弹窗 -->
    <div v-if="showPopup" class="feature-popup">
      <div class="popup-header">
        <h3>要素属性信息</h3>
        <button @click="closePopup" class="close-btn">×</button>
      </div>
      <div class="popup-content">
        <div v-if="selectedFeature" class="feature-info">
          <div v-for="(value, key) in featureProperties" :key="key" class="property-item">
            <span class="property-name">{{ key }}:</span>
            <span class="property-value">{{ formatPropertyValue(value) }}</span>
          </div>
        </div>
        <div v-else class="no-feature">
          未选择要素
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'

// 声明全局OpenLayers类型
declare global {
  interface Window {
    ol: any
  }
}

// ===== 输入数据格式 =====
interface GeoServerConfig {
  wmsUrl: string
  wfsUrl: string
  layers: string[]
  center?: [number, number]
  zoom?: number
}

interface Props {
  config?: GeoServerConfig
}

// ===== 数据处理方法 =====
const props = withDefaults(defineProps<Props>(), {
  config: () => ({
    wmsUrl: '/geoserver/wms', // 使用代理路径
    wfsUrl: '/geoserver/wfs', // 使用代理路径
    layers: [
      'czh:成都市',
      'czh:成都区',
      'czh:水文站点',
      'czh:成都市地貌类型_'
    ],
    center: [104.06, 30.67],
    zoom: 8
  })
})

const mapElement = ref<HTMLElement | null>(null)
const map = ref<any>(null)

// 属性信息相关状态
const showPopup = ref(false)
const selectedFeature = ref<any>(null)
const featureProperties = ref<Record<string, any>>({})

// 图层管理相关状态
const showLayerPanel = ref(true)
const layerList = ref<Array<{
  name: string
  displayName: string
  visible: boolean
  opacity: number
  wmsLayer: any
  wfsLayer: any
}>>([])

// 主题颜色读取函数
const readTheme = (name: string): string => {
  return getComputedStyle(document.documentElement).getPropertyValue(name).trim()
}

// 根据图层基础名获取主题颜色（优先按图层名变量，其次主题强调色）
const getThemeColors = (layerBaseName?: string) => {
  const accent = readTheme('--accent') || '#0078D4'
  const accentRgb = readTheme('--accent-rgb') || '0, 120, 212'

  const strokeVar = layerBaseName ? readTheme(`--layer-stroke-${layerBaseName}`) : ''
  const fillVar = layerBaseName ? readTheme(`--layer-fill-${layerBaseName}`) : ''

  const strokeColor = strokeVar || accent
  const fillColor = fillVar || `rgba(${accentRgb}, 0.15)`
  const pointColor = strokeColor

  return { strokeColor, fillColor, pointColor }
}

// 创建矢量样式（按图层名与几何类型动态生成）
const createVectorStyle = (layerName?: string) => {
  const ol = window.ol
  const base = layerName ? (layerName.split(':').pop() || layerName) : undefined
  const colors = getThemeColors(base)
  const accentRgb = readTheme('--accent-rgb') || '0, 120, 212'
  const transparent = 'rgba(0, 0, 0, 0)'

  const styleCache: Record<string, any> = {}

  return (feature: any) => {
    const geometry = feature.getGeometry()
    const type = geometry ? geometry.getType() : 'Unknown'
    const key = `${base || 'default'}_${type}`
    if (styleCache[key]) return styleCache[key]

    // 点样式：水文站点使用主题蓝点
    if (type === 'Point' || type === 'MultiPoint') {
      const pointStyle = new ol.style.Style({
        image: new ol.style.Circle({
          radius: 5,
          fill: new ol.style.Fill({ color: colors.pointColor }),
          stroke: new ol.style.Stroke({ color: colors.pointColor, width: 2 })
        })
      })
      styleCache[key] = pointStyle
      return pointStyle
    }

    // 线样式：统一主题描边
    if (type === 'LineString' || type === 'MultiLineString') {
      const lineStyle = new ol.style.Style({
        stroke: new ol.style.Stroke({ color: colors.strokeColor, width: 2 })
      })
      styleCache[key] = lineStyle
      return lineStyle
    }

    // 面样式：成都市/成都区透明；地貌类型主题蓝填充；其他默认透明
    if (type === 'Polygon' || type === 'MultiPolygon') {
      let fillColor = transparent
      if (base && (base === '成都市' || base === '成都区')) {
        fillColor = transparent
      } else if (base && base.indexOf('地貌类型') >= 0) {
        fillColor = `rgba(${accentRgb}, 0.25)`
      } else {
        fillColor = transparent
      }

      const polygonStyle = new ol.style.Style({
        stroke: new ol.style.Stroke({ color: colors.strokeColor, width: 2 }),
        fill: new ol.style.Fill({ color: fillColor })
      })
      styleCache[key] = polygonStyle
      return polygonStyle
    }

    // 默认样式（透明填充）
    const defaultStyle = new ol.style.Style({
      stroke: new ol.style.Stroke({ color: colors.strokeColor, width: 2 }),
      fill: new ol.style.Fill({ color: transparent })
    })
    styleCache[key] = defaultStyle
    return defaultStyle
  }
}

// 创建WMS图层
const createWMSLayer = (layerName: string) => {
  const ol = window.ol
  
  const wmsSource = new ol.source.TileWMS({
    url: props.config.wmsUrl,
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
  
  return new ol.layer.Tile({ source: wmsSource })
}

// 创建WFS图层
const createWFSLayer = (layerName: string) => {
  const ol = window.ol
  
  const params = new URLSearchParams()
  params.set('service', 'WFS')
  params.set('request', 'GetFeature')
  params.set('version', '1.1.0')
  params.set('typeName', layerName)
  params.set('outputFormat', 'application/json')
  params.set('srsName', 'EPSG:4326')

  const wfsSource = new ol.source.Vector({
    url: props.config.wfsUrl + '?' + params.toString(),
    format: new ol.format.GeoJSON({ 
      dataProjection: 'EPSG:4326', 
      featureProjection: 'EPSG:4326' 
    })
  })

  const base = layerName.split(':').pop() || layerName

  const vectorLayer = new ol.layer.Vector({ 
    source: wfsSource, 
    style: createVectorStyle(layerName) 
  })
  // 保存基础名以便主题切换时精确更新
  vectorLayer.set('baseLayerName', base)
  return vectorLayer
}

// 初始化地图
const initMap = () => {
  if (!mapElement.value || !window.ol) return

  const ol = window.ol
  
  // 创建视图
  const view = new ol.View({
    center: ol.proj.fromLonLat(props.config.center!),
    zoom: props.config.zoom
  })

  // 创建地图实例
  map.value = new ol.Map({
    target: mapElement.value,
    view: view
  })

  // 添加图层并创建图层管理列表
  props.config.layers.forEach((layerName) => {
    // 添加WMS图层
    const wmsLayer = createWMSLayer(layerName)
    map.value.addLayer(wmsLayer)

    // 添加WFS图层用于属性查询
    const wfsLayer = createWFSLayer(layerName)
    map.value.addLayer(wfsLayer)

    // 添加到图层管理列表
    layerList.value.push({
      name: layerName,
      displayName: getLayerDisplayName(layerName),
      visible: true,
      opacity: 1.0,
      wmsLayer: wmsLayer,
      wfsLayer: wfsLayer
    })
  })

  // 添加点击事件监听
  map.value.on('click', (event: any) => {
    const features = map.value.getFeaturesAtPixel(event.pixel)
    if (features.length > 0) {
      const feature = features[0]
      showFeatureInfo(feature)
    } else {
      closePopup()
    }
  })

  // 强制更新地图尺寸
  setTimeout(() => {
    if (map.value) {
      map.value.updateSize()
    }
  }, 100)
}

// 清理地图
const cleanup = () => {
  if (map.value) {
    map.value.setTarget(null)
    map.value = null
  }
}

// 更新图层样式（主题切换时）
const updateLayerStyles = () => {
  if (!map.value) return

  const ol = window.ol
  
  // 优先使用 layerList 逐一以图层名更新样式
  layerList.value.forEach((info) => {
    if (info.wfsLayer) {
      info.wfsLayer.setStyle(createVectorStyle(info.name))
    }
  })

  // 兜底：遍历地图上所有矢量图层并按其记录的基础名更新
  map.value.getLayers().forEach((layer: any) => {
    if (layer instanceof ol.layer.Vector) {
      const base = layer.get('baseLayerName')
      const guessedName = base ? String(base) : undefined
      layer.setStyle(createVectorStyle(guessedName))
    }
  })
}

// 格式化属性值
const formatPropertyValue = (value: any): string => {
  if (value === null || value === undefined) {
    return '无'
  }
  if (typeof value === 'number') {
    return value.toLocaleString()
  }
  if (typeof value === 'object') {
    return JSON.stringify(value)
  }
  return String(value)
}

// 关闭弹窗
const closePopup = () => {
  showPopup.value = false
  selectedFeature.value = null
  featureProperties.value = {}
}

// 显示要素属性
const showFeatureInfo = (feature: any) => {
  selectedFeature.value = feature
  const allProperties = feature.getProperties()
  
  // 过滤掉geometry字段
  const filteredProperties: Record<string, any> = {}
  Object.keys(allProperties).forEach(key => {
    if (key !== 'geometry') {
      filteredProperties[key] = allProperties[key]
    }
  })
  
  featureProperties.value = filteredProperties
  showPopup.value = true
}

// 图层管理函数
const toggleLayerPanel = () => {
  showLayerPanel.value = !showLayerPanel.value
}

const getLayerDisplayName = (layerName: string): string => {
  const displayNames: Record<string, string> = {
    'czh:成都市': '成都市',
    'czh:成都市地貌类型_': '地貌类型',
    'czh:成都区': '成都区',
    'czh:水文站点': '水文站点'
  }
  return displayNames[layerName] || layerName
}

const toggleLayer = (layerName: string, visible: boolean) => {
  const layerInfo = layerList.value.find(l => l.name === layerName)
  if (layerInfo) {
    layerInfo.visible = visible
    layerInfo.wmsLayer.setVisible(visible)
    layerInfo.wfsLayer.setVisible(visible)
  }
}

const setLayerOpacity = (layerName: string, opacity: number) => {
  const layerInfo = layerList.value.find(l => l.name === layerName)
  if (layerInfo) {
    layerInfo.opacity = opacity
    layerInfo.wmsLayer.setOpacity(opacity)
    layerInfo.wfsLayer.setOpacity(opacity)
  }
}

// 监听主题变化（简化版本，直接使用默认颜色）

// ===== 输出数据格式 =====
// 组件生命周期管理
onMounted(() => {
  initMap()
})

onUnmounted(() => {
  cleanup()
})

// 暴露地图实例供父组件使用
defineExpose({
  map,
  updateLayerStyles,
  cleanup
})
</script>

<style scoped>
.geoserver-map-container {
  width: 100vw;
  height: 100vh;
  position: fixed;
  top: 0;
  left: 0;
  background: transparent;
}

.geoserver-map {
  width: 100%;
  height: 100%;
}

.feature-popup {
  position: absolute;
  top: 20px;
  right: 20px;
  width: 350px;
  max-height: 500px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
  z-index: 1000;
  overflow: hidden;
}

.popup-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px 20px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.popup-header h3 {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
}

.close-btn {
  background: none;
  border: none;
  color: white;
  font-size: 24px;
  cursor: pointer;
  padding: 0;
  width: 30px;
  height: 30px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  transition: background-color 0.2s;
}

.close-btn:hover {
  background-color: rgba(255, 255, 255, 0.2);
}

.popup-content {
  max-height: 400px;
  overflow-y: auto;
  padding: 20px;
}

.feature-info {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.property-item {
  display: flex;
  flex-direction: column;
  padding: 8px 12px;
  background: #f8f9fa;
  border-radius: 4px;
  border-left: 3px solid #667eea;
}

.property-name {
  font-weight: 600;
  color: #495057;
  font-size: 14px;
  margin-bottom: 4px;
}

.property-value {
  color: #6c757d;
  font-size: 13px;
  word-break: break-all;
}

.no-feature {
  text-align: center;
  color: #6c757d;
  font-style: italic;
  padding: 40px 20px;
}

.layer-panel {
  position: absolute;
  top: 20px;
  left: 20px;
  width: 280px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
  z-index: 1000;
  overflow: hidden;
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px 20px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.panel-header h3 {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
}

.toggle-btn {
  background: none;
  border: none;
  color: white;
  font-size: 18px;
  cursor: pointer;
  padding: 5px;
  border-radius: 3px;
  transition: background-color 0.2s;
}

.toggle-btn:hover {
  background-color: rgba(255, 255, 255, 0.2);
}

.panel-content {
  max-height: 400px;
  overflow-y: auto;
  padding: 15px;
}

.layer-item {
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding: 12px;
  border: 1px solid #e9ecef;
  border-radius: 6px;
  margin-bottom: 10px;
  background: #f8f9fa;
}

.layer-info {
  display: flex;
  align-items: center;
  gap: 10px;
}

.layer-checkbox {
  width: 16px;
  height: 16px;
  cursor: pointer;
}

.layer-label {
  font-size: 14px;
  font-weight: 500;
  color: #495057;
  cursor: pointer;
  flex: 1;
}

.layer-controls {
  display: flex;
  align-items: center;
  gap: 8px;
  justify-content: flex-end;
}

.opacity-btn {
  background: #667eea;
  border: none;
  color: white;
  width: 24px;
  height: 24px;
  border-radius: 50%;
  cursor: pointer;
  font-size: 14px;
  font-weight: bold;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background-color 0.2s;
}

.opacity-btn:hover {
  background: #5a67d8;
}

.opacity-value {
  font-size: 12px;
  color: #6c757d;
  min-width: 35px;
  text-align: center;
}
</style>
