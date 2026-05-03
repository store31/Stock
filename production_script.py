import os
import subprocess
import requests
import time

PEXELS_KEY = os.getenv("PEXELS_KEY")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

def produce_ultra_stable():
    # نخدمو كلش في المجلد الحالي لتفادي مشاكل الصلاحيات
    temp_prefix = "vid_"
    
    # 1. الصوت (مهم جداً)
    script = "The intelligence of the future is being built today. Join us in this journey."
    audio_path = "final_audio.mp3"
    subprocess.run(f'edge-tts --text "{script}" --write-media {audio_path}', shell=True)

    # 2. جلب وتجهيز 3 مقاطع (باش نضمنوا السرعة والنجاح)
    headers = {"Authorization": PEXELS_KEY}
    url = "https://api.pexels.com/videos/search?query=cyber&per_page=3"
    res = requests.get(url, headers=headers).json()
    v_links = [v['video_files'][0]['link'] for v in res.get('videos', [])]

    processed = []
    for i, link in enumerate(v_links):
        out = f"p{i}.mp4"
        # توحيد المقاسات والـ FPS
        subprocess.run(f"ffmpeg -y -i {link} -vf 'scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,fps=30' -t 10 {out}", shell=True)
        processed.append(out)

    # 3. الدمج البسيط
    inputs = "".join([f"-i {f} " for f in processed])
    filter_c = "".join([f"[{i}:v]" for i in range(len(processed))]) + f"concat=n={len(processed)}:v=1:a=0[v]"
    subprocess.run(f"ffmpeg -y {inputs} -filter_complex '{filter_c}' -map '[v]' merged.mp4", shell=True)

    # 4. المونتاج النهائي (نصوص بسيطة جداً لتفادي الـ Failure)
    final_output = "factory_ready.mp4"
    # استعملت نصوص أساسية جداً وبدون فلاتر معقدة
    cmd = (
        f"ffmpeg -y -i merged.mp4 -i {audio_path} "
        f"-vf \"drawtext=text='NEURAL TECH':x=(w-text_w)/2:y=300:fontsize=60:fontcolor=white:enable='between(t,0,5)', "
        f"drawtext=text='FUTURE IS NOW':x=(w-text_w)/2:y=h-400:fontsize=50:fontcolor=yellow:enable='between(t,5,30)'\" "
        f"-c:v libx264 -c:a aac -shortest {final_output}"
    )
    subprocess.run(cmd, shell=True)

    # 5. الإرسال الآمن (بدون مسح)
    print("📤 Sending to Telegram...")
    time.sleep(2) # راحة قصيرة للتأكد من اكتمال الملف
    with open(final_output, "rb") as v:
        requests.post(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendVideo", data={"chat_id": CHAT_ID}, files={"video": v})

if __name__ == "__main__":
    produce_ultra_stable()
