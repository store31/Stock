import os
import subprocess
import requests
import time

# 🔑 Secrets (PEXELS_KEY, TELEGRAM_TOKEN, CHAT_ID)
PEXELS_KEY = os.getenv("PEXELS_KEY")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

def run(cmd):
    print(f"▶ {cmd}")
    subprocess.run(cmd, shell=True, check=True)

def produce_masterpiece():
    # 1. القصة (3 دقائق)
    script = (
        "Once upon a time, in a magical village of pumpkins, lived Simba the ginger cat. "
        "His tail glowed with pure magic. One day, the Rainbow Cloud vanished and the world turned grey. "
        "Simba and Pip the bird traveled to the Cave of Silence. "
        "Simba purred with joy, his tail lit up the darkness, and the cloud was free! "
        "Color returned to the world, and happiness stayed forever. The end."
    )
    
    print("🎙️ Generating Voice...")
    run(f'edge-tts --text "{script}" --write-media voice.mp3')

    # 2. جلب الفيديوهات (Multi-Query)
    queries = ["magic cat", "fantasy forest", "mystical nature"]
    links = []
    for q in queries:
        try:
            r = requests.get(f"https://api.pexels.com/videos/search?query={q}&per_page=10", 
                             headers={"Authorization": PEXELS_KEY}).json()
            links.extend([v['video_files'][0]['link'] for v in r.get('videos', [])])
        except: continue

    # 3. معالجة 20 مقطع (كل واحد 9 ثواني = 180 ثانية)
    processed = []
    for i, link in enumerate((links * 5)[:20]):
        out = f"v{i}.mp4"
        run(f"ffmpeg -y -i \"{link}\" -vf scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,fps=25 -t 9 -preset ultrafast {out}")
        processed.append(out)

    # 4. الدمج
    with open("list.txt", "w") as f:
        for p in processed: f.write(f"file '{os.path.abspath(p)}'\n")
    run("ffmpeg -y -f concat -safe 0 -i list.txt -c copy merged.mp4")

    # 5. الرندرة النهائية (جودة عالية)
    final_output = f"Simba_Adventure_{int(time.time())}.mp4"
    run(f"ffmpeg -y -i merged.mp4 -i voice.mp3 -map 0:v:0 -map 1:a:0 -c:v libx264 -preset ultrafast -crf 23 -c:a aac -t 180 {final_output}")

    # 6. الرفع والحصول على رابط تحميل مباشر
    print(f"🚀 Uploading to get a direct download link...")
    upload_cmd = f"curl --upload-file ./{final_output} https://transfer.sh/{final_output}"
    download_url = subprocess.check_output(upload_cmd, shell=True).decode('utf-8').strip()
    
    # 7. إرسال الرابط لتلغرام
    print(f"📤 Sending link to Telegram...")
    msg = f"✅ *Video is Ready!*\n\n🐱 *Story:* Simba's Adventure\n⏱ *Duration:* 3 Minutes\n\n📥 *Download Link:*\n{download_url}"
    
    tel_url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": msg, "parse_mode": "Markdown"}
    requests.post(tel_url, json=payload)
    
    print(f"🔥 Mission Complete! Check your Telegram.")

if __name__ == "__main__":
    produce_masterpiece()
