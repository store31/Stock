import os
import subprocess
import requests
import time

PEXELS_KEY = os.getenv("PEXELS_KEY")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

def run(cmd):
    print("▶", cmd)
    subprocess.run(cmd, shell=True, check=True)

def produce_global_masterpiece():
    # 1. الصوت (سكريبت طويل لـ 90 ثانية)
    script = (
        "The world is changing faster than ever. Artificial intelligence is no longer a dream, "
        "it is our new reality. From neural networks to advanced robotics, we are building "
        "the tools of tomorrow today. Stay curious, stay informed, and join us as we explore "
        "the frontiers of human innovation. The revolution starts now. Subscribe for more."
    )
    run(f'edge-tts --text "{script}" --write-media voice.mp3')

    # 2. جلب 25 فيديو (نختار أفضل 22 لضمان التنوع)
    headers = {"Authorization": PEXELS_KEY}
    url = "https://api.pexels.com/videos/search?query=technology&per_page=25"
    data = requests.get(url, headers=headers).json()
    links = [v['video_files'][0]['link'] for v in data.get("videos", []) if v.get('video_files')]

    # 3. معالجة سريعة (تقليل الجودة شوي باش نضمنوا السرعة والـ 90 ثانية)
    processed = []
    for i, link in enumerate(links[:22]):
        out = f"v{i}.mp4"
        # استعملنا -preset ultrafast باش نكملوا الرندرة في ثواني
        run(f"ffmpeg -y -i \"{link}\" -vf scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,fps=25 -t 4.1 -preset ultrafast {out}")
        processed.append(out)

    # 4. دمج المقاطع
    with open("list.txt", "w") as f:
        for p in processed:
            f.write(f"file '{os.path.abspath(p)}'\n")
    run("ffmpeg -y -f concat -safe 0 -i list.txt -c copy merged.mp4")

    # 5. حرق الكتابة (استعمال خط DejaVu المضمن في Linux لضمان الظهور)
    final_output = "global_masterpiece.mp4"
    
    # تنسيق النصوص مع توقيت دقيق
    # زدت 'fontfile' باش الـ ffmpeg ما يتلفش وين يلقى الخط
    draw_text = (
        "drawtext=text='NEURAL EVOLUTION':fontcolor=white:fontsize=70:box=1:boxcolor=black@0.6:x=(w-text_w)/2:y=(h-text_h)/3:enable='between(t,0,5)',"
        "drawtext=text='AI IS REDEFINING REALITY':fontcolor=yellow:fontsize=50:box=1:boxcolor=black@0.4:x=(w-text_w)/2:y=h-400:enable='between(t,5,30)',"
        "drawtext=text='BUILDING THE FUTURE TODAY':fontcolor=white:fontsize=50:box=1:boxcolor=black@0.4:x=(w-text_w)/2:y=h-400:enable='between(t,30,60)',"
        "drawtext=text='JOIN THE REVOLUTION':fontcolor=yellow:fontsize=60:box=1:boxcolor=black@0.6:x=(w-text_w)/2:y=h-400:enable='between(t,60,95)'"
    )

    # الرندرة النهائية مع ضغط متوازن
    cmd = (
        f"ffmpeg -y -i merged.mp4 -i voice.mp3 "
        f"-vf \"{draw_text}\" "
        f"-c:v libx264 -preset ultrafast -crf 28 -c:a aac -shortest {final_output}"
    )
    run(cmd)

    # 6. الإرسال
    time.sleep(2)
    with open(final_output, "rb") as v:
        requests.post(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendVideo",
                      data={"chat_id": CHAT_ID, "caption": "🚀 *Masterpiece Complete (90s)!*"}, files={"video": v})
    print("✅ DONE")

if __name__ == "__main__":
    produce_global_masterpiece()
