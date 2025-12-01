from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models import Dessert, User
from app.schemas import PDFExportSettings
from app.pdf.generator import generate_pdf
from app.auth import get_current_user

router = APIRouter(prefix="/api/pdf", tags=["pdf"])


@router.post("/export")
def export_pdf(
    settings: PDFExportSettings,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Generate and download PDF catalog (requires authentication)"""
    if not settings.dessert_ids:
        raise HTTPException(status_code=400, detail="No desserts selected")
    
    # Limit number of desserts to prevent abuse
    if len(settings.dessert_ids) > 1000:
        raise HTTPException(status_code=400, detail="Too many desserts selected (max 1000)")
    
    # Get selected desserts
    desserts = db.query(Dessert).filter(
        Dessert.id.in_(settings.dessert_ids),
        Dessert.is_active == True
    ).all()
    
    if not desserts:
        raise HTTPException(status_code=404, detail="Desserts not found")
    
    # Если данные не указаны в настройках, используем данные из профиля пользователя
    if not settings.company_name and current_user.company_name:
        settings.company_name = current_user.company_name
    if not settings.manager_contact and current_user.manager_contact:
        settings.manager_contact = current_user.manager_contact
    if not settings.logo_url and current_user.logo_url:
        settings.logo_url = current_user.logo_url
    if not settings.catalog_description and current_user.catalog_description:
        settings.catalog_description = current_user.catalog_description
    
    # Generate PDF
    pdf_buffer = generate_pdf(desserts, settings)
    
    # Return file for download
    return StreamingResponse(
        pdf_buffer,
        media_type="application/pdf",
        headers={
            "Content-Disposition": "attachment; filename=catalog.pdf"
        }
    )

