/**
 * 字符串ID生成工具
 * 用于根据图层字段信息生成唯一标识符
 */

const crypto = require('crypto');

/**
 * 生成字符串ID
 * 
 * 输入数据格式：
 * @param {Object} options - 生成选项
 * @param {Array<string>} options.fieldNames - 字段名数组
 * @param {Array<any>} options.fieldValues - 字段值数组
 * @param {string} options.id - 图层ID（可选，用于备用）
 * @param {string} options.layerName - 图层名称（可选，用于备用）
 * 
 * 数据处理方法：
 * 1. 优先使用 fieldNames 和 fieldValues 生成哈希值
 * 2. 如果字段数据不完整，使用 id 或 layerName 作为备用
 * 3. 使用 SHA256 算法生成唯一标识符
 * 
 * 输出数据格式：
 * string - 生成的字符串ID
 */
function generateStringID(options = {}) {
  const { fieldNames = [], fieldValues = [], id, layerName } = options;
  
  // 如果 fieldNames 和 fieldValues 都存在且长度一致，使用它们生成ID
  if (fieldNames.length > 0 && fieldValues.length > 0 && fieldNames.length === fieldValues.length) {
    // 将字段名和字段值组合成字符串
    const fieldPairs = fieldNames.map((name, index) => {
      const value = fieldValues[index];
      // 处理各种类型的值
      const valueStr = value === null || value === undefined ? '' : String(value);
      return `${name}:${valueStr}`;
    });
    
    const combinedString = fieldPairs.join('|');
    
    // 使用 SHA256 生成哈希值，取前16位作为ID
    const hash = crypto.createHash('sha256').update(combinedString).digest('hex');
    return hash.substring(0, 16);
  }
  
  // 备用方案：使用 id 或 layerName
  if (id) {
    const hash = crypto.createHash('sha256').update(String(id)).digest('hex');
    return hash.substring(0, 16);
  }
  
  if (layerName) {
    const hash = crypto.createHash('sha256').update(String(layerName)).digest('hex');
    return hash.substring(0, 16);
  }
  
  // 最后的备用方案：使用时间戳和随机数
  const timestamp = Date.now().toString(36);
  const random = Math.random().toString(36).substr(2, 5);
  return `${timestamp}_${random}`;
}

/**
 * 为图层对象添加或更新 stringID
 * 
 * 输入数据格式：
 * @param {Object} layerData - 图层数据对象
 * 
 * 数据处理方法：
 * 1. 检查是否已有 stringID
 * 2. 如果没有或为空，根据字段信息生成
 * 3. 更新图层对象的 stringID 字段
 * 
 * 输出数据格式：
 * Object - 更新后的图层数据对象
 */
function ensureStringID(layerData) {
  if (!layerData) {
    return layerData;
  }
  
  // 如果 stringID 已存在且不为空，直接返回
  if (layerData.stringID && layerData.stringID.trim() !== '') {
    return layerData;
  }
  
  // 生成新的 stringID
  layerData.stringID = generateStringID({
    fieldNames: layerData.fieldNames || [],
    fieldValues: layerData.fieldValues || [],
    id: layerData.id || layerData.ID,
    layerName: layerData.layer_name || layerData.name
  });
  
  return layerData;
}

module.exports = {
  generateStringID,
  ensureStringID
};

