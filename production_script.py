
import os
import subprocess
import requests
import time

# 🔑 الإعدادات (تأكد من وجودها في GitHub Secrets)
PEXELS_KEY = os.getenv("PEXELS_KEY")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

def run(cmd):
    print(f"▶ {cmd}")
    subprocess.run(cmd, shell=True, check=True)

def get_video_links():
    # استراتيجية تعدد البحث باش نضمنوا فيديوهات كافية لـ 3 دقائق
    queries = ["magic forest", "cute cat adventure", "fairytale landscape", "fantasy world", "mystical nature"]
    all_links = []
    headers = {"Authorization": PEXELS_KEY}
    
    for q in queries:
        try:
            url = f"https://api.pexels.com/videos/search?query={q}&per_page=7"
            r = requests.get(url, headers=headers).json()
            if "videos" in r:
                links = [v['video_files'][0]['link'] for v in r['videos']]
                all_links.extend(links)
                print(f"✅ Found {len(links)} videos for: {q}")
        except Exception as e:
            print(f"⚠️ Error fetching {q}: {e}")
            continue
    return all_links

def produce_masterpiece():
    # 1. القصة العالمية (Gemini's 3-Minute Story)
    script = (
        "Once upon a time, in a village where houses were giant pumpkins, lived a fluffy ginger cat named Simba. "
        "Simba had a magical tail that glowed whenever he was happy. One morning, the Great Rainbow Cloud vanished! "
        "The world turned grey. Simba and his friend Pip the bird went to the Whispering Mountains. "
        "They found the cloud stuck in the Cave of Silence, covered in dark shadow webs. "
        "Simba started to purr with all his heart. His tail glowed like a sun, turning darkness into golden light. "
        "The shadows melted away, and the Rainbow Cloud was free! Colors returned to the pumpkin village. "
        "Simba realized that happiness is the strongest magic. They lived colorful forever. The end."
    )
    
    print("🎙️ Generating Voice...")
    run(f'edge-tts --text "{script}" --write-media voice.mp3')

    # 2. جمع الفيديوهات
    links = get_video_links()
    if not links:
        print("❌ No videos found! Check your PEXELS_KEY.")
        return

    # 3. معالجة المقاطع (نحتاج حوالي 20 مقطع لضمان 3 دقائق)
    processed = []
    # تكرار الروابط إذا كان العدد قليل
    final_links = (links * 5)[:22] 

    for i, link in enumerate(final_links):
        out = f"v{i}.mp4"
        # كل مقطع 8.5 ثانية لضمان الطول الإجمالي
        run(f"ffmpeg -y -i \"{link}\" -vf scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,fps=25 -t 8.5 -preset ultrafast {out}")
        processed.append(out)

    # 4. الدمج الأولي للفيديو
    with open("list.txt", "w") as f:
        for p in processed: f.write(f"file '{os.path.abspath(p)}'\n")
    run("ffmpeg -y -f concat -safe 0 -i list.txt -c copy merged.mp4")

    # 5. الرندرة النهائية (الحل السحري للصوت والحجم)
    print("⚙️ Final Merging with Audio...")
    final_output = "simba_story_3min.mp4"
    
    # استعملنا -map لفرض دمج الصوت و -crf 32 لضمان حجم أقل من 50 ميغا
    cmd = (
        f"ffmpeg -y -i merged.mp4 -i voice.mp3 "
        f"-map 0:v:0 -map 1:a:0 "
        f"-c:v libx264 -preset ultrafast -crf 32 "
        f"-c:a aac -b:a 128k -shortest {final_output}"
    )
    run(cmd)

    # 6. الإرسال لتلغرام مع فحص النتيجة
    print("📤 Sending to Telegram...")
    if os.path.exists(final_output):
        with open(final_output, "rb") as v:
            files = {"video": v}
            data = {"chat_id": CHAT_ID, "caption": "🐱 *Simba's 3-Minute Story (With Audio!)*"}
            response = requests.post(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendVideo", data=data, files=files)
            print(f"📩 Telegram Response: {response.text}")

    # تنظيف الملفات المؤقتة
    print("🧹 Cleaning up...")
    for f in processed + ["voice.mp3", "merged.mp4", "list.txt", final_output]:
        if os.path.exists(f): os.remove(f)

if __name__ == "__main__":
    produce_masterpiece()
