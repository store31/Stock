
import os
import time
import requests
import subprocess
import random

# 🔑 الإعدادات
PEXELS_KEY = os.getenv("PEXELS_KEY")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

def produce_ultra_short():
    temp_dir = "pro_work"
    os.makedirs(temp_dir, exist_ok=True)
    
    # 1. تحميل لوغو يوتيوب وSubscribe
    subprocess.run(f"curl -L https://i.imgur.com/8mS6DUL.png -o {temp_dir}/yt_logo.png", shell=True)
    subprocess.run(f"curl -L https://i.imgur.com/3f0I5Ym.png -o {temp_dir}/sub.png", shell=True)

    print("🏭 Manufacturing 1 Ultra-Pro Video (Bottom Subs)...")
    
    # 2. سكريبت طويل (أكثر من 90 ثانية)
    script = (
        "Welcome to the future of neural intelligence. Today we dive deep into how AI is changing our daily lives. "
        "From the way we communicate to the complex systems running our cities, neural networks are everywhere. "
        "Imagine a world where technology understands your needs before you even speak. That world is already here. "
        "We are witnessing a revolution in machine learning that will redefine humanity. "
        "Don't forget to follow our journey into the matrix of tech. The best is yet to come. "
        "Stay curious, stay informed, and let's build the future together."
    )
    
    # 3. الصوت (Edge-TTS)
    audio_path = f"{temp_dir}/pro_audio.mp3"
    subprocess.run(f'edge-tts --text "{script}" --write-media {audio_path} --voice en-US-GuyNeural --rate=+10%', shell=True)
    
    # 4. جلب فيديوهات متنوعة (للوصول لـ 95 ثانية)
    headers = {"Authorization": PEXELS_KEY}
    url = "https://api.pexels.com/videos/search?query=technology&per_page=5&orientation=portrait"
    res = requests.get(url, headers=headers).json()
    v_links = [v['video_files'][0]['link'] for v in res.get('videos', [])]
    
    for idx, link in enumerate(v_links[:4]):
        subprocess.run(f"curl -L {link} -o {temp_dir}/v{idx}.mp4", shell=True)
        subprocess.run(f"ffmpeg -y -i {temp_dir}/v{idx}.mp4 -vf 'scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,fps=30' -t 25 {temp_dir}/part{idx}.mp4", shell=True)
    
    with open(f"{temp_dir}/list.txt", "w") as f:
        for idx in range(4): f.write(f"file 'part{idx}.mp4'\n")
    subprocess.run(f"ffmpeg -y -f concat -safe 0 -i {temp_dir}/list.txt -c copy {temp_dir}/full_v.mp4", shell=True)

    # 5. ملف الترجمة
    srt_path = f"{temp_dir}/pro.srt"
    with open(srt_path, "w") as f:
        f.write("1\n00:00:01,000 --> 00:01:35,000\nTHE FUTURE IS NOW\nEXPLORE THE NEURAL NET")

    # ✨ التعديل: الترجمة في الأسفل (Alignment=2) مع خط واضح
    style = "Alignment=2,MarginV=80,FontSize=22,PrimaryColour=&HFFFFFF,OutlineColour=&H000000,BorderStyle=3,FontName=Arial"
    
    final_output = "ultra_pro_video.mp4"
    cmd = (
        f"ffmpeg -y -i {temp_dir}/full_v.mp4 -i {audio_path} -i {temp_dir}/yt_logo.png -i {temp_dir}/sub.png "
        f"-filter_complex \"[0:v][1:a]concat=n=1:v=1:a=1[v1];"
        f"[v1]subtitles={srt_path}:force_style='{style}'[v2];"
        f"[v2][2:v]overlay=x=main_w-overlay_w-50:y=50[v3];"
        f"[v3][3:v]overlay=x=50:y=main_h-overlay_h-150\" "
        f"-t 95 -c:v libx264 -c:a aac -b:a 192k {final_output}"
    )
    subprocess.run(cmd, shell=True)

    # 6. الإرسال لتلغرام
    url_tg = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendVideo"
    with open(final_output, "rb") as v:
        requests.post(url_tg, files={"video": v}, data={"chat_id": CHAT_ID, "caption": "🌟 *Ultra-Pro (Bottom Subs) Ready!*", "parse_mode": "Markdown"})

if __name__ == "__main__":
    produce_ultra_short()
