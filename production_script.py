    # 6. الرفع لـ BashUpload (مع تجاوز فحص SSL لضمان النجاح)
    print(f"🚀 Uploading to BashUpload...")
    # زدنا -k باش نتفاداو الخطأ 60
    upload_cmd = f"curl -k https://bashupload.com/{final_output} --data-binary @{final_output}"
    
    try:
        response = subprocess.check_output(upload_cmd, shell=True).decode('utf-8')
        
        # استخراج الرابط
        download_url = ""
        for line in response.split('\n'):
            if "https://bashupload.com/" in line:
                download_url = line.strip()
                break

        if not download_url:
            download_url = "Upload link not found in response."

        # 7. إرسال الرابط لتلغرام
        msg = f"✅ *Video 3min Ready!*\n\n📥 *Download Link:*\n{download_url}"
        requests.post(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage", 
                      json={"chat_id": CHAT_ID, "text": msg, "parse_mode": "Markdown"})
        print(f"🔥 Done! Link sent: {download_url}")
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Upload failed with exit code {e.returncode}")
        # نبعثو ميساج لتلغرام بلي كاين مشكل في الرفع باش ما تبقاش تستنى
        requests.post(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage", 
                      json={"chat_id": CHAT_ID, "text": "❌ Upload failed, check GitHub Logs."})
