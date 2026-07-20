from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.brand_service import BrandService
from app.schemas.brand import (
    CreateBrandRequest,
    UpdateBrandRequest,
)

router = APIRouter(
    prefix="/api/brands",
    tags=["Brands"],
)


# ==========================================================
# Create Brand
# ==========================================================

@router.post("/")
def create_brand(
    request: CreateBrandRequest,
    db: Session = Depends(get_db),
):

    # TODO:
    # Replace with authenticated user
    user_id = 1

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
):

    user_id = 1

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
):

    user_id = 1

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
):

    user_id = 1

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
):

    user_id = 1

    return BrandService.delete_brand(
        db=db,
        brand_id=brand_id,
        user_id=user_id,
    )