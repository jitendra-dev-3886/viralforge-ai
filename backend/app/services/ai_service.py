class AIService:

    @staticmethod
    def generate(request):

        return {

            "success": True,

            "title": "Demo AI Content",

            "niche": request.niche,

            "topic": request.topic,

            "package": request.package,

            "quote": "Success begins with one decision.",

            "caption": "This is AI generated caption.",

            "hashtags": [
                "#viral",
                "#motivation",
                "#ai"
            ]

        }