from app.services.script_service import ScriptService
from app.services.content_service import ContentService


class ContentPipeline:

    def __init__(self):
        self.script_service = ScriptService()
        self.content_service = ContentService()


    async def process_trend(self, trend):

        # 1. Create content brief
        brief = self.create_brief(trend)


        # 2. Generate AI script
        script = await self.script_service.generate(
            brief
        )


        # 3. Generate metadata
        content = self.content_service.create_metadata(
            trend,
            script
        )


        return {
            "trend": trend,
            "brief": brief,
            "content": content
        }



    def create_brief(self, trend):

        return {

            "topic": trend["title"],

            "category": trend["category"],

            "platform": trend["platform"],

            "content_type": trend["content_type"],


            "goal":
            "Create viral engaging content",


            "tone":
            self.get_tone(trend["category"])

        }



    def get_tone(self, category):

        tones = {

            "AI":"Futuristic and educational",

            "Finance":"Professional and analytical",

            "Psychology":"Curious and mysterious",

            "Entertainment":"Funny and engaging",

            "Technology":"Explainer style"

        }


        return tones.get(
            category,
            "Informative"
        )