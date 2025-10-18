# 结果保存工具集

## save_query_results_as_layer - 保存查询结果

### 工具描述
将属性查询结果保存为新图层。

### 使用场景
- 用户说"保存查询结果为图层"
- 用户说"另存为图层"
- 用户说"保存为新图层"

### 函数签名
```python
save_query_results_as_layer(layer_name: str) -> Dict[str, Any]
```

### 参数说明
- `layer_name` (string, 可选): 新图层名称
  - 未指定时系统自动生成: `属性查询_图层名_字段操作值`

---

## save_buffer_results_as_layer - 保存缓冲区结果

### 工具描述
将缓冲区分析结果保存为新图层。

### ⚠️ 重要
只有在执行了`execute_buffer_analysis`后才能调用此工具!

### 使用场景
- 用户说"保存缓冲区分析结果为图层"
- 用户说"另存缓冲区结果为图层"
- 紧接缓冲区分析后用户说"保存"

### 函数签名
```python
save_buffer_results_as_layer(layer_name: str) -> Dict[str, Any]
```

### 参数说明
- `layer_name` (string, 可选): 新图层名称
  - 未指定时系统自动生成: `缓冲区分析_源图层名_半径_分段数`

---

## save_intersection_results_as_layer - 保存相交结果

### ⚠️ 重要
只有在执行了`execute_intersection_analysis`后才能调用!

### 函数签名
```python
save_intersection_results_as_layer(layer_name: str) -> Dict[str, Any]
```

---

## save_erase_results_as_layer - 保存擦除结果

### ⚠️ 重要
只有在执行了`execute_erase_analysis`后才能调用!

### 函数签名
```python
save_erase_results_as_layer(layer_name: str) -> Dict[str, Any]
```

---

## save_path_results_as_layer - 保存路径结果

### ⚠️ 重要
只有在执行了`execute_shortest_path_analysis`后才能调用!

### 函数签名
```python
save_path_results_as_layer(layer_name: str) -> Dict[str, Any]
```

---

## 上下文承接规则

当用户仅说"保存为图层"或"保存"时:
1. 系统自动识别最近一次执行的分析类型
2. 调用对应的保存工具
3. **严禁追问用户要保存哪个分析的结果**

示例:
```
用户: "对@学校做500米缓冲区"
系统: 执行 execute_buffer_analysis

用户: "保存"  # 省略上下文
系统: 自动调用 save_buffer_results_as_layer  ✅
系统: 禁止询问"您要保存哪个分析的结果?" ❌
```

