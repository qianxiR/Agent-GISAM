# rename_layer - 图层重命名

## 工具描述
修改图层的名称。

## 分类
图层管理

## 使用场景
- 用户说"修改图层@图层名称的名称为新名称"
- 用户说"重命名@图层名称为新名称"
- 用户说"把@旧名称改成新名称"

## 函数签名
```python
rename_layer(layer_name: str, new_name: str) -> Dict[str, Any]
```

## 参数说明
- `layer_name` (string): 原图层名称,自动解析@符号
- `new_name` (string): 新图层名称

## ⚠️ 限制条件
**服务图层不允许重命名!**

只能重命名以下类型的图层:
- ✅ 分析结果图层
- ✅ 属性查询结果图层
- ✅ 用户上传的图层
- ❌ 服务图层(如来自GeoServer的图层)

## 调用示例
- 用户: "把@缓冲区分析结果改成学校缓冲区"
  - → `rename_layer(layer_name="缓冲区分析结果", new_name="学校缓冲区")`

- 用户: "重命名@查询结果1为学校筛选结果"
  - → `rename_layer(layer_name="查询结果1", new_name="学校筛选结果")`

