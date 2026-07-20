import os
from groq import Groq


class ScriptService:


    def __init__(self):

        self.client = Groq(
            api_key=os.getenv(
                "GROQ_API_KEY"
            )
        )


    async def generate(self, brief):


        prompt=f"""

Create viral social media script.

Topic:
{brief['topic']}

Category:
{brief['category']}

Platform:
{brief['platform']}

Style:
{brief['tone']}


Return JSON:

{{
"hook":"",
"intro":"",
"sections":[],
"ending":"",
"cta":""
}}

"""


        response = self.client.chat.completions.create(

            model="llama-3.3-70b-versatile",

            messages=[
                {
                    "role":"user",
                    "content":prompt
                }
            ],

            temperature=0.8

        )


        return response.choices[0].message.content