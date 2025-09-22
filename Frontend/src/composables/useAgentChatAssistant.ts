/**
 * AI聊天助手工具调用处理
 * 负责处理AI工具调用并转换为前端事件
 */
export function useAgentChatAssistant() {
  
  /**
   * 处理AI工具调用
   * @param toolCalls AI返回的工具调用数组
   */
  const handleToolCalls = (toolCalls: any[]) => {
    if (!Array.isArray(toolCalls) || toolCalls.length === 0) {
      return
    }

    const call = toolCalls[0]
    const name = call?.name || 'unknown'
    const args = call?.args || {}

    // 调试：打印AI实际调用的工具名称
    console.log(`[Agent] 处理工具调用: ${name}`, args)

    // 根据工具名称分发相应事件
    switch (name) {
      case 'toggle_layer_visibility':
        handleToggleLayerVisibility(args)
        break
      case 'query_features_by_attribute':
        handleQueryFeaturesByAttribute(args)
        break
      case 'save_query_results_as_layer':
        handleSaveQueryResultsAsLayer(args)
        break
      case 'export_query_results_as_json':
        handleExportQueryResultsAsJson(args)
        break
      case 'execute_buffer_analysis':
        handleExecuteBufferAnalysis(args)
        break
      case 'execute_intersection_analysis':
        handleExecuteIntersectionAnalysis(args)
        break
      case 'save_intersection_results_as_layer':
        handleSaveIntersectionResultsAsLayer(args)
        break
      case 'export_intersection_results_as_json':
        handleExportIntersectionResultsAsJson(args)
        break
      case 'execute_erase_analysis':
        handleExecuteEraseAnalysis(args)
        break
      case 'execute_shortest_path_analysis':
        handleExecuteShortestPathAnalysis(args)
        break
      case 'save_buffer_results_as_layer':
        handleSaveBufferResultsAsLayer(args)
        break
      case 'export_buffer_results_as_json':
        handleExportBufferResultsAsJson(args)
        break
      case 'save_erase_results_as_layer':
        handleSaveEraseResultsAsLayer(args)
        break
      case 'export_erase_results_as_json':
        handleExportEraseResultsAsJson(args)
        break
      case 'save_path_results_as_layer':
        handleSavePathResultsAsLayer(args)
        break
      case 'export_path_results_as_json':
        handleExportPathResultsAsJson(args)
        break
      case 'rename_layer':
        handleRenameLayer(args)
        break
      default:
        console.warn(`[Agent] 未知工具: ${name}`)
    }
  }

  /**
   * 处理图层可见性切换
   */
  const handleToggleLayerVisibility = (args: any) => {
    try {
      const layerName = args.layer_name || args.layerName
      const action = args.action
      
      if (layerName && action) {
        const ev = new CustomEvent('agent:toggleLayerVisibility', { 
          detail: { layerName, action } 
        })
        window.dispatchEvent(ev)
        console.log('[Agent] dispatched event: agent:toggleLayerVisibility', { layerName, action })
      }
    } catch (error) {
      console.error('[Agent] 处理图层可见性切换时出错:', error)
    }
  }

  /**
   * 处理属性查询
   */
  const handleQueryFeaturesByAttribute = (args: any) => {
    try {
      const layerName = args.layer_name || args.layerName
      const field = args.field
      const operator = args.operator
      const value = args.value
      
      if (layerName && field && operator && value !== undefined) {
        const eventDetail = { layerName, field, operator, value }
        const ev = new CustomEvent('agent:queryFeaturesByAttribute', { 
          detail: eventDetail 
        })
        window.dispatchEvent(ev)
        console.log('[Agent] dispatched event: agent:queryFeaturesByAttribute', eventDetail)
      }
    } catch (error) {
      console.error('[Agent] 处理属性查询工具调用时出错:', error)
    }
  }

  /**
   * 处理保存查询结果为图层
   */
  const handleSaveQueryResultsAsLayer = (args: any) => {
    try {
      const layerName = args.layer_name || args.layerName
      
      if (layerName) {
        const ev = new CustomEvent('agent:saveQueryResultsAsLayer', { 
          detail: { layerName } 
        })
        window.dispatchEvent(ev)
        console.log('[Agent] dispatched event: agent:saveQueryResultsAsLayer', { layerName })
      }
    } catch (error) {
      console.error('[Agent] 处理保存查询结果工具调用时出错:', error)
    }
  }

  /**
   * 处理导出查询结果为JSON
   */
  const handleExportQueryResultsAsJson = (args: any) => {
    try {
      const fileName = args.file_name || args.fileName
      
      if (fileName) {
        const ev = new CustomEvent('agent:exportQueryResultsAsJson', { 
          detail: { fileName } 
        })
        window.dispatchEvent(ev)
        console.log('[Agent] dispatched event: agent:exportQueryResultsAsJson', { fileName })
      }
    } catch (error) {
      console.error('[Agent] 处理导出查询结果工具调用时出错:', error)
    }
  }

  /**
   * 处理缓冲区分析
   */
  const handleExecuteBufferAnalysis = (args: any) => {
    try {
      const layerName = args.layer_name || args.layerName
      const radius = args.radius
      const unit = args.unit || 'meters'
      
      if (layerName && radius !== undefined) {
        const ev = new CustomEvent('agent:executeBufferAnalysis', { 
          detail: { layerName, radius, unit } 
        })
        window.dispatchEvent(ev)
        console.log('[Agent] dispatched event: agent:executeBufferAnalysis', { layerName, radius, unit })
      }
    } catch (error) {
      console.error('[Agent] 处理缓冲区分析工具调用时出错:', error)
    }
  }

  /**
   * 处理相交分析
   */
  const handleExecuteIntersectionAnalysis = (args: any) => {
    try {
      const targetLayerName = args.target_layer_name || args.targetLayerName
      const maskLayerName = args.mask_layer_name || args.maskLayerName
      
      if (targetLayerName && maskLayerName) {
        const ev = new CustomEvent('agent:executeIntersectionAnalysis', { 
          detail: { targetLayerName, maskLayerName } 
        })
        window.dispatchEvent(ev)
        console.log('[Agent] dispatched event: agent:executeIntersectionAnalysis', { targetLayerName, maskLayerName })
      }
    } catch (error) {
      console.error('[Agent] 处理相交分析工具调用时出错:', error)
    }
  }

  /**
   * 处理保存相交分析结果为图层
   */
  const handleSaveIntersectionResultsAsLayer = (args: any) => {
    try {
      const layerName = args.layer_name || args.layerName
      
      if (layerName) {
        const ev = new CustomEvent('agent:saveIntersectionResultsAsLayer', { 
          detail: { layerName } 
        })
        window.dispatchEvent(ev)
        console.log('[Agent] dispatched event: agent:saveIntersectionResultsAsLayer', { layerName })
      }
    } catch (error) {
      console.error('[Agent] 处理保存相交分析结果工具调用时出错:', error)
    }
  }

  /**
   * 处理导出相交分析结果为JSON
   */
  const handleExportIntersectionResultsAsJson = (args: any) => {
    try {
      const fileName = args.file_name || args.fileName
      
      if (fileName) {
        const ev = new CustomEvent('agent:exportIntersectionResultsAsJson', { 
          detail: { fileName } 
        })
        window.dispatchEvent(ev)
        console.log('[Agent] dispatched event: agent:exportIntersectionResultsAsJson', { fileName })
      }
    } catch (error) {
      console.error('[Agent] 处理导出相交分析结果工具调用时出错:', error)
    }
  }

  /**
   * 处理擦除分析
   */
  const handleExecuteEraseAnalysis = (args: any) => {
    try {
      const targetLayerName = args.target_layer_name || args.targetLayerName
      const eraseLayerName = args.erase_layer_name || args.eraseLayerName
      
      if (targetLayerName && eraseLayerName) {
        const ev = new CustomEvent('agent:executeEraseAnalysis', { 
          detail: { targetLayerName, eraseLayerName } 
        })
        window.dispatchEvent(ev)
        console.log('[Agent] dispatched event: agent:executeEraseAnalysis', { targetLayerName, eraseLayerName })
      }
    } catch (error) {
      console.error('[Agent] 处理擦除分析工具调用时出错:', error)
    }
  }

  /**
   * 处理最短路径分析
   */
  const handleExecuteShortestPathAnalysis = (args: any) => {
    try {
      const startLayerName = args.start_layer_name || args.startLayerName
      const endLayerName = args.end_layer_name || args.endLayerName
      const obstacleLayerName = args.obstacle_layer_name || args.obstacleLayerName || ''
      
      if (startLayerName && endLayerName) {
        const ev = new CustomEvent('agent:executeShortestPathAnalysis', { 
          detail: { startLayerName, endLayerName, obstacleLayerName } 
        })
        window.dispatchEvent(ev)
        console.log('[Agent] dispatched event: agent:executeShortestPathAnalysis', { startLayerName, endLayerName, obstacleLayerName })
      }
    } catch (error) {
      console.error('[Agent] 处理最短路径分析工具调用时出错:', error)
    }
  }

  /**
   * 处理保存缓冲区分析结果为图层
   */
  const handleSaveBufferResultsAsLayer = (args: any) => {
    try {
      const layerName = args.layer_name || args.layerName
      
      console.log('[Agent] 准备分发保存缓冲区分析结果事件:', { layerName, args })
      
      if (layerName) {
        const ev = new CustomEvent('agent:saveBufferResultsAsLayer', { 
          detail: { layerName } 
        })
        window.dispatchEvent(ev)
        console.log('[Agent] dispatched event: agent:saveBufferResultsAsLayer', { layerName })
        
        // 测试事件是否被正确分发
        setTimeout(() => {
          console.log('[Agent] 事件分发后检查 - 3秒后')
        }, 3000)
      } else {
        console.warn('[Agent] 保存缓冲区分析结果事件分发失败 - 缺少layerName:', { layerName, args })
      }
    } catch (error) {
      console.error('[Agent] 处理保存缓冲区分析结果工具调用时出错:', error)
    }
  }

  /**
   * 处理导出缓冲区分析结果为JSON
   */
  const handleExportBufferResultsAsJson = (args: any) => {
    try {
      const fileName = args.file_name || args.fileName
      
      if (fileName) {
        const ev = new CustomEvent('agent:exportBufferResultsAsJson', { 
          detail: { fileName } 
        })
        window.dispatchEvent(ev)
        console.log('[Agent] dispatched event: agent:exportBufferResultsAsJson', { fileName })
      }
    } catch (error) {
      console.error('[Agent] 处理导出缓冲区分析结果工具调用时出错:', error)
    }
  }

  /**
   * 处理保存擦除分析结果为图层
   */
  const handleSaveEraseResultsAsLayer = (args: any) => {
    try {
      const layerName = args.layer_name || args.layerName
      
      if (layerName) {
        const ev = new CustomEvent('agent:saveEraseResultsAsLayer', { 
          detail: { layerName } 
        })
        window.dispatchEvent(ev)
        console.log('[Agent] dispatched event: agent:saveEraseResultsAsLayer', { layerName })
      }
    } catch (error) {
      console.error('[Agent] 处理保存擦除分析结果工具调用时出错:', error)
    }
  }

  /**
   * 处理导出擦除分析结果为JSON
   */
  const handleExportEraseResultsAsJson = (args: any) => {
    try {
      const fileName = args.file_name || args.fileName
      
      if (fileName) {
        const ev = new CustomEvent('agent:exportEraseResultsAsJson', { 
          detail: { fileName } 
        })
        window.dispatchEvent(ev)
        console.log('[Agent] dispatched event: agent:exportEraseResultsAsJson', { fileName })
      }
    } catch (error) {
      console.error('[Agent] 处理导出擦除分析结果工具调用时出错:', error)
    }
  }

  /**
   * 处理保存最短路径分析结果为图层
   */
  const handleSavePathResultsAsLayer = (args: any) => {
    try {
      const layerName = args.layer_name || args.layerName
      
      if (layerName) {
        const ev = new CustomEvent('agent:savePathResultsAsLayer', { 
          detail: { layerName } 
        })
        window.dispatchEvent(ev)
        console.log('[Agent] dispatched event: agent:savePathResultsAsLayer', { layerName })
      }
    } catch (error) {
      console.error('[Agent] 处理保存最短路径分析结果工具调用时出错:', error)
    }
  }

  /**
   * 处理导出最短路径分析结果为JSON
   */
  const handleExportPathResultsAsJson = (args: any) => {
    try {
      const fileName = args.file_name || args.fileName
      
      if (fileName) {
        const ev = new CustomEvent('agent:exportPathResultsAsJson', { 
          detail: { fileName } 
        })
        window.dispatchEvent(ev)
        console.log('[Agent] dispatched event: agent:exportPathResultsAsJson', { fileName })
      }
    } catch (error) {
      console.error('[Agent] 处理导出最短路径分析结果工具调用时出错:', error)
    }
  }

  /**
   * 处理重命名图层
   */
  const handleRenameLayer = (args: any) => {
    try {
      const layerName = args.layer_name || args.layerName
      const newName = args.new_name || args.newName
      
      if (layerName && newName) {
        const ev = new CustomEvent('agent:renameLayer', { 
          detail: { layerName, newName } 
        })
        window.dispatchEvent(ev)
        console.log('[Agent] dispatched event: agent:renameLayer', { layerName, newName })
      }
    } catch (error) {
      console.error('[Agent] 处理重命名图层工具调用时出错:', error)
    }
  }

  return {
    handleToolCalls
  }
}
