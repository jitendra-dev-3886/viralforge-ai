from pathlib import Path

from sqlalchemy.orm import Session

from app.models.media import Media
from app.models.image import Image
from app.models.voice import Voice
from app.schemas.media import (
    MediaCreate,
    MediaUpdate,
)


def _storage_path(value):
    if not value:
        return None
    backend = Path(__file__).resolve().parents[2]
    roots = ((backend / "storage").resolve(), (Path.cwd() / "storage").resolve())
    path = Path(value)
    candidates = [path.resolve()]
    if not path.is_absolute():
        candidates.append((backend / path).resolve())
    allowed = [candidate for candidate in candidates if any(candidate.is_relative_to(root) and candidate != root for root in roots)]
    return next((candidate for candidate in allowed if candidate.is_file()), allowed[0] if allowed else None)


def _file_is_shared(db, media, path):
    references = db.query(Media.file_path).filter(Media.id != media.id).all()
    references += db.query(Image.image_path).all()
    references += db.query(Voice.audio_path).all()
    return any(_storage_path(value) == path for (value,) in references if value)


class MediaService:

    # ==========================================================
    # Create Media
    # ==========================================================

    @staticmethod
    def create(
        db: Session,
        request: MediaCreate,
    ):

        media = Media(

            user_id=request.user_id,

            project_id=request.project_id,

            media_type=request.media_type,

            provider=request.provider,

            title=request.title,

            file_name=request.file_name,

            file_path=request.file_path,

            file_url=request.file_url,

            mime_type=request.mime_type,

            extension=request.extension,

            duration=request.duration,

            width=request.width,

            height=request.height,

            file_size=request.file_size,

            status=request.status,

        )

        db.add(media)
        db.commit()
        db.refresh(media)

        return {
            "success": True,
            "message": "Media created successfully.",
            "media": media,
        }

    # ==========================================================
    # Get All Media
    # ==========================================================

    @staticmethod
    def get_all(
        db: Session,
        user_id: int,
    ):

        media = (

            db.query(Media)

            .filter(Media.user_id == user_id)

            .order_by(Media.created_at.desc())

            .all()

        )

        return {

            "success": True,

            "total": len(media),

            "media": media,

        }

    # ==========================================================
    # Get Media By ID
    # ==========================================================

    @staticmethod
    def get_by_id(
        db: Session,
        media_id: int,
        user_id: int,
    ):

        media = (

            db.query(Media)

            .filter(

                Media.id == media_id,

                Media.user_id == user_id,

            )

            .first()

        )

        if not media:

            return {

                "success": False,

                "message": "Media not found.",

            }

        return {

            "success": True,

            "media": media,

        }

    # ==========================================================
    # Get Project Media
    # ==========================================================

    @staticmethod
    def get_project_media(
        db: Session,
        project_id: int,
        user_id: int,
    ):

        media = (

            db.query(Media)

            .filter(

                Media.project_id == project_id,

                Media.user_id == user_id,

            )

            .order_by(Media.created_at.desc())

            .all()

        )

        return {

            "success": True,

            "total": len(media),

            "media": media,

        }

    # ==========================================================
    # Update Media
    # ==========================================================

    @staticmethod
    def update(
        db: Session,
        media_id: int,
        user_id: int,
        request: MediaUpdate,
    ):

        media = (

            db.query(Media)

            .filter(

                Media.id == media_id,

                Media.user_id == user_id,

            )

            .first()

        )

        if not media:

            return {

                "success": False,

                "message": "Media not found.",

            }

        data = request.model_dump(exclude_unset=True)

        for key, value in data.items():

            setattr(media, key, value)

        db.commit()
        db.refresh(media)

        return {

            "success": True,

            "message": "Media updated successfully.",

            "media": media,

        }

    # ==========================================================
    # Delete Media
    # ==========================================================

    @staticmethod
    def delete(
        db: Session,
        media_id: int,
        user_id: int,
    ):

        media = (

            db.query(Media)

            .filter(

                Media.id == media_id,

                Media.user_id == user_id,

            )

            .first()

        )

        if not media:

            return {

                "success": False,

                "message": "Media not found.",

            }

        path = _storage_path(media.file_path)
        try:
            shared = path is not None and _file_is_shared(db, media, path)
            db.delete(media)
            db.flush()
            if path is not None and not shared:
                path.unlink(missing_ok=True)
            db.commit()
        except OSError:
            db.rollback()
            return {
                "success": False,
                "message": "Unable to remove the media file from storage. Close any app using the file and try again.",
            }
        except Exception:
            db.rollback()
            raise

        return {

            "success": True,

            "message": "Media deleted successfully.",

        }
