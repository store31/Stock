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

def get_video_links():
    queries = ["magic forest", "cute cat", "fantasy landscape", "mystical nature"]
    all_links = []
    headers = {"Authorization": PEXELS_KEY}
    for q in queries:
        try:
            r = requests.get(f"https://api.pexels.com/videos/search?query={q}&per_page=10", headers=headers).json()
            all_links.extend([v['video_files'][0]['link'] for v in r.get('videos', [])])
        except: continue
    return all_links

def produce_masterpiece():
    # القصة (لازم تكون طويلة باش تلحق 3 دقائق)
    script = (
        "Once upon a time, in a magical village of pumpkins, lived Simba the ginger cat. " * 15 
    ) # راني درت تكرار هنا فقط كمثال، بصح استعمل القصة الطويلة اللي عطيتها لك
    
    print("🎙️ Generating Voice...")
    run(f'edge-tts --text "{script}" --write-media voice.mp3')

    links = get_video_links()
    
    # 3. معالجة المقاطع (نزيدو في مدة كل مقطع)
    processed = []
    # نرفدو 20 مقطع، كل واحد نردوه 10 ثواني
    for i, link in enumerate(links[:20]):
        out = f"v{i}.mp4"
        # استعملت -t 10 باش نضمن الوصول لـ 200 ثانية (أكثر من 3 دقائق)
        run(f"ffmpeg -y -i \"{link}\" -vf scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,fps=25 -t 10 -preset ultrafast {out}")
        processed.append(out)

    # 4. الدمج (الطريقة المضمونة)
    with open("list.txt", "w") as f:
        for p in processed: f.write(f"file '{p}'\n")
    run("ffmpeg -y -f concat -safe 0 -i list.txt -c copy merged.mp4")

    # 5. الرندرة النهائية (نحينا -shortest وجربنا دمج مباشر)
    final_output = "simba_final.mp4"
    # استعملت -af aresample لضبط الصوت مع الفيديو
    cmd = (
        f"ffmpeg -y -i merged.mp4 -i voice.mp3 "
        f"-map 0:v:0 -map 1:a:0 "
        f"-c:v libx264 -preset ultrafast -crf 32 "
        f"-c:a aac -b:a 128k "
        f"-t 180 {final_output}" 
    ) # هنا فورصينا الوقت يكون 180 ثانية (3 دقائق)
    run(cmd)

    # 6. الإرسال
    with open(final_output, "rb") as v:
        requests.post(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendVideo", 
                      data={"chat_id": CHAT_ID, "caption": "🐱 *Simba 3-Minute Story!*"}, files={"video": v})

if __name__ == "__main__":
    produce_masterpiece()
