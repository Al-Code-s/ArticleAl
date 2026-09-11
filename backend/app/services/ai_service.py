"""
AI 服务

提供 AI 模型调用的统一接口
"""
from typing import Optional, List, Dict, Any
from anthropic import AsyncAnthropic
from openai import AsyncOpenAI

from app.core.config import settings
from app.skills import get_skill
from app.services.ai_runtime import ActiveAIConfig, build_anthropic_client, build_openai_client


class AIService:
    """AI 服务类"""

    def __init__(self):
        """初始化 AI 客户端"""
        self.anthropic_client = None
        self.openai_client = None

        # 初始化 Claude
        if settings.ANTHROPIC_API_KEY:
            self.anthropic_client = AsyncAnthropic(
                api_key=settings.ANTHROPIC_API_KEY
            )

        # 初始化 OpenAI
        if settings.OPENAI_API_KEY:
            self.openai_client = AsyncOpenAI(
                api_key=settings.OPENAI_API_KEY
            )

    @staticmethod
    def _major_category(major: str) -> str:
        """将专业归入研究对象相近的学科类别。"""
        major_text = (major or "").strip().replace(" ", "")
        category_rules = [
            ("chinese_literature", ("汉语言文学", "中国语言文学", "汉语言", "中文")),
            ("computer", ("计算机", "软件工程", "人工智能", "大数据", "网络工程", "信息安全", "物联网", "数字媒体技术")),
            ("medicine", ("临床医学", "护理学", "药学", "中医学", "口腔医学", "动物医学")),
            ("agriculture", ("农学", "园艺", "林学", "生物科学", "生物工程")),
            ("environment_geography", ("环境工程", "地理科学")),
            ("chemistry_material", ("化学工程", "材料科学", "化学")),
            ("engineering", ("电子信息", "通信工程", "自动化", "电气工程", "机械工程", "土木工程", "建筑学")),
            ("business", ("工商管理", "市场营销", "财务管理", "会计学", "人力资源管理")),
            ("finance_economics", ("金融学", "国际经济与贸易", "经济学")),
            ("law", ("法学",)),
            ("education", ("教育学", "学前教育", "小学教育")),
            ("sports", ("体育教育",)),
            ("psychology_social", ("心理学", "社会学")),
            ("journalism_ad", ("新闻学", "广告学")),
            ("language", ("英语",)),
            ("history_philosophy", ("历史学", "哲学")),
            ("math_physics", ("数学", "物理学")),
            ("tourism", ("旅游管理", "酒店管理")),
            ("public_admin", ("公共事业管理", "行政管理")),
            ("art", ("艺术设计", "音乐学", "美术学", "舞蹈学")),
        ]
        for category, names in category_rules:
            if any(name in major_text for name in names):
                return category
        return "general"

    @staticmethod
    def _major_profile_data(category: str) -> Dict[str, Any]:
        """提供各学科的研究对象、问题和标题相关词，供提示词与兜底共用。"""
        profiles = {
            "chinese_literature": {
                "label": "汉语言文学",
                "focus": "中国古代文学、中国现当代文学、语言学与应用汉语、文艺理论、作家作品、文本表达、文学思潮和语文教育",
                "signals": ("文学", "诗", "词", "小说", "散文", "作家", "作品", "文本", "语言", "叙事", "意象", "人物", "审美", "成语", "方言", "阅读", "语文", "《"),
                "objects": ("古代诗歌", "古典小说", "现当代文学作品", "现代汉语", "网络文学", "语文阅读"),
                "issues": ("主题表达", "人物塑造", "叙事视角", "语言风格", "文化意蕴", "审美体验"),
                "keywords": ("文学文本", "语言表达", "作品分析"),
            },
            "computer": {
                "label": "计算机与信息技术",
                "focus": "软件开发、算法模型、数据治理、网络安全、信息系统、人工智能和人机交互",
                "signals": ("计算机", "软件", "算法", "数据", "网络", "系统", "人工智能", "模型", "程序", "信息"),
                "objects": ("软件系统开发", "机器学习模型应用", "网络安全防护", "数据治理", "人机交互设计", "智能推荐系统"),
                "issues": ("可靠性保障", "隐私保护", "算法偏差", "数据质量", "交互体验", "应用效果"),
                "keywords": ("技术应用", "系统分析", "数据处理"),
            },
            "engineering": {
                "label": "工程技术",
                "focus": "工程项目、设备系统、施工过程、自动化控制、能源利用和工程质量安全",
                "signals": ("工程", "建筑", "施工", "机械", "设备", "电气", "通信", "自动化", "结构", "材料"),
                "objects": ("工程项目施工", "机械设备运行", "建筑结构设计", "自动化控制系统", "电气设备维护", "工程材料应用"),
                "issues": ("质量控制", "安全风险", "运行效率", "成本管理", "节能效果", "技术优化"),
                "keywords": ("工程实践", "技术应用", "质量控制"),
            },
            "business": {
                "label": "工商管理与会计",
                "focus": "企业经营、市场营销、财务管理、人力资源、组织管理、会计信息和消费者行为",
                "signals": ("企业", "市场", "营销", "财务", "会计", "组织", "员工", "消费者", "管理", "经营"),
                "objects": ("中小企业经营", "品牌营销活动", "企业财务管理", "员工激励机制", "消费者购买行为", "会计信息披露"),
                "issues": ("数字化转型", "品牌认同", "内部控制", "工作投入", "消费决策", "信息透明度"),
                "keywords": ("企业管理", "经营实践", "管理机制"),
            },
            "finance_economics": {
                "label": "经济与金融",
                "focus": "金融市场、企业融资、产业发展、贸易活动、消费行为和宏观经济现象",
                "signals": ("金融", "经济", "融资", "投资", "市场", "贸易", "产业", "消费", "企业"),
                "objects": ("中小企业融资", "居民消费行为", "金融科技应用", "区域产业发展", "跨境贸易活动", "资本市场波动"),
                "issues": ("风险识别", "影响因素", "发展差异", "政策响应", "资源配置", "市场预期"),
                "keywords": ("经济现象", "金融市场", "影响因素"),
            },
            "law": {
                "label": "法学",
                "focus": "民商事法律关系、合同治理、劳动关系、知识产权、行政法治和司法实践",
                "signals": ("法律", "法治", "合同", "司法", "诉讼", "权利", "责任", "行政", "知识产权", "劳动"),
                "objects": ("网络交易合同", "劳动争议案件", "个人信息保护", "知识产权侵权", "行政裁量行为", "未成年人权益"),
                "issues": ("责任认定", "权利保护", "法律适用", "争议解决", "制度完善", "司法裁判"),
                "keywords": ("法律适用", "权利保护", "制度分析"),
            },
            "education": {
                "label": "教育学",
                "focus": "课程、课堂、教师、学生、家校协同、教育政策、学习活动和学校实践",
                "signals": ("教育", "课程", "课堂", "教师", "学生", "学习", "学校", "教学", "家校", "儿童"),
                "objects": ("课堂提问活动", "教师反馈行为", "学生阅读学习", "家校沟通实践", "学校数字化资源", "幼儿游戏活动"),
                "issues": ("学习参与", "专业发展", "阅读体验", "责任边界", "资源使用", "同伴支持"),
                "keywords": ("教育实践", "学习活动", "教学研究"),
            },
            "psychology_social": {
                "label": "心理学与社会学",
                "focus": "个体心理、社会关系、群体行为、社会结构、身份认同和公共生活",
                "signals": ("心理", "社会", "个体", "群体", "情绪", "认同", "行为", "关系", "社区", "家庭"),
                "objects": ("大学生心理适应", "网络社交行为", "家庭关系互动", "社区志愿服务", "青年身份认同", "老年人社会参与"),
                "issues": ("影响因素", "情绪体验", "关系机制", "参与意愿", "认同建构", "支持需求"),
                "keywords": ("社会现象", "心理体验", "群体行为"),
            },
            "journalism_ad": {
                "label": "新闻传播与广告",
                "focus": "新闻生产、媒介传播、短视频内容、广告文本、受众接受和舆论表达",
                "signals": ("新闻", "传播", "媒介", "广告", "短视频", "舆论", "受众", "媒体", "内容"),
                "objects": ("短视频新闻", "公益广告文本", "地方媒体报道", "社交媒体传播", "品牌广告叙事", "网络舆论事件"),
                "issues": ("叙事方式", "传播效果", "受众接受", "媒介伦理", "情感表达", "议题建构"),
                "keywords": ("媒介文本", "传播效果", "受众研究"),
            },
            "language": {
                "label": "外国语言文学",
                "focus": "英语语言、外国文学、翻译实践、跨文化交际和语言教学",
                "signals": ("英语", "语言", "文学", "翻译", "跨文化", "词汇", "语法", "小说", "教学"),
                "objects": ("英语文学作品", "英语新闻文本", "商务英语表达", "中英翻译文本", "跨文化交际场景", "英语课堂活动"),
                "issues": ("语言风格", "翻译策略", "文化差异", "词汇使用", "表达效果", "学习体验"),
                "keywords": ("语言分析", "文本翻译", "跨文化交际"),
            },
            "medicine": {
                "label": "医学、护理与药学",
                "focus": "临床诊疗、护理服务、药物使用、疾病预防、患者健康和医学伦理",
                "signals": ("医学", "护理", "药物", "疾病", "患者", "临床", "健康", "治疗", "医院", "医护"),
                "objects": ("慢性病患者健康管理", "老年患者护理", "临床用药安全", "医院感染防控", "健康教育干预", "医患沟通实践"),
                "issues": ("依从性", "护理需求", "用药风险", "防控效果", "健康素养", "伦理边界"),
                "keywords": ("临床实践", "健康管理", "医学伦理"),
            },
            "agriculture": {
                "label": "生物与农林",
                "focus": "作物种植、园艺生产、动物养殖、生态保护、生物技术和农业经营",
                "signals": ("农业", "农学", "园艺", "生物", "作物", "植物", "动物", "养殖", "林业", "生态"),
                "objects": ("设施农业生产", "果蔬种植管理", "乡村生态治理", "动物养殖过程", "农业生物技术", "农产品供应"),
                "issues": ("产量品质", "病虫害防治", "资源利用", "生态效益", "技术推广", "经营效率"),
                "keywords": ("农业生产", "生态实践", "技术推广"),
            },
            "environment_geography": {
                "label": "环境与地理",
                "focus": "生态环境、资源利用、地理空间、区域发展、污染治理和可持续发展",
                "signals": ("环境", "生态", "地理", "资源", "污染", "区域", "空间", "气候", "治理", "可持续"),
                "objects": ("城市生态环境", "水资源利用", "区域空间发展", "生活垃圾治理", "乡村生态建设", "空气污染防治"),
                "issues": ("治理效果", "空间差异", "资源配置", "影响因素", "公众参与", "可持续路径"),
                "keywords": ("生态环境", "区域发展", "资源治理"),
            },
            "chemistry_material": {
                "label": "化学与材料",
                "focus": "化学反应、材料性能、实验过程、能源材料、检测分析和工业应用",
                "signals": ("化学", "材料", "反应", "实验", "性能", "能源", "检测", "合成", "催化"),
                "objects": ("功能材料制备", "化学实验教学", "新能源材料", "环境样品检测", "高分子材料应用", "催化反应过程"),
                "issues": ("性能表征", "实验安全", "检测方法", "制备工艺", "应用潜力", "反应效率"),
                "keywords": ("材料性能", "实验分析", "技术应用"),
            },
            "math_physics": {
                "label": "数学与物理",
                "focus": "数学模型、统计方法、物理现象、实验验证、数据分析和科学教育",
                "signals": ("数学", "物理", "模型", "统计", "实验", "数据", "方程", "算法", "测量"),
                "objects": ("数学建模教学", "统计方法应用", "物理实验活动", "复杂系统模型", "数据可视化分析", "科学探究课堂"),
                "issues": ("模型构建", "方法比较", "实验误差", "学习困难", "数据特征", "解释能力"),
                "keywords": ("数学模型", "实验分析", "数据方法"),
            },
            "history_philosophy": {
                "label": "历史与哲学",
                "focus": "历史文献、思想史、社会变迁、哲学思想、文化记忆和价值观念",
                "signals": ("历史", "哲学", "思想", "文献", "文化", "社会变迁", "记忆", "价值", "史料"),
                "objects": ("地方历史文献", "中国传统思想", "近现代社会变迁", "历史人物思想", "文化遗产记忆", "伦理思想文本"),
                "issues": ("思想内涵", "历史影响", "文化认同", "价值取向", "文献解读", "传播方式"),
                "keywords": ("历史文献", "思想分析", "文化记忆"),
            },
            "tourism": {
                "label": "旅游与酒店管理",
                "focus": "旅游目的地、文旅消费、酒店运营、游客体验、旅游资源和服务管理",
                "signals": ("旅游", "酒店", "游客", "景区", "文旅", "住宿", "目的地", "旅行"),
                "objects": ("乡村旅游目的地", "酒店数字化运营", "地方文化旅游", "游客出行体验", "旅游品牌传播", "景区公共服务"),
                "issues": ("体验评价", "运营效率", "文化传播", "品牌认同", "可持续发展", "满意度"),
                "keywords": ("旅游实践", "游客体验", "运营管理"),
            },
            "public_admin": {
                "label": "公共管理",
                "focus": "公共政策、政府治理、社区服务、公共组织、基层治理和公共资源配置",
                "signals": ("公共", "行政", "政府", "政策", "社区", "治理", "基层", "公共服务", "组织"),
                "objects": ("基层社区治理", "公共政策执行", "政务服务平台", "公共资源配置", "社会组织参与", "应急管理实践"),
                "issues": ("执行效果", "协同机制", "公众参与", "服务可及性", "责任边界", "治理能力"),
                "keywords": ("公共治理", "政策执行", "社会参与"),
            },
            "art": {
                "label": "艺术与设计",
                "focus": "视觉设计、艺术作品、音乐表演、舞蹈创作、审美表达和文化传播",
                "signals": ("艺术", "设计", "音乐", "美术", "舞蹈", "视觉", "创作", "审美", "作品"),
                "objects": ("视觉传达设计", "地方艺术作品", "音乐表演实践", "舞蹈编创活动", "公共空间设计", "传统文化视觉表达"),
                "issues": ("形式语言", "审美特征", "创作方法", "文化表达", "受众体验", "设计功能"),
                "keywords": ("艺术表达", "设计实践", "审美分析"),
            },
            "sports": {
                "label": "体育教育",
                "focus": "体育教学、运动训练、身体素质、校园体育、运动参与和健康促进",
                "signals": ("体育", "运动", "训练", "健身", "身体", "校园", "教学", "健康"),
                "objects": ("校园体育活动", "青少年运动训练", "体育课堂教学", "大众健身参与", "学生体质健康", "运动损伤预防"),
                "issues": ("参与动机", "训练效果", "教学方法", "健康促进", "运动风险", "体质差异"),
                "keywords": ("体育实践", "运动参与", "健康促进"),
            },
            "general": {
                "label": "专业实践",
                "focus": "根据专业名称识别其具体工作对象、核心任务、行业问题和知识应用场景",
                "signals": (),
                "objects": ("专业实践场景", "专业课程学习", "行业应用任务", "岗位实践过程", "专业技术应用", "服务对象需求"),
                "issues": ("实践困境", "应用效果", "能力培养", "方法优化", "需求变化", "发展问题"),
                "keywords": ("专业实践", "应用研究", "问题分析"),
            },
        }
        return profiles.get(category, profiles["general"])

    @classmethod
    def _major_profile(cls, major: str) -> str:
        """把专业转换成学科边界提示，避免所有专业被套成通用管理题目。"""
        profile = cls._major_profile_data(cls._major_category(major))
        return (
            f"这是{profile['label']}方向。研究对象应优先来自{profile['focus']}。"
            "题目必须与该专业的知识对象或实践场景直接相关，不能把专业名称机械拼接到"
            "服务质量、客户服务、岗位能力、工作流程等通用模板中。"
        )

    @classmethod
    def _is_topic_relevant(cls, major: str, title: str) -> bool:
        """拦截明显跨专业的 AI 结果，让本地候选有机会补位。"""
        title_text = (title or "").strip()
        category = cls._major_category(major)
        profile = cls._major_profile_data(category)
        if category == "general":
            return True

        generic_unrelated = ("客户服务", "服务质量", "岗位能力", "工作流程")
        if any(signal in title_text for signal in generic_unrelated) and category not in {"business", "tourism", "public_admin"}:
            return False

        return any(signal in title_text for signal in profile["signals"])

    async def generate_topics(
        self,
        major: str,
        education_level: str,
        paper_type: str,
        word_count: Optional[int] = None,
        keywords: Optional[List[str]] = None,
        count: int = 3,
        ai_config: Optional[ActiveAIConfig] = None,
        skill_instructions: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        生成论文选题

        Args:
            major: 专业
            education_level: 学历层次
            paper_type: 论文类型
            keywords: 关键词列表
            count: 生成数量

        Returns:
            选题列表
        """
        keywords_str = "、".join(keywords) if keywords else ""
        keyword_prompt = f"，关键词包括：{keywords_str}" if keywords_str else ""

        system = skill_instructions or get_skill("topics").instructions
        major_profile = self._major_profile(major)
        prompt = f"""生成{count}个论文选题候选。专业：{major}；论文类型：{paper_type}；学历层次：{education_level}{keyword_prompt}。

学科边界：{major_profile}

专业、论文类型和学历层次只用于判断研究方向、研究视角和合适的工作量，不是固定标题模板。请根据专业所属学科自由拟定自然、具体、有研究价值的中文题目，不要把输入字段机械拼进标题，不要使用“基于{major}的1号研究课题”这类占位表达，也不要给所有题目套相同的前缀、后缀或句式。论文类型用于调整研究方式，但不要为了体现类型而强行给每个标题添加“研究”“调查”“路径”等相同后缀；学历层次只用于控制问题范围和难度。候选题目之间要在研究对象、问题、场景或方法上有实质差异。生成后再次检查题目是否真正属于{major}，不符合学科边界的题目必须删除并重写。

请生成恰好{count}个候选选题。只返回 JSON 数组，每项仅含 title、description、keywords。description 用100–200字说明核心问题、研究价值、拟用方法、候选资料来源及完成条件；不编造已获得的资料，不生成大纲。格式如下：
[
  {{
    "title": "选题标题",
    "description": "研究背景、核心问题、研究价值与可行性（100-200字）",
    "keywords": ["关键词1", "关键词2", "关键词3"]
  }}
]"""

        if ai_config:
            content = await self._generate_text(ai_config, prompt, 2000, system=system)
            import json
            import re
            json_match = re.search(r'\[[\s\S]*\]', content)
            if json_match:
                try:
                    topics = json.loads(json_match.group())
                    if isinstance(topics, list):
                        return [
                            topic for topic in topics
                            if isinstance(topic, dict)
                            and isinstance(topic.get("title"), str)
                            and self._is_topic_relevant(major, topic["title"])
                        ]
                except json.JSONDecodeError:
                    pass
        elif self.anthropic_client:
            response = await self.anthropic_client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=2000,
                system=system,
                messages=[{"role": "user", "content": prompt}]
            )
            content = response.content[0].text

            # 解析 JSON
            import json
            import re
            # 提取 JSON 部分
            json_match = re.search(r'\[[\s\S]*\]', content)
            if json_match:
                topics = json.loads(json_match.group())
                if isinstance(topics, list):
                    return [
                        topic for topic in topics
                        if isinstance(topic, dict)
                        and isinstance(topic.get("title"), str)
                        and self._is_topic_relevant(major, topic["title"])
                    ]

        # 如果 AI 不可用或返回内容无法解析，返回有实际内容的本地候选，不能返回占位标题。
        return self._generate_mock_topics(major, education_level, paper_type, count)

    async def generate_outline(
        self,
        topic_title: str,
        major: str,
        education_level: str,
        paper_type: str,
        word_count: Optional[int] = None,
        requirements: Optional[str] = None,
        ai_config: Optional[ActiveAIConfig] = None,
        skill_instructions: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        生成论文大纲

        Args:
            topic_title: 选题标题
            major: 专业
            education_level: 学历层次
            paper_type: 论文类型
            requirements: 额外要求

        Returns:
            大纲结构
        """
        style_text = "文科格式：一级使用‘一、二、三、’，二级使用‘（一）（二）（三）’且不加标点，三级使用‘1. 2. 3.’。" if requirements == 'liberal' else "理科格式：一级使用‘1 2 3’不加标点，二级使用‘1.1’，三级使用‘1.1.1’。"
        req_text = f"\n{style_text}"

        system = skill_instructions or get_skill("outline").instructions
        prompt = f"""生成论文大纲。
论文标题：{topic_title}
专业：{major}
学历层次：{education_level}
论文类型：{paper_type}{req_text}
目标字数：{word_count or '未提供'}

请以JSON格式返回，格式如下：
{{
  "title": "论文标题",
  "sections": [
    {{
      "level": 1,
      "title": "1. 引言",
      "content": "简要说明本章节的内容",
      "order": 1,
      "subsections": [
        {{
          "level": 2,
          "title": "1.1 研究背景",
          "content": "说明",
          "order": 1
        }}
      ]
    }}
  ]
}}"""

        def validate_outline(value: Any) -> Optional[Dict[str, Any]]:
            if not isinstance(value, dict) or not isinstance(value.get("title"), str) or not isinstance(value.get("sections"), list):
                return None
            sections = value["sections"]
            if not sections or any(not isinstance(s, dict) or not isinstance(s.get("title"), str) for s in sections):
                return None
            return {"title": value["title"], "sections": sections}

        def parse_structured(content: str) -> Optional[Dict[str, Any]]:
            import json, re
            if not isinstance(content, str) or not content.strip():
                return None
            text = content.strip()
            # 去除 markdown 代码围栏，并优先截取完整对象
            text = re.sub(r"^```(?:json)?\s*|\s*```$", "", text, flags=re.I)
            start, end = text.find("{"), text.rfind("}")
            if start < 0 or end <= start:
                return None
            try:
                return validate_outline(json.loads(text[start:end + 1]))
            except json.JSONDecodeError:
                return None

        if ai_config:
            content = await self._generate_text(ai_config, prompt, 4000, system=system)
            parsed = parse_structured(content)
            if parsed:
                return parsed
        elif self.anthropic_client:
            response = await self.anthropic_client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=4000,
                system=system,
                messages=[{"role": "user", "content": prompt}]
            )
            content = response.content[0].text

            # 解析 JSON
            parsed = parse_structured(content)
            if parsed:
                return parsed

        # 返回模拟数据
        return self._generate_mock_outline(topic_title)

    async def search_references(
        self,
        keyword: str,
        max_results: int = 10
    ) -> List[Dict[str, Any]]:
        """
        搜索参考文献

        TODO: 集成知网或其他学术数据库 API
        目前返回模拟数据

        Args:
            keyword: 搜索关键词
            max_results: 最大结果数

        Returns:
            文献列表
        """
        # 这里应该调用知网 API 或其他学术数据库
        # 暂时返回模拟数据
        return self._generate_mock_references(keyword, max_results)

    async def generate_document(
        self,
        document_type: str,
        topic_title: str,
        outline: Optional[Dict[str, Any]] = None,
        references: Optional[List[Dict[str, Any]]] = None,
        requirements: Optional[str] = None,
        ai_config: Optional[ActiveAIConfig] = None,
        skill_instructions: Optional[str] = None,
    ) -> str:
        """
        生成文档内容

        Args:
            document_type: 文档类型
            topic_title: 论文标题
            outline: 大纲结构
            references: 参考文献
            requirements: 额外要求

        Returns:
            文档内容（Markdown格式）
        """
        doc_type_names = {
            "assignment": "任务书",
            "proposal": "开题报告",
            "literature_review": "文献综述",
            "thesis": "论文正文"
        }
        doc_name = doc_type_names.get(document_type, "文档")
        req_text = f"\n额外要求：{requirements}" if requirements else ""

        outline_text = ""
        if outline:
            outline_text = f"\n参考大纲：\n{self._format_outline(outline)}"

        refs_text = ""
        if references and document_type in {"literature_review", "thesis"}:
            import json
            refs_text = "\n参考文献材料（未提供的摘要或全文不可推断）：\n" + json.dumps(references, ensure_ascii=False)
        elif document_type == "literature_review":
            refs_text = "\n参考文献未提供：仅生成明确标识的综述框架与资料需求，不能虚构综述结论。"

        system = skill_instructions or get_skill(document_type).instructions
        prompt = f"""撰写{doc_name}。
论文标题：{topic_title}{outline_text}{refs_text}{req_text}
请直接输出 Markdown，依据当前文档 Skill 确定结构和篇幅；未指定字数时，以材料充分性和文档用途为准，不凑字数。"""

        if ai_config:
            return await self._generate_text(ai_config, prompt, 8000, system=system)
        if self.anthropic_client:
            response = await self.anthropic_client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=8000,
                system=system,
                messages=[{"role": "user", "content": prompt}]
            )
            return response.content[0].text

        # 返回模拟数据
        return self._generate_mock_document(doc_name, topic_title)

    async def _generate_text(
        self,
        config: ActiveAIConfig,
        prompt: str,
        requested_max_tokens: int,
        system: Optional[str] = None,
    ) -> str:
        max_tokens = min(config.max_tokens, requested_max_tokens)
        if config.provider == "anthropic":
            client = build_anthropic_client(config)
            kwargs = {
                "model": config.model,
                "max_tokens": max_tokens,
                "temperature": config.temperature,
                "messages": [{"role": "user", "content": prompt}],
            }
            if system:
                kwargs["system"] = system
            response = await client.messages.create(**kwargs)
            return response.content[0].text

        client = build_openai_client(config)
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})
        response = await client.chat.completions.create(
            model=config.model,
            max_tokens=max_tokens,
            temperature=config.temperature,
            messages=messages,
        )
        return response.choices[0].message.content or ""

    def _format_outline(self, outline: Dict[str, Any]) -> str:
        """格式化大纲为文本"""
        lines = []
        def walk(sections, depth=0):
            for section in sections:
                lines.append("  " * depth + section.get("title", ""))
                if section.get("content"):
                    lines.append("  " * depth + "写作任务：" + str(section["content"]))
                walk(section.get("subsections") or [], depth + 1)
        walk(outline.get("sections") or [])
        return "\n".join(lines)

    def _generate_mock_topics(
        self,
        major: str,
        education_level: str,
        paper_type: str,
        count: int
    ) -> List[Dict[str, Any]]:
        """AI 不可用时提供可直接参考的本地候选，而不是编号占位题目。"""
        major_text = major.strip() or "相关专业"
        is_chinese_literature = any(
            name in major_text.replace(" ", "")
            for name in ("汉语言文学", "中国语言文学", "汉语言", "中文")
        )
        is_education = any(
            name in major_text for name in ("教育", "学前", "小学", "教师")
        )

        chinese_literature_pools = {
            "论述性论文": [
                ("《诗经》爱情诗中的情感表达与审美特征", ["《诗经》", "爱情诗", "情感表达"]),
                ("陶渊明田园诗中的隐逸意识与生命态度", ["陶渊明", "田园诗", "隐逸意识"]),
                ("李白诗歌中的浪漫主义想象及其艺术表现", ["李白", "诗歌", "浪漫主义"]),
                ("杜甫诗歌中的忧患意识与现实关怀", ["杜甫", "诗歌", "忧患意识"]),
                ("《红楼梦》中林黛玉形象的悲剧意蕴", ["《红楼梦》", "林黛玉", "悲剧意蕴"]),
                ("鲁迅《狂人日记》的批判思想与叙事表达", ["鲁迅", "《狂人日记》", "批判思想"]),
                ("《边城》中的人性美及其乡土文化意蕴", ["沈从文", "《边城》", "人性美"]),
                ("余华《活着》中的苦难书写与生命意识", ["余华", "《活着》", "苦难主题"]),
                ("网络流行语的构成特点及其文化表达", ["网络流行语", "语言特点", "文化表达"]),
                ("现代汉语成语的文化内涵与语用特点", ["现代汉语", "成语", "文化内涵"]),
            ],
            "研究性论文": [
                ("《三国演义》中诸葛亮人物形象的多重意义", ["《三国演义》", "诸葛亮", "人物形象"]),
                ("《水浒传》中宋江形象的复杂性分析", ["《水浒传》", "宋江", "人物形象"]),
                ("《西游记》中孙悟空形象的成长与变化", ["《西游记》", "孙悟空", "人物形象"]),
                ("白居易新乐府诗的写实特色及其表达方式", ["白居易", "新乐府", "写实特色"]),
                ("老舍《骆驼祥子》中的人物悲剧与社会环境", ["老舍", "《骆驼祥子》", "悲剧主题"]),
                ("朱自清散文的语言艺术与情感表达", ["朱自清", "散文", "语言艺术"]),
                ("张爱玲小说中的女性形象与悲剧意识", ["张爱玲", "小说", "女性形象"]),
                ("莫言小说的乡土叙事特色及其文化意蕴", ["莫言", "小说", "乡土叙事"]),
                ("广告语中的修辞运用与语言表达效果", ["广告语", "修辞", "语言表达"]),
                ("方言在文学作品中的人物塑造作用", ["方言", "文学作品", "人物塑造"]),
            ],
            "实证研究论文": [
                ("网络文学作品中女性人物形象的类型与表达特征", ["网络文学", "女性形象", "文本分析"]),
                ("短视频文案中的网络流行语使用特点分析", ["短视频文案", "网络流行语", "语言分析"]),
                ("现代汉语叠词在文学文本中的表达效果", ["现代汉语", "叠词", "表达效果"]),
                ("中学生经典名著阅读兴趣与阅读体验的关联分析", ["名著阅读", "中学生", "阅读体验"]),
                ("语文课堂文学作品教学中的审美感知表现", ["语文课堂", "文学教学", "审美感知"]),
                ("自媒体标题中的修辞方式与传播特点", ["自媒体标题", "修辞方式", "传播特点"]),
                ("不同体裁文学作品中的叙事视角差异", ["文学体裁", "叙事视角", "文本比较"]),
                ("大学生网络流行语使用与语言态度的关系", ["网络流行语", "大学生", "语言态度"]),
                ("文学作品改编影视作品中的情节取舍特征", ["文学改编", "影视作品", "情节取舍"]),
                ("地方方言使用者的语言认同与文学阅读体验", ["方言", "语言认同", "文学阅读"]),
            ],
            "调查研究论文": [
                ("高校学生经典文学作品阅读现状与阅读需求调查", ["经典文学", "高校学生", "阅读需求"]),
                ("中学生名著阅读兴趣与阅读困难调查", ["名著阅读", "中学生", "阅读困难"]),
                ("网络流行语在大学生语言交往中的使用情况调查", ["网络流行语", "大学生", "语言交往"]),
                ("短视频文案语言风格的受众接受情况调查", ["短视频文案", "语言风格", "受众接受"]),
                ("地方高校学生文学阅读习惯与阅读偏好调查", ["文学阅读", "高校学生", "阅读偏好"]),
                ("语文教育专业学生文学鉴赏能力培养需求调查", ["语文教育", "文学鉴赏", "培养需求"]),
                ("大学生对影视文学改编作品的接受倾向调查", ["影视改编", "大学生", "接受倾向"]),
                ("网络文学读者的作品选择偏好与阅读体验调查", ["网络文学", "读者偏好", "阅读体验"]),
                ("中学生古诗文学习兴趣与学习困难调查", ["古诗文", "中学生", "学习兴趣"]),
                ("汉语委婉语在日常交往中的使用认知调查", ["汉语委婉语", "日常交往", "语言认知"]),
            ],
            "案例研究论文": [
                ("《狂人日记》中“狂人”形象的叙事建构", ["鲁迅", "《狂人日记》", "叙事建构"]),
                ("《边城》翠翠形象的成长过程与审美意蕴", ["沈从文", "《边城》", "翠翠形象"]),
                ("《红楼梦》诗词书写与人物命运表达的案例分析", ["《红楼梦》", "诗词", "人物命运"]),
                ("《骆驼祥子》中祥子悲剧形成过程的文本分析", ["老舍", "《骆驼祥子》", "人物悲剧"]),
                ("一部网络小说中的乡土叙事表达案例分析", ["网络小说", "乡土叙事", "文本分析"]),
                ("经典文学作品影视改编中的人物形象重构", ["文学改编", "影视改编", "人物形象"]),
                ("鲁迅小说中的儿童形象及其社会寓意", ["鲁迅小说", "儿童形象", "社会寓意"]),
                ("唐宋词中“愁”意象的表达案例分析", ["唐宋词", "愁意象", "文学意象"]),
                ("自媒体短视频中的古诗词传播案例分析", ["古诗词", "短视频", "文化传播"]),
                ("一部文学作品中方言描写的表达功能分析", ["文学作品", "方言描写", "表达功能"]),
            ],
            "设计实践论文": [
                ("面向中学生的经典名著阅读导学方案设计", ["经典名著", "中学生", "阅读导学"]),
                ("古诗词意象可视化学习资源的设计与应用", ["古诗词", "意象", "学习资源"]),
                ("基于短视频的古典诗词赏析内容设计", ["古典诗词", "短视频", "内容设计"]),
                ("面向大学生的文学作品导读手册设计", ["文学作品", "大学生", "导读手册"]),
                ("汉语言文学专业古代文学课程学习任务设计", ["古代文学", "课程任务", "学习设计"]),
                ("中学生名著阅读评价量表的设计与试用", ["名著阅读", "评价量表", "中学生"]),
                ("文学作品人物形象分析学习单的设计", ["文学作品", "人物形象", "学习单"]),
                ("面向语文课堂的散文审美阅读活动设计", ["散文阅读", "语文课堂", "审美活动"]),
                ("网络文学文本阅读与批评任务包设计", ["网络文学", "文本批评", "任务设计"]),
                ("汉语成语文化学习微课内容的设计与实践", ["汉语成语", "文化学习", "微课设计"]),
            ],
        }

        education_pools = {
            "论述性论文": [
                ("生成式人工智能进入课堂后的教师角色边界与教育责任", ["生成式人工智能", "教师角色", "教育责任"]),
                ("教育公平视角下城乡义务教育资源配置的现实困境", ["教育公平", "义务教育", "资源配置"]),
                ("家校协同中教师沟通责任的边界与实践启示", ["家校协同", "教师沟通", "教育责任"]),
                ("核心素养导向下课堂评价标准的重构逻辑", ["核心素养", "课堂评价", "评价标准"]),
                ("终身学习理念下成人教育课程内容更新的价值取向", ["终身学习", "成人教育", "课程内容"]),
                ("劳动教育融入学校课程的价值冲突与实施原则", ["劳动教育", "课程融合", "实施原则"]),
            ],
            "研究性论文": [
                ("中小学课堂提问方式与学生学习参与的关系分析", ["课堂提问", "学习参与", "课堂教学"]),
                ("学校数字化资源使用中的教师适应过程研究", ["数字化资源", "教师适应", "教育技术"]),
                ("家校沟通文本中的责任表达与协同机制研究", ["家校沟通", "责任表达", "协同机制"]),
                ("小学阶段阅读素养培养的课堂任务设计研究", ["阅读素养", "课堂任务", "小学教育"]),
                ("成人学习者课程参与动机的形成机制研究", ["成人学习者", "学习动机", "课程参与"]),
                ("乡村学校教师专业发展支持体系的运行逻辑研究", ["乡村教育", "教师发展", "支持体系"]),
            ],
            "实证研究论文": [
                ("课堂形成性评价反馈与学生学习投入的关联研究", ["形成性评价", "学习反馈", "学习投入"]),
                ("教师数字素养与教学资源使用意愿的关系研究", ["教师数字素养", "教学资源", "使用意愿"]),
                ("家长参与方式与学生学习支持感的关系研究", ["家长参与", "学习支持", "家庭教育"]),
                ("合作学习中同伴互动质量与学习表现的关系研究", ["合作学习", "同伴互动", "学习表现"]),
                ("成人学习者学习动机与课程坚持行为的关系研究", ["成人学习者", "学习动机", "课程坚持"]),
                ("学前儿童游戏活动中教师支持行为的观察研究", ["学前儿童", "游戏活动", "教师支持"]),
            ],
            "调查研究论文": [
                ("中小学教师使用生成式人工智能辅助备课的现状调查", ["生成式人工智能", "教师备课", "现状调查"]),
                ("家长对家校线上沟通服务需求的调查研究", ["家校沟通", "家长需求", "线上服务"]),
                ("高校毕业生对职业教育课程实践性的认知调查", ["职业教育", "课程实践性", "认知调查"]),
                ("成人学习者线上课程学习障碍与支持需求调查", ["成人学习", "线上课程", "学习支持"]),
                ("教师对校本研修参与形式与效果感知的调查", ["校本研修", "教师发展", "参与形式"]),
                ("学前儿童家庭阅读活动开展情况与家长需求调查", ["学前教育", "家庭阅读", "家长需求"]),
            ],
            "案例研究论文": [
                ("一所学校推进项目化学习的实施过程与反思", ["项目化学习", "学校改革", "实施过程"]),
                ("班级家校冲突协商过程中的沟通机制分析", ["家校冲突", "班级管理", "沟通机制"]),
                ("乡村学校校本课程开发的实践过程与经验审视", ["乡村学校", "校本课程", "课程开发"]),
                ("一门线上课程学习共同体的形成过程研究", ["线上课程", "学习共同体", "课程实践"]),
                ("幼儿园游戏课程实施中教师支持行为的案例分析", ["幼儿园", "游戏课程", "教师支持"]),
                ("学校家长委员会参与校园治理的实践案例研究", ["家长委员会", "校园治理", "家校合作"]),
            ],
            "设计实践论文": [
                ("面向小学语文阅读课的形成性评价方案设计与试用", ["小学语文", "形成性评价", "方案设计"]),
                ("家校沟通反馈流程的教学管理原型设计与评价", ["家校沟通", "反馈流程", "原型设计"]),
                ("面向成人学习者的微课学习任务包设计与实践", ["成人学习", "微课", "任务设计"]),
                ("幼儿园游戏活动观察记录工具的设计与应用", ["幼儿园", "游戏活动", "观察工具"]),
                ("促进学生同伴互助的班级学习活动方案设计", ["同伴互助", "班级活动", "学习设计"]),
                ("乡村学校数字化教学资源导航方案的设计与评价", ["乡村教育", "数字资源", "方案评价"]),
            ],
        }

        category = self._major_category(major_text)
        profile = self._major_profile_data(category)
        if category == "general":
            profile = {
                **profile,
                "label": major_text,
                "objects": (
                    f"{major_text}专业课程学习",
                    f"{major_text}专业实践场景",
                    f"{major_text}行业应用任务",
                    f"{major_text}岗位实践过程",
                    f"{major_text}专业技术应用",
                    f"{major_text}服务对象需求",
                ),
            }
        domain_pool = {}
        domain_patterns = {
            "论述性论文": [
                "{object}中的{issue}：问题辨析与实践思考",
                "{object}与{issue}之间的关系及其现实意义",
                "{scope}背景下{issue}的价值取向分析",
                "{object}实践中的{issue}问题探讨",
            ],
            "研究性论文": [
                "{object}中{issue}的表现及其形成原因",
                "{issue}在{object}中的应用逻辑研究",
                "{object}视角下{issue}的实践机制分析",
                "{object}与{issue}的比较研究",
            ],
            "实证研究论文": [
                "{object}与{issue}之间的关联研究",
                "{object}中{issue}的差异特征研究",
                "{scope}中{issue}的表现研究",
                "{object}背景下{issue}的影响因素研究",
            ],
            "调查研究论文": [
                "{object}相关{issue}的现状调查",
                "{scope}中{issue}的认知与需求调查",
                "{object}参与者对{issue}的体验调查",
                "{scope}中{issue}问题的调查分析",
            ],
            "案例研究论文": [
                "{object}中{issue}的实践案例分析",
                "{object}推进{issue}的过程与反思",
                "{scope}中{issue}问题的案例研究",
                "{object}场景下{issue}形成机制的分析",
            ],
            "设计实践论文": [
                "面向{object}的{issue}方案设计",
                "{object}场景下{issue}任务流程的设计与评价",
                "支持{object}中{issue}的工具或资源设计",
                "促进{issue}的{object}实践方案设计",
            ],
        }
        domain_scope = profile["label"] + "实践"
        for current_type, current_patterns in domain_patterns.items():
            domain_pool[current_type] = [
                (
                    current_patterns[index % len(current_patterns)].format(
                        object=object_name,
                        issue=issue,
                        scope=domain_scope,
                    ),
                    [object_name, issue, *profile["keywords"][:1]],
                )
                for index, (object_name, issue) in enumerate(
                    zip(profile["objects"], profile["issues"])
                )
            ]

        pool_source = (
            chinese_literature_pools
            if is_chinese_literature
            else education_pools
            if is_education
            else domain_pool
        )
        pool = list(pool_source.get(paper_type) or [])
        if not pool:
            pool = list(pool_source["研究性论文"])

        # 前端目前最多请求 10 个，接口允许更大的数量；不足时继续从不同对象和问题角度扩展。
        # 这些候选仍然是具体题目，不使用“第N号课题”之类的编号占位符。
        education_extension_seeds = [
            ("课堂提问", "学生思维表达"),
            ("教师反馈", "学生修正行为"),
            ("课后服务", "学生参与体验"),
            ("融合教育课堂", "同伴支持"),
            ("职业教育实习", "校企协同"),
            ("儿童数字媒介使用", "家庭教育边界"),
            ("教师减负政策", "学校治理"),
            ("乡村学校发展", "教师留任"),
            ("学校心理支持", "求助意愿"),
            ("阅读教学活动", "学生阅读动机"),
            ("在线学习平台", "学习过程管理"),
            ("班级规则建设", "学生规则认同"),
            ("劳动教育实践", "课程参与方式"),
            ("校本研修活动", "教师专业成长"),
        ]
        literature_extension_seeds = [
            ("古代诗歌", "意象表达"),
            ("古典小说", "人物塑造"),
            ("现当代散文", "抒情方式"),
            ("文学作品", "叙事视角"),
            ("网络文学", "审美特征"),
            ("现代汉语", "词语使用"),
            ("广告文本", "修辞表达"),
            ("影视改编", "文学意蕴"),
            ("古诗文教学", "审美体验"),
            ("地方方言", "地域文化表达"),
        ]
        domain_extension_seeds = [
            (object_name, issue)
            for object_name in profile["objects"]
            for issue in profile["issues"][:3]
        ]
        extension_patterns = {
            "论述性论文": [
                "{scope}中的{object}与{issue}：实践价值及问题边界",
                "{object}与{issue}之间的张力及其调适",
                "{scope}背景下{issue}的价值取向分析",
                "{object}实践中的{issue}问题辨析",
            ],
            "研究性论文": [
                "{scope}中{object}与{issue}的形成机制",
                "{issue}在{object}中的表现及其解释",
                "{object}视角下{issue}的实践逻辑",
                "{object}与{issue}的比较分析",
            ],
            "实证研究论文": [
                "{object}与{issue}之间的关联研究",
                "{scope}中{issue}的差异特征研究",
                "{object}背景下{issue}的观察研究",
                "{object}与{issue}的关系测量研究",
            ],
            "调查研究论文": [
                "{scope}中{issue}的现状与需求调查",
                "{object}相关{issue}的认知情况调查",
                "{scope}中{object}参与体验的调查研究",
                "{object}场景下{issue}支持需求的调查",
            ],
            "案例研究论文": [
                "{scope}中{object}与{issue}的实践过程案例分析",
                "{object}推进{issue}的行动过程与反思",
                "{scope}中{issue}问题的协商处理案例研究",
                "{object}场景下{issue}形成机制的案例分析",
            ],
            "设计实践论文": [
                "面向{object}的{issue}支持方案设计",
                "用于{scope}的{issue}任务流程设计与评价",
                "{object}场景下{issue}反馈工具的原型设计",
                "促进{issue}的{object}活动方案设计与试用",
            ],
        }
        literature_patterns = {
            "论述性论文": [
                "{object}中的{issue}及其审美意蕴",
                "{object}与{issue}的表达特点",
                "{scope}中的{issue}问题辨析",
                "{object}视角下{issue}的文化内涵",
            ],
            "研究性论文": [
                "{object}中的{issue}表现及其形成原因",
                "{issue}在{object}中的表达方式研究",
                "{object}视角下{issue}的文本特征",
                "{object}与{issue}的比较分析",
            ],
            "实证研究论文": [
                "{object}中的{issue}特征分析",
                "{object}与{issue}的关联分析",
                "{scope}中{issue}的表现情况研究",
                "{object}文本中{issue}的分布特点",
            ],
            "调查研究论文": [
                "{object}学习中的{issue}认知情况调查",
                "{scope}中{issue}的阅读体验调查",
                "{object}相关{issue}的接受情况调查",
                "{scope}中{issue}学习需求调查",
            ],
            "案例研究论文": [
                "{object}中{issue}表达方式的案例分析",
                "{object}呈现{issue}的文本案例研究",
                "{scope}中{issue}问题的案例分析",
                "{object}与{issue}结合的作品案例分析",
            ],
            "设计实践论文": [
                "面向{object}的{issue}阅读活动设计",
                "{object}中{issue}学习资源的设计",
                "用于{scope}的{issue}导学任务设计",
                "{object}相关{issue}微课内容设计与实践",
            ],
        }
        patterns = (
            literature_patterns.get(paper_type, literature_patterns["研究性论文"])
            if is_chinese_literature
            else extension_patterns.get(paper_type, extension_patterns["研究性论文"])
        )
        scope = (
            "文学文本"
            if is_chinese_literature
            else "教育实践"
            if is_education
            else f"{major_text}专业实践"
        )
        known_titles = {title for title, _ in pool}
        extension_seeds = (
            literature_extension_seeds
            if is_chinese_literature
            else education_extension_seeds
            if is_education
            else domain_extension_seeds
        )
        for index, (object_name, issue) in enumerate(extension_seeds):
            title = patterns[index % len(patterns)].format(
                scope=scope,
                object=object_name,
                issue=issue,
            )
            if title not in known_titles:
                pool.append((title, [object_name, issue]))
                known_titles.add(title)
            if len(pool) >= count:
                break

        method_by_type = {
            "论述性论文": "可结合相关理论、政策文本和公开资料进行概念梳理与规范分析",
            "研究性论文": "可围绕一个明确问题开展文献梳理、文本分析或比较分析",
            "实证研究论文": "可在取得合适样本和测量资料后进行问卷、访谈或统计分析",
            "调查研究论文": "可根据实际可接触的人群设计问卷或访谈，并进行描述性分析",
            "案例研究论文": "需要先确认具体案例和资料授权，再重建过程并分析其中的问题机制",
            "设计实践论文": "可明确交付物、使用场景和评价方式，完成方案设计、实现或小范围试用",
        }
        method = method_by_type.get(paper_type, method_by_type["研究性论文"])
        topics = []
        for title, topic_keywords in pool[:count]:
            topics.append({
                "title": title,
                "description": (
                    f"本题聚焦“{title}”中的具体问题，适合{education_level}层次的{paper_type}。"
                    f"{method}。研究范围应根据实际可获得的资料、时间和对象进一步收窄，"
                    "涉及问卷、访谈或真实场景时需提前确认接触条件、知情同意和资料使用权限。"
                ),
                "keywords": [major_text, *topic_keywords],
            })
        return topics

    def _generate_mock_outline(self, topic_title: str) -> Dict[str, Any]:
        """生成模拟大纲数据"""
        return {
            "title": topic_title,
            "sections": [
                {
                    "level": 1,
                    "title": "摘要",
                    "content": "论文摘要部分",
                    "order": 1
                },
                {
                    "level": 1,
                    "title": "1. 引言",
                    "content": "介绍研究背景和意义",
                    "order": 2,
                    "subsections": [
                        {"level": 2, "title": "1.1 研究背景", "content": "", "order": 1},
                        {"level": 2, "title": "1.2 研究意义", "content": "", "order": 2},
                    ]
                },
                {
                    "level": 1,
                    "title": "2. 文献综述",
                    "content": "回顾相关研究",
                    "order": 3
                },
                {
                    "level": 1,
                    "title": "3. 研究方法",
                    "content": "说明研究方法",
                    "order": 4
                },
                {
                    "level": 1,
                    "title": "4. 研究结果",
                    "content": "展示研究结果",
                    "order": 5
                },
                {
                    "level": 1,
                    "title": "5. 讨论",
                    "content": "讨论研究发现",
                    "order": 6
                },
                {
                    "level": 1,
                    "title": "6. 结论",
                    "content": "总结研究成果",
                    "order": 7
                },
                {
                    "level": 1,
                    "title": "参考文献",
                    "content": "列出参考文献",
                    "order": 8
                }
            ]
        }

    def _generate_mock_references(
        self,
        keyword: str,
        max_results: int
    ) -> List[Dict[str, Any]]:
        """生成模拟文献数据"""
        return [
            {
                "title": f"关于{keyword}的研究{i+1}",
                "authors": ["张三", "李四"],
                "publication": "学术期刊",
                "year": 2023 - i,
                "volume": f"{40+i}",
                "issue": f"{i+1}",
                "pages": f"{100+i*10}-{120+i*10}",
                "doi": f"10.1234/example.{2023-i}.{i+1:03d}",
                "abstract": f"本文研究了{keyword}相关的问题...",
                "keywords": [keyword, "研究", "应用"],
                "citation_format": "GB/T 7714",
            }
            for i in range(min(max_results, 5))
        ]

    def _generate_mock_document(self, doc_type: str, title: str) -> str:
        """生成模拟文档内容"""
        return f"""# {title} - {doc_type}

## 摘要

本研究针对相关领域的重要问题展开深入探讨，通过系统的理论分析和实证研究，提出了创新性的解决方案。

## 1. 引言

### 1.1 研究背景

随着相关领域的不断发展，该问题日益受到学术界和实践界的关注。

### 1.2 研究意义

本研究具有重要的理论意义和实践价值。

## 2. 文献综述

回顾国内外相关研究...

## 3. 研究方法

本研究采用定性与定量相结合的研究方法...

## 4. 研究结果

通过研究，我们得到了以下主要发现...

## 5. 讨论

研究结果表明...

## 6. 结论

本研究得出以下结论...

## 参考文献

[1] 张三, 李四. 相关研究[J]. 学术期刊, 2023, 40(1): 100-120.
"""


# 全局 AI 服务实例
ai_service = AIService()
