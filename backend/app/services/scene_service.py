import json
from pathlib import Path

from sqlalchemy.orm import Session

from app.models.scene import Scene
from app.models.project import Project


class SceneService:

    @staticmethod
    def generate(
        db: Session,
        project_id: int,
        content_id: int,
        ai_data: dict,
    ):

        project = (
            db.query(Project)
            .filter(Project.id == project_id)
            .first()
        )

        if not project:
            raise Exception("Project not found")

        scenes = ai_data.get("scenes", [])

        saved_scenes = []

        for item in scenes:

            scene = Scene(

                project_id=project_id,

                content_id=content_id,

                scene_no=item.get("scene"),

                title=ai_data.get("title"),

                text=item.get("text"),

                keyword=item.get("keyword"),

                duration=item.get("duration", 5),

                media_type=item.get(
                    "media_type",
                    "image",
                ),

            )

            db.add(scene)

            saved_scenes.append(scene)

        db.commit()

        for scene in saved_scenes:
            db.refresh(scene)

        scene_json = Path(project.path) / "content" / "scenes.json"

        with open(
            scene_json,
            "w",
            encoding="utf-8",
        ) as f:

            json.dump(
                ai_data,
                f,
                indent=4,
                ensure_ascii=False,
            )

        return saved_scenes