import subprocess, os, json, tempfile, textwrap

def burn_captions(video_path: str, captions: list, out_path: str) -> str:
    """Burn simple captions as hard subtitles using drawtext filters.
    captions: list of dicts [{start, end, text}]
    """
    # Build filter_complex with drawtext per segment
    # Requires a truetype font on system; fallback to sans-serif
    draw_cmds = []
    for cap in captions:
        start = cap["start"]
        end = cap["end"]
        txt = cap["text"].replace(':','\:').replace("'", "\'")
        draw = (
          f"drawtext=font='DejaVuSans':text='{txt}':x=(w-text_w)/2:y=h-120:"
          f"fontsize=42:fontcolor=white:box=1:boxcolor=black@0.55:boxborderw=12:"
          f"enable='between(t,{start},{end})'"
        )
        draw_cmds.append(draw)
    filter_complex = ",".join(draw_cmds)
    cmd = [
        "ffmpeg","-y","-i",video_path,
        "-vf", filter_complex,
        "-c:a","copy",
        out_path
    ]
    subprocess.run(cmd, check=True)
    return out_path

def concat_videos(video_paths, out_path):
    # Create a concat list file
    list_path = out_path + ".txt"
    with open(list_path, "w", encoding="utf-8") as f:
        for p in video_paths:
            f.write(f"file '{os.path.abspath(p)}'\n")
    cmd = ["ffmpeg","-y","-f","concat","-safe","0","-i",list_path,"-c","copy", out_path]
    subprocess.run(cmd, check=True)
    os.remove(list_path)
    return out_path

def ken_burns_from_images(image_paths, dur_per=4, out_path="outputs/slideshow.mp4"):
    # Simple pan/zoom Ken Burns
    filters = []
    inputs = []
    for i, img in enumerate(image_paths):
        inputs += ["-loop","1","-t",str(dur_per),"-i",img]
        filters.append(f"[{i}:v]scale=1920:1080,zoompan=z='min(zoom+0.0008,1.3)':d=125:s=1920x1080,setsar=1[v{i}]")
    filter_complex = ";".join(filters) + ";" + "".join([f"[v{i}]" for i in range(len(image_paths))]) + f"concat=n={len(image_paths)}:v=1:a=0,format=yuv420p[v]"
    cmd = ["ffmpeg","-y"] + inputs + ["-filter_complex", filter_complex, "-map","[v]", out_path]
    subprocess.run(cmd, check=True)
    return out_path