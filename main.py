import os
import re
import threading
from flask import Flask
from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    ConversationHandler,
    filters,
)

# Render Web Service
app = Flask(__name__)

@app.route('/')
def home():
    return "SecureFinance Bot is Running Live!"

def run_web():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

# Credentials
TOKEN = "8903019115:AAFjlLmu3dbtmTSGRHiPhZjN_4mf5Iuci8Y"
ADMIN_ID = 6363252980

# Telegram & YouTube Channel Links
TELEGRAM_CHANNEL_URL = "https://t.me/securefinance2" 
YOUTUBE_CHANNEL_URL = "https://www.youtube.com/@SecureFinance-x4m"

PHONE, PAYMENT_METHOD, ACCOUNT_INFO, AMOUNT = range(4)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # የቴሌግራም እና ዩቲዩብ አዝራሮች
    inline_keyboard = [
        [InlineKeyboardButton("📢 Telegram Channel (20 Birr Bonus)", url=TELEGRAM_CHANNEL_URL)],
        [InlineKeyboardButton("▶️ YouTube Channel (20 Birr Bonus)", url=YOUTUBE_CHANNEL_URL)]
    ]
    inline_markup = InlineKeyboardMarkup(inline_keyboard)
    
    reply_keyboard = [["💸 ክፍያ ለመጠየቅ"]]
    reply_markup = ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True)
    
    await update.message.reply_text(
        "እንኳን ወደ SecureFinance በሰላም መጡ!\n\n"
        "🎁 የቴሌግራም እና የዩቲዩብ ቻናላችንን ይቀላቀሉ እና የ 20 birr ሽልማት ያግኙ!",
        reply_markup=inline_markup
    )
    
    await update.message.reply_text(
        "ክፍያ ለመጠየቅ ከታች ያለውን በተን ይጫኑ።",
        reply_markup=reply_markup
    )

async def request_payout(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("እባክዎ የስልክ ቁጥርዎን ያስገቡ፡")
    return PHONE

async def get_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['phone'] = update.message.text
    keyboard = [["Telebirr", "Bank Transfer"]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text("የክፍያ መንገድ ይምረጡ፡", reply_markup=reply_markup)
    return PAYMENT_METHOD

async def get_payment_method(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['method'] = update.message.text
    await update.message.reply_text("የሂሳብ ቁጥር (Account Number) ያስገቡ፡")
    return ACCOUNT_INFO

async def get_account_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['account'] = update.message.text
    await update.message.reply_text("መውጣት የሚፈልጉትን የብር መጠን ያስገቡ፡")
    return AMOUNT

async def get_amount(update: Update, context: ContextTypes.DEFAULT_TYPE):
    raw_text = update.message.text
    
    # ከጽሁፉ ውስጥ ቁጥሮችን ብቻ ነጥሎ ማውጣት ( Regex )
    numbers = re.findall(r'\d+', raw_text)
    
    if not numbers:
        await update.message.reply_text("እባክዎ ትክክለኛ የብር መጠን በቁጥር ያስገቡ (ምሳሌ፦ 200)፡")
        return AMOUNT
        
    amount = int("".join(numbers))
    
    # የ 500 ብር ገደብ (Daily Limit) ማረጋገጥ
    if amount > 500:
        await update.message.reply_text(
            "The maximum withdrawal limit per day is 500 ETB. Please enter a valid amount:"
        )
        return AMOUNT

    context.user_data['amount'] = amount
    user = update.message.from_user
    
    msg = (
        f"🚨 **አዲስ የክፍያ ጥያቄ!**\n\n"
        f"👤 **ተጠቃሚ:** {user.full_name} (@{user.username})\n"
        f"📱 **ስልክ:** {context.user_data['phone']}\n"
        f"💳 **የክፍያ መንገድ:** {context.user_data['method']}\n"
        f"🔢 **የሂሳብ ቁጥር:** {context.user_data['account']}\n"
        f"💰 **የብር መጠን:** {context.user_data['amount']} ETB"
    )
    
    # ወደ አድሚን Telegram ID መላክ
    await context.bot.send_message(chat_id=ADMIN_ID, text=msg, parse_mode="Markdown")
    
    # ለተጠቃሚው የሚላክ ማረጋገጫ
    await update.message.reply_text(
        "የክፍያ ጥያቄዎ በትክክል ደርሶናል! ማረጋገጥ እንድንችል ከ 1 እስከ 2 ቀን ድረስ ይጠብቁን ባለቤቱ ያረጋግጥሎታል።"
    )
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("ሂደቱ ተሰርዟል።")
    return ConversationHandler.END

def main():
    threading.Thread(target=run_web, daemon=True).start()
    
    application = ApplicationBuilder().token(TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[MessageHandler(filters.Regex("^💸 ክፍያ ለመጠየቅ$"), request_payout)],
        states={
            PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_phone)],
            PAYMENT_METHOD: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_payment_method)],
            ACCOUNT_INFO: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_account_info)],
            AMOUNT: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_amount)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    application.add_handler(CommandHandler("start", start))
    application.add_handler(conv_handler)

    application.run_polling()

if __name__ == "__main__":
    main()
