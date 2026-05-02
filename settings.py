import os

DB_URL: str = os.environ.get("ifesif_supabase_url")
DB_KEY: str = os.environ.get("ifesif_supabase_key")
GROK_KEY: str = os.environ.get("GROQ_API_KEY")

with open("prompt.txt", "r", encoding="utf-8") as file:
    LLM_PROMPT = file.read()
