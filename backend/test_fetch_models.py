"""
测试fetch-models API端点
"""
import httpx
import asyncio


async def test_fetch_models():
    """测试获取模型列表"""
    url = "http://localhost:3000/api/ai-configs/actions/fetch-models"

    data = {
        "provider": "deepseek",
        "apiKey": "test-key",
        "baseUrl": "https://api.deepseek.com/v1"
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(url, json=data, timeout=10.0)
            print(f"状态码: {response.status_code}")
            print(f"响应: {response.text}")

            if response.status_code == 200:
                result = response.json()
                print(f"\n成功！获取到 {len(result.get('models', []))} 个模型:")
                for model in result.get('models', []):
                    print(f"  - {model['name']}: {model['description']}")
            else:
                print(f"\n失败: {response.text}")

        except Exception as e:
            print(f"请求失败: {e}")


if __name__ == "__main__":
    asyncio.run(test_fetch_models())
