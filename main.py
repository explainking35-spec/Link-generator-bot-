import asyncio
import json
import os
import requests
from telegram import Update, Bot
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# ===========================
# ⚙️ CONFIGURATION (SET HERE)
# ===========================

BOT_TOKEN = "8598278684:AAGNk3QjauiiM4Lh_ZlOhGh2lul3xG9AM-E"

# Channel chat ID (negative number)
# Example: -1001234567890
CHANNEL_CHAT_ID = -1003261183651

# Your Telegram user ID (owner)
OWNER_ID = 7278872449 

# JSON file to save logo URLs
LOGO_FILE = "logos.json"

# ===========================
# Load/Save Logos
# ===========================
def load_logos():
    if os.path.exists(LOGO_FILE):
        with open(LOGO_FILE, "r") as f:
            return json.load(f)
    return []

def save_logos(logos):
    with open(LOGO_FILE, "w") as f:
        json.dump(logos, f)

logos = load_logos()

# ===========================
# Commands
# ===========================

# /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🙏 नमस्ते! यह *Digital India Dev Bhai* का Auto Logo Bot है!\n\n"
        "📢 हर 1 घंटे में चैनल का लोगो बदल जाएगा!\n"
        "केवल channel owner इस bot को नियंत्रित कर सकते हैं।",
        parse_mode="Markdown"
    )

# /addlogo <url>
async def add_logo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        return await update.message.reply_text("❌ आपको इस कमांड की अनुमति नहीं है।")

    if not context.args:
        return await update.message.reply_text(
            "⚠️ कृपया logo URL दें।\nउदाहरण: /addlogo https://example.com/image.jpg"
        )

    url = context.args[0]
    logos.append(url)
    save_logos(logos)
    await update.message.reply_text(f"✅ Logo जोड़ा गया!\nकुल logo: {len(logos)}")

# /dellogo <index>
async def delete_logo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        return await update.message.reply_text("❌ आपको इस कमांड की अनुमति नहीं है।")

    if not context.args:
        return await update.message.reply_text("⚠️ कृपया index दें। (जैसे /dellogo 1)")

    try:
        index = int(context.args[0]) - 1
        removed = logos.pop(index)
        save_logos(logos)
        await update.message.reply_text(f"🗑️ Logo हटाया गया:\n{removed}")
    except Exception:
        await update.message.reply_text("❌ गलत index दिया गया।")

# /listlogos
async def list_logos(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not logos:
        return await update.message.reply_text("ℹ️ कोई logo जोड़ा नहीं गया है।")
    msg = "📸 *Logo List:*\n\n" + "\n".join([f"{i+1}. {url}" for i, url in enumerate(logos)])
    await update.message.reply_text(msg, parse_mode="Markdown")

# ===========================
# Auto Logo Changer (1 hour)
# ===========================
async def auto_logo_changer(bot: Bot):
    while True:
        if logos:
            for url in logos:
                try:
                    response = requests.get(url)
                    with open("temp_logo.jpg", "wb") as f:
                        f.write(response.content)
                    with open("temp_logo.jpg", "rb") as photo:
                        await bot.set_chat_photo(chat_id=CHANNEL_CHAT_ID, photo=photo)
                    print(f"✅ Logo updated: {url}")
                    await asyncio.sleep(3600)  # ⏰ हर 1 घंटे में change
                except Exception as e:
                    print(f"❌ Error changing logo: {e}")
                    await asyncio.sleep(3600)
        else:
            print("⚠️ कोई logo नहीं मिला, 1 घंटे बाद फिर जांच...")
            await asyncio.sleep(3600)

# ===========================
# Main
# ===========================
async def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("addlogo", add_logo))
    app.add_handler(CommandHandler("dellogo", delete_logo))
    app.add_handler(CommandHandler("listlogos", list_logos))

    bot = Bot(BOT_TOKEN)
    asyncio.create_task(auto_logo_changer(bot))

    print("🚀 Bot started and running...")
    await app.run_polling()

if __name__ == "__main__":
    asyncio.run(main())
