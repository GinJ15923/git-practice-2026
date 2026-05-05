# 网络安全检测API文档

## 基础信息
- 基础URL: ` https://unshapen-diagnosable-alaya.ngrok-free.dev` 或你的ngrok地址
- 编码格式: UTF-8
- 数据格式: JSON

## 接口列表

### 1. 连通性测试
**端点**: `GET /test`

**响应**:
```json
{
    "status": "success",
    "message": "Flask服务器运行正常！",
    "service": "网络安全检测API", 
    "version": "1.0"
}