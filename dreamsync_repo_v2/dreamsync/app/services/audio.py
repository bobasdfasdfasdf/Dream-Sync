import os
from pydub import AudioSegment

def mix_music_and_voiceover(music_path: str, voice_path: str, out_path: str, music_db: float = -14.0, duck_db: float = -6.0):
    music = AudioSegment.from_file(music_path)
    voice = AudioSegment.from_file(voice_path)
    # Normalize volumes
    music = music + music_db
    voice = voice + 0
    # Sidechain-duck music under voice
    mixed = music.overlay(voice - abs(duck_db))
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    mixed.export(out_path, format="mp3")
    return out_path