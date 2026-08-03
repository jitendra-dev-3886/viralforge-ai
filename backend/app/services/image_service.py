from pathlib import Path
import uuid
import requests

from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from app.models.image import Image
from app.schemas.image import ImageCreate, ImageUpdate


class ImageService:

    BASE_DIR = Path("storage/projects")

    # ==========================================================
    # Generate Image
    # ==========================================================

    @staticmethod
    def generate(
        db: Session,
        user_id: int,
        request: ImageCreate,
    ):

        try:

            # ==================================================
            # Create Folder
            # ==================================================

            image_dir = (
                ImageService.BASE_DIR
                / str(request.project_id)
                / "images"
            )

            image_dir.mkdir(
                parents=True,
                exist_ok=True,
            )

            # ==================================================
            # File Name
            # ==================================================

            filename = (
                f"scene_{request.scene_id}_"
                f"{uuid.uuid4().hex[:8]}.png"
            )

            image_path = image_dir / filename

            from app.core.pexels_client import PexelsClient
            from app.core.pixabay_client import PixabayClient

            # ==================================================
            # Get Image Data
            # ==================================================

            image_data = None
            orientation = (
                "portrait" if request.height > request.width
                else "landscape" if request.width > request.height
                else "square"
            )

            if request.provider == "pexels":
                image_data = PexelsClient.search_and_download(
                    keyword=request.prompt,
                    media_type="image",
                    save_path=str(image_path),
                    orientation=orientation,
                )

            elif request.provider == "pixabay":
                image_data = PixabayClient.search_and_download(
                    keyword=request.prompt,
                    media_type="image",
                    save_path=str(image_path),
                    orientation=orientation,
                )

            else:
                url = (
                    "https://image.pollinations.ai/prompt/"
                    + request.prompt.replace(" ", "%20")
                )
                response = requests.get(url, timeout=120)

                if response.status_code != 200:
                    return {
                        "success": False,
                        "message": "Image generation failed.",
                    }

                with open(image_path, "wb") as file:
                    file.write(response.content)

                image_data = {
                    "provider": "Pollinations",
                    "title": request.prompt,
                    "file_url": url,
                    "file_path": str(image_path),
                    "file_size": image_path.stat().st_size if image_path.exists() else 0,
                    "width": request.width,
                    "height": request.height,
                    "mime_type": "image/png",
                    "extension": ".png",
                    "duration": 0,
                }

            if not image_data:
                return {
                    "success": False,
                    "message": "Image generation failed. No image data received.",
                }

            # ==================================================
            # Save Database
            # ==================================================

            image = Image(
                user_id=user_id,
                project_id=request.project_id,
                content_id=request.content_id,
                scene_id=request.scene_id,
                provider=image_data["provider"],
                model=request.model,
                prompt=request.prompt,
                negative_prompt=request.negative_prompt,
                image_name=image_data["title"],
                image_path=image_data["file_path"],
                image_url=image_data["file_url"],
                width=image_data["width"],
                height=image_data["height"],
                file_size=image_data["file_size"],
                status="generated",
                error_message=None,
            )

            db.add(image)
            db.commit()
            db.refresh(image)

            return {
                "success": True,
                "message": "Image generated successfully.",
                "image": image,
            }

        except Exception as e:

            db.rollback()

            return {

                "success": False,

                "message": str(e),

            }
            # ==========================================================
    # Get All Images
    # ==========================================================

    @staticmethod
    def get_all(
        db: Session,
        user_id: int,
    ):

        try:

            images = (
                db.query(Image)
                .filter(
                    Image.user_id == user_id,
                )
                .order_by(
                    Image.created_at.desc(),
                )
                .all()
            )

            return images

        except SQLAlchemyError:

            return []

    # ==========================================================
    # Get Image By ID
    # ==========================================================

    @staticmethod
    def get_by_id(
        db: Session,
        image_id: int,
        user_id: int,
    ):

        try:

            image = (
                db.query(Image)
                .filter(
                    Image.id == image_id,
                    Image.user_id == user_id,
                )
                .first()
            )

            return image

        except SQLAlchemyError:

            return None

    # ==========================================================
    # Get Project Images
    # ==========================================================

    @staticmethod
    def get_project(
        db: Session,
        project_id: int,
        user_id: int,
    ):

        try:

            images = (
                db.query(Image)
                .filter(
                    Image.project_id == project_id,
                    Image.user_id == user_id,
                )
                .order_by(
                    Image.created_at.asc(),
                )
                .all()
            )

            return images

        except SQLAlchemyError:

            return []

    # ==========================================================
    # Get Content Images
    # ==========================================================

    @staticmethod
    def get_content(
        db: Session,
        content_id: int,
        user_id: int,
    ):

        try:

            images = (
                db.query(Image)
                .filter(
                    Image.content_id == content_id,
                    Image.user_id == user_id,
                )
                .order_by(
                    Image.created_at.asc(),
                )
                .all()
            )

            return images

        except SQLAlchemyError:

            return []

    # ==========================================================
    # Get Scene Images
    # ==========================================================

    @staticmethod
    def get_scene(
        db: Session,
        scene_id: int,
        user_id: int,
    ):

        try:

            images = (
                db.query(Image)
                .filter(
                    Image.scene_id == scene_id,
                    Image.user_id == user_id,
                )
                .order_by(
                    Image.created_at.asc(),
                )
                .all()
            )

            return images

        except SQLAlchemyError:

            return []
            # ==========================================================
    # Update Image
    # ==========================================================

    @staticmethod
    def update(
        db: Session,
        image_id: int,
        user_id: int,
        request: ImageUpdate,
    ):

        try:

            image = (
                db.query(Image)
                .filter(
                    Image.id == image_id,
                    Image.user_id == user_id,
                )
                .first()
            )

            if not image:

                return {
                    "success": False,
                    "message": "Image not found.",
                }

            data = request.model_dump(exclude_unset=True)

            for key, value in data.items():
                setattr(image, key, value)

            db.commit()
            db.refresh(image)

            return {
                "success": True,
                "message": "Image updated successfully.",
                "image": image,
            }

        except Exception as e:

            db.rollback()

            return {
                "success": False,
                "message": str(e),
            }

    # ==========================================================
    # Delete Image
    # ==========================================================

    @staticmethod
    def delete(
        db: Session,
        image_id: int,
        user_id: int,
    ):

        try:

            image = (
                db.query(Image)
                .filter(
                    Image.id == image_id,
                    Image.user_id == user_id,
                )
                .first()
            )

            if not image:

                return {
                    "success": False,
                    "message": "Image not found.",
                }

            if image.image_path:

                path = Path(image.image_path)

                if path.exists():
                    path.unlink()

            db.delete(image)

            db.commit()

            return {
                "success": True,
                "message": "Image deleted successfully.",
            }

        except Exception as e:

            db.rollback()

            return {
                "success": False,
                "message": str(e),
            }

    # ==========================================================
    # Regenerate Image
    # ==========================================================

    @staticmethod
    def regenerate(
        db: Session,
        image_id: int,
        user_id: int,
    ):

        try:

            image = (
                db.query(Image)
                .filter(
                    Image.id == image_id,
                    Image.user_id == user_id,
                )
                .first()
            )

            if not image:

                return {
                    "success": False,
                    "message": "Image not found.",
                }

            if image.image_path:

                old = Path(image.image_path)

                if old.exists():
                    old.unlink()

            filename = (
                f"scene_{image.scene_id}_"
                f"{uuid.uuid4().hex[:8]}.png"
            )

            image_dir = (
                ImageService.BASE_DIR
                / str(image.project_id)
                / "images"
            )

            image_dir.mkdir(
                parents=True,
                exist_ok=True,
            )

            image_path = image_dir / filename

            url = (
                "https://image.pollinations.ai/prompt/"
                + image.prompt.replace(" ", "%20")
            )

            response = requests.get(
                url,
                timeout=120,
            )

            if response.status_code != 200:

                return {
                    "success": False,
                    "message": "Image generation failed.",
                }

            with open(image_path, "wb") as f:
                f.write(response.content)

            image.image_name = filename
            image.image_path = str(image_path)
            image.file_size = image_path.stat().st_size
            image.status = "generated"
            image.error_message = None

            db.commit()

            db.refresh(image)

            return {
                "success": True,
                "message": "Image regenerated successfully.",
                "image": image,
            }

        except Exception as e:

            db.rollback()

            return {
                "success": False,
                "message": str(e),
            }

    # ==========================================================
    # Update Status
    # ==========================================================

    @staticmethod
    def update_status(
        db: Session,
        image_id: int,
        status: str,
    ):

        try:

            image = (
                db.query(Image)
                .filter(
                    Image.id == image_id,
                )
                .first()
            )

            if not image:
                return None

            image.status = status

            db.commit()

            db.refresh(image)

            return image

        except Exception:

            db.rollback()

            return None
