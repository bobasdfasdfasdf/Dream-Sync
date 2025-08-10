import os, json, time, tempfile, uuid, pathlib
import streamlit as st
from dotenv import load_dotenv
from app.services.openai_client import dream_to_storyboard, refine_caption
from app.services.runway_client import create_text_to_video
from app.services.elevenlabs_client import tts_to_file
from app.utils.ffmpeg_tools import burn_captions, ken_burns_from_images
from jinja2 import Template

load_dotenv()

st.set_page_config(page_title="DreamSync", page_icon="🌙", layout="wide")
st.title("🌙 DreamSync – Speak Your Dream, See It Come Alive")

with open("app/prompts/narrative_template.txt", "r", encoding="utf-8") as f:
    TEMPLATE = f.read()

st.sidebar.header("Input")
mode = st.sidebar.radio("Describe your dream via:", ["Microphone (upload .wav/.mp3)", "Type text"])

uploaded_audio = None
dream_text = None

if mode.startswith("Microphone"):
    uploaded_audio = st.sidebar.file_uploader("Upload audio file", type=["wav","mp3","m4a"])
else:
    dream_text = st.sidebar.text_area("Type your dream", height=160, placeholder="I was flying over a city made of glass towers...")

col1, col2 = st.columns(2)
with col1:
    if st.button("1) Generate Narrative / Shots", use_container_width=True):
        if not dream_text and not uploaded_audio:
            st.error("Please provide audio or text.")
        else:
            if uploaded_audio and not dream_text:
                # For hackathon speed, rely on client-side/pre-transcribed text (or bring Whisper locally)
                dream_text = st.text_area("Transcribed (paste here if needed)", height=120, value=dream_text or "", help="Paste your transcription if not using Whisper locally")
            story = dream_to_storyboard(dream_text or "A short surreal dream in a neon city.", TEMPLATE)
            st.session_state["story"] = story
            st.success("Storyboard generated!")
            st.json(story)

with col2:
    if st.button("2) Create Video", use_container_width=True):
        story = st.session_state.get("story")
        if not story:
            st.error("Generate a storyboard first.")
        else:
            outputs_dir = pathlib.Path("outputs"); outputs_dir.mkdir(exist_ok=True, parents=True)
            video_paths = []
            # Try text-to-video per shot; fallback to Ken Burns over placeholder image URLs
            for shot in story["shots"]:
                prompt = f"{shot['visual_prompt']} | mood: {shot['mood']} | action: {shot['action']} | ultra cinematic, film grain"
                url = create_text_to_video(prompt, duration=int(shot.get("duration_sec", 4)))
                if url:
                    # download asset
                    local = outputs_dir / f"shot_{shot['id']}.mp4"
                    try:
                        import yt_dlp
                        ydl_opts = {"outtmpl": str(local)}
                        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                            ydl.download([url])
                        video_paths.append(str(local))
                    except Exception as e:
                        st.warning(f"Runway download failed, will fallback to slideshow for shot {shot['id']}.")
                else:
                    # collect placeholder images from LLM prompts (here we just create a local placeholder)
                    placeholder = outputs_dir / f"shot_{shot['id']}.png"
                    from PIL import Image, ImageDraw, ImageFont
                    img = Image.new("RGB",(1920,1080),(20,20,30))
                    d = ImageDraw.Draw(img)
                    d.text((40,40), f"Shot {shot['id']}\n{shot['visual_prompt']}", fill=(220,220,220))
                    img.save(placeholder)
                    ken_out = outputs_dir / f"shot_{shot['id']}_slide.mp4"
                    ken_burns_from_images([str(placeholder)], dur_per=int(shot.get("duration_sec",4)), out_path=str(ken_out))
                    video_paths.append(str(ken_out))

            final_path = str(outputs_dir / "dreamsync_raw.mp4")
            from app.utils.ffmpeg_tools import concat_videos
            concat_videos(video_paths, final_path)
            st.session_state["video_path"] = final_path
            st.video(final_path)
            st.success("Base video assembled.")

st.divider()
st.header("Enhance")

c1, c2, c3 = st.columns(3)
with c1:
    if st.button("Add Voiceover (optional)", use_container_width=True):
        story = st.session_state.get("story")
        video_path = st.session_state.get("video_path")
        if not (story and video_path):
            st.error("Create a video first.")
        else:
            narration = story["logline"] + ". " + " ".join([s["caption"] for s in story["shots"]])
            voice_path = "outputs/voiceover.mp3"
            out = tts_to_file(narration, out_path=voice_path)
            if out:
                st.audio(out)
                st.session_state["voice_path"] = out
                st.success("Voiceover generated.")
            else:
                st.warning("No ElevenLabs key found. Skipping.")

with c2:
    if st.button("Burn Captions", use_container_width=True):
        story = st.session_state.get("story")
        video_path = st.session_state.get("video_path")
        if not (story and video_path):
            st.error("Create a video first.")
        else:
            # build caption timeline
            cur = 0.0
            caps = []
            for s in story["shots"]:
                dur = float(s.get("duration_sec", 4))
                caps.append({"start": round(cur,2), "end": round(cur+dur-0.5,2), "text": refine_caption(s["caption"])})
                cur += dur
            out_path = "outputs/dreamsync_final.mp4"
            try:
                burn_captions(video_path, caps, out_path)
                st.session_state["final_video"] = out_path
                st.video(out_path)
                st.success("Final video with captions is ready.")
            except Exception as e:
                st.error(f"FFmpeg error: {e}")

with c3:
    if st.button("Export Assets", use_container_width=True):
        outputs_dir = pathlib.Path("outputs"); outputs_dir.mkdir(exist_ok=True, parents=True)
        st.success(f"Assets saved under: {outputs_dir.resolve()}")