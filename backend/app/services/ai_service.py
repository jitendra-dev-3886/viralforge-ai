import traceback

from app.services.prompt_engine import PromptEngine
from app.core.gemini_client import GeminiClient



class AIService:

    @staticmethod
    def generate(request):

        try:

            prompt = PromptEngine.build(request)

            print("=" * 80)
            print(prompt)
            print("=" * 80)

            ai_text = GeminiClient.generate(prompt)

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