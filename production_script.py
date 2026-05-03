
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
    # المنطق الوحيد المعدل: تهيئة المسار المطلق للملفات في Linux
    base_dir = os.getcwd()
    # تحويل المسار ليكون متوافق مع فلتر subtitles في ffmpeg
    srt_path = os.path.join(base_dir, "sub.srt").replace("\\", "/").replace(":", "\\:")
    
    script = "The intelligence of the future is being built today. Join us in this journey to explore more."

    # 1. AUDIO
    run(f'edge-tts --text "{script}" --write-media voice.mp3')

    # 2. FETCH VIDEOS
    headers = {"Authorization": PEXELS_KEY}
    url = "https://api.pexels.com/videos/search?query=technology&per_page=6"
    data = requests.get(url, headers=headers).json()

    links = []
    for v in data.get("videos", []):
        try:
            links.append(v['video_files'][0]['link'])
        except:
            pass

    if len(links) == 0:
        raise Exception("❌ No videos from Pexels")

    # 3. PROCESS VIDEOS
    processed = []
    for i, link in enumerate(links[:3]):
        out = f"v{i}.mp4"
        run(f"ffmpeg -y -i \"{link}\" -vf scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,fps=30 -t 30 {out}")
        processed.append(out)

    while len(processed) < 3:
        processed.append(processed[0])

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
    with open("sub.srt", "w", encoding="utf-8") as f:
        f.write(srt)

    # 6. FINAL (استخدام srt_path المنطقي لضمان العمل في Linux)
    cmd = (
        f"ffmpeg -y -i merged.mp4 -i voice.mp3 "
        f"-vf \"subtitles='{srt_path}'\" "
        f"-c:v libx264 -preset fast -crf 23 "
        f"-c:a aac -shortest output.mp4"
    )
    run(cmd)

    # 7. SEND
    print("📤 Sending...")
    time.sleep(2)

    with open("output.mp4", "rb") as v:
        requests.post(
            f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendVideo",
            data={"chat_id": CHAT_ID},
            files={"video": v}
        )

    print("✅ DONE")

if __name__ == "__main__":
    produce_video()
