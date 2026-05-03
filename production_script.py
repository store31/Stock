import os
import subprocess
import requests
import time

# 🔑 Secrets (نجيبوهم من Environment Variables تاع GitHub)
PEXELS_KEY = os.getenv("PEXELS_KEY")

def run(cmd):
    print(f"▶ {cmd}")
    subprocess.run(cmd, shell=True, check=True)

def produce_masterpiece():
    # 1. القصة (3 دقائق)
    script = (
        "In the heart of an ancient forest, Simba the golden cat discovered a path "
        "made of starlight. Every step he took made the flowers sing. "
        "He was looking for the Great Crystal of Purring. "
        "Along the way, he met a wise owl who gave him a feather of courage. "
        "Simba reached the crystal, touched it with his paw, and the forest "
        "glowed with eternal peace. Simba was the hero of the starlight path."
    )
    
    print("🎙️ Generating Voice...")
    run(f'edge-tts --text "{script}" --write-media voice.mp3')

    # 2. جلب فيديوهات متنوعة (لضمان 3 دقائق)
    queries = ["magic cat", "ethereal forest", "mystical nature", "fantasy animal"]
    links = []
    headers = {"Authorization": PEXELS_KEY}
    for q in queries:
        try:
            r = requests.get(f"https://api.pexels.com/videos/search?query={q}&per_page=15", headers=headers).json()
            links.extend([v['video_files'][0]['link'] for v in r.get('videos', [])])
        except: continue

    # 3. معالجة 20 مقطع (كل واحد 9 ثواني = 180 ثانية / 3 دقائق)
    processed = []
    # استعملنا (links * 5) باش نضمنوا كاين فيديوهات كافية
    for i, link in enumerate((links * 5)[:20]):
        out = f"v{i}.mp4"
        # تحويل الأبعاد لـ 1080x1920 (Vertical) وتثبيت الـ FPS
        run(f"ffmpeg -y -i \"{link}\" -vf \"scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,fps=25\" -t 9 -preset ultrafast {out}")
        processed.append(out)

    # 4. دمج المقاطع في ملف واحد
    with open("list.txt", "w") as f:
        for p in processed:
            f.write(f"file '{os.path.abspath(p)}'\n")
    
    run("ffmpeg -y -f concat -safe 0 -i list.txt -c copy merged.mp4")

    # 5. الرندرة النهائية (دمج الصوت مع الفيديو)
    # الاسم يبدأ بـ Simba_ باش الـ YAML يرفدو للـ Release
    final_output = f"Simba_{int(time.time())}.mp4"
    
    # ضغط معقول (crf 28) باش الحجم ما يفوتش 100MB بزاف
    run(f"ffmpeg -y -i merged.mp4 -i voice.mp3 -map 0:v:0 -map 1:a:0 -c:v libx264 -preset ultrafast -crf 28 -c:a aac -shortest {final_output}")
    
    print(f"🔥 Mission Success! Video Created: {final_output}")

if __name__ == "__main__":
    produce_masterpiece()
