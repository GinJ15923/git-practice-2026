import unittest
import requests
import json
import time
import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class TestBasicFunctionality(unittest.TestCase):
    """基础功能测试"""
    
    def setUp(self):
        """测试前设置"""
        self.base_url = "http://localhost:5000"
        self.test_texts = {
            "safe": "今天天气很好，我们去公园散步吧",
            "high_risk": "恭喜您中奖了！请点击 http://scam.com 领取万元奖金",
            "medium_risk": "限时特惠，购买商品享受5折优惠",
            "low_risk": "您的账号需要验证，请提供基本信息"
        }
    
    def test_01_connectivity(self):
        """测试基础连通性"""
        print("\n=== 测试基础连通性 ===")
        response = requests.get(f"{self.base_url}/test", timeout=5)
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertEqual(data["status"], "success")
        self.assertEqual(data["service"], "网络安全检测API")
        print("✅ 基础连通性测试通过")
    
    def test_02_health_check(self):
        """测试健康检查接口"""
        print("\n=== 测试健康检查 ===")
        response = requests.get(f"{self.base_url}/health", timeout=5)
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertEqual(data["status"], "healthy")
        self.assertIn("service_mode", data)
        self.assertIn("ai_service_status", data)
        print(f"✅ 健康检查通过 - 模式: {data['service_mode']}, AI状态: {data['ai_service_status']}")
    
    def test_03_home_page(self):
        """测试首页访问"""
        print("\n=== 测试首页访问 ===")
        response = requests.get(f"{self.base_url}/", timeout=5)
        self.assertEqual(response.status_code, 200)
        self.assertIn("网络安全检测API服务", response.text)
        print("✅ 首页访问测试通过")
    
    def test_04_safe_text_analysis(self):
        """测试安全文本分析"""
        print("\n=== 测试安全文本分析 ===")
        text = self.test_texts["safe"]
        response = requests.post(
            f"{self.base_url}/api/check",
            json={"text": text},
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        # 验证响应格式
        self.assertIn("risk", data)
        self.assertIn("reason", data)
        self.assertIn("advice", data)
        self.assertIn("keywords", data)
        
        # 安全文本应该返回"安全"或"低危"
        self.assertIn(data["risk"], ["安全", "低危"])
        print(f"✅ 安全文本分析通过 - 风险等级: {data['risk']}")
    
    def test_05_high_risk_text_analysis(self):
        """测试高风险文本分析"""
        print("\n=== 测试高风险文本分析 ===")
        text = self.test_texts["high_risk"]
        response = requests.post(
            f"{self.base_url}/api/check",
            json={"text": text},
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        # 验证响应格式
        self.assertIn("risk", data)
        self.assertIn("reason", data)
        self.assertIn("advice", data)
        self.assertIn("keywords", data)
        
        # 高风险文本应该返回"高危"
        self.assertEqual(data["risk"], "高危")
        print(f"✅ 高风险文本分析通过 - 风险等级: {data['risk']}")
    
    def test_06_response_format_consistency(self):
        """测试响应格式一致性"""
        print("\n=== 测试响应格式一致性 ===")
        for risk_type, text in self.test_texts.items():
            with self.subTest(risk_type=risk_type):
                response = requests.post(
                    f"{self.base_url}/api/check",
                    json={"text": text},
                    headers={'Content-Type': 'application/json'},
                    timeout=10
                )
                
                self.assertEqual(response.status_code, 200)
                data = response.json()
                
                # 验证所有响应都有相同的字段
                required_fields = ["risk", "reason", "advice", "keywords"]
                for field in required_fields:
                    self.assertIn(field, data)
                
                # 验证风险等级是预定义的值
                valid_risks = ["高危", "中危", "低危", "安全", "错误"]
                self.assertIn(data["risk"], valid_risks)
        
        print("✅ 响应格式一致性测试通过")
    
    def test_07_performance_basic(self):
        """测试基础性能"""
        print("\n=== 测试基础性能 ===")
        text = "这是一个性能测试文本"
        times = []
        
        for i in range(3):
            start_time = time.time()
            response = requests.post(
                f"{self.base_url}/api/check",
                json={"text": text},
                timeout=15
            )
            end_time = time.time()
            
            self.assertEqual(response.status_code, 200)
            times.append(end_time - start_time)
            print(f"  请求 {i+1}: {times[-1]:.3f}s")
        
        avg_time = sum(times) / len(times)
        self.assertLess(avg_time, 10.0)  # 平均响应时间应小于10秒
        print(f"✅ 基础性能测试通过 - 平均响应时间: {avg_time:.3f}s")
    
    def test_08_cache_stats_endpoint(self):
        """测试缓存统计接口"""
        print("\n=== 测试缓存统计接口 ===")
        response = requests.get(f"{self.base_url}/api/cache/stats", timeout=5)
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertEqual(data["status"], "success")
        self.assertIn("cache_stats", data)
        
        cache_stats = data["cache_stats"]
        expected_fields = ["total_items", "valid_items", "hit_count", "miss_count", "hit_rate"]
        for field in expected_fields:
            self.assertIn(field, cache_stats)
        
        print("✅ 缓存统计接口测试通过")
    
    def test_09_cache_clear_endpoint(self):
        """测试缓存清空接口"""
        print("\n=== 测试缓存清空接口 ===")
        response = requests.post(f"{self.base_url}/api/cache/clear", timeout=5)
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertEqual(data["status"], "success")
        self.assertIn("message", data)
        
        print("✅ 缓存清空接口测试通过")

if __name__ == "__main__":
    # 运行测试
    unittest.main(verbosity=2)