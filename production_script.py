import os
import subprocess
import requests
import time

# 🔑 Secrets
PEXELS_KEY = os.getenv("PEXELS_KEY")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

def run(cmd):
    print(f"▶ {cmd}")
    subprocess.run(cmd, shell=True, check=True)

def produce_masterpiece():
    # 1. القصة
    script = (
        "Once upon a time, in a magical village of pumpkins, lived Simba the ginger cat. "
        "His tail glowed with magic! One day, the Rainbow Cloud vanished. "
        "Simba and Pip the bird went to the Cave of Silence. "
        "Simba purred with joy, his tail lit up the darkness, and the cloud was free! "
        "The world became colorful again. Happiness is the greatest magic. The end."
    )
    
    run(f'edge-tts --text "{script}" --write-media voice.mp3')

    # 2. جلب الفيديوهات
    queries = ["magic cat", "fantasy forest", "mystical nature"]
    links = []
    for q in queries:
        try:
            r = requests.get(f"https://api.pexels.com/videos/search?query={q}&per_page=10", 
                             headers={"Authorization": PEXELS_KEY}).json()
            links.extend([v['video_files'][0]['link'] for v in r.get('videos', [])])
        except: continue

    # 3. معالجة المقاطع
    processed = []
    for i, link in enumerate((links * 5)[:20]):
        out = f"v{i}.mp4"
        run(f"ffmpeg -y -i \"{link}\" -vf scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,fps=25 -t 9 -preset ultrafast {out}")
        processed.append(out)

    # 4. الدمج
    with open("list.txt", "w") as f:
        for p in processed: f.write(f"file '{os.path.abspath(p)}'\n")
    run("ffmpeg -y -f concat -safe 0 -i list.txt -c copy merged.mp4")

    # 5. الرندرة النهائية
    final_output = f"Simba_Adventure_{int(time.time())}.mp4"
    run(f"ffmpeg -y -i merged.mp4 -i voice.mp3 -map 0:v:0 -map 1:a:0 -c:v libx264 -preset ultrafast -crf 23 -c:a aac -t 180 {final_output}")

    # 6. الرفع لـ BashUpload (أكثر استقراراً من Transfer.sh)
    print(f"🚀 Uploading to BashUpload...")
    # رفع الملف واستخراج الرابط
    upload_cmd = f"curl https://bashupload.com/{final_output} --data-binary @{final_output}"
    # BashUpload يرجع الرابط ديريكت في الرد
    response = subprocess.check_output(upload_cmd, shell=True).decode('utf-8')
    
    # استخراج الرابط من الرد (BashUpload يرجعه بشكل نصي)
    download_url = ""
    for line in response.split('\n'):
        if "https://bashupload.com/" in line:
            download_url = line.strip()
            break

    if not download_url:
        download_url = "Error uploading, check GitHub Logs."

    # 7. إرسال الرابط لتلغرام
    msg = f"✅ *Video 3min Ready!*\n\n📥 *Download Link:*\n{download_url}"
    requests.post(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage", 
                  json={"chat_id": CHAT_ID, "text": msg, "parse_mode": "Markdown"})
    
    print(f"🔥 Done! Link sent: {download_url}")

if __name__ == "__main__":
    produce_masterpiece()
