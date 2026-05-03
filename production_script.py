import os
import subprocess
import requests

# الإعدادات
PEXELS_KEY = os.getenv("PEXELS_KEY")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

def produce_final_pro():
    temp_dir = "pro_work"
    os.makedirs(temp_dir, exist_ok=True)
    
    # 1. سكريبت طويل ومقسم
    script = "The future of neural intelligence is here. We dive deep into complex systems. Innovation is our new reality. Subscribe for more updates."
    
    # 2. الصوت (Edge-TTS)
    audio_path = f"{temp_dir}/audio.mp3"
    subprocess.run(f'edge-tts --text "{script}" --write-media {audio_path}', shell=True)

    # 3. جلب فيديوهات (4 فيديوهات لضمان الطول)
    headers = {"Authorization": PEXELS_KEY}
    url = "https://api.pexels.com/videos/search?query=technology&per_page=4"
    res = requests.get(url, headers=headers).json()
    v_links = [v['video_files'][0]['link'] for v in res.get('videos', [])]

    # معالجة الفيديوهات (توحيد المقاسات والـ FPS أهم حاجة للدمج)
    processed = []
    for i, link in enumerate(v_links):
        output = f"{temp_dir}/v{i}.mp4"
        # توحيد كل المقاطع لـ 1080x1920 وبـ 30 إطار في الثانية
        cmd = f"ffmpeg -y -i {link} -vf 'scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,setdar=9/16,fps=30' -t 15 {output}"
        subprocess.run(cmd, shell=True)
        processed.append(output)

    # 4. دمج المقاطع "حبة بحبة" (Concat Filter)
    # هادي الطريقة تضمن أنهم يلصقو بلا مشاكل
    inputs = "".join([f"-i {f} " for f in processed])
    filter_complex = "".join([f"[{i}:v]" for i in range(len(processed))]) + f"concat=n={len(processed)}:v=1:a=0[v]"
    subprocess.run(f"ffmpeg -y {inputs} -filter_complex '{filter_complex}' -map '[v]' {temp_dir}/merged.mp4", shell=True)

    # 5. ملف الترجمة (Subtitle) - يظهر تحت بذكاء
    srt_path = f"{temp_dir}/subs.srt"
    with open(srt_path, "w") as f:
        f.write("1\n00:00:00,500 --> 00:00:10,000\nTHE FUTURE IS NOW\n\n2\n00:00:10,500 --> 00:00:40,000\nEXPLORING NEURAL NETS")

    # 6. المونتاج النهائي (ترجمة + عنوان في البداية فقط + صوت)
    final_output = "factory_final.mp4"
    # العنوان يظهر فقط لأول 5 ثواني (enable='between(t,0,5)')
    cmd_final = (
        f"ffmpeg -y -i {temp_dir}/merged.mp4 -i {audio_path} "
        f"-vf \"subtitles={srt_path}:force_style='Alignment=2,FontSize=20,PrimaryColour=&HFFFFFF,OutlineColour=&H000000,BorderStyle=3,MarginV=50', "
        f"drawtext=text='NEURAL NET TECH':fontcolor=white:fontsize=40:x=(w-text_w)/2:y=(h-text_h)/3:enable='between(t,0,5)'\" "
        f"-c:v libx264 -c:a aac -shortest {final_output}"
    )
    subprocess.run(cmd_final, shell=True)

    # إرسال
    url_tg = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendVideo"
    with open(final_output, "rb") as v:
        requests.post(url_tg, data={"chat_id": CHAT_ID}, files={"video": v})

if __name__ == "__main__":
    produce_final_pro()
