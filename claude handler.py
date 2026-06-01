import anthropic
import os
import httpx
import base64

ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")

SYSTEM_PROMPT = """Sen O'zbekiston maktab biologiya fanining AI yordamchisissan.
5-sinf dan 11-sinf gacha bo'lgan biologiya darsliklarini yaxshi bilasan.

Qoidalar:
1. Faqat biologiya faniga oid savollarga javob ber
2. O'zbek tilida javob ber
3. Imkon qadar qisqa va aniq javob ber
4. Agar sinf ko'rsatilgan bo'lsa, o'sha sinf dasturiga mos javob ber
5. Test savolida to'g'ri javobni aniq ko'rsat (A, B, C, D)
6. Rasmli testlarda rasmni diqqat bilan tahlil qil
7. Javobni HTML formatida ber (bold, italic ishlatsa bo'ladi)
"""


class ClaudeHandler:
    def __init__(self):
        self.client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

    async def answer_text_question(self, question: str) -> str:
        response = self.client.messages.create(
            model="claude-opus-4-5",
            max_tokens=1000,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": question}]
        )
        return response.content[0].text

    async def answer_image_question(self, image_url: str, question: str) -> str:
        async with httpx.AsyncClient() as client:
            resp = await client.get(image_url)
            image_data = base64.standard_b64encode(resp.content).decode("utf-8")

        content_type = resp.headers.get("content-type", "image/jpeg")
        if "png" in content_type:
            media_type = "image/png"
        elif "gif" in content_type:
            media_type = "image/gif"
        elif "webp" in content_type:
            media_type = "image/webp"
        else:
            media_type = "image/jpeg"

        response = self.client.messages.create(
            model="claude-opus-4-5",
            max_tokens=1000,
            system=SYSTEM_PROMPT,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": media_type,
                                "data": image_data,
                            },
                        },
                        {
                            "type": "text",
                            "text": question
                        }
                    ],
                }
            ],
        )
        return response.content[0].text
