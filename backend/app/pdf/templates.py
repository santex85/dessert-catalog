"""
Шаблоны дизайна для PDF каталога
"""
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm, mm
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, 
    PageBreak, KeepTogether, Image, Frame, PageTemplate, BaseDocTemplate
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

# --- COLORS & PALETTES ---
class Colors:
    # Neutral
    DARK_GREY = colors.HexColor('#1A1A1A')
    MID_GREY = colors.HexColor('#4A4A4A')
    LIGHT_GREY = colors.HexColor('#999999')
    OFF_WHITE = colors.HexColor('#F9F9F9')
    WHITE = colors.white
    
    # Accents
    GOLD = colors.HexColor('#C5A059')
    DEEP_BLUE = colors.HexColor('#0F172A')
    SOFT_BLUE = colors.HexColor('#E2E8F0')
    SAGE = colors.HexColor('#84A98C')
    TERRACOTTA = colors.HexColor('#E07A5F')

# --- FONT MANAGEMENT ---
def register_custom_fonts():
    """Регистрация кастомных шрифтов с fallback на системные"""
    fonts_registered = {'main': 'Helvetica', 'main_bold': 'Helvetica-Bold', 'serif': 'Times-Roman', 'serif_bold': 'Times-Bold'}
    
    # Регистрация кириллического шрифта (из старого кода)
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
    
    # Если есть кириллический шрифт, используем его
    if cyrillic_font:
        fonts_registered['main'] = cyrillic_font
        fonts_registered['main_bold'] = cyrillic_font
    
    # Пример регистрации кастомных шрифтов (раскомментируйте, если есть файлы)
    # font_dir = "./fonts" 
    # try:
    #     pdfmetrics.registerFont(TTFont('Montserrat', f'{font_dir}/Montserrat-Regular.ttf'))
    #     pdfmetrics.registerFont(TTFont('Montserrat-Bold', f'{font_dir}/Montserrat-Bold.ttf'))
    #     pdfmetrics.registerFont(TTFont('Playfair', f'{font_dir}/PlayfairDisplay-Regular.ttf'))
    #     pdfmetrics.registerFont(TTFont('Playfair-Bold', f'{font_dir}/PlayfairDisplay-Bold.ttf'))
    #     fonts_registered = {'main': 'Montserrat', 'main_bold': 'Montserrat-Bold', 'serif': 'Playfair', 'serif_bold': 'Playfair-Bold'}
    # except:
    #     pass
    
    return fonts_registered

FONTS = register_custom_fonts()

# --- BASE CLASS ---
class PDFTemplate:
    """Базовый класс с улучшенной загрузкой изображений и утилитами"""
    
    def __init__(self, settings: PDFExportSettings):
        self.settings = settings
        self.fonts = FONTS
    
    def _load_image(self, image_url: Optional[str], width: float = 6*cm, height: float = 6*cm) -> Optional[Image]:
        """
        Улучшенная загрузка изображений.
        Возвращает Image объект ReportLab.
        """
        if not image_url:
            return None
        
        try:
            img_data = None
            
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
                    img_data = buffer
            
            # Если это полный URL (http:// или https://)
            elif image_url.startswith(('http://', 'https://')):
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
                img_data = buffer
            
            if not img_data:
                # Для теста генерируем серый квадрат, если картинки нет
                img = PILImage.new('RGB', (400, 400), color='#e0e0e0')
                buffer = BytesIO()
                img.save(buffer, format='JPEG')
                buffer.seek(0)
                img_data = buffer
            
            # ReportLab Image
            rl_image = Image(img_data, width=width, height=height, kind='proportional')
            rl_image.hAlign = 'CENTER'
            rl_image.vAlign = 'CENTER'
            
            return rl_image
        except Exception as e:
            print(f"Image load error: {e}")
            return None
    
    def get_nutrition_table(self, dessert: Dessert, styles: Dict, text_color=Colors.MID_GREY) -> Table:
        """Создает стильную горизонтальную таблицу КБЖУ"""
        if not self.settings.include_nutrition:
            return Spacer(1, 0)
        
        data = []
        labels = ["KCAL", "PROTEIN", "FATS", "CARBS"]
        values = [
            f"{dessert.calories:.0f}" if dessert.calories else "0", 
            f"{dessert.proteins:.1f}g" if dessert.proteins else "0g", 
            f"{dessert.fats:.1f}g" if dessert.fats else "0g", 
            f"{dessert.carbs:.1f}g" if dessert.carbs else "0g"
        ]
        
        # Строим таблицу: Labels сверху, Values снизу
        cell_style = ParagraphStyle('NutriCell', fontName=self.fonts['main'], fontSize=7, textColor=colors.HexColor('#999999'), alignment=TA_CENTER)
        val_style = ParagraphStyle('NutriVal', fontName=self.fonts['main_bold'], fontSize=10, textColor=text_color, alignment=TA_CENTER)
        
        row1 = [Paragraph(l, cell_style) for l in labels]
        row2 = [Paragraph(v, val_style) for v in values]
        
        t = Table([row1, row2], colWidths=[2.5*cm]*4)
        t.setStyle(TableStyle([
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('TOPPADDING', (0,0), (-1,-1), 2),
            ('BOTTOMPADDING', (0,0), (-1,-1), 2),
        ]))
        return t
    
    def create_styles(self) -> Dict[str, ParagraphStyle]:
        """Создает стили для шаблона. Должен быть переопределен в подклассах."""
        raise NotImplementedError
    
    def create_title_page(self, story: List) -> None:
        """Создает титульный лист. Должен быть переопределен в подклассах."""
        raise NotImplementedError
    
    def create_dessert_page(self, story: List, dessert: Dessert, styles: Dict) -> None:
        """Создает страницу для десерта. Должен быть переопределен в подклассах."""
        raise NotImplementedError


# --- TEMPLATE 1: MINIMAL (Gallery Style) ---
class MinimalTemplate(PDFTemplate):
    """
    Стиль: Чистый, много воздуха.
    Акцент: Огромное фото по центру, типографика Swiss Style.
    """
    def create_styles(self) -> Dict[str, ParagraphStyle]:
        return {
            'title': ParagraphStyle('Title', fontName=self.fonts['main_bold'], fontSize=18, textColor=Colors.DARK_GREY, alignment=TA_CENTER, spaceAfter=20),
            'product_title': ParagraphStyle('ProdTitle', fontName=self.fonts['main_bold'], fontSize=24, textColor=Colors.DARK_GREY, alignment=TA_CENTER, spaceAfter=10, leading=28),
            'category': ParagraphStyle('Cat', fontName=self.fonts['main'], fontSize=9, textColor=Colors.LIGHT_GREY, alignment=TA_CENTER, spaceAfter=20),
            'desc': ParagraphStyle('Desc', fontName=self.fonts['main'], fontSize=10, textColor=Colors.MID_GREY, alignment=TA_CENTER, leading=16, spaceAfter=15),
            'ingredients': ParagraphStyle('Ingr', fontName=self.fonts['main'], fontSize=8, textColor=Colors.LIGHT_GREY, alignment=TA_CENTER, leading=12),
            'footer': ParagraphStyle('Footer', fontName=self.fonts['main'], fontSize=8, textColor=Colors.LIGHT_GREY, alignment=TA_CENTER),
        }
    
    def create_title_page(self, story: List) -> None:
        s = self.create_styles()
        
        # Логотип компании (если есть)
        if self.settings.logo_url:
            logo = self._load_image(self.settings.logo_url, width=6*cm, height=6*cm)
            if logo:
                story.append(Spacer(1, 3*cm))
                story.append(logo)
                story.append(Spacer(1, 1*cm))
            else:
                story.append(Spacer(1, 8*cm))
        else:
            story.append(Spacer(1, 8*cm))
        
        company_name = self.settings.company_name or "Dessert Catalog"
        story.append(Paragraph(company_name.upper(), s['title']))
        story.append(Spacer(1, 0.5*cm))
        story.append(Paragraph("CATALOG 2025", s['category']))
        story.append(PageBreak())
    
    def create_dessert_page(self, story: List, dessert: Dessert, styles: Dict) -> None:
        s = styles or self.create_styles()
        
        # 1. Большое изображение
        img = self._load_image(dessert.image_url, width=16*cm, height=12*cm)  # Широкий формат
        if img:
            tbl_img = Table([[img]], colWidths=[19*cm])
            tbl_img.setStyle(TableStyle([('ALIGN', (0,0), (-1,-1), 'CENTER'), ('VALIGN', (0,0), (-1,-1), 'MIDDLE')]))
            story.append(tbl_img)
        else:
            story.append(Spacer(1, 12*cm))
        
        story.append(Spacer(1, 1.5*cm))
        
        # 2. Заголовок и Категория
        # Отображаем категории через запятую или разделитель
        categories_text = ', '.join([cat.strip() for cat in dessert.category.split(',')])
        story.append(Paragraph(categories_text, s['category']))
        story.append(Paragraph(dessert.title, s['product_title']))
        
        # 3. Описание (ограничиваем ширину текста для читаемости)
        if dessert.description:
            desc_para = Paragraph(dessert.description, s['desc'])
            t_desc = Table([[desc_para]], colWidths=[12*cm]) 
            t_desc.setStyle(TableStyle([('ALIGN', (0,0), (-1,-1), 'CENTER')]))
            story.append(t_desc)
            story.append(Spacer(1, 1*cm))
        
        # 4. КБЖУ
        nutri_table = self.get_nutrition_table(dessert, s)
        story.append(nutri_table)
        story.append(Spacer(1, 1*cm))
        
        # 5. Состав (мелким текстом внизу)
        if self.settings.include_ingredients and dessert.ingredients:
            story.append(Paragraph(f"Ingredients: {dessert.ingredients}", s['ingredients']))
        
        # 6. Стоимость (если есть)
        if dessert.price is not None:
            price_style = ParagraphStyle('Price', fontName=self.fonts['main_bold'], fontSize=16, textColor=Colors.DARK_GREY, alignment=TA_CENTER, spaceBefore=10)
            story.append(Paragraph(f"{dessert.price:.2f} THB", price_style))
        
        story.append(PageBreak())


# --- TEMPLATE 2: MODERN (Magazine/Editorial Style) ---
class ModernTemplate(PDFTemplate):
    """
    Стиль: Эдиториал.
    Акцент: Асимметрия. Картинка слева, контент справа на цветной подложке.
    """
    def create_styles(self) -> Dict[str, ParagraphStyle]:
        return {
            'header': ParagraphStyle('Header', fontName=self.fonts['main_bold'], fontSize=12, textColor=Colors.DEEP_BLUE),
            'product_title': ParagraphStyle('ProdTitle', fontName=self.fonts['serif_bold'], fontSize=26, textColor=Colors.DEEP_BLUE, spaceAfter=8, leading=28),
            'category_badge': ParagraphStyle('Badge', fontName=self.fonts['main_bold'], fontSize=8, textColor=colors.white, backColor=Colors.DEEP_BLUE, alignment=TA_CENTER),
            'price': ParagraphStyle('Price', fontName=self.fonts['main_bold'], fontSize=14, textColor=Colors.TERRACOTTA, alignment=TA_RIGHT),
            'desc_header': ParagraphStyle('DescHead', fontName=self.fonts['main_bold'], fontSize=10, textColor=Colors.MID_GREY, spaceBefore=10),
            'desc': ParagraphStyle('Desc', fontName=self.fonts['serif'], fontSize=11, textColor=Colors.DARK_GREY, leading=15),
            'meta': ParagraphStyle('Meta', fontName=self.fonts['main'], fontSize=9, textColor=Colors.LIGHT_GREY),
        }
    
    def create_title_page(self, story: List) -> None:
        # Простая титулка для Modern
        # Логотип компании (если есть)
        if self.settings.logo_url:
            logo = self._load_image(self.settings.logo_url, width=6*cm, height=6*cm)
            if logo:
                story.append(Spacer(1, 4*cm))
                story.append(logo)
                story.append(Spacer(1, 1*cm))
            else:
                story.append(Spacer(1, 10*cm))
        else:
            story.append(Spacer(1, 10*cm))
        
        company_name = self.settings.company_name or "Dessert Catalog"
        story.append(Paragraph(company_name, 
            ParagraphStyle('T', fontName=self.fonts['serif_bold'], fontSize=40, alignment=TA_CENTER, textColor=Colors.DEEP_BLUE)))
        story.append(PageBreak())
    
    def create_dessert_page(self, story: List, dessert: Dessert, styles: Dict) -> None:
        s = styles or self.create_styles()
        
        # Верстка: Одна большая таблица на всю страницу. 
        # Левая колонка (40%) - Фото, Правая (60%) - Контент.
        
        # Фото
        img = self._load_image(dessert.image_url, width=8*cm, height=10*cm)
        
        # Правая часть
        content_cells = []
        
        # Верхняя строка: Категория (как бейдж) и Цена (если есть)
        # Отображаем все категории через запятую
        categories_text = ', '.join([cat.strip().upper() for cat in dessert.category.split(',')])
        cat_para = Paragraph(f"&nbsp; {categories_text} &nbsp;", s['category_badge'])
        # Цена
        price_text = ""
        if dessert.price is not None:
            price_text = f"{dessert.price:.2f} THB"
        
        if price_text:
            price_para = Paragraph(price_text, s['price'])
            top_row = Table([[cat_para, price_para]], colWidths=[None, None])
            top_row.setStyle(TableStyle([('ALIGN', (0,0), (0,0), 'LEFT'), ('ALIGN', (-1,-1), (-1,-1), 'RIGHT')]))
        else:
            top_row = Table([[cat_para]], colWidths=[None])
            top_row.setStyle(TableStyle([('ALIGN', (0,0), (0,0), 'LEFT')]))
        
        content_cells.append(top_row)
        content_cells.append(Spacer(1, 0.5*cm))
        
        # Заголовок
        content_cells.append(Paragraph(dessert.title, s['product_title']))
        content_cells.append(Spacer(1, 0.5*cm))
        
        # Описание
        if dessert.description:
            content_cells.append(Paragraph(dessert.description, s['desc']))
            content_cells.append(Spacer(1, 0.8*cm))
        
        # КБЖУ (Кастомный стиль)
        nutri = self.get_nutrition_table(dessert, s, text_color=Colors.DEEP_BLUE)
        nutri.hAlign = 'LEFT'
        content_cells.append(nutri)
        content_cells.append(Spacer(1, 0.8*cm))
        
        # Состав и Вес
        if dessert.weight:
            content_cells.append(Paragraph(f"Weight: {dessert.weight}", s['meta']))
        if self.settings.include_ingredients and dessert.ingredients:
            content_cells.append(Paragraph(f"Contains: {dessert.ingredients}", s['meta']))
        
        # Сборка главной таблицы
        right_col_content = content_cells
        
        main_table = Table(
            [[img, right_col_content]], 
            colWidths=[8.5*cm, 10.5*cm]
        )
        main_table.setStyle(TableStyle([
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ('LEFTPADDING', (0,0), (0,0), 0),
            ('RIGHTPADDING', (0,0), (0,0), 10),
            ('LEFTPADDING', (1,0), (1,0), 15),
            # Вертикальная линия разделитель
            ('LINEBEFORE', (1,0), (1,0), 0.5, Colors.SOFT_BLUE),
        ]))
        
        story.append(Spacer(1, 2*cm))
        story.append(main_table)
        story.append(PageBreak())


# --- TEMPLATE 3: LUXURY (Menu Style) ---
class LuxuryTemplate(PDFTemplate):
    """
    Стиль: Ресторанное меню.
    Акцент: Шрифты с засечками (Serif), золотые линии, строгая симметрия.
    """
    def create_styles(self) -> Dict[str, ParagraphStyle]:
        return {
            'title': ParagraphStyle('Title', fontName=self.fonts['serif'], fontSize=22, textColor=Colors.DARK_GREY, alignment=TA_CENTER, spaceAfter=5),
            'category': ParagraphStyle('Cat', fontName=self.fonts['main'], fontSize=8, textColor=Colors.GOLD, alignment=TA_CENTER),
            'desc': ParagraphStyle('Desc', fontName=self.fonts['serif'], fontSize=11, textColor=Colors.MID_GREY, alignment=TA_CENTER, leading=14, leftIndent=1*cm, rightIndent=1*cm),
            'meta': ParagraphStyle('Meta', fontName=self.fonts['main'], fontSize=8, textColor=Colors.LIGHT_GREY, alignment=TA_CENTER),
        }
    
    def create_title_page(self, story: List) -> None:
        s = self.create_styles()
        story.append(Spacer(1, 8*cm))
        company_name = self.settings.company_name or "Dessert Catalog"
        # Золотая рамка вокруг названия
        title = Paragraph(company_name, 
                          ParagraphStyle('T', fontName=self.fonts['serif'], fontSize=32, alignment=TA_CENTER, textColor=Colors.DARK_GREY))
        
        t = Table([[title]], colWidths=[14*cm])
        t.setStyle(TableStyle([
            ('BOX', (0,0), (-1,-1), 1, Colors.GOLD),
            ('TOPPADDING', (0,0), (-1,-1), 20),
            ('BOTTOMPADDING', (0,0), (-1,-1), 20),
        ]))
        t.hAlign = 'CENTER'
        story.append(t)
        story.append(PageBreak())
    
    def create_dessert_page(self, story: List, dessert: Dessert, styles: Dict) -> None:
        s = styles or self.create_styles()
        
        elements = []
        
        # 1. Категория
        categories_text = ', '.join([cat.strip() for cat in dessert.category.split(',')])
        elements.append(Paragraph(categories_text, s['category']))
        elements.append(Spacer(1, 0.2*cm))
        
        # 2. Заголовок
        elements.append(Paragraph(dessert.title, s['title']))
        
        # Декоративная линия
        line = Table([['']], colWidths=[2*cm], rowHeights=[1])
        line.setStyle(TableStyle([('LINEBELOW', (0,0), (-1,-1), 0.5, Colors.GOLD)]))
        elements.append(Spacer(1, 0.3*cm))
        elements.append(line)
        elements.append(Spacer(1, 0.8*cm))
        
        # 3. Изображение (Квадратное или Портретное)
        img = self._load_image(dessert.image_url, width=10*cm, height=10*cm)
        if img:
            elements.append(img)
            elements.append(Spacer(1, 1*cm))
        
        # 4. Описание (Италик для элегантности)
        if dessert.description:
            desc_style = ParagraphStyle('ItalicDesc', parent=s['desc'], fontName='Times-Italic')
            elements.append(Paragraph(dessert.description, desc_style))
            elements.append(Spacer(1, 0.8*cm))
        
        # 5. Стоимость (если есть)
        if dessert.price is not None:
            price_style = ParagraphStyle('Price', fontName=self.fonts['serif_bold'], fontSize=18, textColor=Colors.GOLD, alignment=TA_CENTER, spaceAfter=10)
            elements.append(Paragraph(f"{dessert.price:.2f} THB", price_style))
        
        # 6. КБЖУ (Очень минималистично, одной строкой)
        if self.settings.include_nutrition:
            if dessert.calories is not None:
                calories_val = f"{dessert.calories:.0f}" if dessert.calories else "0"
                proteins_val = f"{dessert.proteins:.1f}" if dessert.proteins else "0"
                fats_val = f"{dessert.fats:.1f}" if dessert.fats else "0"
                carbs_val = f"{dessert.carbs:.1f}" if dessert.carbs else "0"
                nutri_text = f"{calories_val} kcal  |  P: {proteins_val}  F: {fats_val}  C: {carbs_val}"
                elements.append(Paragraph(nutri_text, s['meta']))
        
        # Оборачиваем всё в таблицу с золотой рамкой
        container = Table([[elements]], colWidths=[16*cm])
        container.setStyle(TableStyle([
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('LEFTPADDING', (0,0), (-1,-1), 1*cm),
            ('RIGHTPADDING', (0,0), (-1,-1), 1*cm),
            ('TOPPADDING', (0,0), (-1,-1), 1*cm),
            ('BOTTOMPADDING', (0,0), (-1,-1), 1*cm),
            # Тонкая рамка
            ('BOX', (0,0), (-1,-1), 0.5, Colors.GOLD),
        ]))
        
        story.append(Spacer(1, 1*cm))  # Отступ сверху страницы
        story.append(container)
        story.append(PageBreak())


# --- TEMPLATE 4: CLASSIC (Legacy) ---
class ClassicTemplate(PDFTemplate):
    """Классический шаблон - элегантный с декоративными элементами (сохранен для совместимости)"""
    
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
                fontName=self.fonts['main_bold'],
                leading=36
            ),
            'heading': ParagraphStyle(
                'Heading',
                parent=styles['Heading2'],
                fontSize=24,
                textColor=colors.HexColor('#34495e'),
                spaceAfter=20,
                spaceBefore=24,
                fontName=self.fonts['main_bold'],
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
                fontName=self.fonts['main_bold'],
                leading=16
            ),
            'normal': ParagraphStyle(
                'Normal',
                parent=styles['Normal'],
                fontSize=10.5,
                textColor=colors.HexColor('#34495e'),
                alignment=TA_JUSTIFY,
                fontName=self.fonts['main'],
                leading=15,
                spaceAfter=10
            ),
            'contact': ParagraphStyle(
                'Contact',
                parent=styles['Normal'],
                fontSize=12,
                textColor=colors.HexColor('#7f8c8d'),
                alignment=TA_CENTER,
                fontName=self.fonts['main']
            )
        }
    
    def create_title_page(self, story: List) -> None:
        styles = self.create_styles()
        
        # Логотип компании (если есть)
        if self.settings.logo_url:
            logo = self._load_image(self.settings.logo_url, width=5*cm, height=5*cm)
            if logo:
                story.append(Spacer(1, 4*cm))
                story.append(logo)
                story.append(Spacer(1, 1*cm))
            else:
                story.append(Spacer(1, 9*cm))
        else:
            story.append(Spacer(1, 9*cm))
        
        title_text = self.settings.company_name or "Dessert Catalog"
        story.append(Paragraph(title_text, styles['title']))
        story.append(Spacer(1, 2*cm))
        
        if self.settings.manager_contact:
            story.append(Paragraph(self.settings.manager_contact, styles['contact']))
        
        story.append(PageBreak())
    
    def create_dessert_page(self, story: List, dessert: Dessert, styles: Dict) -> None:
        s = styles or self.create_styles()
        
        # Декоративная верхняя линия
        top_line = Table([['']], colWidths=[18*cm], rowHeights=[0.15*cm])
        top_line.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#34495e')),
        ]))
        story.append(top_line)
        story.append(Spacer(1, 0.3*cm))
        
        # Двухколоночная верстка
        img = self._load_image(dessert.image_url, width=6.5*cm, height=6.5*cm)
        
        # Левая колонка - изображение
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
            ('FONTNAME', (0, 0), (-1, -1), self.fonts['main_bold']),
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
        categories_text = ', '.join([cat.strip() for cat in dessert.category.split(',')])
        category_table = Table([[categories_text]], colWidths=[11*cm])
        category_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#ecf0f1')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#34495e')),
            ('FONTNAME', (0, 0), (-1, -1), self.fonts['main']),
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
            right_col.append(Paragraph("<b>Description:</b>", s['subheading']))
            right_col.append(Paragraph(dessert.description, s['normal']))
            right_col.append(Spacer(1, 0.4*cm))
        
        # Состав
        if self.settings.include_ingredients and dessert.ingredients:
            right_col.append(Paragraph("<b>Ingredients:</b>", s['subheading']))
            right_col.append(Paragraph(dessert.ingredients, s['normal']))
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
                right_col.append(Paragraph("<b>Nutrition (per 100g):</b>", s['subheading']))
                right_col.append(Spacer(1, 0.2*cm))
                
                table = Table(nutrition, colWidths=[5.5*cm, 5.5*cm])
                table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#ecf0f1')),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                    ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#2c3e50')),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('FONTNAME', (0, 0), (-1, -1), self.fonts['main']),
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
            right_col.append(Paragraph(f"<b>Weight/Packaging:</b> {dessert.weight}", s['normal']))
        
        # Стоимость
        if dessert.price is not None:
            right_col.append(Spacer(1, 0.2*cm))
            price_style = ParagraphStyle('Price', parent=s['heading'], fontSize=20, textColor=colors.HexColor('#27ae60'), spaceAfter=10)
            right_col.append(Paragraph(f"<b>Price:</b> {dessert.price:.2f} THB", price_style))
        
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


# --- REGISTRY ---
TEMPLATES = {
    'minimal': MinimalTemplate,
    'classic': ClassicTemplate,
    'modern': ModernTemplate,
    'luxury': LuxuryTemplate,
}
