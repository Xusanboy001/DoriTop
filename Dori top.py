
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, MessageHandler, ContextTypes, CallbackQueryHandler, filters

TOKEN = "8881396847:AAE4xQjFr9L2_ytQVdqjqtcQWd_2Ww5yrGc"

dorilar = {
    "aspirin": [
        {"dorixona":"Madad dorixonasi","bor":True,"narx":"12 000 so'm","telefon":"+998907654321","manzil":"Beshtol mahallasi","lat":40.7640,"lon":72.3330},
        {"dorixona":"Shifo dorixonasi","bor":False,"narx":"-","telefon":"+998901234567","manzil":"Beshtol mahallasi","lat":40.7635,"lon":72.3325},
        {"dorixona":"Oltin Med","bor":True,"narx":"12 500 so'm","telefon":"+998901112233","manzil":"Beshtol mahallasi","lat":40.7630,"lon":72.3310}
    ],
    "paratsetamol":[
        {"dorixona":"Shifo dorixonasi","bor":True,"narx":"8 000 so'm","telefon":"+998901234567","manzil":"Beshtol mahallasi","lat":40.7635,"lon":72.3325},
        {"dorixona":"Madad dorixonasi","bor":True,"narx":"8 500 so'm","telefon":"+998907654321","manzil":"Beshtol mahallasi","lat":40.7640,"lon":72.3330}
    ]
}


async def qidir(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return
    matn=update.message.text.lower()
    for dori, royxat in dorilar.items():
        if dori in matn:
            borlar=[x for x in royxat if x.get("bor")]
            yoqlar=[x for x in royxat if not x.get("bor")]
            msg=f"💊 {dori.title()}\n\n✅ {len(borlar)} ta dorixonada mavjud\n❌ {len(yoqlar)} ta dorixonada mavjud emas\n\n"
            keyboard=[]
            for info in royxat:
                holat="✅ Bor" if info.get("bor") else "❌ Hozir mavjud emas"
                msg += f"🏥 {info['dorixona']}\n{holat}\n📍 {info['manzil']}\n💰 {info['narx']}\n📞 {info['telefon']}\n\n────────────\n"
                keyboard.append([InlineKeyboardButton(f"🗺️ {info['dorixona']}", url=f"https://maps.google.com/?q={info['lat']},{info['lon']}")])
            keyboard.append([InlineKeyboardButton("🔎 Boshqa dori qidirish", callback_data="qidir")])
            await update.message.reply_text(msg, reply_markup=InlineKeyboardMarkup(keyboard))
            return
    await update.message.reply_text("❌ Bu dori hozircha bazada topilmadi.")

async def tugmalar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "qidir":
        await query.message.reply_text(
            "💊 Qaysi dorini qidiryapsiz?\n\nMasalan:\nParatsetamol\nAspirin"
        )

app = Application.builder().token(TOKEN).build()
app.add_handler(CallbackQueryHandler(tugmalar))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, qidir))

print("✅ DoriTop ishga tushdi...")
app.run_polling()
