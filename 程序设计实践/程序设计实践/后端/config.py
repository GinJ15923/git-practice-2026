"""
统一配置文件
整合所有项目配置参数
"""

class Config:
    """主配置类"""
    
    # 基础URL配置
    BASE_URL = "http://localhost:5000"
    
    # 团队外部访问配置（NGROK）
    TEAM_NGROK_URL = " https://unshapen-diagnosable-alaya.ngrok-free.dev"
    
    # API端点配置
    API_ENDPOINTS = {
        "health": f"{TEAM_NGROK_URL}/health",
        "test": f"{TEAM_NGROK_URL}/test", 
        "check": f"{TEAM_NGROK_URL}/api/check"
    }
    
    # 测试超时时间
    TIMEOUT_SHORT = 5
    TIMEOUT_LONG = 15
    
    # 测试文本集合
    TEST_TEXTS = {
        "safe": "今天天气很好，我们去公园散步吧",
        "high_risk": "恭喜您中奖了！请点击 http://scam.com 领取万元奖金",
        "medium_risk": "限时特惠，购买商品享受5折优惠",
        "low_risk": "您的账号需要验证，请提供基本信息",
        "special_chars": "!@#$%^&*()_+-=[]{}|;:,.<>?/",
        "unicode": "中文测试 🚀 🌟 😊 絵文字"
    }
    
    # 测试用例列表
    TEST_CASES = [
        {"text": "恭喜您中奖100万元！", "expected_risk": "高危"},
        {"text": "您的银行账号存在异常", "expected_risk": "中危"},
        {"text": "今天天气很好", "expected_risk": "安全"}
    ]


# 导出单例配置对象，便于其他模块导入使用
config = Config()