import os, requests
from dotenv import load_dotenv

load_dotenv()
EL_KEY = os.getenv("ELEVENLABS_API_KEY")

def tts_to_file(text: str, voice_id: str = "Rachel", out_path: str = "outputs/voiceover.mp3") -> str:
    if not EL_KEY:
        return ""
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
    headers = {
        "xi-api-key": EL_KEY,
        "accept": "audio/mpeg",
        "content-type": "application/json"
    }
    payload = {"text": text, "model_id": "eleven_multilingual_v2"}
    r = requests.post(url, headers=headers, json=payload, timeout=120)
    r.raise_for_status()
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "wb") as f:
        f.write(r.content)
    return out_path