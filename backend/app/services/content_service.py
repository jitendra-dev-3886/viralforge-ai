import logging

from app.schemas.content import GeneratedContent


logger = logging.getLogger(__name__)


class ContentService:
    """
    Responsible for transforming AI generated
    output into production ready content object.
    """


    def create_content(
        self,
        trend: dict,
        script_data: dict
    ) -> GeneratedContent:


        try:

            content = GeneratedContent(

                title=trend.get(
                    "title",
                    "Untitled"
                ),

                category=trend.get(
                    "category",
                    "General"
                ),

                platform=trend.get(
                    "platform",
                    "Unknown"
                ),

                content_type=trend.get(
                    "content_type",
                    "Post"
                ),

                score=trend.get(
                    "score",
                    0
                ),

                hook=script_data.get(
                    "hook"
                ),

                script=script_data.get(
                    "script"
                ),

                caption=self.generate_caption(
                    trend,
                    script_data
                ),

                hashtags=self.generate_hashtags(
                    trend
                ),

                status="draft"

            )


            return content


        except Exception as e:

            logger.exception(
                "Content creation failed"
            )

            raise e



    def generate_caption(
        self,
        trend,
        script
    ):

        return (
            f"{trend['title']}\n\n"
            f"{script.get('hook','')}\n\n"
            "#ViralForgeAI"
        )



    def generate_hashtags(
        self,
        trend
    ):

        category = trend.get(
            "category",
            ""
        )


        mapping = {

            "AI":[
                "#AI",
                "#ArtificialIntelligence",
                "#FutureTech"
            ],


            "Finance":[
                "#Finance",
                "#Investment",
                "#Money"
            ],


            "Psychology":[
                "#Psychology",
                "#HumanBehavior"
            ],


            "Technology":[
                "#Technology",
                "#Innovation"
            ],


            "Entertainment":[
                "#Entertainment",
                "#Trending"
            ]

        }


        return mapping.get(
            category,
            [
                "#Trending",
                "#Viral"
            ]
        )