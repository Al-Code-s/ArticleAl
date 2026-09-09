"""
测试路由注册情况
"""
import sys
sys.path.insert(0, '.')

from app.api import api_router

print("\n========== API Router 路由检查 ==========")
print(f"总路由数: {len(api_router.routes)}\n")

for route in api_router.routes:
    if hasattr(route, 'path'):
        methods = getattr(route, 'methods', 'N/A')
        path = route.path
        name = getattr(route, 'name', 'N/A')

        if 'ai-config' in path.lower():
            print(f"[OK] {methods} {path}")
            print(f"  函数名: {name}")
            print()

print("==========================================\n")

# 专门检查 fetch-models
print("========== 检查 fetch-models 路由 ==========")
from app.api.ai_configs import router as ai_config_router

print(f"ai_configs router 总路由数: {len(ai_config_router.routes)}\n")

for route in ai_config_router.routes:
    if hasattr(route, 'path'):
        methods = getattr(route, 'methods', set())
        path = route.path
        name = getattr(route, 'name', 'N/A')
        print(f"{methods} {path} -> {name}")

print("==========================================\n")
