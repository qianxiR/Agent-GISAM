import type { ServiceResponse } from '@/types/map'
import { createAPIConfig } from '@/utils/config'

export class GeoServerError extends Error {
  constructor(
    message: string,
    public code?: number,
    public type: 'network' | 'service' | 'timeout' = 'service'
  ) {
    super(message)
    this.name = 'GeoServerError'
  }
}

export class GeoServerClient {
  private config = createAPIConfig()

  /**
   * 执行带重试的请求
   */
  private async executeWithRetry<T>(
    operation: () => Promise<T>,
    retryCount: number = 0
  ): Promise<T> {
    try {
      return await operation()
    } catch (error) {
      if (this.shouldRetry(error) && retryCount < this.config.retryCount) {
        console.warn(`请求失败，正在重试 (${retryCount + 1}/${this.config.retryCount}):`, error)
        await new Promise(resolve => setTimeout(resolve, 1000 * (retryCount + 1)))
        return this.executeWithRetry(operation, retryCount + 1)
      }
      throw error
    }
  }

  private shouldRetry(error: any): boolean {
    return (error instanceof GeoServerError && 
      error.type === 'network' || error.type === 'timeout')
  }

  /**
   * 检查GeoServer服务健康状态
   */
  async checkServiceHealth(): Promise<ServiceResponse<boolean>> {
    return this.executeWithRetry(async () => {
      try {
        // 使用WMS GetCapabilities进行健康检查
        const testUrl = `${this.config.baseUrl}/${this.config.mapService}?service=WMS&request=GetCapabilities&version=1.3.0`
        const response = await fetch(testUrl, { 
          method: 'GET',
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
          error: error instanceof Error ? error.message : 'GeoServer服务健康检查失败'
        }
      }
    })
  }

  /**
   * 获取WFS要素数据
   */
  async getFeatures(layerName: string, options: {
    maxFeatures?: number
    outputFormat?: string
    srsName?: string
  } = {}): Promise<ServiceResponse<any>> {
    return this.executeWithRetry(async () => {
      try {
        const params = new URLSearchParams({
          service: 'WFS',
          request: 'GetFeature',
          version: '1.1.0',
          typeName: layerName,
          outputFormat: options.outputFormat || 'application/json',
          srsName: options.srsName || 'EPSG:4326'
        })

        if (options.maxFeatures) {
          params.set('maxFeatures', options.maxFeatures.toString())
        }

        const url = `${this.config.baseUrl}/${this.config.dataService}?${params.toString()}`
        const response = await fetch(url, {
          method: 'GET',
          signal: AbortSignal.timeout(this.config.timeout)
        })

        if (!response.ok) {
          throw new GeoServerError(`WFS请求失败: HTTP ${response.status}`, response.status)
        }

        const data = await response.json()
        return {
          success: true,
          data: data,
          error: undefined
        }
      } catch (error) {
        throw new GeoServerError(
          error instanceof Error ? error.message : '获取要素数据失败',
          500,
          'network'
        )
      }
    })
  }

  /**
   * 获取WMS地图图像
   */
  async getMap(layerName: string, options: {
    bbox?: string
    width?: number
    height?: number
    format?: string
    srs?: string
  } = {}): Promise<ServiceResponse<Blob>> {
    return this.executeWithRetry(async () => {
      try {
        const params = new URLSearchParams({
          service: 'WMS',
          request: 'GetMap',
          version: '1.3.0',
          layers: layerName,
          styles: '',
          format: options.format || 'image/png',
          transparent: 'true',
          width: (options.width || 256).toString(),
          height: (options.height || 256).toString(),
          srs: options.srs || 'EPSG:4326'
        })

        if (options.bbox) {
          params.set('bbox', options.bbox)
        }

        const url = `${this.config.baseUrl}/${this.config.mapService}?${params.toString()}`
        const response = await fetch(url, {
          method: 'GET',
          signal: AbortSignal.timeout(this.config.timeout)
        })

        if (!response.ok) {
          throw new GeoServerError(`WMS请求失败: HTTP ${response.status}`, response.status)
        }

        const blob = await response.blob()
        return {
          success: true,
          data: blob,
          error: undefined
        }
      } catch (error) {
        throw new GeoServerError(
          error instanceof Error ? error.message : '获取地图图像失败',
          500,
          'network'
        )
      }
    })
  }
}

// 导出单例实例
export const geoServerClient = new GeoServerClient()
