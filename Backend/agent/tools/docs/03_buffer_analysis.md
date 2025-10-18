# execute_buffer_analysis - 缓冲区分析

## 工具描述
对指定图层执行缓冲区分析,生成指定半径的缓冲区。

## 分类
空间分析

## 使用场景
- 用户说"对@图层名称进行缓冲区分析"
- 用户说"创建@图层名称的缓冲区"
- 用户说"给@学校图层做500米缓冲区"

## 函数签名
```python
execute_buffer_analysis(
    layer_name: str, 
    radius: float, 
    unit: str = "meters"
) -> Dict[str, Any]
```

## 参数说明
- `layer_name` (string): 图层名称
- `radius` (float): 缓冲区半径(数值)
- `unit` (string): 单位,默认`meters`
  - 可选: `meters`, `kilometers`, `feet`, `miles`

## 注意事项
- 必须指定图层名称、半径和单位
- 半径必须为正数

## 调用示例
- 用户: "对@学校图层做500米缓冲区"
  - → `execute_buffer_analysis(layer_name="学校图层", radius=500, unit="meters")`

- 用户: "给@河流创建1公里缓冲区"
  - → `execute_buffer_analysis(layer_name="河流", radius=1, unit="kilometers")`

