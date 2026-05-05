"""API模块包初始化文件"""

# 使用Python代码添加项目根目录到搜索路径
import sys
import os
# 获取当前文件的父目录（即项目根目录）
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# 将项目根目录添加到Python搜索路径
if project_root not in sys.path:
    sys.path.append(project_root)

# 包级别的版本信息
__version__ = "1.0.0"
__author__ = "网络安全检测团队"

# 由于路由现在已直接集成在app.py中，不再需要导入register_routes

# 定义包的公共接口
__all__ = []

# 包初始化时可以执行的代码
import logging

# 配置包级别的日志记录器
logger = logging.getLogger(__name__)
try:
    logger.info("API模块已初始化")
except Exception:
    # 如果日志记录器未配置，跳过日志记录
    pass