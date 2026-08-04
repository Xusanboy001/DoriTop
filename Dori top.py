from telegram import Update
from telegram import InlineKeyboardButton
from telegram import InlineKeyboardMarkup

from telegram.ext import (
    Application,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters
)

import openpyxl
from difflib import get_close_matches

import os

TOKEN = os.getenv("TOKEN")

EXCEL_FILE = "DoriTop_10ta_dori.xlsx"

# ==========================
# EXCELDAN DORILARNI O'QISH
# ==========================

def yuklash():

    workbook = openpyxl.load_workbook(EXCEL_FILE)
    sheet = workbook.active

    dorilar = {}

    for row in sheet.iter_rows(min_row=2, values_only=True):

        dori_nomi = str(row[0]).strip().lower()

        if dori_nomi not in dorilar:
            dorilar[dori_nomi] = []

        dorilar[dori_nomi].append({
            "dorixona": row[1],
            "narx": row[2],
            "bor": str(row[3]).lower() == "ha",
            "telefon": row[4],
            "manzil": row[5],
            "lat": row[6],
            "lon": row[7]
        })

    workbook.close()

    return dorilar


# Excel bazasini yuklaymiz
dorilar = yuklash()

# ==========================
# DORI NOMINI TOPISH
# ==========================

def dori_top(matn):

    matn = matn.lower()

    # Avval aniq moslikni tekshiramiz
    for nom in dorilar.keys():
        if nom in matn:
            return nom

    # Gapni alohida so'zlarga ajratamiz
    sozlar = matn.replace(",", " ").replace(".", " ").split()

    # O'xshash yozilgan nomlarni qidiramiz
    for soz in sozlar:
        natija = get_close_matches(
            soz,
            dorilar.keys(),
            n=1,
            cutoff=0.60
        )

        if natija:
            return natija[0]

    return None
    
# ==========================
# DORI QIDIRISH
# ==========================

async def qidir(update: Update, context: ContextTypes.DEFAULT_TYPE):

    global dorilar
    dorilar = yuklash()

    if not update.message or not update.message.text:
        return

    dori = dori_top(update.message.text)

    if dori is None:
        await update.message.reply_text(
            "❌ Bu dori bazada topilmadi."
        )
        return

    royxat = dorilar[dori]

    borlar = [x for x in royxat if x["bor"]]
    yoqlar = [x for x in royxat if not x["bor"]]

    text = f"""💊 {dori.title()}

✅ {len(borlar)} ta dorixonada mavjud
❌ {len(yoqlar)} ta dorixonada mavjud emas

━━━━━━━━━━━━━━
"""

    keyboard = []

    for info in royxat:

        if info["bor"]:
            holat = "✅ Bor"
        else:
            holat = "❌ Hozir mavjud emas"

        text += f"""
🏥 {info['dorixona']}
{holat}
📍 {info['manzil']}
"""

        if info["bor"]:
            text += f"""
💰 {info['narx']}
📞 {info['telefon']}
"""

        text += "\n━━━━━━━━━━━━━━\n"

        keyboard.append([
            InlineKeyboardButton(
                f"🗺️ {info['dorixona']}",
                url=f"https://maps.google.com/?q={info['lat']},{info['lon']}"
            )
        ])

    keyboard.append([
        InlineKeyboardButton(
            "🔎 Boshqa dori qidirish",
            callback_data="qidir"
        )
    ])

    await update.message.reply_text(
        text,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    
# ==========================
# TUGMALAR
# ==========================

async def tugmalar(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

    if query.data == "qidir":
        await query.message.reply_text(
            "💊 Kerakli dori nomini yozing.\n\nMasalan:\nParatsetamol\nAspirin"
        )


# ==========================
# BOTNI ISHGA TUSHIRISH
# ==========================

app = Application.builder().token(TOKEN).build()

app.add_handler(
    CallbackQueryHandler(tugmalar)
)

app.add_handler(
    MessageHandler(
        filters.TEXT & ~filters.COMMAND,
        qidir
    )
)

print("✅ DoriTop 3.0 ishga tushdi...")

app.run_polling()