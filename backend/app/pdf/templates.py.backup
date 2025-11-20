"""
Шаблоны дизайна для PDF каталога
"""
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, 
    PageBreak, KeepTogether, Image
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY, TA_RIGHT
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from typing import List, Dict, Any, Optional
from app.models import Dessert
from app.schemas import PDFExportSettings
from app.config import UPLOAD_DIR, IMAGES_URL_PREFIX
from pathlib import Path
import os
import requests
from PIL import Image as PILImage
from io import BytesIO

# Регистрация шрифта для кириллицы
cyrillic_font = None
try:
    font_paths = [
        "/System/Library/Fonts/Helvetica.ttc",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "C:/Windows/Fonts/arial.ttf",
    ]
    for path in font_paths:
        if os.path.exists(path):
            pdfmetrics.registerFont(TTFont('CyrillicFont', path))
            cyrillic_font = 'CyrillicFont'
            break
except:
    pass


class PDFTemplate:
    """Базовый класс для шаблонов PDF"""
    
    def __init__(self, settings: PDFExportSettings):
        self.settings = settings
        self.font_name = cyrillic_font or 'Helvetica'
        self.font_bold = cyrillic_font or 'Helvetica-Bold'
    
    def _load_image(self, image_url: Optional[str], width: float = 6*cm, height: float = 6*cm) -> Optional[Image]:
        """Загружает изображение по URL и возвращает объект Image для ReportLab"""
        if not image_url:
            return None
        
        try:
            # Если это локальный путь (/static/images/...)
            if image_url.startswith(IMAGES_URL_PREFIX):
                filename = image_url.replace(IMAGES_URL_PREFIX, '')
                file_path = UPLOAD_DIR / filename
                if file_path.exists():
                    # Загружаем локальный файл
                    img = PILImage.open(file_path)
                    # Конвертируем в RGB если нужно (для PNG с прозрачностью)
                    if img.mode in ('RGBA', 'LA', 'P'):
                        rgb_img = PILImage.new('RGB', img.size, (255, 255, 255))
                        if img.mode == 'P':
                            img = img.convert('RGBA')
                        rgb_img.paste(img, mask=img.split()[-1] if img.mode in ('RGBA', 'LA') else None)
                        img = rgb_img
                    
                    # Сохраняем во временный буфер
                    buffer = BytesIO()
                    img.save(buffer, format='JPEG', quality=85)
                    buffer.seek(0)
                    return Image(buffer, width=width, height=height, kind='proportional')
            
            # Если это полный URL (http:// или https://)
            elif image_url.startswith('http://') or image_url.startswith('https://'):
                response = requests.get(image_url, timeout=10, stream=True)
                response.raise_for_status()
                img = PILImage.open(BytesIO(response.content))
                # Конвертируем в RGB если нужно
                if img.mode in ('RGBA', 'LA', 'P'):
                    rgb_img = PILImage.new('RGB', img.size, (255, 255, 255))
                    if img.mode == 'P':
                        img = img.convert('RGBA')
                    rgb_img.paste(img, mask=img.split()[-1] if img.mode in ('RGBA', 'LA') else None)
                    img = rgb_img
                
                buffer = BytesIO()
                img.save(buffer, format='JPEG', quality=85)
                buffer.seek(0)
                return Image(buffer, width=width, height=height, kind='proportional')
            
        except Exception as e:
            print(f"Error loading image {image_url}: {e}")
            return None
        
        return None
    
    def create_styles(self) -> Dict[str, ParagraphStyle]:
        """Создает стили для шаблона. Должен быть переопределен в подклассах."""
        raise NotImplementedError
    
    def create_title_page(self, story: List) -> None:
        """Создает титульный лист. Должен быть переопределен в подклассах."""
        raise NotImplementedError
    
    def create_dessert_page(self, story: List, dessert: Dessert, styles: Dict) -> None:
        """Создает страницу для десерта. Должен быть переопределен в подклассах."""
        raise NotImplementedError


class MinimalTemplate(PDFTemplate):
    """Минималистичный шаблон - чистый и простой"""
    
    def create_styles(self) -> Dict[str, ParagraphStyle]:
        styles = getSampleStyleSheet()
        return {
            'title': ParagraphStyle(
                'Title',
                parent=styles['Heading1'],
                fontSize=28,
                textColor=colors.HexColor('#1a1a1a'),
                spaceAfter=40,
                alignment=TA_CENTER,
                fontName=self.font_bold,
                leading=32
            ),
            'heading': ParagraphStyle(
                'Heading',
                parent=styles['Heading2'],
                fontSize=22,
                textColor=colors.HexColor('#2c3e50'),
                spaceAfter=16,
                spaceBefore=20,
                fontName=self.font_bold,
                leading=26
            ),
            'subheading': ParagraphStyle(
                'Subheading',
                parent=styles['Heading3'],
                fontSize=12,
                textColor=colors.HexColor('#7f8c8d'),
                spaceAfter=8,
                spaceBefore=12,
                fontName=self.font_bold,
                leading=14
            ),
            'normal': ParagraphStyle(
                'Normal',
                parent=styles['Normal'],
                fontSize=10,
                textColor=colors.HexColor('#34495e'),
                alignment=TA_JUSTIFY,
                fontName=self.font_name,
                leading=14,
                spaceAfter=8
            ),
            'contact': ParagraphStyle(
                'Contact',
                parent=styles['Normal'],
                fontSize=11,
                textColor=colors.HexColor('#7f8c8d'),
                alignment=TA_CENTER,
                fontName=self.font_name
            )
        }
    
    def create_title_page(self, story: List) -> None:
        styles = self.create_styles()
        story.append(Spacer(1, 10*cm))
        title_text = self.settings.company_name or "Dessert Catalog"
        story.append(Paragraph(title_text, styles['title']))
        story.append(Spacer(1, 1.5*cm))
        
        if self.settings.manager_contact:
            story.append(Paragraph(self.settings.manager_contact, styles['contact']))
        
        story.append(PageBreak())
    
    def create_dessert_page(self, story: List, dessert: Dessert, styles: Dict) -> None:
        # Двухколоночная верстка: изображение слева, информация справа
        img = self._load_image(dessert.image_url, width=6.5*cm, height=6.5*cm)
        
        # Левая колонка - изображение без рамки
        left_col = []
        if img:
            left_col.append(Spacer(1, 0.2*cm))
            left_col.append(img)
        else:
            left_col.append(Spacer(1, 7*cm))
        
        # Правая колонка - информация
        right_col = []
        
        # Название с подчеркиванием
        right_col.append(Paragraph(dessert.title, styles['heading']))
        right_col.append(Spacer(1, 0.3*cm))
        
        # Категория в цветной рамке
        category_table = Table([[dessert.category]], colWidths=[11*cm])
        category_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#e8f4f8')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#2980b9')),
            ('FONTNAME', (0, 0), (-1, -1), self.font_name),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('LEFTPADDING', (0, 0), (-1, -1), 10),
            ('RIGHTPADDING', (0, 0), (-1, -1), 10),
            ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#3498db')),
        ]))
        right_col.append(category_table)
        right_col.append(Spacer(1, 0.3*cm))
        
        # Описание
        if dessert.description:
            right_col.append(Paragraph("<b>Description:</b>", styles['subheading']))
            right_col.append(Paragraph(dessert.description, styles['normal']))
            right_col.append(Spacer(1, 0.4*cm))
        
        # Состав
        if self.settings.include_ingredients and dessert.ingredients:
            right_col.append(Paragraph("<b>Ingredients:</b>", styles['subheading']))
            right_col.append(Paragraph(dessert.ingredients, styles['normal']))
            right_col.append(Spacer(1, 0.4*cm))
        
        # КБЖУ в компактной таблице
        if self.settings.include_nutrition:
            nutrition = []
            if dessert.calories:
                nutrition.append(["Calories", f"{dessert.calories:.1f} kcal"])
            if dessert.proteins:
                nutrition.append(["Proteins", f"{dessert.proteins:.1f} g"])
            if dessert.fats:
                nutrition.append(["Fats", f"{dessert.fats:.1f} g"])
            if dessert.carbs:
                nutrition.append(["Carbs", f"{dessert.carbs:.1f} g"])
            
            if nutrition:
                right_col.append(Paragraph("<b>Nutrition (per 100g):</b>", styles['subheading']))
                right_col.append(Spacer(1, 0.2*cm))
                
                table = Table(nutrition, colWidths=[5.5*cm, 5.5*cm])
                table.setStyle(TableStyle([
                    ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#2c3e50')),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('FONTNAME', (0, 0), (-1, -1), self.font_name),
                    ('FONTSIZE', (0, 0), (-1, -1), 9),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                    ('TOPPADDING', (0, 0), (-1, -1), 6),
                    ('LEFTPADDING', (0, 0), (-1, -1), 10),
                    ('RIGHTPADDING', (0, 0), (-1, -1), 10),
                    ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e0e0e0')),
                    ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f8f9fa')),
                ]))
                right_col.append(table)
                right_col.append(Spacer(1, 0.4*cm))
        
        # Вес
        if dessert.weight:
            right_col.append(Paragraph(f"<b>Weight/Packaging:</b> {dessert.weight}", styles['normal']))
        
        # Объединяем колонки
        main_table = Table([
            [left_col, right_col]
        ], colWidths=[7*cm, 11*cm])
        main_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LEFTPADDING', (0, 0), (0, -1), 0.5*cm),
            ('RIGHTPADDING', (0, 0), (0, -1), 0.5*cm),
            ('LEFTPADDING', (1, 0), (1, -1), 0.3*cm),
            ('RIGHTPADDING', (1, 0), (1, -1), 0),
        ]))
        story.append(main_table)
        story.append(Spacer(1, 0.5*cm))
        
        # Разделительная линия
        line = Table([['']], colWidths=[18*cm], rowHeights=[0.05*cm])
        line.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#e0e0e0')),
        ]))
        story.append(line)
        story.append(Spacer(1, 0.3*cm))
        story.append(PageBreak())


class ClassicTemplate(PDFTemplate):
    """Классический шаблон - элегантный с декоративными элементами"""
    
    def create_styles(self) -> Dict[str, ParagraphStyle]:
        styles = getSampleStyleSheet()
        return {
            'title': ParagraphStyle(
                'Title',
                parent=styles['Heading1'],
                fontSize=32,
                textColor=colors.HexColor('#2c3e50'),
                spaceAfter=50,
                alignment=TA_CENTER,
                fontName=self.font_bold,
                leading=36
            ),
            'heading': ParagraphStyle(
                'Heading',
                parent=styles['Heading2'],
                fontSize=24,
                textColor=colors.HexColor('#34495e'),
                spaceAfter=20,
                spaceBefore=24,
                fontName=self.font_bold,
                leading=28,
                borderWidth=0,
                borderPadding=10
            ),
            'subheading': ParagraphStyle(
                'Subheading',
                parent=styles['Heading3'],
                fontSize=13,
                textColor=colors.HexColor('#5d6d7e'),
                spaceAfter=10,
                spaceBefore=14,
                fontName=self.font_bold,
                leading=16
            ),
            'normal': ParagraphStyle(
                'Normal',
                parent=styles['Normal'],
                fontSize=10.5,
                textColor=colors.HexColor('#34495e'),
                alignment=TA_JUSTIFY,
                fontName=self.font_name,
                leading=15,
                spaceAfter=10
            ),
            'contact': ParagraphStyle(
                'Contact',
                parent=styles['Normal'],
                fontSize=12,
                textColor=colors.HexColor('#7f8c8d'),
                alignment=TA_CENTER,
                fontName=self.font_name
            )
        }
    
    def create_title_page(self, story: List) -> None:
        styles = self.create_styles()
        story.append(Spacer(1, 9*cm))
        title_text = self.settings.company_name or "Dessert Catalog"
        story.append(Paragraph(title_text, styles['title']))
        story.append(Spacer(1, 2*cm))
        
        if self.settings.manager_contact:
            story.append(Paragraph(self.settings.manager_contact, styles['contact']))
        
        story.append(PageBreak())
    
    def create_dessert_page(self, story: List, dessert: Dessert, styles: Dict) -> None:
        # Декоративная верхняя линия
        top_line = Table([['']], colWidths=[18*cm], rowHeights=[0.15*cm])
        top_line.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#34495e')),
        ]))
        story.append(top_line)
        story.append(Spacer(1, 0.3*cm))
        
        # Двухколоночная верстка
        img = self._load_image(dessert.image_url, width=6.5*cm, height=6.5*cm)
        
        # Левая колонка - изображение без рамки
        left_col = []
        if img:
            left_col.append(Spacer(1, 0.2*cm))
            left_col.append(img)
        else:
            left_col.append(Spacer(1, 7*cm))
        
        # Правая колонка - информация
        right_col = []
        
        # Название в элегантной рамке
        title_table = Table([[dessert.title]], colWidths=[11*cm])
        title_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#34495e')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.white),
            ('FONTNAME', (0, 0), (-1, -1), self.font_bold),
            ('FONTSIZE', (0, 0), (-1, -1), 18),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
            ('TOPPADDING', (0, 0), (-1, -1), 10),
            ('LEFTPADDING', (0, 0), (-1, -1), 12),
            ('RIGHTPADDING', (0, 0), (-1, -1), 12),
        ]))
        right_col.append(title_table)
        right_col.append(Spacer(1, 0.25*cm))
        
        # Категория в рамке
        category_table = Table([[dessert.category]], colWidths=[11*cm])
        category_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#ecf0f1')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#34495e')),
            ('FONTNAME', (0, 0), (-1, -1), self.font_name),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('LEFTPADDING', (0, 0), (-1, -1), 10),
            ('RIGHTPADDING', (0, 0), (-1, -1), 10),
            ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#bdc3c7')),
        ]))
        right_col.append(category_table)
        right_col.append(Spacer(1, 0.3*cm))
        
        # Описание
        if dessert.description:
            right_col.append(Paragraph("<b>Description:</b>", styles['subheading']))
            right_col.append(Paragraph(dessert.description, styles['normal']))
            right_col.append(Spacer(1, 0.4*cm))
        
        # Состав
        if self.settings.include_ingredients and dessert.ingredients:
            right_col.append(Paragraph("<b>Ingredients:</b>", styles['subheading']))
            right_col.append(Paragraph(dessert.ingredients, styles['normal']))
            right_col.append(Spacer(1, 0.4*cm))
        
        # КБЖУ в таблице
        if self.settings.include_nutrition:
            nutrition = []
            if dessert.calories:
                nutrition.append(["Calories", f"{dessert.calories:.1f} kcal"])
            if dessert.proteins:
                nutrition.append(["Proteins", f"{dessert.proteins:.1f} g"])
            if dessert.fats:
                nutrition.append(["Fats", f"{dessert.fats:.1f} g"])
            if dessert.carbs:
                nutrition.append(["Carbs", f"{dessert.carbs:.1f} g"])
            
            if nutrition:
                right_col.append(Paragraph("<b>Nutrition (per 100g):</b>", styles['subheading']))
                right_col.append(Spacer(1, 0.2*cm))
                
                table = Table(nutrition, colWidths=[5.5*cm, 5.5*cm])
                table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#ecf0f1')),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                    ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#2c3e50')),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('FONTNAME', (0, 0), (-1, -1), self.font_name),
                    ('FONTSIZE', (0, 0), (-1, -1), 9),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                    ('TOPPADDING', (0, 0), (-1, -1), 6),
                    ('LEFTPADDING', (0, 0), (-1, -1), 10),
                    ('RIGHTPADDING', (0, 0), (-1, -1), 10),
                    ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#bdc3c7')),
                ]))
                right_col.append(table)
                right_col.append(Spacer(1, 0.4*cm))
        
        # Вес
        if dessert.weight:
            right_col.append(Paragraph(f"<b>Weight/Packaging:</b> {dessert.weight}", styles['normal']))
        
        # Объединяем колонки
        main_table = Table([
            [left_col, right_col]
        ], colWidths=[7*cm, 11*cm])
        main_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LEFTPADDING', (0, 0), (0, -1), 0.5*cm),
            ('RIGHTPADDING', (0, 0), (0, -1), 0.5*cm),
            ('LEFTPADDING', (1, 0), (1, -1), 0.3*cm),
            ('RIGHTPADDING', (1, 0), (1, -1), 0),
        ]))
        story.append(main_table)
        story.append(Spacer(1, 0.5*cm))
        
        # Декоративная нижняя линия
        bottom_line = Table([['']], colWidths=[18*cm], rowHeights=[0.1*cm])
        bottom_line.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#bdc3c7')),
        ]))
        story.append(bottom_line)
        story.append(Spacer(1, 0.3*cm))
        story.append(PageBreak())


class ModernTemplate(PDFTemplate):
    """Современный шаблон - с акцентами и цветными элементами"""
    
    def create_styles(self) -> Dict[str, ParagraphStyle]:
        styles = getSampleStyleSheet()
        accent_color = colors.HexColor('#3498db')
        dark_color = colors.HexColor('#2c3e50')
        
        return {
            'title': ParagraphStyle(
                'Title',
                parent=styles['Heading1'],
                fontSize=30,
                textColor=accent_color,
                spaceAfter=40,
                alignment=TA_CENTER,
                fontName=self.font_bold,
                leading=34
            ),
            'heading': ParagraphStyle(
                'Heading',
                parent=styles['Heading2'],
                fontSize=26,
                textColor=accent_color,
                spaceAfter=18,
                spaceBefore=22,
                fontName=self.font_bold,
                leading=30
            ),
            'subheading': ParagraphStyle(
                'Subheading',
                parent=styles['Heading3'],
                fontSize=13,
                textColor=dark_color,
                spaceAfter=8,
                spaceBefore=12,
                fontName=self.font_bold,
                leading=16
            ),
            'normal': ParagraphStyle(
                'Normal',
                parent=styles['Normal'],
                fontSize=10,
                textColor=colors.HexColor('#34495e'),
                alignment=TA_JUSTIFY,
                fontName=self.font_name,
                leading=14,
                spaceAfter=8
            ),
            'contact': ParagraphStyle(
                'Contact',
                parent=styles['Normal'],
                fontSize=11,
                textColor=colors.HexColor('#7f8c8d'),
                alignment=TA_CENTER,
                fontName=self.font_name
            )
        }
    
    def create_title_page(self, story: List) -> None:
        styles = self.create_styles()
        accent_color = colors.HexColor('#3498db')
        
        # Цветная полоса
        bar_table = Table([['']], colWidths=[18*cm], rowHeights=[0.5*cm])
        bar_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), accent_color),
        ]))
        story.append(bar_table)
        story.append(Spacer(1, 8.5*cm))
        
        title_text = self.settings.company_name or "Dessert Catalog"
        story.append(Paragraph(title_text, styles['title']))
        story.append(Spacer(1, 1.5*cm))
        
        if self.settings.manager_contact:
            story.append(Paragraph(self.settings.manager_contact, styles['contact']))
        
        story.append(PageBreak())
    
    def create_dessert_page(self, story: List, dessert: Dessert, styles: Dict) -> None:
        accent_color = colors.HexColor('#3498db')
        
        # Двухколоночная верстка
        img = self._load_image(dessert.image_url, width=6.5*cm, height=6.5*cm)
        
        # Левая колонка - изображение без рамки
        left_col = []
        if img:
            left_col.append(Spacer(1, 0.2*cm))
            left_col.append(img)
        else:
            left_col.append(Spacer(1, 7*cm))
        
        # Правая колонка - информация
        right_col = []
        
        # Цветная полоса с названием
        title_bar = Table([[dessert.title]], colWidths=[11*cm])
        title_bar.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), accent_color),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), self.font_bold),
            ('FONTSIZE', (0, 0), (-1, -1), 18),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
            ('TOPPADDING', (0, 0), (-1, -1), 10),
            ('LEFTPADDING', (0, 0), (-1, -1), 12),
            ('RIGHTPADDING', (0, 0), (-1, -1), 12),
        ]))
        right_col.append(title_bar)
        right_col.append(Spacer(1, 0.25*cm))
        
        # Категория
        category_table = Table([[dessert.category]], colWidths=[11*cm])
        category_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#ebf5fb')),
            ('TEXTCOLOR', (0, 0), (-1, -1), accent_color),
            ('FONTNAME', (0, 0), (-1, -1), self.font_name),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('LEFTPADDING', (0, 0), (-1, -1), 10),
            ('RIGHTPADDING', (0, 0), (-1, -1), 10),
            ('BOX', (0, 0), (-1, -1), 1, accent_color),
        ]))
        right_col.append(category_table)
        right_col.append(Spacer(1, 0.3*cm))
        
        # Описание
        if dessert.description:
            right_col.append(Paragraph("<b>Description:</b>", styles['subheading']))
            right_col.append(Paragraph(dessert.description, styles['normal']))
            right_col.append(Spacer(1, 0.4*cm))
        
        # Состав
        if self.settings.include_ingredients and dessert.ingredients:
            right_col.append(Paragraph("<b>Ingredients:</b>", styles['subheading']))
            right_col.append(Paragraph(dessert.ingredients, styles['normal']))
            right_col.append(Spacer(1, 0.4*cm))
        
        # КБЖУ с цветными акцентами
        if self.settings.include_nutrition:
            nutrition = []
            if dessert.calories:
                nutrition.append(["Calories", f"{dessert.calories:.1f} kcal"])
            if dessert.proteins:
                nutrition.append(["Proteins", f"{dessert.proteins:.1f} g"])
            if dessert.fats:
                nutrition.append(["Fats", f"{dessert.fats:.1f} g"])
            if dessert.carbs:
                nutrition.append(["Carbs", f"{dessert.carbs:.1f} g"])
            
            if nutrition:
                right_col.append(Paragraph("<b>Nutrition (per 100g):</b>", styles['subheading']))
                right_col.append(Spacer(1, 0.2*cm))
                
                table = Table(nutrition, colWidths=[5.5*cm, 5.5*cm])
                table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), accent_color),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                    ('TEXTCOLOR', (0, 1), (-1, -1), colors.HexColor('#2c3e50')),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('FONTNAME', (0, 0), (-1, -1), self.font_name),
                    ('FONTSIZE', (0, 0), (-1, -1), 9),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                    ('TOPPADDING', (0, 0), (-1, -1), 6),
                    ('LEFTPADDING', (0, 0), (-1, -1), 10),
                    ('RIGHTPADDING', (0, 0), (-1, -1), 10),
                    ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e0e0e0')),
                ]))
                right_col.append(table)
                right_col.append(Spacer(1, 0.4*cm))
        
        # Вес
        if dessert.weight:
            right_col.append(Paragraph(f"<b>Weight/Packaging:</b> {dessert.weight}", styles['normal']))
        
        # Объединяем колонки
        main_table = Table([
            [left_col, right_col]
        ], colWidths=[7*cm, 11*cm])
        main_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LEFTPADDING', (0, 0), (0, -1), 0.5*cm),
            ('RIGHTPADDING', (0, 0), (0, -1), 0.5*cm),
            ('LEFTPADDING', (1, 0), (1, -1), 0.3*cm),
            ('RIGHTPADDING', (1, 0), (1, -1), 0),
        ]))
        story.append(main_table)
        story.append(Spacer(1, 0.5*cm))
        
        # Цветная разделительная линия
        divider = Table([['']], colWidths=[18*cm], rowHeights=[0.1*cm])
        divider.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), accent_color),
        ]))
        story.append(divider)
        story.append(Spacer(1, 0.3*cm))
        story.append(PageBreak())


class LuxuryTemplate(PDFTemplate):
    """Премиум шаблон - роскошный с золотыми акцентами"""
    
    def create_styles(self) -> Dict[str, ParagraphStyle]:
        styles = getSampleStyleSheet()
        gold_color = colors.HexColor('#d4af37')
        dark_color = colors.HexColor('#1a1a1a')
        
        return {
            'title': ParagraphStyle(
                'Title',
                parent=styles['Heading1'],
                fontSize=34,
                textColor=dark_color,
                spaceAfter=50,
                alignment=TA_CENTER,
                fontName=self.font_bold,
                leading=38
            ),
            'heading': ParagraphStyle(
                'Heading',
                parent=styles['Heading2'],
                fontSize=28,
                textColor=dark_color,
                spaceAfter=20,
                spaceBefore=24,
                fontName=self.font_bold,
                leading=32
            ),
            'subheading': ParagraphStyle(
                'Subheading',
                parent=styles['Heading3'],
                fontSize=13,
                textColor=gold_color,
                spaceAfter=10,
                spaceBefore=14,
                fontName=self.font_bold,
                leading=16
            ),
            'normal': ParagraphStyle(
                'Normal',
                parent=styles['Normal'],
                fontSize=10.5,
                textColor=colors.HexColor('#2c2c2c'),
                alignment=TA_JUSTIFY,
                fontName=self.font_name,
                leading=15,
                spaceAfter=10
            ),
            'contact': ParagraphStyle(
                'Contact',
                parent=styles['Normal'],
                fontSize=12,
                textColor=colors.HexColor('#666666'),
                alignment=TA_CENTER,
                fontName=self.font_name
            )
        }
    
    def create_title_page(self, story: List) -> None:
        styles = self.create_styles()
        gold_color = colors.HexColor('#d4af37')
        
        # Декоративная золотая линия
        line_table = Table([['']], colWidths=[18*cm], rowHeights=[0.3*cm])
        line_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), gold_color),
        ]))
        story.append(Spacer(1, 8*cm))
        story.append(line_table)
        story.append(Spacer(1, 1*cm))
        
        title_text = self.settings.company_name or "Dessert Catalog"
        story.append(Paragraph(title_text, styles['title']))
        story.append(Spacer(1, 1*cm))
        story.append(line_table)
        story.append(Spacer(1, 2*cm))
        
        if self.settings.manager_contact:
            story.append(Paragraph(self.settings.manager_contact, styles['contact']))
        
        story.append(PageBreak())
    
    def create_dessert_page(self, story: List, dessert: Dessert, styles: Dict) -> None:
        gold_color = colors.HexColor('#d4af37')
        
        # Золотая декоративная верхняя линия
        top_line = Table([['']], colWidths=[18*cm], rowHeights=[0.2*cm])
        top_line.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), gold_color),
        ]))
        story.append(top_line)
        story.append(Spacer(1, 0.3*cm))
        
        # Двухколоночная верстка
        img = self._load_image(dessert.image_url, width=6.5*cm, height=6.5*cm)
        
        # Левая колонка - изображение без рамки
        left_col = []
        if img:
            left_col.append(Spacer(1, 0.2*cm))
            left_col.append(img)
        else:
            left_col.append(Spacer(1, 7*cm))
        
        # Правая колонка - информация
        right_col = []
        
        # Название
        title_table = Table([[dessert.title]], colWidths=[11*cm])
        title_table.setStyle(TableStyle([
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#1a1a1a')),
            ('FONTNAME', (0, 0), (-1, -1), self.font_bold),
            ('FONTSIZE', (0, 0), (-1, -1), 20),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('LINEBELOW', (0, 0), (-1, -1), 2, gold_color),
        ]))
        right_col.append(title_table)
        right_col.append(Spacer(1, 0.25*cm))
        
        # Категория с золотым акцентом
        category_table = Table([[dessert.category]], colWidths=[11*cm])
        category_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#fffef7')),
            ('TEXTCOLOR', (0, 0), (-1, -1), gold_color),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), self.font_bold),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('LEFTPADDING', (0, 0), (-1, -1), 12),
            ('RIGHTPADDING', (0, 0), (-1, -1), 12),
            ('BOX', (0, 0), (-1, -1), 2, gold_color),
        ]))
        right_col.append(category_table)
        right_col.append(Spacer(1, 0.3*cm))
        
        # Описание
        if dessert.description:
            right_col.append(Paragraph("<b>Description:</b>", styles['subheading']))
            right_col.append(Paragraph(dessert.description, styles['normal']))
            right_col.append(Spacer(1, 0.4*cm))
        
        # Состав
        if self.settings.include_ingredients and dessert.ingredients:
            right_col.append(Paragraph("<b>Ingredients:</b>", styles['subheading']))
            right_col.append(Paragraph(dessert.ingredients, styles['normal']))
            right_col.append(Spacer(1, 0.4*cm))
        
        # КБЖУ в премиум стиле
        if self.settings.include_nutrition:
            nutrition = []
            if dessert.calories:
                nutrition.append(["Calories", f"{dessert.calories:.1f} kcal"])
            if dessert.proteins:
                nutrition.append(["Proteins", f"{dessert.proteins:.1f} g"])
            if dessert.fats:
                nutrition.append(["Fats", f"{dessert.fats:.1f} g"])
            if dessert.carbs:
                nutrition.append(["Carbs", f"{dessert.carbs:.1f} g"])
            
            if nutrition:
                right_col.append(Paragraph("<b>Nutrition (per 100g):</b>", styles['subheading']))
                right_col.append(Spacer(1, 0.2*cm))
                
                table = Table(nutrition, colWidths=[5.5*cm, 5.5*cm])
                table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#fffef7')),
                    ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#2c2c2c')),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('FONTNAME', (0, 0), (-1, -1), self.font_name),
                    ('FONTSIZE', (0, 0), (-1, -1), 9),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                    ('TOPPADDING', (0, 0), (-1, -1), 6),
                    ('LEFTPADDING', (0, 0), (-1, -1), 10),
                    ('RIGHTPADDING', (0, 0), (-1, -1), 10),
                    ('GRID', (0, 0), (-1, -1), 0.5, gold_color),
                ]))
                right_col.append(table)
                right_col.append(Spacer(1, 0.4*cm))
        
        # Вес
        if dessert.weight:
            right_col.append(Paragraph(f"<b>Weight/Packaging:</b> {dessert.weight}", styles['normal']))
        
        # Объединяем колонки
        main_table = Table([
            [left_col, right_col]
        ], colWidths=[7*cm, 11*cm])
        main_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LEFTPADDING', (0, 0), (0, -1), 0.5*cm),
            ('RIGHTPADDING', (0, 0), (0, -1), 0.5*cm),
            ('LEFTPADDING', (1, 0), (1, -1), 0.3*cm),
            ('RIGHTPADDING', (1, 0), (1, -1), 0),
        ]))
        story.append(main_table)
        story.append(Spacer(1, 0.5*cm))
        
        # Золотая декоративная нижняя линия
        bottom_line = Table([['']], colWidths=[18*cm], rowHeights=[0.15*cm])
        bottom_line.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), gold_color),
        ]))
        story.append(bottom_line)
        story.append(Spacer(1, 0.3*cm))
        story.append(PageBreak())


# Реестр шаблонов
TEMPLATES = {
    'minimal': MinimalTemplate,
    'classic': ClassicTemplate,
    'modern': ModernTemplate,
    'luxury': LuxuryTemplate,
}

