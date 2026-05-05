# test_json_handling.py
import requests
import json

def test_json_handling():
    """专门测试JSON处理"""
    base_url = "http://localhost:5000"
    
    print("=" * 60)
    print("JSON处理专项测试")
    print("=" * 60)
    
    test_cases = [
        {
            "name": "有效JSON",
            "data": '{"text": "hello world"}',
            "expected_code": 200,
            "should_succeed": True
        },
        {
            "name": "无效JSON - 缺少引号",
            "data": '{text: "hello world"}',
            "expected_code": 400,
            "should_succeed": False
        },
        {
            "name": "无效JSON - 不完整",
            "data": '{"text": "hello world"',
            "expected_code": 400,
            "should_succeed": False
        },
        {
            "name": "无效JSON - 语法错误",
            "data": '{"text": "hello world",}',
            "expected_code": 400,
            "should_succeed": False
        },
        {
            "name": "无效JSON - 单引号",
            "data": "{'text': 'hello world'}",
            "expected_code": 400,
            "should_succeed": False
        },
        {
            "name": "空JSON对象",
            "data": "{}",
            "expected_code": 400,
            "should_succeed": False
        },
        {
            "name": "空字符串",
            "data": "",
            "expected_code": 400,
            "should_succeed": False
        },
        {
            "name": "纯文本",
            "data": "just plain text",
            "expected_code": 400,
            "should_succeed": False
        },
        {
            "name": "null值",
            "data": "null",
            "expected_code": 400,
            "should_succeed": False
        }
    ]
    
    passed = 0
    failed = 0
    
    for test_case in test_cases:
        print(f"\n测试: {test_case['name']}")
        print(f"数据: {test_case['data'][:50]}...")
        
        try:
            response = requests.post(
                f"{base_url}/api/check",
                data=test_case['data'],
                headers={'Content-Type': 'application/json'},
                timeout=5
            )
            
            if response.status_code == test_case['expected_code']:
                print(f"   ✅ 状态码正确: {response.status_code}")
                
                if response.status_code == 200:
                    data = response.json()
                    if all(key in data for key in ["risk", "reason", "advice", "keywords"]):
                        print(f"   ✅ 响应格式正确")
                        passed += 1
                    else:
                        print(f"   ❌ 响应格式不正确")
                        failed += 1
                else:
                    data = response.json()
                    if data.get("risk") == "错误":
                        print(f"   ✅ 错误响应格式正确")
                        passed += 1
                    else:
                        print(f"   ❌ 错误响应格式不正确")
                        failed += 1
            else:
                print(f"   ❌ 状态码错误: 期望 {test_case['expected_code']}, 实际 {response.status_code}")
                print(f"      响应: {response.text}")
                failed += 1
                
        except Exception as e:
            print(f"   ❌ 请求异常: {e}")
            failed += 1
    
    # 输出总结
    print("\n" + "=" * 60)
    print("JSON处理测试总结")
    print("=" * 60)
    print(f"通过: {passed}")
    print(f"失败: {failed}")
    print(f"总计: {passed + failed}")
    
    success_rate = (passed / (passed + failed)) * 100
    print(f"成功率: {success_rate:.1f}%")
    
    if failed == 0:
        print("🎉 所有JSON处理测试通过！")
        return True
    else:
        print("⚠️  部分JSON处理测试失败")
        return False

if __name__ == "__main__":
    success = test_json_handling()
    exit(0 if success else 1)