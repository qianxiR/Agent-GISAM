# 空间分析工具集

## execute_intersection_analysis - 相交分析

### 工具描述
计算两个图层的相交部分。

### 使用场景
- 用户说"对@图层名称进行相交分析"
- 用户说"计算@图层A与@图层B的相交"
- 用户说"相交分析"

### 函数签名
```python
execute_intersection_analysis(
    target_layer_name: str, 
    mask_layer_name: str
) -> Dict[str, Any]
```

### 参数说明
- `target_layer_name` (string): 目标图层名称
- `mask_layer_name` (string): 掩膜图层名称

---

## execute_erase_analysis - 擦除分析

### 工具描述
从目标图层中擦除与擦除图层相交的部分。

### 使用场景
- 用户说"对@图层名称进行擦除分析"
- 用户说"从@图层A中擦除@图层B"
- 用户说"擦除分析"

### 函数签名
```python
execute_erase_analysis(
    target_layer_name: str, 
    erase_layer_name: str
) -> Dict[str, Any]
```

### 参数说明
- `target_layer_name` (string): 目标图层名称
- `erase_layer_name` (string): 擦除图层名称

---

## execute_shortest_path_analysis - 最短路径分析

### 工具描述
计算从起点到终点的最短路径,可选障碍物图层。

### 使用场景
- 用户说"计算@起点到@终点的最短路径"
- 用户说"最短路径分析"
- 用户说"规划从@A到@B的路线"

### 函数签名
```python
execute_shortest_path_analysis(
    start_layer_name: str, 
    end_layer_name: str, 
    obstacle_layer_name: str = ""
) -> Dict[str, Any]
```

### 参数说明
- `start_layer_name` (string): 起点图层名称
- `end_layer_name` (string): 终点图层名称
- `obstacle_layer_name` (string, 可选): 障碍物图层名称

