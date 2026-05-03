import os
import subprocess
import requests
import time

PEXELS_KEY = os.getenv("PEXELS_KEY")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

def run(cmd):
    subprocess.run(cmd, shell=True, check=True)

def get_video_links():
    # كلمات بحث مختلفة باش نجمعو أكبر عدد ممكن
    queries = ["magic cat", "fantasy forest", "mystical cloud", "cute kitten adventure", "fairy tale world"]
    all_links = []
    headers = {"Authorization": PEXELS_KEY}
    
    for q in queries:
        try:
            url = f"https://api.pexels.com/videos/search?query={q}&per_page=5"
            r = requests.get(url, headers=headers).json()
            if "videos" in r:
                links = [v['video_files'][0]['link'] for v in r['videos']]
                all_links.extend(links)
                print(f"✅ Found {len(links)} videos for: {q}")
        except:
            continue
    return all_links

def produce_masterpiece():
    # 1. القصة (Gemini Masterpiece)
    script = (
        "In a magical village of pumpkins, lived Simba the cat with a glowing tail. "
        "One day, the Rainbow Cloud disappeared, leaving the world grey. "
        "Simba met Pip the bird, and together they reached the Cave of Silence. "
        "With a happy purr and a bright glow, Simba broke the shadows and freed the cloud. "
        "Color returned to the world, and they lived happily ever after. The end."
    )
    
    run(f'edge-tts --text "{script}" --write-media voice.mp3')

    # 2. جمع الفيديوهات (Multi-Query Strategy)
    links = get_video_links()
    
    if not links:
        print("❌ No videos found at all!")
        return

    # 3. معالجة المقاطع (نحتاج حوالي 15-20 مقطع لـ 3 دقائق)
    processed = []
    # نكرر القائمة إذا كانت قصيرة باش نوصلو لـ 3 دقائق
    final_links = (links * 5)[:20] 

    for i, link in enumerate(final_links):
        out = f"v{i}.mp4"
        # كل مقطع 9 ثواني × 20 مقطع = 180 ثانية (3 دقائق)
        run(f"ffmpeg -y -i \"{link}\" -vf scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,fps=25 -t 9 -preset ultrafast {out}")
        processed.append(out)

    # 4. الدمج النهائي
    with open("list.txt", "w") as f:
        for p in processed: f.write(f"file '{os.path.abspath(p)}'\n")
    
    run("ffmpeg -y -f concat -safe 0 -i list.txt -c copy merged.mp4")
    
    final_output = "simba_3min_story.mp4"
    run(f"ffmpeg -y -i merged.mp4 -i voice.mp3 -c:v libx264 -preset ultrafast -crf 28 -shortest {final_output}")

    # 5. الإرسال
    with open(final_output, "rb") as v:
        requests.post(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendVideo",
                      data={"chat_id": CHAT_ID, "caption": "🐱 *Simba Story (3 Minutes) is Live!*"}, files={"video": v})

if __name__ == "__main__":
    produce_masterpiece()
