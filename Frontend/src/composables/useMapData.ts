import { useMapStore } from '@/stores/mapStore'
import { useLoadingStore } from '@/stores/loadingStore'
import { useLayerDataStore } from '@/stores/layerDataStore'
import { createAPIConfig } from '@/utils/config'
import { notificationManager } from '@/utils/notification'
import { useMapStyles } from './useMapStyles'

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

  /**
   * 加载矢量图层 - 连接SuperMap iServer数据服务获取地理要素数据
   * 调用者: useMapData() -> loadVectorLayers() -> loadVectorLayer()
   * 作用: 从SuperMap服务器加载指定图层的矢量要素数据并渲染到地图上
   */
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
    
    // ===== 从服务器加载数据 =====
    const apiConfig = createAPIConfig()
    console.log(`[${layerName}] 从服务器加载数据`)
    
      // 创建新的图层容器
      const style = createLayerStyle(layerConfig, layerName);
      
      // 创建Openlayers矢量图层容器，图层创建和渲染：
      // 1. 创建图层容器
      // 2. 创建图层源
      // 3. 创建图层样式
      // 4. 创建图层
      // 5. 添加图层到地图
      // 6. 渲染图层
      // 7. 更新图层样式
    const vectorlayer = new ol.layer.Vector({
        source: new ol.source.Vector({}),
        style: style
      });
    
    // ===== 连接SuperMap iServer数据服务 =====
    // 调用者: loadVectorLayer()
    // 服务器地址: ${baseUrl}/${dataService} (来自 src/utils/config.ts 配置)
    // 作用: 创建SuperMap要素服务客户端，用于获取矢量数据
    const dataServiceUrl = `${apiConfig.baseUrl}/${apiConfig.dataService}`
    const featureService = new ol.supermap.FeatureService(dataServiceUrl);
    
    // 解析图层名称获取数据集和数据源信息
    const parts = layerConfig.name.split('@');
    const dataset = parts[0];    // 数据集名称，如: '武汉_县级'
    const datasource = parts[1]; // 数据源名称，如: 'wuhan'
    const datasetNames = [`${datasource}:${dataset}`];

    // ===== 第一次服务器调用：获取图层要素总数 =====
    // 调用者: loadVectorLayer()
    // 服务器地址: ${baseUrl}/${dataService}/datasources/${datasource}/datasets/${dataset}/features.json
    // 作用: 获取图层的要素总数(featureCount)，用于计算分页
    const featuresUrl = `${apiConfig.baseUrl}/${apiConfig.dataService}/datasources/${datasource}/datasets/${encodeURIComponent(dataset)}/features.json`;
    
    // 调试日志：显示实际访问的URL
    console.log(`[${layerName}] 访问要素总数URL:`, featuresUrl);
    
    // 添加错误处理，检查响应是否为JSON
    let featuresJson;
    try {
      const response = await fetch(featuresUrl);
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }
      const contentType = response.headers.get('content-type');
      if (!contentType || !contentType.includes('application/json')) {
        const responseText = await response.text();
        throw new Error(`服务器返回非JSON数据: ${responseText.substring(0, 200)}...`);
      }
      featuresJson = await response.json();
    } catch (error) {
      console.error(`获取图层要素总数失败 [${layerName}]:`, error);
      console.error(`请求URL: ${featuresUrl}`);
      throw error;
    }
    
    // 获取要素总数
    let featureCountBounds: number = (featuresJson && typeof featuresJson.featureCount === 'number') ? featuresJson.featureCount : 15;
    
    // 如果图层配置了maxFeatures，则限制要素数量
    if (layerConfig.maxFeatures && layerConfig.maxFeatures > 0) {
      featureCountBounds = Math.min(featureCountBounds, layerConfig.maxFeatures);
    }
    
    // 计算总页数：featureCount / 20，有余数则页数加一
    const totalPages = Math.ceil(featureCountBounds / DATA_CONFIG.PAGE_SIZE);
    
    // 打印分页加载参数信息
    console.log(`[${layerName}] 分页加载参数:`, {
      要素总数: featureCountBounds,
      每页大小: DATA_CONFIG.PAGE_SIZE,
      总页数: totalPages,
      要素总数响应: featuresJson
    });

    // ===== 从配置中获取地图边界范围 =====
    // 调用者: loadVectorLayer()
    // 配置来源: createAPIConfig().mapBounds.extent
    const mapExtent = apiConfig.mapBounds.extent
    const mapBounds = new ol.geom.Polygon([[
      [mapExtent[0], mapExtent[1]], // 左下角 [minLon, minLat]
      [mapExtent[2], mapExtent[1]], // 右下角 [maxLon, minLat]
      [mapExtent[2], mapExtent[3]], // 右上角 [maxLon, maxLat]
      [mapExtent[0], mapExtent[3]], // 左上角 [minLon, maxLat]
      [mapExtent[0], mapExtent[1]]  // 闭合 [minLon, minLat]
    ]]);

    // ===== 根据正确的API接口实现分页加载逻辑 =====
    // 1. 获取featureCount总数
    // 2. 计算总页数：featureCount / 15，有余数则页数加一
    // 3. 使用正确的API接口循环加载每页数据
    
    const pageSize = DATA_CONFIG.PAGE_SIZE; // 20个要素/页
    
    // 存储所有要素数据的数组
    let allFeatures: any[] = [];
    
    // 定义分页加载函数 - 只获取数据，不渲染
    const loadPage = (pageIndex: number): Promise<any[]> => new Promise(resolve => {
      const fromIndex = pageIndex * pageSize;
      const toIndex = Math.min(fromIndex + pageSize - 1, featureCountBounds - 1);
      
      console.log(`[${layerName}] 加载第${pageIndex + 1}页，索引范围: ${fromIndex}-${toIndex}`);
      
      // 使用正确的API接口格式获取分页数据
      const pageUrl = `${apiConfig.baseUrl}/${apiConfig.dataService}/datasources/${datasource}/datasets/${encodeURIComponent(dataset)}/features.json?fromIndex=${fromIndex}&toIndex=${toIndex}`;
      
      console.log(`[${layerName}] 分页请求URL:`, pageUrl);
      
      fetch(pageUrl)
        .then(response => {
          if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
          }
          return response.json();
        })
        .then(async (data) => {
          if (data && data.childUriList && Array.isArray(data.childUriList)) {
            console.log(`[${layerName}] 第${pageIndex + 1}页获取到${data.childUriList.length}个要素链接`);
            
            // 并行获取所有childUriList中的geometry数据
            const geometryPromises = data.childUriList.map(async (uri: string, index: number) => {
              // 确保URI以.json结尾
              const geometryUrl = uri.endsWith('.json') ? uri : `${uri}.json`;
              
              try {
                console.log(`[${layerName}] 第${pageIndex + 1}页-要素${index + 1} 获取geometry:`, geometryUrl);
                
                const geometryResponse = await fetch(geometryUrl);
                if (!geometryResponse.ok) {
                  throw new Error(`HTTP ${geometryResponse.status}: ${geometryResponse.statusText}`);
                }
                
                // 检查响应内容类型
                const contentType = geometryResponse.headers.get('content-type');
                console.log(`[${layerName}] 第${pageIndex + 1}页-要素${index + 1} 响应类型:`, contentType);
                
                if (!contentType || !contentType.includes('application/json')) {
                  // 如果不是JSON，打印响应内容的前200个字符
                  const responseText = await geometryResponse.text();
                  console.error(`[${layerName}] 第${pageIndex + 1}页-要素${index + 1} 非JSON响应:`, responseText.substring(0, 200));
                  throw new Error(`服务器返回非JSON数据: ${responseText.substring(0, 100)}...`);
                }
                
                const geometryData = await geometryResponse.json();
                console.log(`[${layerName}] 第${pageIndex + 1}页-要素${index + 1} geometry数据:`, geometryData);
                return geometryData;
              } catch (error) {
                console.error(`[${layerName}] 第${pageIndex + 1}页-要素${index + 1} geometry获取失败:`, error);
                console.error(`[${layerName}] 失败的URL:`, geometryUrl);
                return null;
              }
            });
            
            // 等待所有geometry数据加载完成
            const geometryResults = await Promise.all(geometryPromises);
            
            // 过滤掉失败的请求，只处理成功获取的geometry数据
            const validGeometries = geometryResults.filter(result => result !== null);
            
            if (validGeometries.length > 0) {
              // 将SuperMap格式的geometry数据转换为OpenLayers要素
              const features: any[] = [];
              
              validGeometries.forEach((geometryData: any, index: number) => {
                try {
                  // 解析SuperMap格式的geometry数据
                  if (geometryData.geometry && geometryData.geometry.type === 'REGION') {
                    // 处理面要素（REGION）
                    const coordinates = geometryData.geometry.points.map((point: any) => [point.x, point.y]);
                    // 闭合多边形（首尾坐标相同）
                    if (coordinates.length > 0 && (coordinates[0][0] !== coordinates[coordinates.length - 1][0] || coordinates[0][1] !== coordinates[coordinates.length - 1][1])) {
                      coordinates.push([coordinates[0][0], coordinates[0][1]]);
                    }
                    
                    const polygon = new ol.geom.Polygon([coordinates]);
                    const feature = new ol.Feature({
                      geometry: polygon,
                      properties: {
                        id: geometryData.ID,
                        name: geometryData.fieldValues ? geometryData.fieldValues[5] : '', // NAME字段
                        area: geometryData.fieldValues ? geometryData.fieldValues[2] : '', // SMAREA字段
                        height: geometryData.fieldValues ? geometryData.fieldValues[8] : '', // HEIGHT字段
                        ...geometryData
                      }
                    });
                    features.push(feature);
                  } else if (geometryData.geometry && geometryData.geometry.type === 'LINE') {
                    // 处理线要素（LINE）
                    const coordinates = geometryData.geometry.points.map((point: any) => [point.x, point.y]);
                    const lineString = new ol.geom.LineString(coordinates);
                    const feature = new ol.Feature({
                      geometry: lineString,
                      properties: {
                        id: geometryData.ID,
                        name: geometryData.fieldValues ? geometryData.fieldValues[5] : '',
                        ...geometryData
                      }
                    });
                    features.push(feature);
                  } else if (geometryData.geometry && geometryData.geometry.type === 'POINT') {
                    // 处理点要素（POINT）
                    const point = geometryData.geometry.points[0];
                    const pointGeom = new ol.geom.Point([point.x, point.y]);
                    const feature = new ol.Feature({
                      geometry: pointGeom,
                      properties: {
                        id: geometryData.ID,
                        name: geometryData.fieldValues ? geometryData.fieldValues[5] : '',
                        ...geometryData
                      }
                    });
                    features.push(feature);
                  }
                } catch (error) {
                  console.error(`[${layerName}] 第${pageIndex + 1}页-要素${index + 1} geometry解析失败:`, error);
                }
              });
              
              // 返回转换后的要素，不直接渲染
              console.log(`[${layerName}] 第${pageIndex + 1}页数据转换完成，获得${features.length}个要素`);
              resolve(features);
            } else {
              console.warn(`[${layerName}] 第${pageIndex + 1}页没有成功获取到任何geometry数据`);
              resolve([]);
            }
          } else {
            console.warn(`[${layerName}] 第${pageIndex + 1}页响应中没有childUriList字段或格式不正确`);
            resolve([]);
          }
        })
        .catch(error => {
          console.error(`[${layerName}] 第${pageIndex + 1}页加载失败:`, error);
          resolve([]); // 返回空数组
        });
    });

    // ===== 批量加载和渲染流程 =====
    // 1. 先批量保存所有要素数据（1000个一批）
    // 2. 保存完成后，分批渲染到地图（10000个一批）
    const batchSaveSize = 100; // 每批保存1000个要素
    const batchRenderSize = 100; // 每批渲染10000个要素
    
        setTimeout(() => {
          (async () => {
            try {
          console.log(`[${layerName}] 开始批量加载，共${totalPages}页`);
          
          // 第一阶段：批量加载所有数据
          for (let pageIndex = 0; pageIndex < totalPages; pageIndex++) {
            const pageFeatures = await loadPage(pageIndex);
            allFeatures = allFeatures.concat(pageFeatures);
            
            // 每1000个要素打印一次进度
            if (allFeatures.length % batchSaveSize === 0 || pageIndex === totalPages - 1) {
              console.log(`[${layerName}] 已保存${allFeatures.length}个要素数据`);
            }
            
            // 每页之间添加小延迟，避免服务器压力过大
            if (pageIndex < totalPages - 1) {
              await new Promise(resolve => setTimeout(resolve, 50));
            }
          }
          
          console.log(`[${layerName}] 数据加载完成，共获得${allFeatures.length}个要素`);
          
          // 第二阶段：分批渲染到地图
          console.log(`[${layerName}] 开始分批渲染到地图，每批${batchRenderSize}个要素`);
          
          for (let i = 0; i < allFeatures.length; i += batchRenderSize) {
            const batchFeatures = allFeatures.slice(i, i + batchRenderSize);
            vectorlayer.getSource().addFeatures(batchFeatures);
            
            const batchNumber = Math.floor(i / batchRenderSize) + 1;
            const totalBatches = Math.ceil(allFeatures.length / batchRenderSize);
            console.log(`[${layerName}] 渲染第${batchNumber}/${totalBatches}批，${batchFeatures.length}个要素`);
            
            // 每批渲染之间添加延迟，避免界面卡顿
            if (i + batchRenderSize < allFeatures.length) {
              await new Promise(resolve => setTimeout(resolve, 100));
            }
          }
          
          console.log(`[${layerName}] 批量加载和渲染完成，共渲染${allFeatures.length}个要素`);
          
          // 更新图层状态管理中的要素数量信息
          const layerIndex = mapStore.vectorlayers.findIndex(l => l.name === layerName);
          if (layerIndex > -1) {
            mapStore.vectorlayers[layerIndex] = {
              ...mapStore.vectorlayers[layerIndex],
              featureCount: allFeatures.length,
              isLoaded: true
            };
          }
          
            } catch (error) {
          console.error(`[${layerName}] 批量加载错误:`, error);
            }
          })();
        }, DATA_CONFIG.PAGINATION_DELAY);
        
    // ===== 加载完成通知 =====
        // 调用者: loadVectorLayer()
    // 作用: 显示图层加载完成的统计信息
        notificationManager.info(
      `图层 ${layerName} 开始加载`,
      `要素总数: ${featureCountBounds}\n总页数: ${totalPages}\n每页大小: ${pageSize}\n数据来源: SuperMap iServer\n服务器地址: ${apiConfig.baseUrl}\n✅ 使用标准分页加载`
        );
    
    const resolvedVisible = typeof visibleOverride === 'boolean' ? visibleOverride : !!layerConfig.visible
    vectorlayer.setVisible(resolvedVisible);
    let zIndex;
    if (layerName === '武汉_市级') {
      zIndex = DATA_CONFIG.Z_INDEX.CITY_BOUNDARY; // 武汉_市级图层使用最低Z-index
    } else if (layerName === '武汉_县级') {
      zIndex = DATA_CONFIG.Z_INDEX.COUNTY_BOUNDARY; // 武汉_县级图层使用中等Z-index
    } else {
      zIndex = DATA_CONFIG.Z_INDEX.DEFAULT_OFFSET + mapStore.vectorlayers.length; // 其他图层使用默认Z-index
    }
    vectorlayer.setZIndex(zIndex);
    
    // 添加图层到地图和状态管理
      map.addLayer(vectorlayer);
      
      mapStore.vectorlayers.push({
        id: layerConfig.name,
        name: layerName,
        layer: vectorlayer,
        visible: resolvedVisible,
      type: 'vector',
      source: 'supermap',
      isLazyLoaded: false, // 明确设置为非懒加载
      isLoaded: true       // 明确设置为已加载
    });
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
   * @param map 地图实例
   * @param visibleLayers 指定要显示的图层名称数组，如果不提供则使用默认配置
   */
  const loadVectorLayers = async (map: any, visibleLayers?: string[]): Promise<void> => {
    // ===== 首先清空所有现有图层 =====
    clearAllLayersBeforeInit()
    
    const apiConfig = createAPIConfig()
    
    
    const loadTasks: Promise<void>[] = []
    
    for (const layerConfig of apiConfig.wuhanlayers) {
      const layerName = layerConfig.name.split('@')[0] || layerConfig.name
      
      if (layerConfig.type === 'raster') {
        continue;
      }
      
      // 所有图层都立即加载，但根据配置和参数控制可见性
      let shouldBeVisible = true
      
      if (visibleLayers && visibleLayers.length > 0) {
        // 如果指定了可见图层列表，则只有指定的图层可见
        shouldBeVisible = visibleLayers.includes(layerName)
      } else {
        // 如果没有指定，则使用配置中的默认可见性设置
        shouldBeVisible = !!layerConfig.visible
      }
      
      // 所有图层都加载，但控制可见性
        loadingStore.updateLoading('map-init', `正在加载图层: ${layerName}`)
      loadTasks.push(loadVectorLayer(map, layerConfig, shouldBeVisible))
    }
    
    await Promise.allSettled(loadTasks)
  }

  return {
    loadVectorLayer,
    loadVectorLayers,
    clearAllLayersBeforeInit
  }
}
