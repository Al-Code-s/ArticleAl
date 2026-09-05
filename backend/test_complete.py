"""
完整功能测试脚本
测试所有已实现的后端 API 功能
"""
import asyncio
import json
from typing import Optional
import aiohttp


class APITester:
    def __init__(self, base_url: str = "http://localhost:3000"):
        self.base_url = base_url
        self.token: Optional[str] = None
        self.session: Optional[aiohttp.ClientSession] = None
        self.project_id: Optional[int] = None
        self.topic_id: Optional[int] = None
        self.outline_id: Optional[int] = None
        self.reference_id: Optional[int] = None
        self.document_id: Optional[int] = None

    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()

    def get_headers(self):
        headers = {"Content-Type": "application/json"}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        return headers

    async def test_register(self):
        """测试用户注册"""
        print("\n[1] Testing User Registration...")
        url = f"{self.base_url}/api/auth/register"
        data = {
            "username": "testuser_new",
            "email": "testuser_new@example.com",
            "password": "Test123456"
        }

        async with self.session.post(url, json=data, headers={"Content-Type": "application/json"}) as response:
            if response.status == 200:
                result = await response.json()
                print(f"✅ Registration successful: {result.get('username')}")
                return True
            else:
                text = await response.text()
                print(f"⚠️  Registration failed (may already exist): {response.status}")
                return False

    async def test_login(self):
        """测试用户登录"""
        print("\n[2] Testing User Login...")
        url = f"{self.base_url}/api/auth/login"
        data = {
            "username": "testuser_new",
            "password": "Test123456"
        }

        async with self.session.post(url, data=data) as response:
            if response.status == 200:
                result = await response.json()
                self.token = result.get("access_token")
                print(f"✅ Login successful, token received")
                return True
            else:
                text = await response.text()
                print(f"❌ Login failed: {response.status} - {text}")
                return False

    async def test_create_project(self):
        """测试创建项目"""
        print("\n[3] Testing Create Project...")
        url = f"{self.base_url}/api/projects"
        data = {
            "title": "AI测试项目",
            "major": "计算机科学",
            "education_level": "本科",
            "paper_type": "毕业论文",
            "description": "这是一个测试项目"
        }

        async with self.session.post(url, json=data, headers=self.get_headers()) as response:
            if response.status == 200:
                result = await response.json()
                self.project_id = result.get("id")
                print(f"✅ Project created: ID={self.project_id}, Title={result.get('title')}")
                return True
            else:
                text = await response.text()
                print(f"❌ Project creation failed: {response.status} - {text}")
                return False

    async def test_generate_topics(self):
        """测试生成选题"""
        print("\n[4] Testing Generate Topics (AI)...")
        url = f"{self.base_url}/api/topics/generate"
        data = {
            "project_id": self.project_id,
            "major": "计算机科学",
            "education_level": "本科",
            "paper_type": "毕业论文",
            "keywords": ["人工智能", "机器学习"],
            "count": 3
        }

        async with self.session.post(url, json=data, headers=self.get_headers()) as response:
            if response.status == 200:
                result = await response.json()
                if result and len(result) > 0:
                    self.topic_id = result[0].get("id")
                    print(f"✅ Generated {len(result)} topics")
                    for i, topic in enumerate(result, 1):
                        print(f"   Topic {i}: {topic.get('title')}")
                    return True
                else:
                    print("❌ No topics generated")
                    return False
            else:
                text = await response.text()
                print(f"❌ Topic generation failed: {response.status} - {text}")
                return False

    async def test_generate_outline(self):
        """测试生成大纲"""
        print("\n[5] Testing Generate Outline (AI)...")
        url = f"{self.base_url}/api/outlines/generate"
        data = {
            "project_id": self.project_id,
            "topic_title": "基于深度学习的图像识别研究",
            "requirements": "需要包含实验部分"
        }

        async with self.session.post(url, json=data, headers=self.get_headers()) as response:
            if response.status == 200:
                result = await response.json()
                self.outline_id = result.get("id")
                sections = result.get("content", {}).get("sections", [])
                print(f"✅ Outline generated: ID={self.outline_id}")
                print(f"   Sections count: {len(sections)}")
                if sections:
                    print(f"   First section: {sections[0].get('title')}")
                return True
            else:
                text = await response.text()
                print(f"❌ Outline generation failed: {response.status} - {text}")
                return False

    async def test_search_references(self):
        """测试搜索参考文献"""
        print("\n[6] Testing Search References (AI)...")
        url = f"{self.base_url}/api/references/search"
        data = {
            "keyword": "深度学习",
            "project_id": self.project_id,
            "max_results": 5,
            "save_to_project": True
        }

        async with self.session.post(url, json=data, headers=self.get_headers()) as response:
            if response.status == 200:
                result = await response.json()
                if result and len(result) > 0:
                    self.reference_id = result[0].get("id")
                    print(f"✅ Found {len(result)} references")
                    for i, ref in enumerate(result[:3], 1):
                        print(f"   Reference {i}: {ref.get('title')}")
                    return True
                else:
                    print("❌ No references found")
                    return False
            else:
                text = await response.text()
                print(f"❌ Reference search failed: {response.status} - {text}")
                return False

    async def test_generate_document(self):
        """测试生成文档"""
        print("\n[7] Testing Generate Document (AI)...")
        url = f"{self.base_url}/api/documents/generate"
        data = {
            "project_id": self.project_id,
            "document_type": "proposal",
            "requirements": "需要详细的研究方法说明"
        }

        async with self.session.post(url, json=data, headers=self.get_headers()) as response:
            if response.status == 200:
                result = await response.json()
                self.document_id = result.get("id")
                word_count = result.get("word_count", 0)
                print(f"✅ Document generated: ID={self.document_id}")
                print(f"   Title: {result.get('title')}")
                print(f"   Type: {result.get('type')}")
                print(f"   Word count: {word_count}")
                return True
            else:
                text = await response.text()
                print(f"❌ Document generation failed: {response.status} - {text}")
                return False

    async def test_list_apis(self):
        """测试列表查询 API"""
        print("\n[8] Testing List APIs...")

        # Test topics list
        url = f"{self.base_url}/api/topics?project_id={self.project_id}"
        async with self.session.get(url, headers=self.get_headers()) as response:
            if response.status == 200:
                result = await response.json()
                print(f"✅ Topics list: {result.get('total')} items")
            else:
                print(f"❌ Topics list failed: {response.status}")

        # Test outlines list
        url = f"{self.base_url}/api/outlines?project_id={self.project_id}"
        async with self.session.get(url, headers=self.get_headers()) as response:
            if response.status == 200:
                result = await response.json()
                print(f"✅ Outlines list: {result.get('total')} items")
            else:
                print(f"❌ Outlines list failed: {response.status}")

        # Test references list
        url = f"{self.base_url}/api/references?project_id={self.project_id}"
        async with self.session.get(url, headers=self.get_headers()) as response:
            if response.status == 200:
                result = await response.json()
                print(f"✅ References list: {result.get('total')} items")
            else:
                print(f"❌ References list failed: {response.status}")

        # Test documents list
        url = f"{self.base_url}/api/documents?project_id={self.project_id}"
        async with self.session.get(url, headers=self.get_headers()) as response:
            if response.status == 200:
                result = await response.json()
                print(f"✅ Documents list: {result.get('total')} items")
            else:
                print(f"❌ Documents list failed: {response.status}")

        return True

    async def test_websocket(self):
        """测试 WebSocket 连接"""
        print("\n[9] Testing WebSocket Connection...")
        try:
            ws_url = f"ws://localhost:3000/ws/chat?token={self.token}&project_id={self.project_id}"
            async with self.session.ws_connect(ws_url) as ws:
                print("✅ WebSocket connected")

                # Send a test message
                await ws.send_json({
                    "type": "chat",
                    "message": "你好，这是一个测试消息"
                })
                print("✅ Message sent")

                # Wait for response
                try:
                    msg = await asyncio.wait_for(ws.receive(), timeout=5.0)
                    if msg.type == aiohttp.WSMsgType.TEXT:
                        data = json.loads(msg.data)
                        print(f"✅ Received response: {data.get('type')}")
                    return True
                except asyncio.TimeoutError:
                    print("⚠️  No response received (timeout)")
                    return True
        except Exception as e:
            print(f"❌ WebSocket test failed: {str(e)}")
            return False

    async def test_export(self):
        """测试导出功能"""
        print("\n[10] Testing Export Functionality...")

        if not self.document_id:
            print("⚠️  Skipping export test (no document available)")
            return True

        # Test Word export
        url = f"{self.base_url}/api/export/document/{self.document_id}?format=word"
        async with self.session.post(url, headers=self.get_headers()) as response:
            if response.status == 200:
                content_length = response.content_length or len(await response.read())
                print(f"✅ Word export successful ({content_length} bytes)")
            else:
                print(f"❌ Word export failed: {response.status}")

        # Test PDF export
        url = f"{self.base_url}/api/export/document/{self.document_id}?format=pdf"
        async with self.session.post(url, headers=self.get_headers()) as response:
            if response.status == 200:
                content_length = response.content_length or len(await response.read())
                print(f"✅ PDF export successful ({content_length} bytes)")
            else:
                print(f"❌ PDF export failed: {response.status}")

        return True

    async def run_all_tests(self):
        """运行所有测试"""
        print("=" * 60)
        print("ArticleAI Backend API Test Suite")
        print("=" * 60)

        # Test authentication
        await self.test_register()
        if not await self.test_login():
            print("\n❌ Cannot proceed without authentication")
            return

        # Test core features
        if not await self.test_create_project():
            print("\n❌ Cannot proceed without project")
            return

        # Test AI generation features
        await self.test_generate_topics()
        await self.test_generate_outline()
        await self.test_search_references()
        await self.test_generate_document()

        # Test list APIs
        await self.test_list_apis()

        # Test WebSocket
        await self.test_websocket()

        # Test export
        await self.test_export()

        print("\n" + "=" * 60)
        print("Test Suite Completed!")
        print("=" * 60)


async def main():
    async with APITester() as tester:
        await tester.run_all_tests()


if __name__ == "__main__":
    asyncio.run(main())
