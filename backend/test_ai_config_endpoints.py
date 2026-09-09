"""
测试 AI 配置端点
"""
import httpx
import asyncio


async def test_endpoints():
    """测试所有 AI 配置相关端点"""
    base_url = "http://localhost:3000/api"

    print("=" * 60)
    print("测试 AI 配置端点")
    print("=" * 60)

    async with httpx.AsyncClient() as client:
        # 1. 测试获取供应商列表
        print("\n1. 测试 GET /ai-configs/providers")
        try:
            response = await client.get(f"{base_url}/ai-configs/providers")
            print(f"   状态码: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ 成功获取 {len(data.get('providers', []))} 个供应商")
                for provider in data.get('providers', [])[:3]:
                    print(f"      - {provider['display_name']}: {provider['model_count']} 个模型")
            else:
                print(f"   ❌ 失败: {response.text}")
        except Exception as e:
            print(f"   ❌ 异常: {e}")

        # 2. 测试获取 Anthropic 模型列表
        print("\n2. 测试 POST /ai-configs/actions/fetch-models (Anthropic)")
        try:
            response = await client.post(
                f"{base_url}/ai-configs/actions/fetch-models",
                json={
                    "provider": "anthropic",
                    "apiKey": "test-key-for-registry"
                }
            )
            print(f"   状态码: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ 成功获取 {len(data.get('models', []))} 个模型")
                for model in data.get('models', [])[:3]:
                    print(f"      - {model['name']}: {model['description']}")
            else:
                print(f"   ❌ 失败: {response.text}")
        except Exception as e:
            print(f"   ❌ 异常: {e}")

        # 3. 测试获取 OpenAI 模型列表
        print("\n3. 测试 POST /ai-configs/actions/fetch-models (OpenAI)")
        try:
            response = await client.post(
                f"{base_url}/ai-configs/actions/fetch-models",
                json={
                    "provider": "openai",
                    "apiKey": "test-key-for-registry"
                }
            )
            print(f"   状态码: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ 成功获取 {len(data.get('models', []))} 个模型")
                for model in data.get('models', [])[:3]:
                    print(f"      - {model['name']}: {model['description']}")
            else:
                print(f"   ❌ 失败: {response.text}")
        except Exception as e:
            print(f"   ❌ 异常: {e}")

        # 4. 测试获取通义千问模型列表
        print("\n4. 测试 POST /ai-configs/actions/fetch-models (通义千问)")
        try:
            response = await client.post(
                f"{base_url}/ai-configs/actions/fetch-models",
                json={
                    "provider": "qwen",
                    "apiKey": "test-key-for-registry"
                }
            )
            print(f"   状态码: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ 成功获取 {len(data.get('models', []))} 个模型")
                for model in data.get('models', []):
                    print(f"      - {model['name']}: {model['description']}")
            else:
                print(f"   ❌ 失败: {response.text}")
        except Exception as e:
            print(f"   ❌ 异常: {e}")

        # 5. 测试所有预定义供应商
        print("\n5. 测试所有预定义供应商")
        providers = ["anthropic", "openai", "deepseek", "qwen", "chatglm", "moonshot"]
        for provider in providers:
            try:
                response = await client.post(
                    f"{base_url}/ai-configs/actions/fetch-models",
                    json={
                        "provider": provider,
                        "apiKey": "test-key"
                    }
                )
                if response.status_code == 200:
                    data = response.json()
                    print(f"   ✅ {provider}: {len(data.get('models', []))} 个模型")
                else:
                    print(f"   ❌ {provider}: 失败 ({response.status_code})")
            except Exception as e:
                print(f"   ❌ {provider}: 异常 - {e}")

    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(test_endpoints())
