from pathlib import Path
import uuid

import edge_tts

from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from app.models.voice import Voice
from app.models.media import Media
from app.models.content import Content
from app.models.project import Project
from app.models.scene import Scene

from app.schemas.voice import (
    VoiceCreate,
    VoiceUpdate,
)


class VoiceService:

    BASE_DIR = Path("storage/projects")

    # ==========================================================
    # Generate Voice
    # ==========================================================

    @staticmethod
    async def generate(
        db: Session,
        user_id: int,
        request: VoiceCreate,
    ):

        audio_path = None

        try:

            # ==================================================
            # Validate Project
            # ==================================================

            project = (
                db.query(Project)
                .filter(
                    Project.id == request.project_id,
                    Project.user_id == user_id,
                )
                .first()
            )

            # ==================================================
            # Validate Content
            # ==================================================

            content = (
                db.query(Content)
                .filter(
                    Content.id == request.content_id,
                    Content.user_id == user_id,
                    Content.project_id == request.project_id,
                )
                .first()
            )

            # ==================================================
            # Validate Scene
            # ==================================================

            scene = (
                db.query(Scene)
                .filter(
                    Scene.id == request.scene_id,
                    Scene.user_id == user_id,
                    Scene.project_id == request.project_id,
                    Scene.content_id == request.content_id,
                )
                .first()
            )

            if not project or not content or not scene:

                return {
                    "success": False,
                    "message": (
                        "Select a valid project, content, and scene."
                    ),
                }

            # ==================================================
            # Create Audio Folder
            # ==================================================

            audio_dir = (
                VoiceService.BASE_DIR
                / str(request.project_id)
                / "audio"
            )

            audio_dir.mkdir(
                parents=True,
                exist_ok=True,
            )

            # ==================================================
            # Audio File Name
            # ==================================================

            filename = (
                f"scene_{request.scene_id}_"
                f"{uuid.uuid4().hex[:8]}.mp3"
            )

            audio_path = audio_dir / filename

            # ==================================================
            # Generate Audio
            # ==================================================

            communicate = edge_tts.Communicate(
                text=request.text,
                voice=request.voice,
                rate=request.speed,
                pitch=request.pitch,
            )

            await communicate.save(
                str(audio_path)
            )

            # ==================================================
            # Validate Audio File
            # ==================================================

            if not audio_path.exists():

                raise Exception(
                    "Voice generation completed but audio file "
                    "was not created."
                )

            file_size = audio_path.stat().st_size

            if file_size <= 0:

                raise Exception(
                    "Generated audio file is empty."
                )

            # ==================================================
            # Create Voice Record
            # ==================================================

            voice = Voice(

                user_id=user_id,

                project_id=request.project_id,

                content_id=request.content_id,

                scene_id=request.scene_id,

                provider=request.provider,

                voice=request.voice,

                gender=request.gender,

                language=request.language,

                speed=request.speed,

                pitch=request.pitch,

                text=request.text,

                audio_name=filename,

                audio_path=str(audio_path),

                audio_url=None,

                duration=0,

                file_size=file_size,

                status="generated",

                error_message=None,
            )

            db.add(voice)

            db.flush()

            # ==================================================
            # Create Media Record
            # ==================================================

            media = Media(

                user_id=user_id,

                project_id=request.project_id,

                media_type="audio",

                provider=request.provider,

                title=f"Scene {scene.scene_number} Voice",

                file_name=filename,

                file_path=str(audio_path),

                file_url="",

                mime_type="audio/mpeg",

                extension=".mp3",

                duration=0,

                width=None,

                height=None,

                file_size=file_size,

                status="ready",
            )

            db.add(media)

            db.flush()

            # ==================================================
            # Commit Both Records
            # ==================================================

            db.commit()

            db.refresh(voice)

            db.refresh(media)

            # ==================================================
            # Return Response
            # ==================================================

            return {

                "success": True,

                "message": (
                    "Voice generated successfully."
                ),

                "voice": voice,

                "media": media,

            }

        # ======================================================
        # Database Error
        # ======================================================

        except SQLAlchemyError as e:

            db.rollback()

            # Remove generated file if DB failed

            if audio_path and audio_path.exists():

                try:
                    audio_path.unlink()
                except Exception:
                    pass

            return {

                "success": False,

                "message": (
                    f"Database error: {str(e)}"
                ),

            }

        # ======================================================
        # General Error
        # ======================================================

        except Exception as e:

            db.rollback()

            # Remove generated file if generation/DB failed

            if audio_path and audio_path.exists():

                try:
                    audio_path.unlink()
                except Exception:
                    pass

            return {

                "success": False,

                "message": str(e),

            }

    # ==========================================================
    # Get All Voices
    # ==========================================================

    @staticmethod
    def get_all(
        db: Session,
        user_id: int,
    ):

        try:

            voices = (
                db.query(Voice)
                .filter(
                    Voice.user_id == user_id,
                )
                .order_by(
                    Voice.created_at.desc(),
                )
                .all()
            )

            return voices

        except SQLAlchemyError:

            return []

    # ==========================================================
    # Get Voice By ID
    # ==========================================================

    @staticmethod
    def get_by_id(
        db: Session,
        voice_id: int,
        user_id: int,
    ):

        try:

            voice = (
                db.query(Voice)
                .filter(
                    Voice.id == voice_id,
                    Voice.user_id == user_id,
                )
                .first()
            )

            return voice

        except SQLAlchemyError:

            return None

    # ==========================================================
    # Get Project Voices
    # ==========================================================

    @staticmethod
    def get_project(
        db: Session,
        project_id: int,
        user_id: int,
    ):

        try:

            voices = (
                db.query(Voice)
                .filter(
                    Voice.project_id == project_id,
                    Voice.user_id == user_id,
                )
                .order_by(
                    Voice.created_at.asc(),
                )
                .all()
            )

            return voices

        except SQLAlchemyError:

            return []

    # ==========================================================
    # Get Content Voices
    # ==========================================================

    @staticmethod
    def get_content(
        db: Session,
        content_id: int,
        user_id: int,
    ):

        try:

            voices = (
                db.query(Voice)
                .filter(
                    Voice.content_id == content_id,
                    Voice.user_id == user_id,
                )
                .order_by(
                    Voice.created_at.asc(),
                )
                .all()
            )

            return voices

        except SQLAlchemyError:

            return []

    # ==========================================================
    # Get Scene Voice
    # ==========================================================

    @staticmethod
    def get_scene(
        db: Session,
        scene_id: int,
        user_id: int,
    ):

        try:

            voice = (
                db.query(Voice)
                .filter(
                    Voice.scene_id == scene_id,
                    Voice.user_id == user_id,
                )
                .first()
            )

            return voice

        except SQLAlchemyError:

            return None

    # ==========================================================
    # Update Voice
    # ==========================================================

    @staticmethod
    def update(
        db: Session,
        voice_id: int,
        user_id: int,
        request: VoiceUpdate,
    ):

        try:

            voice = (
                db.query(Voice)
                .filter(
                    Voice.id == voice_id,
                    Voice.user_id == user_id,
                )
                .first()
            )

            if not voice:

                return {
                    "success": False,
                    "message": "Voice not found.",
                }

            data = request.model_dump(
                exclude_unset=True
            )

            for key, value in data.items():

                setattr(
                    voice,
                    key,
                    value,
                )

            db.commit()

            db.refresh(voice)

            return {

                "success": True,

                "message": (
                    "Voice updated successfully."
                ),

                "voice": voice,

            }

        except SQLAlchemyError as e:

            db.rollback()

            return {

                "success": False,

                "message": str(e),

            }

    # ==========================================================
    # Delete Voice
    # ==========================================================

    @staticmethod
    def delete(
        db: Session,
        voice_id: int,
        user_id: int,
    ):

        try:

            voice = (
                db.query(Voice)
                .filter(
                    Voice.id == voice_id,
                    Voice.user_id == user_id,
                )
                .first()
            )

            if not voice:

                return {

                    "success": False,

                    "message": "Voice not found.",

                }

            # ==================================================
            # Delete Audio File
            # ==================================================

            if voice.audio_path:

                path = Path(
                    voice.audio_path
                )

                if path.exists():

                    path.unlink()

            # ==================================================
            # Delete Related Media
            # ==================================================

            media = (
                db.query(Media)
                .filter(
                    Media.project_id == voice.project_id,
                    Media.media_type == "audio",
                    Media.file_path == voice.audio_path,
                )
                .first()
            )

            if media:

                db.delete(media)

            # ==================================================
            # Delete Voice
            # ==================================================

            db.delete(voice)

            db.commit()

            return {

                "success": True,

                "message": (
                    "Voice deleted successfully."
                ),

            }

        except Exception as e:

            db.rollback()

            return {

                "success": False,

                "message": str(e),

            }

    # ==========================================================
    # Regenerate Voice
    # ==========================================================

    @staticmethod
    async def regenerate(
        db: Session,
        voice_id: int,
        user_id: int,
    ):

        audio_path = None

        try:

            # ==================================================
            # Get Voice
            # ==================================================

            voice = (
                db.query(Voice)
                .filter(
                    Voice.id == voice_id,
                    Voice.user_id == user_id,
                )
                .first()
            )

            if not voice:

                return {

                    "success": False,

                    "message": "Voice not found.",

                }

            # ==================================================
            # Remove Old File
            # ==================================================

            if voice.audio_path:

                old_file = Path(
                    voice.audio_path
                )

                if old_file.exists():

                    old_file.unlink()

            # ==================================================
            # Generate New Filename
            # ==================================================

            filename = (
                f"scene_{voice.scene_id}_"
                f"{uuid.uuid4().hex[:8]}.mp3"
            )

            audio_dir = (
                VoiceService.BASE_DIR
                / str(voice.project_id)
                / "audio"
            )

            audio_dir.mkdir(
                parents=True,
                exist_ok=True,
            )

            audio_path = (
                audio_dir / filename
            )

            # ==================================================
            # Generate New Audio
            # ==================================================

            communicate = edge_tts.Communicate(

                text=voice.text,

                voice=voice.voice,

                rate=voice.speed,

                pitch=voice.pitch,

            )

            await communicate.save(
                str(audio_path)
            )

            if not audio_path.exists():

                raise Exception(
                    "Voice regeneration completed but "
                    "audio file was not created."
                )

            file_size = audio_path.stat().st_size

            # ==================================================
            # Update Voice
            # ==================================================

            voice.audio_name = filename

            voice.audio_path = str(
                audio_path
            )

            voice.file_size = file_size

            voice.status = "generated"

            voice.error_message = None

            # ==================================================
            # Update Related Media
            # ==================================================

            media = (
                db.query(Media)
                .filter(
                    Media.project_id == voice.project_id,
                    Media.media_type == "audio",
                    Media.title == (
                        f"Scene {voice.scene.scene_number} Voice"
                        if hasattr(voice, "scene")
                        else None
                    ),
                )
                .first()
            )

            # If existing media isn't found,
            # create it.

            if not media:

                scene = (
                    db.query(Scene)
                    .filter(
                        Scene.id == voice.scene_id,
                        Scene.user_id == user_id,
                    )
                    .first()
                )

                if not scene:

                    raise Exception(
                        "Scene not found for voice."
                    )

                media = Media(

                    user_id=user_id,

                    project_id=voice.project_id,

                    media_type="audio",

                    provider=voice.provider,

                    title=(
                        f"Scene "
                        f"{scene.scene_number} Voice"
                    ),

                    file_name=filename,

                    file_path=str(audio_path),

                    file_url="",

                    mime_type="audio/mpeg",

                    extension=".mp3",

                    duration=0,

                    width=None,

                    height=None,

                    file_size=file_size,

                    status="ready",

                )

                db.add(media)

            else:

                media.file_name = filename

                media.file_path = str(
                    audio_path
                )

                media.file_size = file_size

                media.provider = voice.provider

                media.status = "ready"

            db.commit()

            db.refresh(voice)

            db.refresh(media)

            return {

                "success": True,

                "message": (
                    "Voice regenerated successfully."
                ),

                "voice": voice,

                "media": media,

            }

        except Exception as e:

            db.rollback()

            if audio_path and audio_path.exists():

                try:
                    audio_path.unlink()
                except Exception:
                    pass

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
        voice_id: int,
        status: str,
    ):

        try:

            voice = (
                db.query(Voice)
                .filter(
                    Voice.id == voice_id,
                )
                .first()
            )

            if not voice:

                return None

            voice.status = status

            db.commit()

            db.refresh(voice)

            return voice

        except SQLAlchemyError:

            db.rollback()

            return None