from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from pathlib import Path
import uuid
from sqlalchemy.orm import Session

from app.database import get_db
from app.core.security import get_current_user_id
from app.services.brand_service import BrandService
from app.schemas.brand import (
    CreateBrandRequest,
    UpdateBrandRequest,
)

router = APIRouter(
    prefix="/api/brands",
    tags=["Brands"],
)


@router.post("/logo")
async def upload_brand_logo(
    file: UploadFile = File(...),
    user_id: int = Depends(get_current_user_id),
):
    """Store a reusable brand logo and return its public storage URL."""
    extension = Path(file.filename or "").suffix.lower()
    allowed = {
        ".png": "image/png",
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".webp": "image/webp",
    }
    if extension not in allowed:
        raise HTTPException(status_code=400, detail="Upload a PNG, JPG, JPEG, or WebP logo.")

    folder = Path(__file__).resolve().parents[2] / "storage" / "brands" / str(user_id)
    folder.mkdir(parents=True, exist_ok=True)
    filename = f"logo_{uuid.uuid4().hex}{extension}"
    path = folder / filename
    size = 0
    try:
        with path.open("wb") as destination:
            while chunk := await file.read(1024 * 1024):
                size += len(chunk)
                if size > 5 * 1024 * 1024:
                    raise HTTPException(status_code=413, detail="Logo image must be 5 MB or smaller.")
                destination.write(chunk)
        if size == 0:
            raise HTTPException(status_code=400, detail="The uploaded logo image is empty.")
    except Exception:
        path.unlink(missing_ok=True)
        raise

    return {
        "success": True,
        "logo_url": f"/storage/brands/{user_id}/{filename}",
    }


# ==========================================================
# Create Brand
# ==========================================================

@router.post("/")
def create_brand(
    request: CreateBrandRequest,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    return BrandService.create_brand(
        db=db,
        user_id=user_id,
        request=request,
    )


# ==========================================================
# Get All Brands
# ==========================================================

@router.get("/")
def get_all_brands(
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    return BrandService.get_all_brands(
        db=db,
        user_id=user_id,
    )


# ==========================================================
# Get Brand By ID
# ==========================================================

@router.get("/{brand_id}")
def get_brand(
    brand_id: int,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    return BrandService.get_brand(
        db=db,
        brand_id=brand_id,
        user_id=user_id,
    )


# ==========================================================
# Update Brand
# ==========================================================

@router.put("/{brand_id}")
def update_brand(
    brand_id: int,
    request: UpdateBrandRequest,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    return BrandService.update_brand(
        db=db,
        brand_id=brand_id,
        user_id=user_id,
        request=request,
    )


# ==========================================================
# Delete Brand
# ==========================================================

@router.delete("/{brand_id}")
def delete_brand(
    brand_id: int,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    return BrandService.delete_brand(
        db=db,
        brand_id=brand_id,
        user_id=user_id,
    )
