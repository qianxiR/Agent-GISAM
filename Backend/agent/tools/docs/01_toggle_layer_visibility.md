# toggle_layer_visibility - 图层可见性切换

## 工具描述
切换前端图层的显示/隐藏状态。

## 分类
图层控制

## 使用场景
- 用户说"打开@图层名称"
- 用户说"隐藏@图层名称"
- 用户说"切换@图层名称"

## 函数签名
```python
toggle_layer_visibility(layer_name: str, action: str) -> Dict[str, Any]
```

## 参数说明
- `layer_name` (string): 图层名称,使用@符号标识
- `action` (string): 操作类型
  - `show`: 显示图层
  - `hide`: 隐藏图层
  - `toggle`: 切换图层状态

## 注意事项
⚠️ 必须使用图层名称而非图层ID进行操作

## 调用示例
- 用户: "打开@建筑物图层"
  - → `toggle_layer_visibility(layer_name="建筑物图层", action="show")`
- 用户: "隐藏@道路图层"
  - → `toggle_layer_visibility(layer_name="道路图层", action="hide")`

