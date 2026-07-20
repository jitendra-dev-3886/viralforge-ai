import traceback
import json

from app.services.prompt_engine import PromptEngine
from app.core.gemini_client import GeminiClient
from app.core.groq_client import groq_client

from app.models.project import Project
from app.models.content import Content

from app.services.scene_service import SceneService


class AIService:

    @staticmethod
    def generate(request, db):

        try:

            # ==========================
            # Build Prompt
            # ==========================

            prompt = PromptEngine.build(request)


            print("=" * 80)
            print(prompt)
            print("=" * 80)



            # ==========================
            # Generate AI Content
            # ==========================

            try:

                print("Trying Gemini...")

                ai_text = GeminiClient.generate(prompt)

                provider = "gemini"


            except Exception as gemini_error:

                print("Gemini Failed:")
                print(gemini_error)

                print("Switching to Groq...")


                ai_text = groq_client.generate(prompt)

                provider = "groq"



            print("AI RESPONSE:")
            print(ai_text)



            # ==========================
            # Convert JSON
            # ==========================

            try:

                ai_data = json.loads(ai_text)


            except json.JSONDecodeError:

                ai_data = {
                    "raw": ai_text
                }



            # # ==========================
            # # Normalize AI Response
            # # ==========================

            # try:

            #     platform = request.platforms[0].lower()

            #     content_type = request.content_types[0].lower()


            #     generated = ai_data[platform][content_type]


            #     ai_data = {

            #         "title": request.topic,

            #         "hook": generated.get(
            #             "voiceover",
            #             ""
            #         )[:200],


            #         "script": generated.get(
            #             "voiceover",
            #             ""
            #         ),


            #         "caption": generated.get(
            #             "caption",
            #             ""
            #         ),


            #         "hashtags": generated.get(
            #             "hashtags",
            #             ""
            #         ),


            #         "video": generated.get(
            #             "video",
            #             ""
            #         )

            #     }


            # except Exception as e:

            #     print("Normalization Failed:")
            #     print(e)

            # ==========================
            # Find Project
            # ==========================

            project = db.query(Project).filter(
                Project.id == request.project_id
            ).first()


            if not project:

                return {
                    "success": False,
                    "error": "Project not found"
                }



            # ==========================
            # Save Content
            # ==========================

            content = Content(

                user_id=project.user_id,

                project_id=project.id,

                title=ai_data.get(
                    "title",
                    "Untitled"
                ),

                hook=ai_data.get(
                    "hook"
                ),

                script=ai_data.get(
                    "script",
                    ""
                ),

                caption=ai_data.get(
                    "caption"
                ),
            hashtags=(
                ",".join(ai_data.get("hashtags"))
                if isinstance(ai_data.get("hashtags"), list)
                else ai_data.get("hashtags")
            ),

                keywords=ai_data.get(
                    "keywords"
                ),

                cta=ai_data.get(
                    "cta"
                ),

                platform=",".join(request.platforms),

                content_type=",".join(request.content_types),
                language=request.language,

                ai_provider=provider,

                ai_model=provider,

                prompt=prompt,

                status="generated"

            )


            db.add(content)

            db.commit()

            db.refresh(content)

            SceneService.generate(
                db=db,
                project_id=project.id,
                content_id=content.id,
                ai_data=ai_data,
            )



            return {

                "success": True,

                "provider": provider,

                "content_id": content.id,

                "data": ai_data

            }



        except Exception as e:

            traceback.print_exc()

            db.rollback()


            return {

                "success": False,

                "error": str(e)

            }
        