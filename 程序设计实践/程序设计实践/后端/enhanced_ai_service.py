import requests
import json
import time
import logging
from typing import Dict, Any, Optional
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class CircuitBreaker:
    """断路器模式实现，防止连续失败"""
    
    def __init__(self, failure_threshold=3, recovery_timeout=60):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failure_count = 0
        self.last_failure_time = None
        self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN
        
    def record_failure(self):
        """记录失败"""
        self.failure_count += 1
        self.last_failure_time = datetime.now()
        
        if self.failure_count >= self.failure_threshold:
            self.state = "OPEN"
            logger.warning(f"断路器状态变为 OPEN，失败次数: {self.failure_count}")
    
    def record_success(self):
        """记录成功"""
        self.failure_count = 0
        self.state = "CLOSED"
        logger.info("断路器状态变为 CLOSED")
    
    def can_execute(self):
        """检查是否允许执行"""
        if self.state == "CLOSED":
            return True
        
        if self.state == "OPEN":
            if (datetime.now() - self.last_failure_time).total_seconds() > self.recovery_timeout:
                self.state = "HALF_OPEN"
                logger.info("断路器状态变为 HALF_OPEN，尝试恢复")
                return True
            return False
        
        return True  # HALF_OPEN 状态允许执行

class EmergencyAISimulator:
    """增强的应急AI模拟器"""
    
    def __init__(self):
        self.responses = {
            "中奖": {
                "risk": "高危",
                "reason": "检测到中奖诈骗特征：包含虚假中奖信息和可疑链接",
                "advice": "🚨 这是典型的中奖诈骗！请勿点击任何链接，不要提供个人信息，立即删除该信息",
                "keywords": ["中奖", "一等奖", "奖金", "领奖"]
            },
            "密码": {
                "risk": "高危", 
                "reason": "检测到账号密码安全风险：涉及身份验证或密码重置请求",
                "advice": "🔐 请勿在不可信的平台上输入密码！通过官方渠道验证账号安全",
                "keywords": ["密码", "账号", "登录", "验证", "安全码"]
            },
            "转账": {
                "risk": "高危",
                "reason": "检测到资金转账相关风险：涉及金钱交易或汇款请求",
                "advice": "💰 涉及资金操作请务必谨慎！通过官方渠道核实对方身份，不要向陌生人转账",
                "keywords": ["转账", "汇款", "付款", "资金", "保证金"]
            },
            "优惠": {
                "risk": "中危",
                "reason": "检测到营销推广内容：可能存在夸大宣传或诱导消费",
                "advice": "🛍️ 请谨慎对待优惠信息，核实活动真实性再参与",
                "keywords": ["优惠", "促销", "特价", "折扣", "限时"]
            },
            "链接": {
                "risk": "中危",
                "reason": "检测到可疑链接：可能存在钓鱼或恶意网站风险",
                "advice": "🔗 请勿点击不明链接，确认网址安全性后再访问",
                "keywords": ["http://", "https://", "点击链接", "网址", ".com"]
            },
            "个人信息": {
                "risk": "中危", 
                "reason": "检测到个人信息收集企图：要求提供敏感个人信息",
                "advice": "📝 请勿随意提供身份证号、银行卡号等敏感信息",
                "keywords": ["身份证", "手机号", "银行卡", "个人信息", "身份证号"]
            },
            "default": {
                "risk": "安全",
                "reason": "未检测到明显的网络安全风险特征",
                "advice": "✅ 内容相对安全，但仍需保持警惕",
                "keywords": []
            }
        }
        
        # 风险关键词权重
        self.keyword_weights = {
            "高危": ["中奖", "密码", "转账", "汇款", "保证金", "安全码"],
            "中危": ["优惠", "链接", "个人信息", "验证", "登录"],
            "低危": ["促销", "特价", "折扣", "活动"]
        }
    
    def analyze(self, text: str) -> Dict[str, Any]:
        """增强的应急分析逻辑"""
        text_lower = text.lower()
        
        # 检测风险关键词
        detected_risks = []
        for pattern, response in self.responses.items():
            if pattern == "default":
                continue
                
            for keyword in response["keywords"]:
                if keyword in text_lower:
                    detected_risks.append((pattern, response))
                    break
        
        # 根据检测到的风险确定最终响应
        if detected_risks:
            # 优先返回最高风险等级的响应
            risk_priority = {"高危": 3, "中危": 2, "低危": 1}
            highest_risk = max(detected_risks, key=lambda x: risk_priority.get(x[1]["risk"], 0))
            
            logger.info(f"应急模式匹配到风险: {highest_risk[0]}, 等级: {highest_risk[1]['risk']}")
            return highest_risk[1]
        
        # 默认安全响应
        logger.info("应急模式未检测到明显风险，返回默认安全响应")
        return self.responses["default"]

class EnhancedAIService:
    """增强的AI服务，集成智能降级功能"""
    
    def __init__(self, api_key: str, base_url: str, model: str = "glm-4-flash"):
        self.api_key = api_key
        self.base_url = base_url
        self.model = model
        
        # 初始化断路器和应急模拟器
        self.circuit_breaker = CircuitBreaker()
        self.emergency_simulator = EmergencyAISimulator()
        
        # 系统提示词
        self.system_prompt = '''你是专业网络安全分析助手，仅输出JSON格式结果，不要添加任何额外内容（如解释、注释）：

{
"risk": "高危|中危|低危|安全",
"reason": "详细说明风险判断的依据",
"advice": "给用户的具体防范建议", 
"keywords": ["提取的风险关键词"]
}

分析标准：
- 高危：涉及资金转账、账号密码、中奖诈骗、冒充公检法；
- 中危：包含可疑链接、诱导点击、虚假宣传、个人信息收集；
- 低危：普通营销广告、轻微夸大的推广内容；
- 安全：正常日常交流、无风险内容。'''
    
    def _create_headers(self) -> Dict[str, str]:
        """创建请求头"""
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    def _create_payload(self, text: str) -> Dict[str, Any]:
        """创建请求体"""
        return {
            "model": self.model,
            "messages": [
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": f"分析以下文本：{text}"}
            ],
            "temperature": 0.0,
            "max_tokens": 500
        }
    
    def _process_ai_response(self, response_text: str) -> Dict[str, Any]:
        """处理AI响应"""
        try:
            # 清理响应文本
            cleaned_text = response_text.replace("```json", "").replace("```", "").strip()
            result = json.loads(cleaned_text)
            
            # 验证响应格式
            required_fields = ["risk", "reason", "advice", "keywords"]
            if all(field in result for field in required_fields):
                return result
            else:
                raise ValueError("AI响应缺少必要字段")
                
        except (json.JSONDecodeError, ValueError) as e:
            logger.warning(f"AI响应格式错误: {e}，使用应急方案")
            return self.emergency_simulator.analyze("格式错误")
    
    def analyze_with_ai(self, text: str) -> Dict[str, Any]:
        """使用真实AI服务进行分析"""
        try:
            start_time = time.time()
            
            response = requests.post(
                self.base_url,
                headers=self._create_headers(),
                json=self._create_payload(text),
                timeout=30
            )
            response.raise_for_status()
            
            result_text = response.json()["choices"][0]["message"]["content"].strip()
            result = self._process_ai_response(result_text)
            
            # 记录成功
            self.circuit_breaker.record_success()
            
            end_time = time.time()
            logger.info(f"AI分析成功: 风险={result['risk']}, 耗时={end_time-start_time:.2f}s")
            
            return result
            
        except Exception as e:
            # 记录失败
            self.circuit_breaker.record_failure()
            logger.warning(f"AI服务调用失败: {e}")
            raise
    
    def analyze_text(self, text: str) -> Dict[str, Any]:
        """智能降级分析文本"""
        
        # 参数验证
        if not isinstance(text, str) or not text.strip():
            return {
                "risk": "错误",
                "reason": "输入文本无效",
                "advice": "请提供有效的文本内容",
                "keywords": []
            }
        
        text = text.strip()
        if len(text) > 1000:
            return {
                "risk": "错误", 
                "reason": f"文本过长({len(text)}字符)，超过1000字符限制",
                "advice": "请提供不超过1000字符的文本",
                "keywords": []
            }
        
        logger.info(f"开始分析文本: {text[:50]}...")
        
        # 检查断路器状态
        if self.circuit_breaker.can_execute():
            try:
                # 尝试使用真实AI服务
                return self.analyze_with_ai(text)
                
            except Exception as e:
                logger.warning(f"AI服务不可用，降级到应急模式: {e}")
                # 继续执行到应急方案
        else:
            logger.warning("断路器处于OPEN状态，直接使用应急模式")
        
        # 使用应急方案
        emergency_result = self.emergency_simulator.analyze(text)
        logger.info(f"应急分析完成: 风险等级={emergency_result['risk']}")
        
        return emergency_result
    
    def get_service_status(self) -> Dict[str, Any]:
        """获取服务状态"""
        return {
            "ai_service": "available" if self.circuit_breaker.state == "CLOSED" else "degraded",
            "circuit_breaker_state": self.circuit_breaker.state,
            "failure_count": self.circuit_breaker.failure_count,
            "emergency_mode": self.circuit_breaker.state != "CLOSED"
        }