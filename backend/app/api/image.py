from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db

from app.schemas.image import (
    ImageCreate,
    ImageUpdate,
)

from app.services.image_service import ImageService


router = APIRouter(
    prefix="/api/image",
    tags=["Image"],
)


# ==========================================================
# Generate Image
# ==========================================================

@router.post("/generate")
def generate_image(
    request: ImageCreate,
    db: Session = Depends(get_db),
):

    user_id = 1  # TODO: Replace with authenticated user

    return ImageService.generate(
        db=db,
        user_id=user_id,
        request=request,
    )


# ==========================================================
# Get All Images
# ==========================================================

@router.get("/")
def get_all_images(
    db: Session = Depends(get_db),
):

    user_id = 1

    images = ImageService.get_all(
        db=db,
        user_id=user_id,
    )

    return {
        "success": True,
        "total": len(images),
        "images": images,
    }


# ==========================================================
# Get Image By ID
# ==========================================================

@router.get("/{image_id}")
def get_image(
    image_id: int,
    db: Session = Depends(get_db),
):

    user_id = 1

    image = ImageService.get_by_id(
        db=db,
        image_id=image_id,
        user_id=user_id,
    )

    if not image:

        return {
            "success": False,
            "message": "Image not found.",
        }

    return {
        "success": True,
        "image": image,
    }


# ==========================================================
# Get Project Images
# ==========================================================

@router.get("/project/{project_id}")
def get_project_images(
    project_id: int,
    db: Session = Depends(get_db),
):

    user_id = 1

    images = ImageService.get_project(
        db=db,
        project_id=project_id,
        user_id=user_id,
    )

    return {
        "success": True,
        "total": len(images),
        "images": images,
    }


# ==========================================================
# Get Content Images
# ==========================================================

@router.get("/content/{content_id}")
def get_content_images(
    content_id: int,
    db: Session = Depends(get_db),
):

    user_id = 1

    images = ImageService.get_content(
        db=db,
        content_id=content_id,
        user_id=user_id,
    )

    return {
        "success": True,
        "total": len(images),
        "images": images,
    }


# ==========================================================
# Get Scene Images
# ==========================================================

@router.get("/scene/{scene_id}")
def get_scene_images(
    scene_id: int,
    db: Session = Depends(get_db),
):

    user_id = 1

    images = ImageService.get_scene(
        db=db,
        scene_id=scene_id,
        user_id=user_id,
    )

    return {
        "success": True,
        "total": len(images),
        "images": images,
    }


# ==========================================================
# Update Image
# ==========================================================

@router.put("/{image_id}")
def update_image(
    image_id: int,
    request: ImageUpdate,
    db: Session = Depends(get_db),
):

    user_id = 1

    return ImageService.update(
        db=db,
        image_id=image_id,
        user_id=user_id,
        request=request,
    )


# ==========================================================
# Delete Image
# ==========================================================

@router.delete("/{image_id}")
def delete_image(
    image_id: int,
    db: Session = Depends(get_db),
):

    user_id = 1

    return ImageService.delete(
        db=db,
        image_id=image_id,
        user_id=user_id,
    )


# ==========================================================
# Regenerate Image
# ==========================================================

@router.post("/{image_id}/regenerate")
def regenerate_image(
    image_id: int,
    db: Session = Depends(get_db),
):

    user_id = 1

    return ImageService.regenerate(
        db=db,
        image_id=image_id,
        user_id=user_id,
    )