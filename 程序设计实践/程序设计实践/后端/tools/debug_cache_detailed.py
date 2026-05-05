# debug_cache_detailed.py
import requests
import time
import json
import hashlib

def debug_cache_detailed():
    """详细调试缓存问题"""
    base_url = "http://localhost:5000"
    
    print("=== 详细缓存调试 ===\n")
    
    # 1. 清空缓存
    print("1. 清空缓存:")
    clear_response = requests.post(f"{base_url}/api/cache/clear")
    print(f"   结果: {clear_response.json()}")
    
    # 2. 检查初始缓存统计
    print("\n2. 初始缓存统计:")
    stats1 = requests.get(f"{base_url}/api/cache/stats").json()
    print(f"   统计: {json.dumps(stats1['cache_stats'], indent=6)}")
    
    # 3. 第一次请求
    test_text = "测试缓存功能的文本内容"
    print(f"\n3. 第一次请求:")
    print(f"   文本: '{test_text}'")
    
    # 手动计算缓存键，用于调试
    cache_key = hashlib.md5(test_text.encode('utf-8')).hexdigest()
    print(f"   预期缓存键: security_{cache_key}")
    
    start_time1 = time.time()
    response1 = requests.post(
        f"{base_url}/api/check",
        json={"text": test_text},
        timeout=10
    )
    time1 = time.time() - start_time1
    result1 = response1.json()
    print(f"   响应时间: {time1:.3f}s")
    print(f"   风险等级: {result1.get('risk', '未知')}")
    print(f"   状态码: {response1.status_code}")
    
    # 4. 检查第一次请求后的缓存统计
    print("\n4. 第一次请求后缓存统计:")
    stats2 = requests.get(f"{base_url}/api/cache/stats").json()
    print(f"   统计: {json.dumps(stats2['cache_stats'], indent=6)}")
    
    # 5. 第二次请求
    print(f"\n5. 第二次相同请求:")
    start_time2 = time.time()
    response2 = requests.post(
        f"{base_url}/api/check",
        json={"text": test_text},
        timeout=10
    )
    time2 = time.time() - start_time2
    result2 = response2.json()
    print(f"   响应时间: {time2:.3f}s")
    print(f"   风险等级: {result2.get('risk', '未知')}")
    print(f"   状态码: {response2.status_code}")
    
    # 6. 检查第二次请求后的缓存统计
    print("\n6. 第二次请求后缓存统计:")
    stats3 = requests.get(f"{base_url}/api/cache/stats").json()
    print(f"   统计: {json.dumps(stats3['cache_stats'], indent=6)}")
    
    # 7. 分析问题
    print("\n7. 问题分析:")
    hit_count_after = stats3['cache_stats']['hit_count']
    if hit_count_after == 0:
        print("   ❌ 缓存命中次数为0，缓存没有命中")
        print("   可能原因:")
        print("   - 缓存键生成不一致")
        print("   - 缓存设置失败")
        print("   - 缓存获取失败")
    else:
        print(f"   ✅ 缓存命中次数: {hit_count_after}")
        if time2 >= time1:
            print("   ⚠️  缓存命中了，但性能没有提升")
            print("   可能原因:")
            print("   - 缓存查找开销大")
            print("   - 网络波动")
            print("   - 服务器负载变化")
    
    # 8. 验证缓存内容
    print(f"\n8. 验证缓存内容:")
    # 再请求一次，观察日志中的缓存命中信息
    print("   第三次请求（观察服务器日志中的缓存命中信息）:")
    start_time3 = time.time()
    response3 = requests.post(
        f"{base_url}/api/check",
        json={"text": test_text},
        timeout=10
    )
    time3 = time.time() - start_time3
    print(f"   响应时间: {time3:.3f}s")
    
    final_stats = requests.get(f"{base_url}/api/cache/stats").json()
    print(f"   最终命中次数: {final_stats['cache_stats']['hit_count']}")

if __name__ == "__main__":
    debug_cache_detailed()