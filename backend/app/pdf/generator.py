from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate
from io import BytesIO
from typing import List
from app.schemas import PDFExportSettings
from app.models import Dessert
from app.pdf.templates import TEMPLATES, PDFTemplate


def generate_pdf(desserts: List[Dessert], settings: PDFExportSettings) -> BytesIO:
    """Генерация PDF каталога с выбранным шаблоном"""
    buffer = BytesIO()
    
    # Выбираем шаблон (по умолчанию 'minimal')
    template_name = getattr(settings, 'template', 'minimal')
    if template_name not in TEMPLATES:
        template_name = 'minimal'
    
    TemplateClass = TEMPLATES[template_name]
    template = TemplateClass(settings)
    
    # Создаем документ
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        topMargin=2*cm,
        bottomMargin=2*cm,
        leftMargin=2*cm,
        rightMargin=2*cm
    )
    
    story = []
    styles = template.create_styles()
    
    # Титульный лист
    if settings.include_title_page:
        template.create_title_page(story)
    
    # Генерация страниц для каждого десерта
    for dessert in desserts:
        template.create_dessert_page(story, dessert, styles)
    
    doc.build(story)
    buffer.seek(0)
    return buffer

