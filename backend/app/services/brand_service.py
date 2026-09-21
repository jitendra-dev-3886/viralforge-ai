from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.brand import Brand
from app.schemas.brand import (
    CreateBrandRequest,
    UpdateBrandRequest,
)


class BrandService:

    # ==========================================================
    # Create Brand
    # ==========================================================

    @staticmethod
    def create_brand(
        db: Session,
        user_id: int,
        request: CreateBrandRequest,
    ):

        existing = (
            db.query(Brand)
            .filter(
                Brand.user_id == user_id,
                func.lower(Brand.name) == request.name.lower(),
            )
            .first()
        )

        if existing:
            return {
                "success": False,
                "message": "Brand already exists.",
            }

        from app.services.billing_service import check_brand_limit
        check_brand_limit(db, user_id)

        brand = Brand(
            user_id=user_id,
            name=request.name,
            description=request.description,
            niche=request.niche,
            website=str(request.website)
            if request.website
            else None,
            logo=request.logo,
            primary_color=request.primary_color,
            secondary_color=request.secondary_color,
            font=request.font,
        )

        db.add(brand)
        db.commit()
        db.refresh(brand)

        return {
            "success": True,
            "message": "Brand created successfully.",
            "brand": brand,
        }

    # ==========================================================
    # Get All Brands
    # ==========================================================

    @staticmethod
    def get_all_brands(
        db: Session,
        user_id: int,
    ):

        brands = (
            db.query(Brand)
            .filter(
                Brand.user_id == user_id
            )
            .order_by(
                Brand.created_at.desc()
            )
            .all()
        )

        return {
            "success": True,
            "total": len(brands),
            "brands": brands,
        }

    # ==========================================================
    # Get Single Brand
    # ==========================================================

    @staticmethod
    def get_brand(
        db: Session,
        brand_id: int,
        user_id: int,
    ):

        brand = (
            db.query(Brand)
            .filter(
                Brand.id == brand_id,
                Brand.user_id == user_id,
            )
            .first()
        )

        if not brand:
            return {
                "success": False,
                "message": "Brand not found.",
            }

        return {
            "success": True,
            "brand": brand,
        }

    # ==========================================================
    # Update Brand
    # ==========================================================

    @staticmethod
    def update_brand(
        db: Session,
        brand_id: int,
        user_id: int,
        request: UpdateBrandRequest,
    ):

        brand = (
            db.query(Brand)
            .filter(
                Brand.id == brand_id,
                Brand.user_id == user_id,
            )
            .first()
        )

        if not brand:
            return {
                "success": False,
                "message": "Brand not found.",
            }

        # Duplicate name check
        if (
            request.name
            and request.name.lower() != brand.name.lower()
        ):

            exists = (
                db.query(Brand)
                .filter(
                    Brand.user_id == user_id,
                    func.lower(Brand.name) == request.name.lower(),
                    Brand.id != brand_id,
                )
                .first()
            )

            if exists:
                return {
                    "success": False,
                    "message": "Brand name already exists.",
                }

        data = request.model_dump(
            exclude_none=True,
            exclude_unset=True,
        )

        if "website" in data:
            data["website"] = str(data["website"])

        for key, value in data.items():
            setattr(
                brand,
                key,
                value,
            )

        db.commit()
        db.refresh(brand)

        return {
            "success": True,
            "message": "Brand updated successfully.",
            "brand": brand,
        }

    # ==========================================================
    # Delete Brand
    # ==========================================================

    @staticmethod
    def delete_brand(
        db: Session,
        brand_id: int,
        user_id: int,
    ):

        brand = (
            db.query(Brand)
            .filter(
                Brand.id == brand_id,
                Brand.user_id == user_id,
            )
            .first()
        )

        if not brand:
            return {
                "success": False,
                "message": "Brand not found.",
            }

        db.delete(brand)
        db.commit()

        return {
            "success": True,
            "message": "Brand deleted successfully.",
        }