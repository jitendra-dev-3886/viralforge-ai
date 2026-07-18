import traceback

from app.core.openai_client import OpenAIClient
from app.services.prompt_engine import PromptEngine


class AIService:

    @staticmethod
    def generate(request):

        try:

            prompt = PromptEngine.build(request)

            print("=" * 80)
            print(prompt)
            print("=" * 80)

            ai_text = OpenAIClient.generate(prompt)

            print("AI RESPONSE:")
            print(ai_text)

            return {
                "success": True,
                "data": ai_text
            }

        except Exception as e:

            traceback.print_exc()

            return {
                "success": False,
                "error": str(e)
            }