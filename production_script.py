import os
import subprocess
import requests
import time

PEXELS_KEY = os.getenv("PEXELS_KEY")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

def produce_safe_upload():
    temp_dir = "secure_storage"
    os.makedirs(temp_dir, exist_ok=True)
    
    # 1. الصوت
    script = "Innovation is the key to the future. Neural networks are rewriting the rules of technology. Stay tuned for more."
    audio_path = f"{temp_dir}/voice.mp3"
    subprocess.run(f'edge-tts --text "{script}" --write-media {audio_path}', shell=True)

    # 2. جلب 4 مقاطع لضمان فيديو طويل
    headers = {"Authorization": PEXELS_KEY}
    url = "https://api.pexels.com/videos/search?query=future&per_page=4"
    res = requests.get(url, headers=headers).json()
    v_links = [v['video_files'][0]['link'] for v in res.get('videos', [])]

    processed = []
    for i, link in enumerate(v_links):
        output = f"{temp_dir}/p{i}.mp4"
        # توحيد كلش لضمان الدمج
        subprocess.run(f"ffmpeg -y -i {link} -vf 'scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,fps=30' -t 15 {output}", shell=True)
        processed.append(output)

    # 3. الدمج الصافي (لحام المقاطع)
    inputs = "".join([f"-i {f} " for f in processed])
    filter_concat = "".join([f"[{i}:v]" for i in range(len(processed))]) + f"concat=n={len(processed)}:v=1:a=0[v]"
    merged_path = f"{temp_dir}/merged.mp4"
    subprocess.run(f"ffmpeg -y {inputs} -filter_complex '{filter_concat}' -map '[v]' {merged_path}", shell=True)

    # 4. المونتاج (نصوص متغيرة + إخفاء العنوان)
    final_output = "ultimate_secure_video.mp4"
    # النصوص محروقة في الفيديو مباشرة لضمان الظهور
    draw_v = (
        "drawtext=text='TECH REVOLUTION':fontcolor=white:fontsize=70:x=(w-text_w)/2:y=(h-text_h)/4:enable='between(t,0,5)':box=1:boxcolor=black@0.5,"
        "drawtext=text='THE FUTURE IS HERE':fontcolor=yellow:fontsize=50:x=(w-text_w)/2:y=h-400:enable='between(t,5,20)':box=1:boxcolor=black@0.7,"
        "drawtext=text='SUBSCRIBE FOR MORE':fontcolor=white:fontsize=50:x=(w-text_w)/2:y=h-400:enable='between(t,20,60)':box=1:boxcolor=black@0.7"
    )

    subprocess.run(f"ffmpeg -y -i {merged_path} -i {audio_path} -vf \"{draw_v}\" -c:v libx264 -c:a aac -shortest {final_output}", shell=True)

    # 5. الإرسال لتلغرام (بدون مسح!)
    print("📤 Sending to Telegram... waiting for confirmation.")
    with open(final_output, "rb") as v:
        response = requests.post(
            f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendVideo", 
            data={"chat_id": CHAT_ID, "caption": "🚀 *Safe Upload Complete!*"}, 
            files={"video": v}
        )
    
    if response.status_code == 200:
        print("✅ Video sent successfully!")
    else:
        print(f"❌ Error sending: {response.text}")

    # ملاحظة: GitHub Actions غادي يمسح كل المجلدات آلياً بمجرد انتهاء الـ Job.
    # هكذا نضمنوا أن الفيديو يبقى في الماكينة حتى يوصل كامل لتلغرام.

if __name__ == "__main__":
    produce_safe_upload()
