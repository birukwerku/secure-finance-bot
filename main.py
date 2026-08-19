import logging
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler

TOKEN = "8903019115:AAFjlLmu3dbtmTSGRHiPhZjN_4mf5Iuci8Y"
ADMIN_CHAT_ID = "1341194577"

PHONE, METHOD, ACCOUNT, AMOUNT = range(4)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [["💸 ክፍያ ለመጠየቅ"]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text(
        "እንኳን ወደ SecureFinance የክፍያ መጠየቂያ ቦት በደህና መጡ! ክፍያ ለመጠየቅ ከታች ያለውን በተን ይጫኑ።",
        reply_markup=reply_markup
    )

async def request_payout(update: Update, context: ContextTypes.DEFAULT_TYPE):
    button = KeyboardButton("📱 ስልክ ቁጥር አጋራ", request_contact=True)
    reply_markup = ReplyKeyboardMarkup([[button]], resize_keyboard=True, one_time_keyboard=True)
    await update.message.reply_text("እባክዎን ስልክ ቁጥርዎን ያጋሩ፡", reply_markup=reply_markup)
    return PHONE

async def get_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['phone'] = update.message.contact.phone_number
    keyboard = [["Telebirr", "Bank Transfer"]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
    await update.message.reply_text("የክፍያ ዘዴ ይምረጡ፡", reply_markup=reply_markup)
    return METHOD

async def get_method(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['method'] = update.message.text
    await update.message.reply_text("እባክዎን የቴሌብር ወይም የባንክ አካውንት ቁጥርዎን ያስገቡ፡")
    return ACCOUNT

async def get_account(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['account'] = update.message.text
    await update.message.reply_text("ማውጣት የሚፈልጉትን የብር መጠን ያስገቡ፡")
    return AMOUNT

async def get_amount(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['amount'] = update.message.text
    user = update.message.from_user
    
    admin_msg = (
        f"🚨 **አዲስ የክፍያ ጥያቄ!** 🚨\n\n"
        f"👤 ተጠቃሚ: @{user.username} ({user.full_name})\n"
        f"📱 ስልክ: {context.user_data['phone']}\n"
        f"💳 መንገድ: {context.user_data['method']}\n"
        f"🔢 አካውንት: {context.user_data['account']}\n"
        f"💰 መጠን: {context.user_data['amount']} ETB"
    )
    
    await context.bot.send_message(chat_id=ADMIN_CHAT_ID, text=admin_msg)
    await update.message.reply_text("የክፍያ ጥያቄዎ በተሳካ ሁኔታ ደርሶናል! መረጃው ተጣርቶ በቅርቡ ገቢ ይደረጋል።")
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("ሂደቱ ተሰርዟል።")
    return ConversationHandler.END

if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()
    
    conv_handler = ConversationHandler(
        entry_points=[MessageHandler(filters.Regex('^💸 ክፍያ ለመጠየቅ$'), request_payout)],
        states={
            PHONE: [MessageHandler(filters.CONTACT, get_phone)],
            METHOD: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_method)],
            ACCOUNT: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_account)],
            AMOUNT: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_amount)],
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )
    
    app.add_handler(CommandHandler('start', start))
    app.add_handler(conv_handler)
    
    print("Bot is running...")
    app.run_polling()
