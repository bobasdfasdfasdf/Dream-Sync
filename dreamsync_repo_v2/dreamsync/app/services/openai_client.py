import os, json
from typing import Dict, Any
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def dream_to_storyboard(transcript: str, template: str) -> Dict[str, Any]:
    prompt = f"""{template}

RAW TRANSCRIPT:
{transcript}
"""
    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a precise JSON generator."},
            {"role": "user", "content": prompt},
        ],
        temperature=0.9,
        response_format={"type":"json_object"}
    )
    return json.loads(resp.choices[0].message.content)

def refine_caption(caption: str) -> str:
    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "Polish caption to 6-12 words, present tense."},
            {"role": "user", "content": caption}
        ],
        temperature=0.7,
    )
    return resp.choices[0].message.content.strip()