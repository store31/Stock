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
    # 1. القصة السحرية (Gemini's Masterpiece)
    script = (
        "Once upon a time, in a village where the houses were made of giant pumpkins, lived a fluffy ginger cat named Simba. "
        "Simba wasn’t an ordinary cat; he wore a tiny blue scarf and had a tail that glowed whenever he felt excited. "
        "One sunny morning, Simba noticed something very strange. The Great Rainbow Cloud, which gave the village its beautiful colors, had vanished! "
        "Simba headed towards the Whispering Mountains. He met a tiny blue bird named Pip. Pip was crying silver tears because the cloud was stuck in the Cave of Silence. "
        "Simba began to purr the loudest, happiest purr ever. His tail began to glow, turning the dark cave into golden light. "
        "The Rainbow Cloud was free! It floated up, bursting with pink, green, and gold colors. "
        "The villagers cheered, Simba realized that a happy heart can light up the darkest cave. The village stayed colorful forever. The end."
    )
    
    # توليد الصوت (حوالي 3 دقائق)
    run(f'edge-tts --text "{script}" --write-media voice.mp3')

    # 2. جلب 25 فيديو متنوع (لضمان 3 دقائق)
    headers = {"Authorization": PEXELS_KEY}
    url = "https://api.pexels.com/videos/search?query=magic+forest+cat+adventure&per_page=25"
    data = requests.get(url, headers=headers).json()
    links = [v['video_files'][0]['link'] for v in data.get("videos", [])]

    # 3. معالجة المقاطع (نحتاج 22 مقطع كل واحد 8.5 ثانية)
    processed = []
    for i, link in enumerate(links[:22]):
        out = f"v{i}.mp4"
        # توحيد المقاسات والسرعة
        run(f"ffmpeg -y -i \"{link}\" -vf scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,fps=25 -t 8.5 -preset ultrafast {out}")
        processed.append(out)

    # 4. دمج المقاطع
    with open("list.txt", "w") as f:
        for p in processed: f.write(f"file '{os.path.abspath(p)}'\n")
    run("ffmpeg -y -f concat -safe 0 -i list.txt -c copy merged.mp4")

    # 5. حرق نصوص القصة (كتابة عالمية)
    final_output = "simba_adventure.mp4"
    draw_text = (
        "drawtext=text='SIMBA: THE MAGIC CAT':fontcolor=white:fontsize=80:box=1:boxcolor=black@0.6:x=(w-text_w)/2:y=(h-text_h)/3:enable='between(t,0,10)',"
        "drawtext=text='THE CLOUD HAS VANISHED':fontcolor=yellow:fontsize=60:box=1:boxcolor=black@0.4:x=(w-text_w)/2:y=h-450:enable='between(t,10,60)',"
        "drawtext=text='THE CAVE OF SILENCE':fontcolor=white:fontsize=60:box=1:boxcolor=black@0.4:x=(w-text_w)/2:y=h-450:enable='between(t,60,120)',"
        "drawtext=text='HAPPINESS IS THE KEY':fontcolor=yellow:fontsize=60:box=1:boxcolor=black@0.6:x=(w-text_w)/2:y=h-450:enable='between(t,120,180)'"
    )

    cmd = (
        f"ffmpeg -y -i merged.mp4 -i voice.mp3 "
        f"-vf \"{draw_text}\" "
        f"-c:v libx264 -preset ultrafast -crf 28 -c:a aac -shortest {final_output}"
    )
    run(cmd)

    # 6. الإرسال لتلغرام
    time.sleep(2)
    with open(final_output, "rb") as v:
        requests.post(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendVideo",
                      data={"chat_id": CHAT_ID, "caption": "🐱 *3-Minute Global Story Ready!*"}, files={"video": v})
    print("✅ DONE")

if __name__ == "__main__":
    produce_masterpiece()
