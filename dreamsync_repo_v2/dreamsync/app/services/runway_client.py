# Minimal Runway Gen-3 style client (pseudo; adapt to your access/version)
import os, time, requests
from typing import List, Dict, Optional
from dotenv import load_dotenv

load_dotenv()
RUNWAY_API_KEY = os.getenv("RUNWAY_API_KEY")
RUNWAY_API_BASE = "https://api.runwayml.com/v1"

HEADERS = {"Authorization": f"Bearer {RUNWAY_API_KEY}"} if RUNWAY_API_KEY else {}

def create_text_to_video(prompt: str, duration: int = 4) -> Optional[str]:
    if not RUNWAY_API_KEY:
        return None
    payload = {
        "prompt": prompt,
        "duration": duration,
        "ratio": "16:9",
        "seed": 42,
    }
    r = requests.post(f"{RUNWAY_API_BASE}/generations", headers=HEADERS, json=payload, timeout=60)
    r.raise_for_status()
    job = r.json()
    job_id = job.get("id")
    # poll
    for _ in range(240):
        time.sleep(3)
        jr = requests.get(f"{RUNWAY_API_BASE}/generations/{job_id}", headers=HEADERS, timeout=30)
        jr.raise_for_status()
        data = jr.json()
        status = data.get("status")
        if status == "succeeded":
            return data.get("output_url")
        if status in ("failed","canceled"):
            break
    return None