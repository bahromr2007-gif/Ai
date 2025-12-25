import requests
import time
import os
from collections import defaultdict
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, CommandHandler, ContextTypes, filters
from gtts import gTTS

# Telegram token
TOKEN = "8510224624:AAFXb1OCbgwMfp4S7xgFYwls2PPDNRLxwCs"

# HuggingFace public inference modellari (auto-switch)
HF_MODELS = [
    "https://api-inference.huggingface.co/models/TinyLlama/TinyLlama-1.1B-Chat-v1.0",
    "https://api-inference.huggingface.co/models/Qwen/Qwen1.5-0.5B-Chat"
]

# User xotirasi va flood protection
memory = defaultdict(list)
last_message_time = defaultdict(float)

SYSTEM_PROMPT = (
    "Sen aqlli AI yordamsan. "
    "Faqat o‘zbek tilida javob ber. "
    "Javoblaring qisqa, tushunarli va foydali bo‘lsin."
)

# -------------------- AI Chat funksiyasi --------------------
def ask_ai(user_id, text):
    history = memory[user_id][-3:]
    prompt = SYSTEM_PROMPT + "\n"
    for h in history:
        prompt += f"User: {h}\n"
    prompt += f"User: {text}\nAI:"

    payload = {"inputs": prompt}

    for model in HF_MODELS:
        for _ in range(3):
            try:
                r = requests.post(model, json=payload, timeout=60)
                if r.status_code == 200:
                    data = r.json()
                    if isinstance(data, list):
                        answer = data[0]["generated_text"]
                        answer = answer.split("AI:")[-1].strip()
                        memory[user_id].append(text)
                        memory[user_id] = memory[user_id][-5:]
                        return answer[:4000]
            except:
                time.sleep(2)
    return "⚠️ AI hozir band. 1–2 daqiqadan keyin qayta yozing."

# -------------------- Rasm chizish funksiyasi --------------------
def generate_image(prompt):
    url = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-2"
    payload = {"inputs": prompt}
    for _ in range(3):
        try:
            r = requests.post(url, json=payload, timeout=60)
            if r.status_code == 200:
                return r.content
        except:
            time.sleep(2)
    return None

# -------------------- Voice funksiyasi --------------------
def text_to_voice(text, filename="reply.mp3"):
    tts = gTTS(text=text, lang="uz")
    tts.save(filename)
    return filename

# -------------------- Chat handler --------------------
async def handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    now = time.time()

    # Flood protection
    if now - last_message_time[user_id] < 3:
        await update.message.reply_text("⏳ Biroz sekinroq yozing 🙂")
        return
    last_message_time[user_id] = now

    user_text = update.message.text
    await update.message.chat.send_action("typing")
    reply = ask_ai(user_id, user_text)
    await update.message.reply_text(reply)

    # Voice javob
    voice_file = text_to_voice(reply)
    await update.message.reply_voice(voice=open(voice_file, "rb"))

# -------------------- Rasm handler --------------------
async def image_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text.replace("/image ", "")
    await update.message.chat.send_action("upload_photo")
    image_data = generate_image(user_text)
    if image_data:
        with open("output.png", "wb") as f:
            f.write(image_data)
        await update.message.reply_photo(photo=open("output.png", "rb"))
    else:
        await update.message.reply_text("⚠️ Rasm hosil bo‘lmadi, keyinroq urinib ko‘ring.")

# -------------------- Bot ishga tushirish --------------------
if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handler))
    app.add_handler(CommandHandler("image", image_handler))  # /image <prompt> bilan rasm

    print("🤖 Railway AI bot ishga tushdi...")

    # Webhook mode
    app.run_webhook(
        listen="0.0.0.0",
        port=int(os.environ.get("PORT", 8443)),
        webhook_url="https://blissful-charm.up.railway.app/"
    )
