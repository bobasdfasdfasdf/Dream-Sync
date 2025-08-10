# 🌙 DreamSync — Speak Your Dream, See It Come Alive

Turn a spoken dream description into a **short cinematic video** with captions and optional voiceover/music — perfect for a hackathon demo.

**Made for FAF Multimodal Hackathon** • **Multimodal: Voice → Narrative → Video → Captions → (TTS/Music)**

---

## ✨ Why DreamSync? (100 words for Devpost)
Memories of dreams fade quickly, and visualizing them is nearly impossible—until now. DreamSync lets you describe a dream out loud and instantly transforms it into a short cinematic scene with AI-generated visuals, optional voiceover, and captions. By fusing speech-to-text (or typed input), LLM narrative shaping, text-to-video (or fallback slideshow), and audio assembly, we preserve dreams as immersive experiences to rewatch and share. Beyond personal use, DreamSync helps therapists, artists, and storytellers turn fleeting thoughts into vivid worlds—blurring the line between imagination and reality.

---

## 🧩 Architecture (One Flow, Big Payoff)
```
Mic/Typed Dream → LLM (storyboard: title/logline/shots)
      ↓
Video per shot (Runway/PIKA/Luma) → concat
      ↓
Optional TTS (ElevenLabs) + background music
      ↓
Burn short captions → final MP4
```

- **Input:** Mic upload (.wav/.mp3) or typed text
- **LLM:** OpenAI (storyboard + captions polish)
- **Video:** Runway (or fallback: Ken Burns slideshow from placeholders)
- **Audio:** Optional TTS via ElevenLabs (music track slot included)
- **Assembly:** ffmpeg/moviepy for stitching & captions

---

## 🚀 Quickstart
```bash
git clone <your-repo-url>.git
cd dreamsync
pip install -r requirements.txt

# Keys
cp .env.example .env   # fill OPENAI_API_KEY and one video gen key (RUNWAY_API_KEY, etc.)

# Verify ffmpeg
ffmpeg -version

# Run
streamlit run app/app.py
```

**No video-gen key?** The app automatically falls back to a clean slideshow with Ken Burns motion so your demo still looks polished.

---

## 🧪 Demo Steps (Happy Path)
1. **Input**: Paste a one-sentence dream or upload a short audio.
2. **Generate Narrative**: Produces 4–6 shots with visuals/mood/durations.
3. **Create Video**: Generates per-shot clips (or slideshow) and concatenates.
4. **Add Voiceover (optional)**: TTS narration from the logline + captions.
5. **Burn Captions**: Hard subtitles onto the final video.
6. **Export**: Final MP4 in `outputs/dreamsync_final.mp4`.

---

## 🗃 Submission Helpers
- `submission/100_words.txt` — copy/paste to Devpost.
- `demo_script.md` — timed script for a crisp 2‑minute video.
- `outputs/` — all generated assets land here.

---

## 🧱 Tech Stack
- **Python**: Streamlit, requests, python-dotenv
- **AI**: OpenAI (gpt-4o-mini), Runway (or other), ElevenLabs (optional)
- **Media**: ffmpeg, moviepy, pydub
- **Scaffold**: MIT License, commit template, submission files

---

## ⚙️ Environment
Create `.env` from `.env.example` and fill:
```
OPENAI_API_KEY=sk-...
RUNWAY_API_KEY=rwk_...      # or PIKA/LUMA if you swap clients
ELEVENLABS_API_KEY=el-...   # optional
```

---

## 🧭 Project Structure
```
app/
  app.py
  prompts/narrative_template.txt
  services/
    openai_client.py
    runway_client.py
    elevenlabs_client.py
    audio.py
  utils/
    ffmpeg_tools.py
outputs/
submission/
  100_words.txt
demo_script.md
.gitmessage.txt
```

---

## ✅ Demo Readiness Checklist
- [ ] `.env` keys set (OpenAI + *one* video provider)
- [ ] `ffmpeg` installed and on PATH
- [ ] One dream text ready (10–25 words works best)
- [ ] Dry run end‑to‑end once; confirm `outputs/dreamsync_final.mp4`
- [ ] Record your screen + mic for the 2‑min demo

---

## 📝 License
MIT — see `LICENSE`.