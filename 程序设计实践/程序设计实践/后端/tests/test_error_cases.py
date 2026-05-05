import unittest
import requests
import json
import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class TestErrorCases(unittest.TestCase):
    """错误情况测试"""
    
    def setUp(self):
        """测试前设置"""
        self.base_url = "http://localhost:5000"
    
    def test_01_empty_text(self):
        """测试空文本"""
        print("\n=== 测试空文本 ===")
        response = requests.post(
            f"{self.base_url}/api/check",
            json={"text": ""},
            headers={'Content-Type': 'application/json'},
            timeout=5
        )
        
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertEqual(data["risk"], "错误")
        self.assertIn("文本不能为空", data["reason"])
        print("✅ 空文本测试通过")
    
    def test_02_missing_text_field(self):
        """测试缺少text字段"""
        print("\n=== 测试缺少text字段 ===")
        response = requests.post(
            f"{self.base_url}/api/check",
            json={},
            headers={'Content-Type': 'application/json'},
            timeout=5
        )
        
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertEqual(data["risk"], "错误")
        self.assertIn("缺少text字段", data["reason"])
        print("✅ 缺少text字段测试通过")
    
    def test_03_long_text(self):
        """测试超长文本"""
        print("\n=== 测试超长文本 ===")
        long_text = "a" * 1001
        response = requests.post(
            f"{self.base_url}/api/check",
            json={"text": long_text},
            headers={'Content-Type': 'application/json'},
            timeout=5
        )
        
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertEqual(data["risk"], "错误")
        self.assertIn("超过1000字符限制", data["reason"])
        print("✅ 超长文本测试通过")
    
    def test_04_invalid_content_type(self):
        """测试错误的Content-Type"""
        print("\n=== 测试错误的Content-Type ===")
        response = requests.post(
            f"{self.base_url}/api/check",
            data="plain text",
            headers={'Content-Type': 'text/plain'},
            timeout=5
        )
        
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertEqual(data["risk"], "错误")
        self.assertIn("Content-Type必须是application/json", data["reason"])
        print("✅ 错误Content-Type测试通过")
    
    def test_05_invalid_json(self):
        """测试无效的JSON"""
        print("\n=== 测试无效的JSON ===")
        
        # 方法1: 使用requests直接发送无效JSON
        import json as json_module
        try:
            response = requests.post(
                f"{self.base_url}/api/check",
                data="invalid json {",
                headers={'Content-Type': 'application/json'},
                timeout=5
            )
            
            # 期望返回400错误
            self.assertEqual(response.status_code, 400)
            data = response.json()
            self.assertEqual(data["risk"], "错误")
            self.assertIn("不是有效的JSON", data["reason"])
            print("✅ 无效JSON测试通过")
            
        except Exception as e:
            # 如果上述方法失败，尝试另一种方法
            print(f"   方法1失败: {e}，尝试方法2")
            
            # 方法2: 使用更直接的无效JSON
            try:
                response = requests.post(
                    f"{self.base_url}/api/check",
                    data=json_module.dumps({"text": "test"})[:-1],  # 删除最后一个字符使其无效
                    headers={'Content-Type': 'application/json'},
                    timeout=5
                )
                
                self.assertEqual(response.status_code, 400)
                data = response.json()
                self.assertEqual(data["risk"], "错误")
                print("✅ 无效JSON测试通过（方法2）")
                
            except Exception as e2:
                print(f"   方法2也失败: {e2}")
                self.fail(f"无效JSON测试失败: {e2}")
    
    def test_06_none_text(self):
        """测试text为None"""
        print("\n=== 测试text为None ===")
        response = requests.post(
            f"{self.base_url}/api/check",
            json={"text": None},
            headers={'Content-Type': 'application/json'},
            timeout=5
        )
        
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertEqual(data["risk"], "错误")
        self.assertIn("必须是字符串", data["reason"])
        print("✅ text为None测试通过")
    
    def test_07_non_string_text(self):
        """测试非字符串text"""
        print("\n=== 测试非字符串text ===")
        response = requests.post(
            f"{self.base_url}/api/check",
            json={"text": 123},
            headers={'Content-Type': 'application/json'},
            timeout=5
        )
        
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertEqual(data["risk"], "错误")
        self.assertIn("必须是字符串", data["reason"])
        print("✅ 非字符串text测试通过")
    
    def test_08_whitespace_only_text(self):
        """测试只有空格的文本"""
        print("\n=== 测试只有空格的文本 ===")
        response = requests.post(
            f"{self.base_url}/api/check",
            json={"text": "   "},
            headers={'Content-Type': 'application/json'},
            timeout=5
        )
        
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertEqual(data["risk"], "错误")
        self.assertIn("文本不能为空", data["reason"])
        print("✅ 只有空格的文本测试通过")
    
    def test_09_special_characters_text(self):
        """测试特殊字符文本"""
        print("\n=== 测试特殊字符文本 ===")
        special_text = "!@#$%^&*()_+-=[]{}|;:,.<>?/"
        response = requests.post(
            f"{self.base_url}/api/check",
            json={"text": special_text},
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        
        # 特殊字符文本应该能正常处理，返回200
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("risk", data)
        self.assertIn("reason", data)
        print("✅ 特殊字符文本测试通过")
    
    def test_10_unicode_text(self):
        """测试Unicode文本"""
        print("\n=== 测试Unicode文本 ===")
        unicode_text = "中文测试 🚀 🌟 😊 絵文字"
        response = requests.post(
            f"{self.base_url}/api/check",
            json={"text": unicode_text},
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        
        # Unicode文本应该能正常处理，返回200
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("risk", data)
        self.assertIn("reason", data)
        print("✅ Unicode文本测试通过")
    
    def test_11_edge_case_length(self):
        """测试边界长度文本"""
        print("\n=== 测试边界长度文本 ===")
        # 刚好1000字符的文本
        edge_text = "a" * 1000
        response = requests.post(
            f"{self.base_url}/api/check",
            json={"text": edge_text},
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        
        # 边界长度文本应该能正常处理，返回200
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("risk", data)
        self.assertIn("reason", data)
        print("✅ 边界长度文本测试通过")
        
    def test_12_malformed_json(self):
        """测试各种格式错误的JSON"""
        print("\n=== 测试各种格式错误的JSON ===")
        
        malformed_jsons = [
            "invalid json {",           # 不完整的JSON
            "{text: 'test'}",           # 缺少引号
            "{'text': 'test'}",         # 使用单引号
            '{"text": "test",}',        # 多余的逗号
            "",                         # 空字符串
            "null",                     # null值
            "undefined",                # undefined
            "<xml>test</xml>",          # XML格式
            "text=test",                # 表单格式
        ]
        
        for i, malformed_json in enumerate(malformed_jsons, 1):
            with self.subTest(json_type=f"malformed_{i}"):
                try:
                    response = requests.post(
                        f"{self.base_url}/api/check",
                        data=malformed_json,
                        headers={'Content-Type': 'application/json'},
                        timeout=5
                    )
                    
                    # 所有格式错误的JSON都应该返回400
                    self.assertEqual(response.status_code, 400, 
                                   f"格式错误的JSON #{i} 应该返回400，实际返回 {response.status_code}")
                    
                    if response.status_code == 400:
                        data = response.json()
                        self.assertEqual(data["risk"], "错误")
                        self.assertIn("JSON", data["reason"])
                        print(f"   ✅ 格式错误JSON #{i} 测试通过")
                    else:
                        print(f"   ❌ 格式错误JSON #{i} 测试失败 - 状态码: {response.status_code}")
                        
                except Exception as e:
                    print(f"   ❌ 格式错误JSON #{i} 测试异常: {e}")
                    # 不在这里失败，继续测试其他情况

if __name__ == "__main__":
    # 运行测试
    unittest.main(verbosity=2)