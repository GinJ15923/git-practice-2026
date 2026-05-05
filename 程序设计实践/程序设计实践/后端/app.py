import requests
import json
from typing import Dict, Any, Optional
from flask import Flask, request, jsonify
from flask_cors import CORS
import logging
import os
import time
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 创建Flask应用实例
app = Flask(__name__)
CORS(app)  # 启用跨域支持

# 导入增强的AI服务
try:
    from enhanced_ai_service import EnhancedAIService, EmergencyAISimulator
    ENHANCED_SERVICE_AVAILABLE = True
except ImportError:
    logger.warning("enhanced_ai_service 导入失败，使用原始应急方案")
    ENHANCED_SERVICE_AVAILABLE = False

# 导入缓存管理器
try:
    from cache_manager_optimized import optimized_cache as cache_manager
    logger.info("使用优化缓存管理器")
except ImportError:
    try:
        from cache_manager_optimized import cache_manager
        logger.info("使用标准缓存管理器")
    except ImportError:
        logger.error("缓存管理器导入失败，创建空缓存管理器")
        # 创建空的缓存管理器作为回退
        class EmptyCache:
            def get(self, text): return None
            def set(self, text, data, ttl=None): pass
            def clear(self): pass
            def get_stats(self): return {}
            def debug_info(self): return {}
        cache_manager = EmptyCache()

class EmergencyAISimulator:
    """应急AI模拟器"""
    
    def __init__(self):
        self.responses = {
            "中奖": {
                "risk": "高危",
                "reason": "检测到中奖诈骗特征",
                "advice": "🚨 这是典型的中奖诈骗，请勿相信！",
                "keywords": ["中奖", "诈骗"]
            },
            "密码": {
                "risk": "高危",
                "reason": "检测到账号密码相关风险",
                "advice": "🔐 请勿在不可信的平台输入密码！",
                "keywords": ["密码", "账号"]
            },
            "转账": {
                "risk": "高危",
                "reason": "涉及资金转账请求",
                "advice": "💰 涉及资金操作请务必谨慎！",
                "keywords": ["转账", "资金"]
            },
            "优惠": {
                "risk": "中危",
                "reason": "检测到营销推广内容",
                "advice": "🛍️ 请谨慎对待优惠信息",
                "keywords": ["优惠", "促销"]
            },
            "default": {
                "risk": "安全",
                "reason": "未检测到明显风险",
                "advice": "✅ 内容相对安全",
                "keywords": []
            }
        }
    
    def analyze(self, text):
        """模拟AI分析"""
        text_lower = text.lower()
        
        for pattern, response in self.responses.items():
            if pattern in text_lower:
                logger.info(f"匹配应急模式: {pattern}")
                return response
        
        return self.responses["default"]

class SecurityAnalyzer:
    """安全分析器，集成增强服务和缓存"""
    
    DEFAULT_CONFIG = {
        "model": "glm-4-flash",
        "temperature": 0.0,
        "max_tokens": 500,
        "timeout": 30,
        "base_url": "https://open.bigmodel.cn/api/paas/v4/chat/completions"
    }
    
    def __init__(self):
        # 从环境变量加载配置
        self.api_key = os.getenv('ZHIPU_API_KEY')
        self.model = os.getenv('AI_MODEL', self.DEFAULT_CONFIG["model"])
        self.base_url = os.getenv('AI_API_BASE_URL', self.DEFAULT_CONFIG["base_url"])
        
        # 初始化服务
        if ENHANCED_SERVICE_AVAILABLE and self.api_key:
            try:
                self.enhanced_service = EnhancedAIService(
                    api_key=self.api_key,
                    base_url=self.base_url,
                    model=self.model
                )
                self.service_mode = "enhanced"
                logger.info("增强AI服务初始化成功")
            except Exception as e:
                logger.error(f"增强AI服务初始化失败: {e}")
                self.service_mode = "emergency_only"
                self.emergency_simulator = EmergencyAISimulator()
        else:
            self.service_mode = "emergency_only"
            self.emergency_simulator = EmergencyAISimulator()
            logger.info("使用应急模式")
    
    def analyze_text(self, text: str) -> Dict[str, Any]:
        """分析文本安全性 - 集成缓存功能和详细性能日志"""
        
        import time
        start_total = time.perf_counter()
        
        # 首先检查缓存
        cache_start = time.perf_counter()
        cached_result = cache_manager.get(text)
        cache_time = time.perf_counter() - cache_start
        
        if cached_result is not None:
            total_time = time.perf_counter() - start_total
            logger.info(f"✅ 缓存命中 - 缓存查找: {cache_time:.6f}s, 总时间: {total_time:.6f}s")
            return cached_result
        
        logger.info(f"🔄 缓存未命中 - 缓存查找: {cache_time:.6f}s")
        logger.info(f"开始分析文本: {text[:50]}...")
        
        # 根据服务模式选择分析方法
        if self.service_mode == "enhanced":
            try:
                result = self.enhanced_service.analyze_text(text)
                logger.info(f"AI分析完成: 风险等级={result.get('risk', '未知')}")
                
                # 只有正常结果才缓存（非错误结果）
                if result.get('risk') != '错误':
                    cache_manager.set(text, result, ttl=300)
                    logger.info(f"已缓存分析结果: {result.get('risk')}")
                else:
                    logger.warning(f"分析结果错误，不缓存: {result.get('reason', '未知错误')}")
                
                analysis_time = time.perf_counter() - start_total
                logger.info(f"📊 增强分析完成 - 总耗时: {analysis_time:.6f}s")
                return result
            except Exception as e:
                logger.error(f"增强服务分析失败: {e}")
                # 降级到应急方案
                result = self.emergency_simulator.analyze(text)
                
                # 应急结果也缓存，但时间较短（2分钟）
                cache_manager.set(text, result, ttl=120)
                return result
        else:
            # 直接使用应急方案
            result = self.emergency_simulator.analyze(text)
            
            # 缓存应急结果
            cache_manager.set(text, result, ttl=300)
            
            analysis_time = time.perf_counter() - start_total
            logger.info(f"📊 应急分析完成 - 总耗时: {analysis_time:.6f}s")
            return result
    
    def _get_fallback_response(self) -> Dict[str, Any]:
        """获取降级响应"""
        return {
            "risk": "中危",
            "reason": "服务暂时不可用，采用保守判断",
            "advice": "请谨慎对待当前内容，等待服务恢复后重新检测",
            "keywords": ["服务降级"]
        }
    
    def get_service_info(self) -> Dict[str, Any]:
        """获取服务信息"""
        if self.service_mode == "enhanced":
            try:
                status = self.enhanced_service.get_service_status()
                cache_stats = cache_manager.get_stats()
                return {
                    "mode": "enhanced",
                    "ai_service": status["ai_service"],
                    "circuit_breaker_state": status["circuit_breaker_state"],
                    "failure_count": status["failure_count"],
                    "emergency_mode": status["emergency_mode"],
                    "cache_stats": cache_stats
                }
            except Exception as e:
                logger.error(f"获取增强服务信息失败: {e}")
                # 降级信息
                cache_stats = cache_manager.get_stats()
                return {
                    "mode": "enhanced_error",
                    "ai_service": "error",
                    "circuit_breaker_state": "unknown",
                    "failure_count": 0,
                    "emergency_mode": True,
                    "cache_stats": cache_stats
                }
        else:
            cache_stats = cache_manager.get_stats()
            return {
                "mode": "emergency_only",
                "ai_service": "unavailable",
                "circuit_breaker_state": "N/A",
                "failure_count": 0,
                "emergency_mode": True,
                "cache_stats": cache_stats
            }
    
    def clear_cache(self) -> Dict[str, Any]:
        """清空缓存"""
        cache_manager.clear()
        return {"status": "success", "message": "缓存已清空"}

# 创建全局实例
security_analyzer = SecurityAnalyzer()

@app.route('/test', methods=['GET'])
def test():
    """测试基础连通性"""
    logger.info("接收到/test接口请求")
    return jsonify({
        "status": "success",
        "message": "Flask服务器运行正常！",
        "service": "网络安全检测API",
        "version": "1.0"
    })

@app.route('/health', methods=['GET'])
def health():
    """增强的健康检查"""
    logger.info("接收到/health接口请求")
    
    # 获取服务状态信息
    service_info = security_analyzer.get_service_info()
    
    return jsonify({
        "status": "healthy",
        "timestamp": int(time.time()),
        "service": "网络安全检测API",
        "version": "1.0",
        "service_mode": service_info["mode"],
        "ai_service_status": service_info["ai_service"],
        "circuit_breaker_state": service_info["circuit_breaker_state"],
        "emergency_mode": service_info["emergency_mode"],
        "cache_stats": service_info.get("cache_stats", {})
    })

@app.route('/api/check', methods=['POST'])
def check_security():
    """安全检测接口"""
    logger.info("接收到/api/check接口请求")
    
    # 首先检查请求内容类型
    if not request.is_json:
        logger.warning("请求Content-Type错误，不是application/json")
        return jsonify({
            "risk": "错误",
            "reason": "Content-Type必须是application/json",
            "advice": "请使用正确的Content-Type",
            "keywords": []
        }), 400
    
    try:
        # 获取请求数据 - 使用silent=True避免JSON解析异常
        data = request.get_json(silent=True, force=False)
        
        # 验证请求数据
        if data is None:
            logger.warning("请求体不是有效的JSON")
            return jsonify({
                "risk": "错误",
                "reason": "请求体不是有效的JSON格式，请检查JSON语法",
                "advice": "请提供有效的JSON数据，例如: {\"text\": \"需要检测的内容\"}",
                "keywords": ["JSON格式错误"]
            }), 400
        
        if 'text' not in data:
            logger.warning("请求缺少text字段")
            return jsonify({
                "risk": "错误",
                "reason": "请求格式错误，缺少text字段",
                "advice": "请提供有效的text参数",
                "keywords": []
            }), 400
        
        text = data['text']
        
        # 参数验证
        if not isinstance(text, str):
            logger.warning("text参数不是字符串类型")
            return jsonify({
                "risk": "错误",
                "reason": "text参数必须是字符串",
                "advice": "请提供有效的文本",
                "keywords": []
            }), 400
        
        text = text.strip()
        
        if len(text) == 0:
            logger.warning("接收到空文本")
            return jsonify({
                "risk": "错误",
                "reason": "文本不能为空",
                "advice": "请提供有效的文本",
                "keywords": []
            }), 400
        
        if len(text) > 1000:
            logger.warning(f"文本过长: {len(text)}字符")
            return jsonify({
                "risk": "错误",
                "reason": f"文本长度{len(text)}超过1000字符限制",
                "advice": "请提供不超过1000字符的文本",
                "keywords": []
            }), 400
        
        # 调用安全分析器进行分析
        result = security_analyzer.analyze_text(text)
        
        # 检查分析器返回的是否是错误结果
        if result.get('risk') == '错误':
            # 如果分析器返回错误，也返回400状态码
            return jsonify(result), 400
        else:
            return jsonify(result)
        
    except Exception as e:
        logger.error(f"接口处理异常: {e}")
        return jsonify({
            "risk": "错误",
            "reason": f"服务器内部错误: {str(e)}",
            "advice": "请稍后重试",
            "keywords": []
        }), 500

@app.route('/api/cache/clear', methods=['POST'])
def clear_cache():
    """清空缓存接口"""
    logger.info("接收到缓存清空请求")
    
    try:
        result = security_analyzer.clear_cache()
        return jsonify(result)
    except Exception as e:
        logger.error(f"清空缓存失败: {e}")
        return jsonify({
            "status": "error",
            "message": f"清空缓存失败: {str(e)}"
        }), 500

@app.route('/api/cache/stats', methods=['GET'])
def cache_stats():
    """获取缓存统计信息"""
    logger.info("接收到缓存统计请求")
    
    try:
        cache_stats = cache_manager.get_stats()
        return jsonify({
            "status": "success",
            "cache_stats": cache_stats
        })
    except Exception as e:
        logger.error(f"获取缓存统计失败: {e}")
        return jsonify({
            "status": "error",
            "message": f"获取缓存统计失败: {str(e)}"
        }), 500

@app.route('/api/debug/cache', methods=['GET'])
def debug_cache():
    """缓存调试接口"""
    try:
        debug_info = cache_manager.debug_info()
        stats = cache_manager.get_stats()
        return jsonify({
            "status": "success",
            "cache_stats": stats,
            "debug_info": debug_info
        })
    except Exception as e:
        logger.error(f"调试缓存失败: {e}")
        return jsonify({
            "status": "error",
            "message": f"调试缓存失败: {str(e)}"
        }), 500

@app.route('/', methods=['GET'])
def home():
    """增强的首页"""
    service_info = security_analyzer.get_service_info()
    
    status_html = "🟢 运行中" if service_info["ai_service"] == "available" else "🟡 降级运行"
    mode_html = "增强模式" if service_info["mode"] == "enhanced" else "应急模式"
    
    cache_stats = service_info.get("cache_stats", {})
    cache_html = f"有效缓存: {cache_stats.get('valid_items', 0)} 项, 命中率: {cache_stats.get('hit_rate', '0%')}"
    
    return f"""
    <h1>网络安全检测API服务</h1>
    <p>服务状态: <strong>{status_html}</strong></p>
    <p>当前模式: <strong>{mode_html}</strong></p>
    <p>断路器状态: <strong>{service_info['circuit_breaker_state']}</strong></p>
    <p>缓存状态: <strong>{cache_html}</strong></p>
    <p>可用接口:</p>
    <ul>
        <li>GET /test - 连通性测试</li>
        <li>GET /health - 健康检查</li>
        <li>POST /api/check - 文本安全检测</li>
        <li>GET /api/cache/stats - 缓存统计</li>
        <li>POST /api/cache/clear - 清空缓存</li>
        <li>GET /api/debug/cache - 缓存调试</li>
    </ul>
    <p><a href="/health">查看详细状态</a></p>
    """

if __name__ == '__main__':
    print("=" * 50)
    print("启动网络安全检测API服务...")
    
    service_info = security_analyzer.get_service_info()
    if service_info["mode"] == "enhanced":
        print("当前模式: 增强AI服务模式")
        print(f"断路器状态: {service_info['circuit_breaker_state']}")
    else:
        print("当前模式: 应急模拟模式")
    
    print("服务将在 http://0.0.0.0:5000 运行")
    print("=" * 50)
    
    # 根据环境决定是否启用调试模式
    debug_mode = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    app.run(host='0.0.0.0', port=5000, debug=debug_mode)