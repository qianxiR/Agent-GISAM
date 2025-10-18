# query_features_by_attribute - 属性查询

## 工具描述
按属性条件查询筛选图层要素。

## 分类
属性查询

## 使用场景
- 用户说"在@图层名称中查找字段=值"
- 用户说"查询@图层名称的属性"
- 用户说"筛选@图层名称"
- 用户说"找出NAME等于学校的要素"

## 函数签名
```python
query_features_by_attribute(
    layer_name: str, 
    field: str, 
    operator: str, 
    value: str
) -> Dict[str, Any]
```

## 参数说明
- `layer_name` (string): 图层名称
- `field` (string): 属性字段名
- `operator` (string): 比较操作符
- `value` (string): 查询值

## ⚠️ 操作符映射规则(重要)
前端只支持特定格式,必须进行映射:

| 用户输入 | 必须映射为 | 说明 |
|---------|-----------|------|
| `=`     | `eq`      | 等于 |
| `!=`    | `ne`      | 不等于 |
| `>`     | `gt`      | 大于 |
| `>=`    | `gte`     | 大于等于 |
| `<`     | `lt`      | 小于 |
| `<=`    | `lte`     | 小于等于 |
| `like`  | `like`    | 模糊匹配(保持不变) |

## 调用示例
- 用户: "查找NAME=学校"
  - ❌ 错误: `operator="="`
  - ✅ 正确: `operator="eq"`
  
- 用户: "筛选人口>1000"
  - → `query_features_by_attribute(field="人口", operator="gt", value="1000")`

