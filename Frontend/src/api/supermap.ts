import type { ServiceResponse } from '@/types/map'
import { createAPIConfig } from '@/utils/config'

export class SuperMapError extends Error {
  constructor(
    message: string,
    public code?: number,
    public type: 'network' | 'service' | 'timeout' = 'service'
  ) {
    super(message)
    this.name = 'SuperMapError'
  }
}

export class SuperMapClient {
  private config = createAPIConfig()
  
  private async delay(ms: number): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms))
  }

  private async executeWithRetry<T>(
    operation: () => Promise<T>,
    retries: number = this.config.retryCount
  ): Promise<T> {
    try {
      return await operation()
    } catch (error) {
      if (retries > 0 && this.shouldRetry(error)) {
        await this.delay(Math.pow(2, this.config.retryCount - retries) * 1000) // 指数退避
        return this.executeWithRetry(operation, retries - 1)
      }
      throw error
    }
  }

  private shouldRetry(error: any): boolean {
    // 网络错误或超时错误可以重试
    return error instanceof SuperMapError && 
           (error.type === 'network' || error.type === 'timeout')
  }



  async checkServiceHealth(): Promise<ServiceResponse<boolean>> {
    return this.executeWithRetry(async () => {
      try {
        // 使用服务根URL进行健康检查
        const testUrl = `${this.config.baseUrl}/iserver/services/map-guanlifenxipingtai-2/rest/maps/wuhan_map`
        const response = await fetch(testUrl, { 
          method: 'HEAD',
          signal: AbortSignal.timeout(this.config.timeout)
        })
        
        return {
          success: response.ok,
          data: response.ok,
          error: response.ok ? undefined : `HTTP ${response.status}`
        }
      } catch (error) {
        return {
          success: false,
          data: false,
          error: error instanceof Error ? error.message : '服务健康检查失败'
        }
      }
    })
  }

  /**
   * 获取数据集的要素列表信息
   * @param datasetName 数据集名称（可以是纯数据集名称，也可以是 dataset@datasource 格式）
   */
  async getFeaturesList(datasetName: string): Promise<ServiceResponse<any>> {
    return this.executeWithRetry(async () => {
      try {
        // 解析数据集名称和数据源名称
        let dataset: string
        let datasource: string
        
        if (datasetName.includes('@')) {
          // 如果包含@，按格式 dataset@datasource 解析
          const parts = datasetName.split('@')
          dataset = parts[0]
          datasource = parts[1] || this.config.workspace || 'wuhan'
        } else {
          // 如果不包含@，使用纯数据集名称，数据源从配置获取
          dataset = datasetName
          // 从配置中获取工作空间名称作为数据源名称
          datasource = this.config.workspace || 'wuhan'
        }
        
        // SuperMap iServer REST API 获取要素列表的标准端点
        // 格式: /datasources/{datasource}/datasets/{dataset}/features.json
        const url = `${this.config.baseUrl}/${this.config.dataService}/datasources/${datasource}/datasets/${encodeURIComponent(dataset)}/features.json`
        console.log(`[SuperMap API] 获取要素列表 - 数据集: ${dataset}, 数据源: ${datasource}, URL: ${url}`)
        
        const response = await fetch(url, {
          signal: AbortSignal.timeout(this.config.timeout),
          headers: {
            'Accept': 'application/json'
          }
        })
        
        if (!response.ok) {
          const errorText = await response.text().catch(() => '无法读取错误信息')
          const errorMsg = `获取要素列表失败: HTTP ${response.status}\n数据集: ${dataset}\n数据源: ${datasource}\nURL: ${url}\n错误详情: ${errorText.substring(0, 200)}`
          throw new SuperMapError(errorMsg, response.status)
        }
        
        // 检查响应内容类型
        const contentType = response.headers.get('content-type') || ''
        if (!contentType.includes('application/json') && !contentType.includes('text/json')) {
          const text = await response.text()
          if (text.trim().startsWith('<!DOCTYPE') || text.trim().startsWith('<html')) {
            throw new SuperMapError(`服务器返回了HTML错误页面而不是JSON数据\nURL: ${url}\n响应内容: ${text.substring(0, 500)}`, response.status, 'service')
          }
          throw new SuperMapError(`响应内容类型不正确: ${contentType}\nURL: ${url}`, response.status, 'service')
        }
        
        const data = await response.json()
        console.log(`[SuperMap API] 获取要素列表响应数据:`, data)
        
        // SuperMap返回的格式: { startIndex, childUriList: [...], geometryType, featureCount }
        // 从childUriList中提取要素ID
        let featureIds: string[] = []
        
        if (data.childUriList && Array.isArray(data.childUriList)) {
          console.log(`[SuperMap API] 找到 childUriList，共 ${data.childUriList.length} 个要素URL`)
          // 从URL中提取要素ID，格式如: http://.../feature/0-0-0
          featureIds = data.childUriList.map((uri: string) => {
            // 提取URL最后一部分作为要素ID
            const parts = uri.split('/')
            const lastPart = parts[parts.length - 1]
            console.log(`[SuperMap API] 从URL提取要素ID: ${uri} -> ${lastPart}`)
            return lastPart
          })
          console.log(`[SuperMap API] 提取到的要素ID列表:`, featureIds)
        } else if (Array.isArray(data)) {
          console.log(`[SuperMap API] 响应数据是数组格式，共 ${data.length} 个元素`)
          // 如果直接是数组
          featureIds = data.map((item: any) => item.id || item.ID || String(item))
        } else if (data.features && Array.isArray(data.features)) {
          console.log(`[SuperMap API] 找到 features 数组，共 ${data.features.length} 个要素`)
          featureIds = data.features.map((item: any) => item.id || item.ID || String(item))
        } else if (data.featureIds && Array.isArray(data.featureIds)) {
          console.log(`[SuperMap API] 找到 featureIds 数组，共 ${data.featureIds.length} 个要素ID`)
          featureIds = data.featureIds
        } else {
          console.warn(`[SuperMap API] 未找到预期的数据格式，响应数据结构:`, Object.keys(data))
        }
        
        const featureCount = data.featureCount || featureIds.length
        console.log(`[SuperMap API] 最终提取到 ${featureIds.length} 个要素ID，要素总数: ${featureCount}`)
        
        return {
          success: true,
          data: {
            startIndex: data.startIndex || 0,
            featureCount: featureCount,
            totalCount: featureCount,
            currentCount: featureIds.length,
            featureIds: featureIds,
            geometryType: data.geometryType,
            childUriList: data.childUriList
          },
          error: undefined
        }
      } catch (error) {
        return {
          success: false,
          data: null,
          error: error instanceof Error ? error.message : '获取要素列表失败'
        }
      }
    })
  }



  /**
   * @param datasetNames 数据集名称数组
   * @param bounds 空间边界范围
   * @param options 查询选项
   */
  async getFeaturesByBoundsOptimized(
    datasetNames: string[],
    bounds: number[],
    options: {
      fromIndex?: number
      toIndex?: number
      maxFeatures?: number
      attributeFilter?: string
      spatialQueryMode?: string
    } = {}
  ): Promise<ServiceResponse<any>> {
    return this.executeWithRetry(async () => {
      try {
        const datasetName = datasetNames[0]
        const parts = datasetName.split(':')
        const datasource = parts[0]
        const dataset = parts[1]
        
        // 构建查询参数
        const params = new URLSearchParams({
          returnContent: 'true',
          returnFeaturesOnly: 'true', // ✅ 官方推荐：设置为true提升性能
          maxFeatures: (options.maxFeatures || -1).toString(),
          fromIndex: (options.fromIndex || 0).toString(),
          toIndex: (options.toIndex || -1).toString(),
          bounds: bounds.join(','),
          spatialQueryMode: options.spatialQueryMode || 'INTERSECT'
        })
        
        if (options.attributeFilter) {
          params.append('attributeFilter', options.attributeFilter)
        }
        
        const url = `${this.config.baseUrl}/${this.config.dataService}/datasources/${datasource}/datasets/${dataset}/features/?${params}`
        const response = await fetch(url, {
          signal: AbortSignal.timeout(this.config.timeout)
        })
        
        if (!response.ok) {
          throw new SuperMapError(`要素查询失败: HTTP ${response.status}`, response.status)
        }
        
        const data = await response.json()
        return {
          success: true,
          data: data,
          error: undefined
        }
      } catch (error) {
        return {
          success: false,
          data: null,
          error: error instanceof Error ? error.message : '要素查询失败'
        }
      }
    })
  }

  /**
   * 加载数据集的所有要素
   * @param datasetName 数据集名称
   * @param batchSize 批次大小
   * @param progressCallback 进度回调函数
   */
  async getAllFeatures(
    datasetName: string, 
    batchSize: number = 10000,
    progressCallback?: (loaded: number, total: number) => void
  ): Promise<ServiceResponse<any[]>> {
    return this.executeWithRetry(async () => {
      try {

        
        // 首先获取数据集信息和要素ID列表
        const listResult = await this.getFeaturesList(datasetName)
        if (!listResult.success) {
          throw new Error(listResult.error || '获取数据集信息失败')
        }
        
        const totalCount = listResult.data.totalCount || listResult.data.featureCount || 0
        const featureIds = listResult.data.featureIds || []
        const allFeatures: any[] = []
        
        // 分页加载所有要素
        for (let fromIndex = 0; fromIndex < totalCount; fromIndex += batchSize) {
          const toIndex = Math.min(fromIndex + batchSize - 1, totalCount - 1)
          
          const batchResult = await this.getFeaturesBatch(datasetName, fromIndex, toIndex, featureIds)
          if (batchResult.success && batchResult.data) {
            allFeatures.push(...batchResult.data)
            
            // 调用进度回调
            if (progressCallback) {
              progressCallback(allFeatures.length, totalCount)
            }
          } else {
            console.warn(`批次加载失败: ${fromIndex}-${toIndex}`)
          }
        }
        
        return {
          success: true,
          data: allFeatures,
          error: undefined
        }
      } catch (error) {
        return {
          success: false,
          data: [],
          error: error instanceof Error ? error.message : '加载所有要素失败'
        }
      }
    })
  }

  /**
   * 获取单个要素的详细信息
   * @param featureId 要素ID（格式如 "0-0-0"）
   */
  async getFeatureById(featureId: string): Promise<ServiceResponse<any>> {
    return this.executeWithRetry(async () => {
      try {
        // SuperMap iServer REST API 获取单个要素的端点
        // 格式: /data/feature/{featureId}.json?hasGeometry=true
        const url = `${this.config.baseUrl}/${this.config.dataService}/feature/${featureId}.json`
        const params = new URLSearchParams({
          hasGeometry: 'true'
        })
        const fullUrl = `${url}?${params}`
        
        const response = await fetch(fullUrl, {
          signal: AbortSignal.timeout(this.config.timeout),
          headers: {
            'Accept': 'application/json'
          }
        })
        
        if (!response.ok) {
          const errorText = await response.text().catch(() => '无法读取错误信息')
          const errorMsg = `获取要素失败: HTTP ${response.status}\n要素ID: ${featureId}\nURL: ${fullUrl}\n错误详情: ${errorText.substring(0, 200)}`
          throw new SuperMapError(errorMsg, response.status)
        }
        
        // 检查响应内容类型
        const contentType = response.headers.get('content-type') || ''
        if (!contentType.includes('application/json') && !contentType.includes('text/json')) {
          const text = await response.text()
          if (text.trim().startsWith('<!DOCTYPE') || text.trim().startsWith('<html')) {
            throw new SuperMapError(`服务器返回了HTML错误页面而不是JSON数据\nURL: ${fullUrl}\n响应内容: ${text.substring(0, 500)}`, response.status, 'service')
          }
          throw new SuperMapError(`响应内容类型不正确: ${contentType}\nURL: ${fullUrl}`, response.status, 'service')
        }
        
        const data = await response.json()
        return {
          success: true,
          data: data,
          error: undefined
        }
      } catch (error) {
        return {
          success: false,
          data: null,
          error: error instanceof Error ? error.message : '获取要素失败'
        }
      }
    })
  }

  /**
   * 加载指定范围的要素
   * @param datasetName 数据集名称（可以是纯数据集名称，也可以是 dataset@datasource 格式）
   * @param startIndex 起始索引
   * @param endIndex 结束索引
   * @param featureIds 要素ID列表（可选，如果提供则直接使用）
   */
  async getFeaturesBatch(
    datasetName: string, 
    startIndex: number, 
    endIndex: number,
    featureIds?: string[]
  ): Promise<ServiceResponse<any[]>> {
    return this.executeWithRetry(async () => {
      try {
        // 如果没有提供要素ID列表，先获取要素列表
        let ids: string[] = []
        if (!featureIds || featureIds.length === 0) {
          const listResult = await this.getFeaturesList(datasetName)
          if (!listResult.success || !listResult.data?.featureIds) {
            throw new Error(listResult.error || '无法获取要素ID列表')
          }
          ids = listResult.data.featureIds
        } else {
          ids = featureIds
        }
        
        // 根据索引范围获取要素ID子集
        const targetIds = ids.slice(startIndex, endIndex + 1)
        if (targetIds.length === 0) {
          return {
            success: true,
            data: [],
            error: undefined
          }
        }
        
        // 批量获取要素详细信息
        const features: any[] = []
        const batchSize = 10 // 每次并发请求10个要素
        
        for (let i = 0; i < targetIds.length; i += batchSize) {
          const batch = targetIds.slice(i, i + batchSize)
          const batchPromises = batch.map(id => this.getFeatureById(id))
          const batchResults = await Promise.allSettled(batchPromises)
          
          batchResults.forEach((result, index) => {
            if (result.status === 'fulfilled' && result.value.success && result.value.data) {
              features.push(result.value.data)
            } else {
              console.warn(`获取要素失败 [${batch[index]}]:`, 
                result.status === 'fulfilled' ? result.value.error : result.reason)
            }
          })
        }
        
        return {
          success: true,
          data: features,
          error: undefined
        }
      } catch (error) {
        return {
          success: false,
          data: [],
          error: error instanceof Error ? error.message : '获取要素批次失败'
        }
      }
    })
  }
}

export const superMapClient = new SuperMapClient()