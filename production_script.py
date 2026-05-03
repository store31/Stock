import os, time, requests, subprocess, random

# 🔑 الإعدادات (GitHub Actions يرفدهم من الـ Secrets)
PEXELS_KEY = os.getenv("PEXELS_KEY", "DOPSJVN9K0TAzuJTtO75WzH6MI0eZHLnGrEcvLAEzx5uwA9Cfa3ceXuF")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "8369664408:AAFHBtm1dB1Q-9r6dvr6nzvqshADzqPJna8")
CHAT_ID = os.getenv("CHAT_ID", "8177936569")
BASE_PATH = "/content/drive/MyDrive/AI_Shorts_Factory" # المسار في الدرايف

CHANNELS = ["NeuralNet", "Kids_Educational", "InnovateNow", "SmartSystems", "MechMind", "Tech_Gadget", "DarkSecrets"]

def cleanup_old_files(days=2):
    """تنظيف الملفات اللي فات عليها يومين باش الدرايف يبقى يشعل"""
    print(f"🧹 Cleaning files older than {days} days...")
    seconds = days * 24 * 60 * 60
    current_time = time.time()
    for channel in CHANNELS:
        folder = f"{BASE_PATH}/{channel}/Final_Videos"
        if os.path.exists(folder):
            for file in os.listdir(folder):
                file_path = os.path.join(folder, file)
                if current_time - os.stat(file_path).st_mtime > seconds:
                    try: os.remove(file_path)
                    except: pass

def get_pexels_videos(query, count=10):
    headers = {"Authorization": PEXELS_KEY}
    url = f"https://api.pexels.com/videos/search?query={query}&per_page={count}&orientation=portrait"
    res = requests.get(url, headers=headers).json()
    return [v['video_files'][0]['link'] for v in res.get('videos', [])]

def produce_35_shorts():
    temp_dir = "/content/temp_work"
    os.makedirs(temp_dir, exist_ok=True)
    cleanup_old_files(2) # التنظيف قبل البدء

    total_count = 0
    for channel in CHANNELS:
        print(f"🏭 Working on: {channel}")
        assets_dir = f"{BASE_PATH}/{channel}/Assets"
        final_dir = f"{BASE_PATH}/{channel}/Final_Videos"
        os.makedirs(final_dir, exist_ok=True)
        
        # جلب فيديوهات للمحتوى
        links = get_pexels_videos(channel.split('_')[0])
        
        for i in range(1, 6): # 5 فيديوهات لكل قناة
            output_file = f"{final_dir}/{channel}_V{i}_{int(time.time())}.mp4"
            
            # 1. سكريبت (Hook + Content + CTA)
            script = f"Ever wondered how {channel.replace('_',' ')} is shaping tomorrow? The innovation we see today is just the beginning. Stay tuned for more and subscribe to join the revolution."
            
            # 2. الصوت (Edge-TTS)
            audio_path = f"{temp_dir}/audio.mp3"
            subprocess.run(f'edge-tts --text "{script}" --write-media {audio_path} --voice en-US-GuyNeural --rate=+15%', shell=True)

            # 3. معالجة الفيديوهات (التحميل والقص)
            v_url = random.choice(links)
            subprocess.run(f"curl -L {v_url} -o {temp_dir}/raw.mp4", shell=True, capture_output=True)
            subprocess.run(f"ffmpeg -y -i {temp_dir}/raw.mp4 -vf 'scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,fps=30' -t 80 {temp_dir}/content.mp4", shell=True, capture_output=True)

            # 4. الدمج النهائي (Intro + Content + Outro) مع Subtitles في الأسفل
            intro = f"{assets_dir}/intro.mp4"
            outro = f"{assets_dir}/outro.mp4"
            
            # صناعة ملف SRT بسيط للمزامنة
            srt_path = f"{temp_dir}/subs.srt"
            with open(srt_path, "w") as f:
                f.write(f"1\n00:00:05,000 --> 00:01:20,000\n{script.upper()}")

            # دمج كل الأجزاء
            # التعديل: الـ Subtitles تظهر في الأسفل (Alignment=2)
            style = "Alignment=2,MarginV=50,FontSize=20,PrimaryColour=&H00FFFF,OutlineColour=&H000000,BorderStyle=3"
            
            cmd = f"ffmpeg -y -i {intro} -i {temp_dir}/content.mp4 -i {outro} -i {audio_path} -filter_complex '[0:v][1:v][2:v]concat=n=3:v=1:a=0[vv];[vv]subtitles={srt_path}:force_style=\"{style}\"[v]' -map '[v]' -map 3:a -c:v libx264 -shortest {output_file}"
            subprocess.run(cmd, shell=True, capture_output=True)
            total_count += 1

    # إشعار تلغرام النهائي
    requests.post(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage", json={"chat_id": CHAT_ID, "text": f"✅ *Success!*\n🚀 Total Videos Produced: {total_count}\n🧹 Auto-Cleanup Done."})

if __name__ == "__main__":
    produce_35_shorts()
