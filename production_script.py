import os
import subprocess
import requests

PEXELS_KEY = os.getenv("PEXELS_KEY")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

def produce_world_class():
    temp_dir = "final_touch"
    os.makedirs(temp_dir, exist_ok=True)
    
    # 1. الصوت
    script = "The future is here. Neural networks are changing everything. Subscribe to stay updated."
    audio_path = f"{temp_dir}/voice.mp3"
    subprocess.run(f'edge-tts --text "{script}" --write-media {audio_path}', shell=True)

    # 2. جلب وتجهيز فيديوهات (نضمنو 4 مقاطع)
    headers = {"Authorization": PEXELS_KEY}
    url = "https://api.pexels.com/videos/search?query=technology&per_page=4"
    res = requests.get(url, headers=headers).json()
    v_links = [v['video_files'][0]['link'] for v in res.get('videos', [])]

    processed = []
    for i, link in enumerate(v_links):
        output = f"{temp_dir}/p{i}.mp4"
        # توحيد المقاسات والـ FPS أهم خطوة للدمج
        subprocess.run(f"ffmpeg -y -i {link} -vf 'scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,fps=30' -t 15 {output}", shell=True)
        processed.append(output)

    # 3. الدمج الصافي
    inputs = "".join([f"-i {f} " for f in processed])
    filter_concat = "".join([f"[{i}:v]" for i in range(len(processed))]) + f"concat=n={len(processed)}:v=1:a=0[v]"
    subprocess.run(f"ffmpeg -y {inputs} -filter_complex '{filter_concat}' -map '[v]' {temp_dir}/merged.mp4", shell=True)

    # 4. المونتاج النهائي: العنوان يختفي + نصوص متغيرة (بدل Subtitles)
    # العنوان يظهر (0-5ث) | النص الأول (5-15ث) | النص الثاني (15-30ث)
    final_output = "pro_video_fixed.mp4"
    draw_title = "drawtext=text='NEURAL GENESIS':fontcolor=white:fontsize=60:x=(w-text_w)/2:y=(h-text_h)/4:enable='between(t,0,5)':box=1:boxcolor=black@0.5"
    draw_txt1 = "drawtext=text='THE FUTURE IS NOW':fontcolor=yellow:fontsize=45:x=(w-text_w)/2:y=h-300:enable='between(t,5,15)':box=1:boxcolor=black@0.7"
    draw_txt2 = "drawtext=text='SUBSCRIBE FOR TECH SECRETS':fontcolor=white:fontsize=45:x=(w-text_w)/2:y=h-300:enable='between(t,15,60)':box=1:boxcolor=black@0.7"

    cmd = (
        f"ffmpeg -y -i {temp_dir}/merged.mp4 -i {audio_path} "
        f"-vf \"{draw_title}, {draw_txt1}, {draw_txt2}\" "
        f"-c:v libx264 -c:a aac -shortest {final_output}"
    )
    subprocess.run(cmd, shell=True)

    # إرسال لتلغرام
    with open(final_output, "rb") as v:
        requests.post(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendVideo", data={"chat_id": CHAT_ID}, files={"video": v})

if __name__ == "__main__":
    produce_world_class()
