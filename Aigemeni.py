from google import genai
from google.genai import types
import Tokens

_chats = {}

client = genai.Client(api_key=Tokens.GoogleAi_Token)
MODEL = "gemini-3.6-flash"
SYSTEM_PROMPT = "Ты создатель контрольных работ."


def _get_chat(user_id: int):
    if user_id not in _chats:
        _chats[user_id] = client.chats.create(
            model=MODEL,
            config=types.GenerateContentConfig(system_instruction=SYSTEM_PROMPT),
        )
    return _chats[user_id]


def ask(user_id: int, text: str) -> str:
    try:
        response = _get_chat(user_id).send_message(text)
        return response.text
    except Exception as e:
        print("Gemini error:", e)
        return 0


def reset(user_id: int) -> None:
    _chats.pop(user_id, None)