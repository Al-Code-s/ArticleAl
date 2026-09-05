"""
导出服务 - 将文档导出为 Word/PDF
"""
import os
from datetime import datetime
from typing import Optional
from pathlib import Path
import markdown
from docx import Document
from docx.shared import Pt, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.enums import TA_CENTER, TA_LEFT

from app.core.config import settings


class ExportService:
    """文档导出服务"""

    def __init__(self):
        self.export_dir = Path(settings.EXPORT_DIR)
        self.export_dir.mkdir(parents=True, exist_ok=True)

    async def export_to_word(
        self,
        title: str,
        content: str,
        metadata: Optional[dict] = None
    ) -> str:
        """
        导出为 Word 文档

        Args:
            title: 文档标题
            content: 文档内容（Markdown 格式）
            metadata: 元数据（作者、日期等）

        Returns:
            导出的文件路径
        """
        # 创建 Word 文档
        doc = Document()

        # 设置文档属性
        if metadata:
            doc.core_properties.title = title
            doc.core_properties.author = metadata.get("author", "ArticleAI")
            doc.core_properties.comments = metadata.get("description", "")

        # 添加标题
        heading = doc.add_heading(title, 0)
        heading.alignment = WD_ALIGN_PARAGRAPH.CENTER

        # 添加元数据
        if metadata:
            info_paragraph = doc.add_paragraph()
            info_paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER

            if metadata.get("author"):
                info_paragraph.add_run(f"作者：{metadata['author']}\n")
            if metadata.get("major"):
                info_paragraph.add_run(f"专业：{metadata['major']}\n")
            if metadata.get("date"):
                info_paragraph.add_run(f"日期：{metadata['date']}\n")

            doc.add_paragraph()  # 空行

        # 解析 Markdown 并添加到文档
        self._add_markdown_to_word(doc, content)

        # 生成文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{title}_{timestamp}.docx"
        filepath = self.export_dir / filename

        # 保存文档
        doc.save(str(filepath))

        return str(filepath)

    async def export_to_pdf(
        self,
        title: str,
        content: str,
        metadata: Optional[dict] = None
    ) -> str:
        """
        导出为 PDF 文档

        Args:
            title: 文档标题
            content: 文档内容（Markdown 格式）
            metadata: 元数据（作者、日期等）

        Returns:
            导出的文件路径
        """
        # 生成文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{title}_{timestamp}.pdf"
        filepath = self.export_dir / filename

        # 创建 PDF 文档
        doc = SimpleDocTemplate(
            str(filepath),
            pagesize=A4,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=18,
        )

        # 准备样式
        styles = getSampleStyleSheet()

        # 标题样式
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=RGBColor(0, 0, 0),
            spaceAfter=30,
            alignment=TA_CENTER,
        )

        # 正文样式
        body_style = ParagraphStyle(
            'CustomBody',
            parent=styles['BodyText'],
            fontSize=12,
            spaceAfter=12,
            alignment=TA_LEFT,
        )

        # 构建文档内容
        story = []

        # 添加标题
        story.append(Paragraph(title, title_style))
        story.append(Spacer(1, 0.2 * inch))

        # 添加元数据
        if metadata:
            meta_text = []
            if metadata.get("author"):
                meta_text.append(f"作者：{metadata['author']}")
            if metadata.get("major"):
                meta_text.append(f"专业：{metadata['major']}")
            if metadata.get("date"):
                meta_text.append(f"日期：{metadata['date']}")

            if meta_text:
                meta_style = ParagraphStyle(
                    'MetaStyle',
                    parent=styles['BodyText'],
                    fontSize=10,
                    alignment=TA_CENTER,
                    spaceAfter=20,
                )
                for line in meta_text:
                    story.append(Paragraph(line, meta_style))
                story.append(Spacer(1, 0.3 * inch))

        # 转换 Markdown 内容为 HTML
        html_content = markdown.markdown(content)

        # 简单处理 HTML 标签（实际应用中可能需要更复杂的处理）
        # 这里简化处理，直接按段落分割
        paragraphs = content.split('\n\n')

        for para in paragraphs:
            if para.strip():
                # 处理标题
                if para.startswith('#'):
                    level = len(para) - len(para.lstrip('#'))
                    text = para.lstrip('#').strip()
                    heading_style = styles[f'Heading{min(level, 3)}']
                    story.append(Paragraph(text, heading_style))
                else:
                    # 普通段落
                    story.append(Paragraph(para.strip(), body_style))
                    story.append(Spacer(1, 0.1 * inch))

        # 生成 PDF
        doc.build(story)

        return str(filepath)

    def _add_markdown_to_word(self, doc: Document, markdown_text: str):
        """将 Markdown 文本添加到 Word 文档"""
        lines = markdown_text.split('\n')

        for line in lines:
            line = line.strip()

            if not line:
                doc.add_paragraph()
                continue

            # 处理标题
            if line.startswith('#'):
                level = len(line) - len(line.lstrip('#'))
                text = line.lstrip('#').strip()
                doc.add_heading(text, level=min(level, 3))

            # 处理列表
            elif line.startswith('- ') or line.startswith('* '):
                text = line[2:].strip()
                doc.add_paragraph(text, style='List Bullet')

            elif line[0:1].isdigit() and '. ' in line:
                text = line.split('. ', 1)[1].strip()
                doc.add_paragraph(text, style='List Number')

            # 处理代码块标记（跳过）
            elif line.startswith('```'):
                continue

            # 普通段落
            else:
                doc.add_paragraph(line)

    async def get_export_file(self, filename: str) -> Optional[Path]:
        """获取导出文件路径"""
        filepath = self.export_dir / filename
        if filepath.exists():
            return filepath
        return None

    async def cleanup_old_exports(self, days: int = 7):
        """清理旧的导出文件"""
        import time
        current_time = time.time()

        for file in self.export_dir.iterdir():
            if file.is_file():
                file_age = current_time - file.stat().st_mtime
                if file_age > days * 86400:  # 转换为秒
                    file.unlink()


export_service = ExportService()
