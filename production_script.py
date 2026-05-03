import os
import subprocess
import requests
import time

PEXELS_KEY = os.getenv("PEXELS_KEY")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

def run(cmd):
    subprocess.run(cmd, shell=True, check=True)

def produce_masterpiece():
    # القصة (3 دقائق)
    script = "Once upon a time... [القصة اللي تفاهمنا عليها]"
    
    run(f'edge-tts --text "{script}" --write-media voice.mp3')

    # جلب الفيديوهات (Multi-Query)
    queries = ["magic cat", "fantasy forest", "space kitten"]
    links = []
    for q in queries:
        try:
            r = requests.get(f"https://api.pexels.com/videos/search?query={q}&per_page=5", 
                             headers={"Authorization": PEXELS_KEY}).json()
            links.extend([v['video_files'][0]['link'] for v in r.get('videos', [])])
        except: continue

    # معالجة المقاطع (تكرار لضمان الطول)
    processed = []
    final_links = (links * 5)[:20]
    for i, link in enumerate(final_links):
        out = f"v{i}.mp4"
        run(f"ffmpeg -y -i \"{link}\" -vf scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,fps=25 -t 9 -preset ultrafast {out}")
        processed.append(out)

    # الدمج
    with open("list.txt", "w") as f:
        for p in processed: f.write(f"file '{os.path.abspath(p)}'\n")
    run("ffmpeg -y -f concat -safe 0 -i list.txt -c copy merged.mp4")
    
    # الرندرة النهائية (ضغط الحجم لضمان وصوله لتلغرام)
    final_output = "video_final.mp4"
    run(f"ffmpeg -y -i merged.mp4 -i voice.mp3 -c:v libx264 -preset ultrafast -crf 32 -c:a aac -shortest {final_output}")

    # 📤 الإرسال مع كاشف الأخطاء
    print(f"📡 Sending {final_output} to Telegram...")
    with open(final_output, "rb") as v:
        files = {"video": v}
        data = {"chat_id": CHAT_ID, "caption": "🐱 *Simba Story Ready!*"}
        response = requests.post(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendVideo", data=data, files=files)
        
        # هاد السطر غادي يوريلك علاه ما وصلكش في GitHub Logs
        print(f"📩 Telegram Response: {response.text}")

if __name__ == "__main__":
    produce_masterpiece()
