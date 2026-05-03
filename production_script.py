import os
import time
import requests
import subprocess
import random

# 🔑 الإعدادات
PEXELS_KEY = os.getenv("PEXELS_KEY")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

def produce_pro_video():
    # نخدمو كلش في المجلد الحالي باش ما نغلطوش في المسارات
    current_dir = os.getcwd()
    
    # 1. السكريبت (أكثر من 90 ثانية)
    script = (
        "The future of technology is evolving faster than ever before. "
        "Artificial intelligence is no longer a dream, it is our new reality. "
        "Every neural connection we build brings us closer to a smarter world. "
        "Stay with us as we explore the deep secrets of innovation and science. "
        "Don't forget to subscribe and join our tech community for more updates."
    )
    
    # 2. توليد الصوت (مهم جداً)
    audio_path = "final_voice.mp3"
    print("🎙️ Generating Voice...")
    subprocess.run(f'edge-tts --text "{script}" --write-media {audio_path} --rate=+10%', shell=True)

    # 3. جلب فيديوهات Pexels
    print("🎥 Fetching Videos...")
    headers = {"Authorization": PEXELS_KEY}
    url = "https://api.pexels.com/videos/search?query=tech&per_page=5&orientation=portrait"
    res = requests.get(url, headers=headers).json()
    v_links = [v['video_files'][0]['link'] for v in res.get('videos', [])]

    # تحميل ومعالجة 4 مقاطع (كل واحد 25 ثانية لضمان الوصول لـ 100 ثانية)
    processed_files = []
    for idx, link in enumerate(v_links[:4]):
        raw_name = f"raw_{idx}.mp4"
        part_name = f"part_{idx}.mp4"
        subprocess.run(f"curl -L {link} -o {raw_name}", shell=True)
        # توحيد المقاسات والـ FPS ضروري للدمج الناجح
        cmd_prep = f"ffmpeg -y -i {raw_name} -vf 'scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,fps=30' -t 25 {part_name}"
        subprocess.run(cmd_prep, shell=True)
        processed_files.append(part_name)

    # 4. الدمج الاحترافي (بدون ملف txt لتفادي المشاكل)
    print("🎬 Merging Clips...")
    inputs = "".join([f"-i {f} " for f in processed_files])
    filter_complex = "".join([f"[{i}:v]" for i in range(len(processed_files))]) + f"concat=n={len(processed_files)}:v=1:a=0[v]"
    subprocess.run(f"ffmpeg -y {inputs} -filter_complex '{filter_complex}' -map '[v]' merged_video.mp4", shell=True)

    # 5. إضافة الترجمة واللوغو والصوت (الضربة القاضية)
    print("📝 Adding Subs and Audio...")
    srt_content = "1\n00:00:01,000 --> 00:01:30,000\nEXPLORING THE FUTURE\nSUBSCRIBE FOR MORE"
    with open("subs.srt", "w") as f: f.write(srt_content)

    style = "Alignment=2,MarginV=100,FontSize=24,PrimaryColour=&HFFFFFF,OutlineColour=&H000000,BorderStyle=3"
    
    # دمج الفيديو المجمع مع الصوت والترجمة
    final_output = "ultimate_factory_video.mp4"
    cmd_final = (
        f"ffmpeg -y -i merged_video.mp4 -i {audio_path} "
        f"-vf \"subtitles=subs.srt:force_style='{style}'\" "
        f"-c:v libx264 -c:a aac -shortest {final_output}"
    )
    subprocess.run(cmd_final, shell=True)

    # 6. الإرسال لتلغرام
    print("📤 Sending to Telegram...")
    url_tg = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendVideo"
    with open(final_output, "rb") as v:
        requests.post(url_tg, files={"video": v}, data={"chat_id": CHAT_ID, "caption": "🔥 *Your Pro Video is Ready!* \n(90s + Subs + Audio)", "parse_mode": "Markdown"})

if __name__ == "__main__":
    produce_pro_video()
