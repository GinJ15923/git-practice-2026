import time
import hashlib
from typing import Dict, Any, Optional
import logging
import threading

logger = logging.getLogger(__name__)

class OptimizedCache:
    """优化的内存缓存管理器"""
    
    def __init__(self):
        self._cache: Dict[str, Dict[str, Any]] = {}
        self.default_ttl = 300  # 默认缓存5分钟
        self.hit_count = 0
        self.miss_count = 0
        self._lock = threading.RLock()  # 线程安全锁
        
        # 性能统计
        self.lookup_times = []
        self.set_times = []
    
    def _generate_key(self, text: str) -> str:
        """为文本生成缓存键 - 优化版本"""
        # 使用更快的哈希算法和更短的键
        return f"sec_{hashlib.md5(text.encode('utf-8')).hexdigest()[:12]}"
    
    def get(self, text: str) -> Optional[Dict[str, Any]]:
        """从缓存中获取结果 - 优化版本"""
        if not text or not isinstance(text, str):
            return None
            
        start_time = time.time()
        cache_key = self._generate_key(text)
        
        with self._lock:
            if cache_key in self._cache:
                cache_item = self._cache[cache_key]
                
                # 检查是否过期
                if time.time() < cache_item['expires_at']:
                    self.hit_count += 1
                    lookup_time = time.time() - start_time
                    self.lookup_times.append(lookup_time)
                    
                    if len(self.lookup_times) > 100:  # 只保留最近100次
                        self.lookup_times.pop(0)
                    
                    logger.debug(f"✅ 缓存命中: 查找时间 {lookup_time:.6f}s")
                    return cache_item['data']
                else:
                    # 删除过期缓存
                    del self._cache[cache_key]
                    self.miss_count += 1
            else:
                self.miss_count += 1
        
        return None
    
    def set(self, text: str, data: Dict[str, Any], ttl: Optional[int] = None) -> None:
        """设置缓存 - 优化版本"""
        if not text or not isinstance(text, str):
            return
            
        start_time = time.time()
        cache_key = self._generate_key(text)
        ttl = ttl or self.default_ttl
        
        # 只缓存必要字段，避免深拷贝
        cached_data = {
            'risk': data.get('risk'),
            'reason': data.get('reason'),
            'advice': data.get('advice'),
            'keywords': data.get('keywords', [])
        }
        
        with self._lock:
            self._cache[cache_key] = {
                'data': cached_data,
                'expires_at': time.time() + ttl,
                'created_at': time.time()
            }
        
        set_time = time.time() - start_time
        self.set_times.append(set_time)
        
        if len(self.set_times) > 100:
            self.set_times.pop(0)
        
        logger.debug(f"📝 设置缓存: 耗时 {set_time:.6f}s")
    
    def clear(self) -> None:
        """清空所有缓存"""
        with self._lock:
            count = len(self._cache)
            self._cache.clear()
            self.hit_count = 0
            self.miss_count = 0
            self.lookup_times.clear()
            self.set_times.clear()
            logger.info(f"清空了所有缓存，共 {count} 项")
    
    def get_stats(self) -> Dict[str, Any]:
        """获取缓存统计信息"""
        with self._lock:
            current_time = time.time()
            valid_count = 0
            
            for item in self._cache.values():
                if current_time < item['expires_at']:
                    valid_count += 1
            
            total_requests = self.hit_count + self.miss_count
            hit_rate = (self.hit_count / total_requests * 100) if total_requests > 0 else 0
            
            # 性能统计
            avg_lookup_time = sum(self.lookup_times) / len(self.lookup_times) if self.lookup_times else 0
            avg_set_time = sum(self.set_times) / len(self.set_times) if self.set_times else 0
            
            return {
                'total_items': len(self._cache),
                'valid_items': valid_count,
                'hit_count': self.hit_count,
                'miss_count': self.miss_count,
                'hit_rate': f"{hit_rate:.1f}%",
                'avg_lookup_time_ms': f"{avg_lookup_time * 1000:.3f}",
                'avg_set_time_ms': f"{avg_set_time * 1000:.3f}",
                'memory_usage': f"{sum(len(str(k)) + len(str(v)) for k, v in self._cache.items())} bytes"
            }

# 创建全局优化缓存实例
optimized_cache = OptimizedCache()