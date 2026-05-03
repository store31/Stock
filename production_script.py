import os
import subprocess
import requests
import time

PEXELS_KEY = os.getenv("PEXELS_KEY")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

def produce_final_subtitle_version():
    temp_dir = os.getcwd() # استخدام المسار الحالي لضمان عمل libass
    
    # 1. توليد الصوت
    script = "The intelligence of the future is being built today. Join us in this journey to explore more."
    audio_path = os.path.join(temp_dir, "final_voice.mp3")
    subprocess.run(f'edge-tts --text "{script}" --write-media {audio_path}', shell=True)

    # 2. جلب وتجهيز المقاطع (30 ثانية لكل مقطع كما طلبت)
    headers = {"Authorization": PEXELS_KEY}
    url = "https://api.pexels.com/videos/search?query=future&per_page=3"
    res = requests.get(url, headers=headers).json()
    v_links = [v['video_files'][0]['link'] for v in res.get('videos', [])]

    processed = []
    for i, link in enumerate(v_links):
        out = f"part_{i}.mp4"
        # توحيد المقاسات والمدة لـ 30 ثانية
        subprocess.run(f"ffmpeg -y -i {link} -vf 'scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,fps=30' -t 30 {out}", shell=True)
        processed.append(out)

    # 3. الدمج الصافي (Merged)
    inputs = "".join([f"-i {f} " for f in processed])
    filter_c = "".join([f"[{i}:v]" for i in range(len(processed))]) + f"concat=n={len(processed)}:v=1:a=0[v]"
    merged_path = os.path.join(temp_dir, "merged_video.mp4")
    subprocess.run(f"ffmpeg -y {inputs} -filter_complex '{filter_c}' -map '[v]' {merged_path}", shell=True)

    # 4. إنشاء ملف Subtitle (SRT)
    srt_path = os.path.join(temp_dir, "subtitles.srt")
    srt_content = """1
00:00:00,000 --> 00:00:05,000
The intelligence of the future

2
00:00:05,000 --> 00:00:10,000
is being built today

3
00:00:10,000 --> 00:00:20,000
Join us in this journey
"""
    with open(srt_path, "w", encoding='utf-8') as f:
        f.write(srt_content)

    # 5. FFmpeg النهائي مع دعم libass وستايل احترافي
    final_output = "factory_subtitle_pro.mp4"
    
    # اجتهاد: إضافة ستايل للنص (Alignment=2 هو الأسفل، BorderStyle=3 هو خلفية الصندوق)
    style = "Alignment=2,MarginV=100,FontSize=20,PrimaryColour=&H00FFFF,OutlineColour=&H000000,BorderStyle=3,Outline=1,Shadow=1"
    
    # استخدام المسار المطلق للملف وتفادي مشاكل الهروب (Escaping) في Linux
    abs_srt_path = srt_path.replace("\\", "/").replace(":", "\\:")
    
    cmd = (
        f"ffmpeg -y -i {merged_path} -i {audio_path} "
        f"-vf \"subtitles='{abs_srt_path}':force_style='{style}'\" "
        f"-c:v libx264 -c:a aac -shortest {final_output}"
    )
    
    print(f"🎬 Running final command: {cmd}")
    subprocess.run(cmd, shell=True)

    # 6. الإرسال لتلغرام
    with open(final_output, "rb") as v:
        requests.post(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendVideo", data={"chat_id": CHAT_ID}, files={"video": v})

if __name__ == "__main__":
    produce_final_subtitle_version()
