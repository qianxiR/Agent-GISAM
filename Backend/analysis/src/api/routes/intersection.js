/**
 * 相交分析路由
 */
const express = require('express');
const router = express.Router();
const IntersectionAnalysisController = require('../controllers/IntersectionAnalysisController');
const { validateIntersectionRequest } = require('../../middleware/validation');

// 创建控制器实例
const intersectionAnalysisController = new IntersectionAnalysisController();

/**
 * @swagger
 * /api/v1/spatial-analysis/intersection:
 *   post:
 *     summary: 执行相交分析
 *     description: 计算两个图层之间的几何相交关系，返回相交区域
 *     tags: [Intersection Analysis]
 *     requestBody:
 *       required: true
 *       content:
 *         application/json:
 *           schema:
 *             $ref: '#/components/schemas/IntersectionAnalysisRequest'
 *           examples:
 *             example1:
 *               summary: 多边形相交分析示例
 *               value:
 *                 targetData:
 *                   type: "FeatureCollection"
 *                   features:
 *                     - type: "Feature"
 *                       geometry:
 *                         type: "Polygon"
 *                         coordinates: [[[114.1, 30.1], [114.2, 30.1], [114.2, 30.2], [114.1, 30.2], [114.1, 30.1]]]
 *                       properties:
 *                         name: "目标区域"
 *                 maskData:
 *                   type: "FeatureCollection"
 *                   features:
 *                     - type: "Feature"
 *                       geometry:
 *                         type: "Polygon"
 *                         coordinates: [[[114.15, 30.15], [114.25, 30.15], [114.25, 30.25], [114.15, 30.25], [114.15, 30.15]]]
 *                       properties:
 *                         name: "裁剪区域"
 *                 analysisOptions:
 *                   batchSize: 100
 *                   enableProgress: true
 *                   returnGeometry: true
 *                 options:
 *                   resultLayerName: "相交分析测试"
 *     responses:
 *       200:
 *         description: 相交分析执行成功
 *         content:
 *           application/json:
 *             schema:
 *               $ref: '#/components/schemas/IntersectionAnalysisResponse'
 *             examples:
 *               success:
 *                 summary: 成功响应示例
 *                 value:
 *                   success: true
 *                   data:
 *                     id: "intersection_123"
 *                     name: "相交分析结果"
 *                     results:
 *                       - id: "intersection_0_0_1234567890"
 *                         name: "相交区域 1"
 *                         geometry:
 *                           type: "Polygon"
 *                           coordinates: [[[114.15, 30.15], [114.2, 30.15], [114.2, 30.2], [114.15, 30.2], [114.15, 30.15]]]
 *                     statistics:
 *                       totalResults: 1
 *                       targetFeatureCount: 1
 *                       maskFeatureCount: 1
 *                       totalPairs: 1
 *                       successRate: 100
 *                     metadata:
 *                       version: "1.0.0"
 *                       algorithm: "turf-intersect"
 *                       coordinateSystem: "EPSG:4326"
 *                   message: "相交分析执行成功"
 *       400:
 *         description: 请求参数错误
 *         content:
 *           application/json:
 *             schema:
 *               $ref: '#/components/schemas/ErrorResponse'
 *       500:
 *         description: 服务器内部错误
 *         content:
 *           application/json:
 *             schema:
 *               $ref: '#/components/schemas/ErrorResponse'
 */
router.post('/', validateIntersectionRequest, async (req, res) => {
  await intersectionAnalysisController.executeIntersectionAnalysis(req, res);
});

/**
 * @swagger
 * /api/v1/spatial-analysis/intersection/result/{resultId}:
 *   get:
 *     summary: 获取相交分析结果
 *     description: 根据结果ID获取相交分析的结果数据
 *     tags: [Intersection Analysis]
 *     parameters:
 *       - in: path
 *         name: resultId
 *         required: true
 *         description: 分析结果ID
 *         schema:
 *           type: string
 *           example: "intersection_result_2024-01-01T00:00:00-000Z"
 *     responses:
 *       200:
 *         description: 获取分析结果成功
 *         content:
 *           application/json:
 *             schema:
 *               $ref: '#/components/schemas/AnalysisResultResponse'
 *       400:
 *         description: 请求参数错误
 *         content:
 *           application/json:
 *             schema:
 *               $ref: '#/components/schemas/ErrorResponse'
 */
router.get('/result/:resultId', async (req, res) => {
  await intersectionAnalysisController.getAnalysisResult(req, res);
});

/**
 * @swagger
 * /api/v1/spatial-analysis/intersection/options:
 *   get:
 *     summary: 获取相交分析参数选项
 *     description: 获取相交分析支持的参数选项、默认值和限制
 *     tags: [Intersection Analysis]
 *     responses:
 *       200:
 *         description: 获取参数选项成功
 *         content:
 *           application/json:
 *             schema:
 *               type: object
 *               properties:
 *                 success:
 *                   type: boolean
 *                   example: true
 *                 data:
 *                   type: object
 *                   properties:
 *                     options:
 *                       type: object
 *                       properties:
 *                         batchSize:
 *                           type: object
 *                           properties:
 *                             type:
 *                               type: string
 *                               example: "number"
 *                             default:
 *                               type: number
 *                               example: 100
 *                             min:
 *                               type: number
 *                               example: 10
 *                             max:
 *                               type: number
 *                               example: 1000
 *                             description:
 *                               type: string
 *                               example: "批处理大小，控制每次处理的要素组合数量"
 *                         enableProgress:
 *                           type: object
 *                           properties:
 *                             type:
 *                               type: string
 *                               example: "boolean"
 *                             default:
 *                               type: boolean
 *                               example: true
 *                             description:
 *                               type: string
 *                               example: "是否启用进度显示"
 *                         returnGeometry:
 *                           type: object
 *                           properties:
 *                             type:
 *                               type: string
 *                               example: "boolean"
 *                             default:
 *                               type: boolean
 *                               example: true
 *                             description:
 *                               type: string
 *                               example: "是否返回几何数据"
 *                     description:
 *                       type: string
 *                       example: "相交分析参数选项"
 *                     version:
 *                       type: string
 *                       example: "1.0.0"
 *                 message:
 *                   type: string
 *                   example: "获取相交分析选项成功"
 */
router.get('/options', async (req, res) => {
  await intersectionAnalysisController.getAnalysisOptions(req, res);
});


module.exports = router;
