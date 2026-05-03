import os
import time
import requests
import subprocess
import random

# 🔑 الإعدادات
PEXELS_KEY = os.getenv("PEXELS_KEY")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

BASE_PATH = "workdir"
CHANNELS = ["NeuralNet", "Kids_Educational", "InnovateNow", "SmartSystems", "MechMind", "Tech_Gadget", "DarkSecrets"]

def send_video_to_telegram(file_path, caption):
    """إرسال الفيديو إلى تلغرام"""
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendVideo"
    with open(file_path, "rb") as video:
        files = {"video": video}
        data = {"chat_id": CHAT_ID, "caption": caption, "parse_mode": "Markdown"}
        res = requests.post(url, files=files, data=data)
        return res.status_code == 200

def produce_and_upload():
    temp_dir = "temp_work"
    os.makedirs(temp_dir, exist_ok=True)
    
    total_sent = 0
    for channel in CHANNELS:
        print(f"🏭 Working on: {channel}")
        links = get_pexels_videos(channel.split('_')[0])
        
        for i in range(1, 6):
            output_file = f"{temp_dir}/{channel}_V{i}.mp4"
            
            # --- نفس مراحل التصنيع (TTS + FFmpeg) ---
            script = f"Ever wondered how {channel} is shaping tomorrow? Subscribe for more!"
            audio_path = f"{temp_dir}/audio.mp3"
            subprocess.run(f'edge-tts --text "{script}" --write-media {audio_path}', shell=True)
            
            v_url = random.choice(links)
            subprocess.run(f"curl -L {v_url} -o {temp_dir}/raw.mp4", shell=True)
            subprocess.run(f"ffmpeg -y -i {temp_dir}/raw.mp4 -i {audio_path} -vf 'scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,fps=30' -t 15 -c:v libx264 -c:a aac -shortest {output_file}", shell=True)
            
            # --- الإرسال لتلغرام ---
            print(f"📤 Sending {channel}_V{i} to Telegram...")
            if send_video_to_telegram(output_file, f"🎬 *New Video!* \nChannel: {channel}"):
                total_sent += 1
            
            # --- المسح الفوري بعد الإرسال (أفضل من ساعة باش الماكينة ما تعمرش) ---
            if os.path.exists(output_file):
                os.remove(output_file)

    # رسالة نهائية
    requests.post(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage", 
                  json={"chat_id": CHAT_ID, "text": f"✅ تم إنتاج وإرسال {total_sent} فيديو بنجاح!"})

def get_pexels_videos(query):
    headers = {"Authorization": PEXELS_KEY}
    url = f"https://api.pexels.com/videos/search?query={query}&per_page=10&orientation=portrait"
    res = requests.get(url, headers=headers).json()
    return [v['video_files'][0]['link'] for v in res.get('videos', [])]

if __name__ == "__main__":
    produce_and_upload()
