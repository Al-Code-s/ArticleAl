"""选题生成的本地兜底测试。"""

import re

import pytest

from app.services.ai_service import AIService


@pytest.mark.parametrize(
    "paper_type",
    [
        "论述性论文",
        "研究性论文",
        "实证研究论文",
        "调查研究论文",
        "案例研究论文",
        "设计实践论文",
    ],
)
def test_education_fallback_returns_natural_unique_topics(paper_type):
    service = AIService()

    topics = service._generate_mock_topics("教育学", "本科", paper_type, 10)
    titles = [topic["title"] for topic in topics]

    assert len(topics) == 10
    assert len(set(titles)) == 10
    assert all("号研究课题" not in title for title in titles)
    assert all("毕业论文选题" not in title for title in titles)
    assert len({re.split(r"[：与的视面中]", title, maxsplit=1)[0] for title in titles}) > 1


def test_fallback_supports_backend_maximum_topic_count():
    service = AIService()

    topics = service._generate_mock_topics("教育学", "专科", "研究性论文", 20)

    assert len(topics) == 20
    assert len({topic["title"] for topic in topics}) == 20


@pytest.mark.asyncio
async def test_generate_topics_without_ai_uses_contentful_fallback():
    service = AIService()
    service.anthropic_client = None
    service.openai_client = None

    topics = await service.generate_topics(
        major="教育学",
        education_level="本科",
        paper_type="研究性论文",
        count=5,
    )

    assert len(topics) == 5
    assert all(topic["title"] for topic in topics)
    assert all("号研究课题" not in topic["title"] for topic in topics)


def test_chinese_literature_fallback_matches_major_and_paper_type():
    service = AIService()

    topics = service._generate_mock_topics("汉语言文学", "专科", "论述性论文", 5)
    titles = [topic["title"] for topic in topics]

    assert len(topics) == 5
    assert any(
        keyword in " ".join(titles)
        for keyword in ("《", "诗", "小说", "文学", "语言", "作家", "散文")
    )
    assert all(
        keyword not in " ".join(titles)
        for keyword in ("客户服务", "服务质量", "岗位能力", "工作流程", "企业管理")
    )
    assert all(topic["keywords"][0] == "汉语言文学" for topic in topics)


def test_chinese_literature_ai_result_filters_cross_discipline_titles():
    service = AIService()

    assert service._is_topic_relevant("汉语言文学", "《红楼梦》中林黛玉形象的悲剧意蕴")
    assert not service._is_topic_relevant("汉语言文学", "汉语言文学专业实践中的服务质量评价边界")


@pytest.mark.parametrize(
    ("major", "expected_signal"),
    [
        ("计算机科学与技术", "系统"),
        ("工商管理", "企业"),
        ("法学", "合同"),
        ("临床医学", "患者"),
        ("农学", "农业"),
        ("艺术设计", "设计"),
        ("英语", "英语"),
    ],
)
def test_fallback_topics_follow_major_domain(major, expected_signal):
    service = AIService()

    topics = service._generate_mock_topics(major, "专科", "论述性论文", 5)
    titles = " ".join(topic["title"] for topic in topics)

    assert len(topics) == 5
    assert expected_signal in titles
    assert "客户服务" not in titles
    assert "服务质量评价边界" not in titles
    assert "岗位能力" not in titles
