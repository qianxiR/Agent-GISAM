# Agent工具集成测试 - 前端状态监测功能

## 概述

增强版的Agent工具集成测试脚本现在支持前端状态监测功能，可以验证各个分析工具执行后是否正确更新了前端地图和图层管理状态。

## 主要功能

### 1. 前端状态监测
- 监测地图状态变化
- 监测图层数量变化
- 监测分析状态变化
- 验证前端状态变化是否符合预期

### 2. 增强的测试报告
- 包含前端状态变化信息
- 验证前端状态变化是否符合工具执行预期
- 详细的错误分析和状态对比

## 使用方法

### 基本测试
```bash
# 运行所有测试（包含前端状态监测）
python test_tools_integration.py

# 指定Agent服务URL
python test_tools_integration.py --url http://localhost:8089

# 指定前端服务URL
python test_tools_integration.py --frontend-url http://localhost:5173
```

### 调试模式
```bash
# 调试单个测试，显示详细响应信息
python test_tools_integration.py --debug "显示医院图层"

# 调试工具调用解析
python test_tools_integration.py --debug "查询医院图层中等级等于三级的医院"
```

### 列出所有测试
```bash
python test_tools_integration.py --list
```

## 前端状态监测

### 状态监测内容
1. **地图状态**
   - 地图是否准备就绪
   - 地图中心点和缩放级别

2. **图层状态**
   - 图层数量变化
   - 图层可见性状态
   - 图层类型和来源

3. **分析状态**
   - 分析状态文本变化
   - 分析进度信息

### 期望状态变化映射
不同工具执行后期望的前端状态变化：

- **图层管理工具** (`toggle_layer_visibility`, `get_open_layers`)
  - 期望变化：`layer_changes`

- **属性查询工具** (`query_features_by_attribute`)
  - 期望变化：`analysis_changes`

- **空间分析工具** (`execute_buffer_analysis`, `execute_intersection_analysis`, 等)
  - 期望变化：`analysis_changes`, `layer_changes`

- **结果保存工具** (`save_*_results_as_layer`)
  - 期望变化：`layer_changes`

- **结果导出工具** (`export_*_results_as_json`)
  - 期望变化：无（导出操作不改变前端状态）

- **知识库工具** (`query_knowledge_base`, `update_knowledge_base`)
  - 期望变化：无（知识库操作不改变前端状态）

## 前端状态API

### 状态API接口
前端提供了状态查询API接口：

```typescript
// 获取前端状态
GET /api/state

// 返回格式
{
  "map_ready": boolean,
  "layers": Array<{
    "name": string,
    "visible": boolean,
    "type": string,
    "source": string
  }>,
  "analysis_status": string,
  "timestamp": number
}
```

### 浏览器控制台监测
在浏览器控制台中可以使用以下脚本监测前端状态：

```javascript
// 加载状态监测脚本
// 在浏览器控制台中执行
const script = document.createElement('script')
script.src = '/frontend_state_monitor.js'
document.head.appendChild(script)

// 获取当前状态
getFrontendState()

// 监测状态变化
monitorStateChanges((before, after) => {
  console.log('状态变化:', { before, after })
}, 2000)
```

## 测试报告

### 报告内容
测试报告现在包含以下信息：

1. **工具调用验证**
   - 工具名称是否正确
   - 参数是否完整
   - 工具执行结果

2. **前端状态监测**
   - 执行前后状态对比
   - 状态变化检测
   - 变化验证结果

3. **详细错误分析**
   - 工具调用错误
   - 前端状态验证错误
   - 状态变化不符合预期的原因

### 报告文件
- 控制台输出：实时显示测试进度和结果
- JSON报告文件：`test_report_<timestamp>.json`
- 日志文件：`test_tools_integration.log`

## 故障排除

### 常见问题

1. **前端状态API不可用**
   - 确保前端服务正在运行
   - 检查前端URL配置是否正确
   - 测试脚本会使用模拟状态继续测试

2. **状态变化未检测到**
   - 检查工具是否实际执行了前端操作
   - 确认前端状态更新机制是否正常工作
   - 使用调试模式查看详细响应信息

3. **工具调用解析失败**
   - 使用 `--debug` 参数查看原始响应
   - 检查Agent服务响应格式是否发生变化
   - 更新解析逻辑以适配新的响应格式

### 调试建议

1. **使用调试模式**
   ```bash
   python test_tools_integration.py --debug "测试提示词"
   ```

2. **检查Agent服务日志**
   - 查看Agent服务的控制台输出
   - 确认工具调用是否成功执行

3. **验证前端状态**
   - 在浏览器控制台中使用状态监测脚本
   - 手动执行工具操作并观察状态变化

## 扩展功能

### 自定义状态验证
可以通过修改 `validate_frontend_changes` 方法来自定义状态验证逻辑：

```python
def validate_frontend_changes(self, test_name: str, frontend_changes: Dict[str, Any], expected_tool: str) -> Dict[str, Any]:
    # 自定义验证逻辑
    # 根据具体需求添加验证规则
    pass
```

### 添加新的状态监测项
可以在 `monitor_frontend_changes` 方法中添加新的状态监测项：

```python
def monitor_frontend_changes(self, test_name: str, before_state: Dict[str, Any], after_state: Dict[str, Any]) -> Dict[str, Any]:
    # 添加新的状态监测逻辑
    # 例如：监测特定图层的变化
    pass
```

## 总结

前端状态监测功能大大增强了测试脚本的验证能力，不仅验证Agent工具调用的正确性，还验证前端状态是否正确更新。这有助于确保整个系统的端到端功能正常工作。
