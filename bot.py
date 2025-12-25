import requests
import time
from collections import defaultdict
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters

TOKEN = "8510224624:AAFXb1OCbgwMfp4S7xgFYwls2PPDNRLxwCs"

# Bepul, public HF inference (API KEY YO‘Q)
HF_MODEL = "https://api-inference.huggingface.co/models/microsoft/phi-2"

# User xotirasi
memory = defaultdict(list)
last_message_time = defaultdict(float)

SYSTEM_PROMPT = (
    "Sen aqlli AI yordamsan. "
    "Faqat o‘zbek tilida javob ber. "
    "Javoblaring qisqa, tushunarli va foydali bo‘lsin."
)

def ask_ai(user_id, text):
    history = memory[user_id][-3:]
    prompt = SYSTEM_PROMPT + "\n"

    for h in history:
        prompt += f"User: {h}\n"

    prompt += f"User: {text}\nAI:"

    payload = {"inputs": prompt}
    r = requests.post(HF_MODEL, json=payload, timeout=60)

    try:
        answer = r.json()[0]["generated_text"]
        answer = answer.split("AI:")[-1].strip()
    except:
        answer = "⏳ Hozir AI band, keyinroq urinib ko‘ring."

    memory[user_id].append(text)
    memory[user_id] = memory[user_id][-5:]

    return answer[:4000]

async def handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    now = time.time()

    # Flood protection (3 soniya)
    if now - last_message_time[user_id] < 3:
        await update.message.reply_text("⏳ Biroz sekinroq yozing 🙂")
        return

    last_message_time[user_id] = now
    user_text = update.message.text

    await update.message.chat.send_action("typing")
    reply = ask_ai(user_id, user_text)
    await update.message.reply_text(reply)

app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handler))

print("🤖 Railway AI bot ishga tushdi...")
app.run_polling()