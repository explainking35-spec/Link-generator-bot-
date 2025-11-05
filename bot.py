from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from flask import Flask, redirect, jsonify
import threading, json, random, string, os

# ============ सेटिंग ============
BOT_TOKEN = "8521728775:AAE7nFY__kmJmSZLVzASDmEq1Hc4f3Zn-dg"  # यहाँ अपना Bot Token डालो
CHANNEL_USERNAME = "Digitalindia8"        # यहाँ अपना चैनल username डालो (बिना @)
BASE_URL = "https://link-generator-bot-1lxv.onrender.com" # बाद में Render का URL यहाँ डालना
DATA_FILE = "data.json"

app = Flask(__name__)

# File data load/save
if os.path.exists(DATA_FILE):
    with open(DATA_FILE, "r") as f:
        data = json.load(f)
else:
    data = {}

@app.route("/d/<code>")
def redirect_file(code):
    if code not in data:
        return jsonify({"error": "Invalid or expired link"}), 404
    file_path = data[code]
    file_url = f"https://api.telegram.org/file/bot{BOT_TOKEN}/{file_path}"
    return redirect(file_url, code=302)

def run_flask():
    from waitress import serve
    serve(app, host="0.0.0.0", port=8080)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        f"👋 स्वागत है!\n\n📁 इस बॉट से आप फाइल अपलोड करके डायरेक्ट डाउनलोड लिंक बना सकते हैं।\n"
        f"📢 सिर्फ हमारे चैनल (@{CHANNEL_USERNAME}) के सदस्य उपयोग कर सकते हैं।"
    )

async def handle_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id = user.id

    try:
        member = await context.bot.get_chat_member(f"@{CHANNEL_USERNAME}", user_id)
        if member.status not in ["member", "administrator", "creator"]:
            await update.message.reply_text(
                f"❌ पहले हमारे चैनल से जुड़िए: https://t.me/{CHANNEL_USERNAME}"
            )
            return
    except Exception as e:
        print("Error:", e)
        await update.message.reply_text("⚠️ चैनल सदस्यता जांचने में समस्या आई।")
        return

    # File upload
    file = update.message.document
    if not file:
        await update.message.reply_text("📄 कृपया कोई फाइल भेजें।")
        return

    file_info = await context.bot.get_file(file.file_id)
    file_path = file_info.file_path

    # Short link बनाना
    code = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
    data[code] = file_path
    with open(DATA_FILE, "w") as f:
        json.dump(data, f)

    short_link = f"{BASE_URL}/d/{code}"
    await update.message.reply_text(
        f"✅ **फाइल अपलोड सफल!**\n\n"
        f"📥 **शॉर्ट डाउनलोड लिंक:**\n{short_link}\n\n"
        f"🔗 क्लिक करते ही फाइल डाउनलोड शुरू हो जाएगी!"
    )

def main():
    threading.Thread(target=run_flask).start()
    app_bot = ApplicationBuilder().token(BOT_TOKEN).build()
    app_bot.add_handler(CommandHandler("start", start))
    app_bot.add_handler(MessageHandler(filters.Document.ALL, handle_file))
    print("🤖 Bot चल रहा है...")
    app_bot.run_polling()

if __name__ == "__main__":
    main()
