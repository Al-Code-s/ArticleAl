"""
API 测试脚本

测试所有后端 API 端点
"""
import requests
import json

BASE_URL = "http://localhost:3000/api"

# 存储测试数据
test_data = {
    "token": None,
    "user_id": None,
    "project_id": None,
    "topic_id": None,
    "outline_id": None,
    "reference_id": None,
    "document_id": None,
}


def print_test(name, response):
    """打印测试结果"""
    status = "OK" if response.status_code < 400 else "FAIL"
    print(f"{status} {name}: {response.status_code}")
    if response.status_code >= 400:
        print(f"  Error: {response.text[:200]}")
    return response


def test_auth():
    """测试认证 API"""
    print("\n=== 测试认证 API ===")

    # 1. 注册
    register_data = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "password123"
    }
    response = print_test(
        "POST /auth/register",
        requests.post(f"{BASE_URL}/auth/register", json=register_data)
    )

    # 2. 登录
    login_data = {
        "username": "testuser",
        "password": "password123"
    }
    response = print_test(
        "POST /auth/login",
        requests.post(f"{BASE_URL}/auth/login", json=login_data)
    )

    if response.status_code == 200:
        data = response.json()
        test_data["token"] = data["access_token"]
        test_data["user_id"] = data["user"]["id"]
        print(f"  Token: {test_data['token'][:20]}...")

    # 3. 获取用户信息
    headers = {"Authorization": f"Bearer {test_data['token']}"}
    print_test(
        "GET /auth/me",
        requests.get(f"{BASE_URL}/auth/me", headers=headers)
    )


def test_projects():
    """测试项目 API"""
    print("\n=== 测试项目 API ===")
    headers = {"Authorization": f"Bearer {test_data['token']}"}

    # 1. 创建项目
    project_data = {
        "title": "基于AI的论文写作系统研究",
        "major": "计算机科学",
        "education_level": "本科",
        "paper_type": "毕业论文",
        "description": "这是一个测试项目"
    }
    response = print_test(
        "POST /projects",
        requests.post(f"{BASE_URL}/projects", json=project_data, headers=headers)
    )
    if response.status_code == 200:
        test_data["project_id"] = response.json()["id"]

    # 2. 获取项目列表
    print_test(
        "GET /projects",
        requests.get(f"{BASE_URL}/projects", headers=headers)
    )

    # 3. 获取项目详情
    if test_data["project_id"]:
        print_test(
            f"GET /projects/{test_data['project_id']}",
            requests.get(f"{BASE_URL}/projects/{test_data['project_id']}", headers=headers)
        )


def test_topics():
    """测试选题 API"""
    print("\n=== 测试选题 API ===")
    headers = {"Authorization": f"Bearer {test_data['token']}"}

    # 1. 生成选题
    generate_data = {
        "project_id": test_data["project_id"],
        "major": "计算机科学",
        "education_level": "本科",
        "paper_type": "毕业论文",
        "keywords": ["人工智能", "深度学习"]
    }
    response = print_test(
        "POST /topics/generate",
        requests.post(f"{BASE_URL}/topics/generate", json=generate_data, headers=headers)
    )
    if response.status_code == 200:
        topics = response.json()
        if topics:
            test_data["topic_id"] = topics[0]["id"]
            print(f"  Generated {len(topics)} topics")

    # 2. 获取选题列表
    print_test(
        "GET /topics",
        requests.get(f"{BASE_URL}/topics?project_id={test_data['project_id']}", headers=headers)
    )

    # 3. 选择选题
    if test_data["topic_id"]:
        print_test(
            f"POST /topics/{test_data['topic_id']}/select",
            requests.post(f"{BASE_URL}/topics/{test_data['topic_id']}/select", headers=headers)
        )


def test_outlines():
    """测试大纲 API"""
    print("\n=== 测试大纲 API ===")
    headers = {"Authorization": f"Bearer {test_data['token']}"}

    # 1. 生成大纲
    generate_data = {
        "project_id": test_data["project_id"],
        "topic_title": "基于深度学习的图像识别研究",
        "requirements": "需要包含实验部分"
    }
    response = print_test(
        "POST /outlines/generate",
        requests.post(f"{BASE_URL}/outlines/generate", json=generate_data, headers=headers)
    )
    if response.status_code == 200:
        test_data["outline_id"] = response.json()["id"]

    # 2. 获取大纲列表
    print_test(
        "GET /outlines",
        requests.get(f"{BASE_URL}/outlines?project_id={test_data['project_id']}", headers=headers)
    )


def test_references():
    """测试参考文献 API"""
    print("\n=== 测试参考文献 API ===")
    headers = {"Authorization": f"Bearer {test_data['token']}"}

    # 1. 搜索文献
    search_data = {
        "keyword": "深度学习",
        "project_id": test_data["project_id"],
        "max_results": 5
    }
    response = print_test(
        "POST /references/search",
        requests.post(f"{BASE_URL}/references/search", json=search_data, headers=headers)
    )
    if response.status_code == 200:
        references = response.json()
        if references:
            test_data["reference_id"] = references[0]["id"]
            print(f"  Found {len(references)} references")

    # 2. 获取文献列表
    print_test(
        "GET /references",
        requests.get(f"{BASE_URL}/references?project_id={test_data['project_id']}", headers=headers)
    )


def test_documents():
    """测试文档 API"""
    print("\n=== 测试文档 API ===")
    headers = {"Authorization": f"Bearer {test_data['token']}"}

    # 1. 生成文档
    generate_data = {
        "project_id": test_data["project_id"],
        "document_type": "proposal",
        "requirements": "需要包含研究方法"
    }
    response = print_test(
        "POST /documents/generate",
        requests.post(f"{BASE_URL}/documents/generate", json=generate_data, headers=headers)
    )
    if response.status_code == 200:
        test_data["document_id"] = response.json()["id"]

    # 2. 获取文档列表
    print_test(
        "GET /documents",
        requests.get(f"{BASE_URL}/documents?project_id={test_data['project_id']}", headers=headers)
    )

    # 3. 获取文档详情
    if test_data["document_id"]:
        response = print_test(
            f"GET /documents/{test_data['document_id']}",
            requests.get(f"{BASE_URL}/documents/{test_data['document_id']}", headers=headers)
        )
        if response.status_code == 200:
            doc = response.json()
            print(f"  Word count: {doc['word_count']}")


def main():
    """运行所有测试"""
    print("="*50)
    print("ArticleAI API 测试")
    print("="*50)

    try:
        test_auth()
        test_projects()
        test_topics()
        test_outlines()
        test_references()
        test_documents()

        print("\n" + "="*50)
        print("测试完成！")
        print("="*50)
        print("\n测试数据:")
        print(json.dumps(test_data, indent=2))

    except Exception as e:
        print(f"\n测试失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
