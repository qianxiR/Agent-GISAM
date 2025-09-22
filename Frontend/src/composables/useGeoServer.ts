/*
  GeoServer 图层加载组合式函数（OpenLayers）

  1) 输入数据格式（接口定义）
     - createWMSLayer(params: WMSParams): ol.layer.Tile
       params: {
         url: string              // GeoServer WMS 服务根地址，例如 https://server/geoserver/wms
         layers: string           // 图层名，格式 workspace:layer
         styles?: string          // 样式名
         format?: string          // 图片格式，默认 image/png
         version?: string         // WMS 版本，默认 1.3.0
         transparent?: boolean    // 透明背景，默认 true
       }

     - createWMTSLayer(params: WMTSParams): ol.layer.Tile
       params: {
         url: string              // GeoServer WMTS 服务根地址，例如 https://server/geoserver/gwc/service/wmts
         layer: string            // 图层名，格式 workspace:layer
         matrixSet?: string       // 瓦片矩阵集，默认 EPSG:4326
         format?: string          // 瓦片格式，默认 image/png
         style?: string           // 样式名，默认 ''
       }

     - createWFSVectorLayer(params: WFSParams): ol.layer.Vector
       params: {
         url: string              // GeoServer WFS 服务根地址，例如 https://server/geoserver/wfs
         typeName: string         // 图层名，格式 workspace:layer
         outputFormat?: string    // 输出格式，默认 application/json
         geometryName?: string    // 几何字段名，默认 the_geom
       }

  2) 数据处理方法
     - 直接构造 ol 源与图层，坐标系固定使用 EPSG:4326，不做条件分支与兜底逻辑。
     - WFS 以 GeoJSON（application/json）请求，srsName 固定 EPSG:4326。
     - 样式颜色从 theme.css 的 CSS 变量读取，避免硬编码颜色。

  3) 输出数据格式
     - 返回 OpenLayers 图层实例：ol.layer.Tile 或 ol.layer.Vector，可直接 addLayer() 到现有地图。
*/

import type TileLayer from 'ol/layer/Tile'
import type VectorLayer from 'ol/layer/Vector'
import type { Options } from 'ol/layer/BaseTile'
import type TileSource from 'ol/source/Tile'
import OLTileLayer from 'ol/layer/Tile'
import OLVectorLayer from 'ol/layer/Vector'
import TileWMS from 'ol/source/TileWMS'
import WMTS, { optionsFromCapabilities } from 'ol/source/WMTS'
import WMTSTileGrid from 'ol/tilegrid/WMTS'
import VectorSource from 'ol/source/Vector'
import GeoJSON from 'ol/format/GeoJSON'
import Style from 'ol/style/Style'
import Fill from 'ol/style/Fill'
import Stroke from 'ol/style/Stroke'
import CircleStyle from 'ol/style/Circle'
 

export interface WMSParams {
  url: string
  layers: string
  styles?: string
  format?: string
  version?: string
  transparent?: boolean
  tileLayerOptions?: TileLayerOptions
}

export interface WMTSParams {
  url: string
  layer: string
  matrixSet?: string
  format?: string
  style?: string
  tileLayerOptions?: TileLayerOptions
}

export interface WFSParams {
  url: string
  typeName: string
  outputFormat?: string
  geometryName?: string
}

type TileLayerOptions = Options<TileSource>

const readThemeColor = (varName: string): string => {
  return getComputedStyle(document.documentElement).getPropertyValue(varName).trim()
}

const defaultVectorStyle = (): Style => {
  const strokeColor = readThemeColor('--sm-analysis-stroke') || 'rgba(255,0,0,1)'
  const fillColor = readThemeColor('--sm-analysis-fill') || 'rgba(255,0,0,0.15)'
  const pointColor = readThemeColor('--sm-analysis-point') || 'rgba(255,0,0,1)'
  return new Style({
    image: new CircleStyle({
      radius: 5,
      fill: new Fill({ color: pointColor })
    }),
    stroke: new Stroke({ color: strokeColor, width: 2 }),
    fill: new Fill({ color: fillColor })
  })
}

export const createWMSLayer = (params: WMSParams): TileLayer => {
  const source = new TileWMS({
    url: params.url,
    params: {
      LAYERS: params.layers,
      STYLES: params.styles ?? '',
      FORMAT: params.format ?? 'image/png',
      VERSION: params.version ?? '1.3.0',
      TRANSPARENT: (params.transparent ?? true) ? 'true' : 'false',
      CRS: 'EPSG:4326'
    },
    projection: 'EPSG:4326'
  })
  return new OLTileLayer({ source, ...params.tileLayerOptions })
}

export const createWMTSLayer = (params: WMTSParams): TileLayer => {
  const projection = 'EPSG:4326'
  const matrixSet = params.matrixSet ?? 'EPSG:4326'

  const size = 256
  const extent = [-180, -90, 180, 90]
  const resolutions: number[] = []
  const matrixIds: string[] = []
  for (let z = 0; z <= 18; z++) {
    resolutions.push(0.703125 / Math.pow(2, z))
    matrixIds.push(`${matrixSet}:${z}`)
  }

  const tileGrid = new WMTSTileGrid({
    origin: [-180, 90],
    resolutions,
    matrixIds,
    tileSize: size,
    extent
  })

  const source = new WMTS({
    url: params.url,
    layer: params.layer,
    matrixSet,
    format: params.format ?? 'image/png',
    style: params.style ?? '',
    projection,
    tileGrid
  })

  return new OLTileLayer({ source, ...params.tileLayerOptions })
}

export const createWFSVectorLayer = (params: WFSParams): VectorLayer => {
  const queryParams = new URLSearchParams()
  queryParams.set('service', 'WFS')
  queryParams.set('request', 'GetFeature')
  queryParams.set('version', '1.1.0')
  queryParams.set('typeName', params.typeName)
  queryParams.set('outputFormat', params.outputFormat ?? 'application/json')
  queryParams.set('srsName', 'EPSG:4326')

  const source = new VectorSource({
    url: `${params.url}?${queryParams.toString()}`,
    format: new GeoJSON({ dataProjection: 'EPSG:4326', featureProjection: 'EPSG:4326' })
  })

  return new OLVectorLayer({ source, style: defaultVectorStyle() })
}

export function useGeoServer() {
  return {
    createWMSLayer,
    createWMTSLayer,
    createWFSVectorLayer
  }
}



