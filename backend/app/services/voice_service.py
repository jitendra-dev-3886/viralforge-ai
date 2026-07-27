from pathlib import Path
import uuid

import edge_tts

from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from app.models.voice import Voice
from app.schemas.voice import VoiceCreate


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

        try:

            # ==========================================
            # Create Audio Folder
            # ==========================================

            audio_dir = (
                VoiceService.BASE_DIR
                / str(request.project_id)
                / "audio"
            )

            audio_dir.mkdir(
                parents=True,
                exist_ok=True,
            )

            # ==========================================
            # Audio File
            # ==========================================

            filename = (
                f"scene_{request.scene_id}_"
                f"{uuid.uuid4().hex[:8]}.mp3"
            )

            audio_path = audio_dir / filename

            # ==========================================
            # Generate Audio
            # ==========================================

            communicate = edge_tts.Communicate(

                text=request.text,

                voice=request.voice,

                rate=request.speed,

                pitch=request.pitch,

            )

            await communicate.save(str(audio_path))

            # ==========================================
            # File Size
            # ==========================================

            file_size = (
                audio_path.stat().st_size
                if audio_path.exists()
                else 0
            )

            # ==========================================
            # Save Database
            # ==========================================

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

            db.commit()

            db.refresh(voice)

            return {

                "success": True,

                "message": "Voice generated successfully.",

                "voice": voice,

            }

        except Exception as e:

            db.rollback()

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

            data = request.model_dump(exclude_unset=True)

            for key, value in data.items():

                setattr(voice, key, value)

            db.commit()

            db.refresh(voice)

            return {

                "success": True,

                "message": "Voice updated successfully.",

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

            # Delete MP3 if exists
            if voice.audio_path:

                path = Path(voice.audio_path)

                if path.exists():

                    path.unlink()

            db.delete(voice)

            db.commit()

            return {

                "success": True,

                "message": "Voice deleted successfully.",

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

            # Remove old file

            if voice.audio_path:

                old_file = Path(voice.audio_path)

                if old_file.exists():

                    old_file.unlink()

            # Generate new filename

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

            audio_path = audio_dir / filename

            communicate = edge_tts.Communicate(

                text=voice.text,

                voice=voice.voice,

                rate=voice.speed,

                pitch=voice.pitch,

            )

            await communicate.save(str(audio_path))

            voice.audio_name = filename

            voice.audio_path = str(audio_path)

            voice.file_size = audio_path.stat().st_size

            voice.status = "generated"

            voice.error_message = None

            db.commit()

            db.refresh(voice)

            return {

                "success": True,

                "message": "Voice regenerated successfully.",

                "voice": voice,

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