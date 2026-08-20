import os
import threading
from flask import Flask
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    ConversationLogic,
    filters,
)

# Render Web Service እንዳይዘጋ Dummy Web Server
app = Flask(__name__)

@app.route('/')
def home():
    return "SecureFinance Bot is Running Live!"

def run_web():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

# Bot Configuration
TOKEN = "8171052631:AAEUQj2oBWWu-1k3K9vTfXmR8uX0k628Olo"
ADMIN_ID = 1341194577

PHONE, PAYMENT_METHOD, ACCOUNT_INFO, AMOUNT = range(4)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [["💸 ክፍያ ለመጠየቅ"]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text(
        "እንኳን ወደ SecureFinance በሰላም መጡ!\n\nክፍያ ለመጠየቅ ከታች ያለውን በተን ይጫኑ።",
        reply_markup=reply_markup,
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
    context.user_data['amount'] = update.message.text
    user = update.message.from_user
    
    msg = (
        f"🚨 **አዲስ የክፍያ ጥያቄ!**\n\n"
        f"👤 **ተጠቃሚ:** {user.full_name} (@{user.username})\n"
        f"📱 **ስልክ:** {context.user_data['phone']}\n"
        f"💳 **የክፍያ መንገድ:** {context.user_data['method']}\n"
        f"🔢 **የሂሳብ ቁጥር:** {context.user_data['account']}\n"
        f"💰 **የብር መጠን:** {context.user_data['amount']} ETB"
    )
    
    await context.bot.send_message(chat_id=ADMIN_ID, text=msg, parse_mode="Markdown")
    await update.message.reply_text("የክፍያ ጥያቄዎ በትክክል ደርሶናል! በቅርቡ ይከናወናል።")
    return ConversationLogic.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("ሂደቱ ተሰርዟል።")
    return ConversationLogic.END

def main():
    # Flask Web Server በ Thread ማስነሳት
    threading.Thread(target=run_web, daemon=True).start()
    
    # Telegram Bot ማስነሳት
    application = ApplicationBuilder().token(TOKEN).build()

    conv_handler = ConversationLogic(
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
