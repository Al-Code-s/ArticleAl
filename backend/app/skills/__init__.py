"""Bundled skills, selected explicitly by the application's task type."""
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class SkillDefinition:
    key: str
    name: str
    description: str
    output_format: str

    @property
    def instructions(self) -> str:
        return (Path(__file__).parent / self.key / "SKILL.md").read_text(encoding="utf-8")


SKILLS = {skill.key: skill for skill in [
    SkillDefinition("topics", "论文选题", "根据专业、学历、论文类型和关键词生成可行的选题。", "JSON 选题数组"),
    SkillDefinition("outline", "论文大纲", "按研究问题组织章节，明确各章任务与逻辑关系。", "JSON 大纲结构"),
    SkillDefinition("assignment", "任务书", "明确研究任务、交付成果、进度和完成条件。", "Markdown"),
    SkillDefinition("proposal", "开题报告", "论证研究价值、文献基础、研究方法与实施可行性。", "Markdown"),
    SkillDefinition("literature_review", "文献综述", "围绕主题比较已有研究，梳理证据与研究缺口。", "Markdown"),
    SkillDefinition("thesis", "论文正文", "依照大纲组织论证，区分已有事实与待补充材料。", "Markdown"),
    SkillDefinition("chat", "学术助手", "结合项目上下文提供写作分析和修改建议。", "自然语言 / Markdown"),
]}


def get_skill(key: str) -> SkillDefinition:
    if key not in SKILLS:
        raise KeyError(f"Unknown skill: {key}")
    return SKILLS[key]
