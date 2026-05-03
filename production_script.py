import os
import subprocess
import requests
import time

PEXELS_KEY = os.getenv("PEXELS_KEY")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

def run(cmd):
    print("▶", cmd)
    subprocess.run(cmd, shell=True, check=True)

def produce_video():
    # التعديل الوحيد لضمان اشتغال السيبتايتل في GitHub Actions
    base_dir = os.getcwd()
    srt_filename = "sub.srt"
    srt_path = os.path.join(base_dir, srt_filename).replace("\\", "/").replace(":", "\\:")
    
    script = "The intelligence of the future is being built today. Join us in this journey to explore more."

    # 1. AUDIO
    run(f'edge-tts --text "{script}" --write-media voice.mp3')

    # 2. FETCH VIDEOS
    headers = {"Authorization": PEXELS_KEY}
    url = "https://api.pexels.com/videos/search?query=technology&per_page=6"
    data = requests.get(url, headers=headers).json()
    links = [v['video_files'][0]['link'] for v in data.get("videos", []) if v.get('video_files')]

    if not links:
        raise Exception("❌ No videos from Pexels")

    # 3. PROCESS VIDEOS (30s each)
    processed = []
    for i, link in enumerate(links[:3]):
        out = f"v{i}.mp4"
        run(f"ffmpeg -y -i \"{link}\" -vf scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,fps=30 -t 30 {out}")
        processed.append(out)

    # 4. CONCAT
    with open("list.txt", "w") as f:
        for p in processed:
            f.write(f"file '{os.path.abspath(p)}'\n")
    run("ffmpeg -y -f concat -safe 0 -i list.txt -c copy merged.mp4")

    # 5. SUBTITLE
    srt = """1
00:00:00,000 --> 00:00:04,000
The future is being built

2
00:00:04,000 --> 00:00:08,000
with artificial intelligence

3
00:00:08,000 --> 00:00:12,000
Join the revolution
"""
    with open(srt_filename, "w", encoding="utf-8") as f:
        f.write(srt)

    # 6. FINAL (استعمال srt_path لضمان التعرف على الملف في Linux)
    # زدت لك ستايل بسيط باش النص يبان واضح في GitHub
    style = "Alignment=2,MarginV=100,FontSize=22,PrimaryColour=&H00FFFF,BorderStyle=3"
    
    cmd = (
        f"ffmpeg -y -i merged.mp4 -i voice.mp3 "
        f"-vf \"subtitles='{srt_path}':force_style='{style}'\" "
        f"-c:v libx264 -preset fast -crf 23 -c:a aac -shortest output.mp4"
    )
    run(cmd)

    # 7. SEND
    print("📤 Sending...")
    time.sleep(2)
    with open("output.mp4", "rb") as v:
        requests.post(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendVideo",
                      data={"chat_id": CHAT_ID}, files={"video": v})
    print("✅ DONE")

if __name__ == "__main__":
    produce_video()
