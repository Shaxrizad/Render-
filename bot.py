import asyncio
import logging
import os
import time
from io import BytesIO

import aiohttp
import replicate
from PIL import Image, ImageEnhance, ImageFilter

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
    ContextTypes,
)

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

BOT_TOKEN       = os.getenv("BOT_TOKEN",       "8707546862:AAGoeL3mfX0zNTWUPsQupOlXGw4a_lmu0bw")
REPLICATE_TOKEN = os.getenv("REPLICATE_API_TOKEN", "r8_BqUefvCo6P1JoU4B6AWGAvjEFAYxc8r2bVnZb")

os.environ["REPLICATE_API_TOKEN"] = REPLICATE_TOKEN

# ─── Modellar ─────────────────────────────────────────────────────────────────
MODELS = {
    "real_esrgan_4x": {
        "id":    "nightmareai/real-esrgan:42fed1c4974146d4d2414e2be2c5277c7fcf05fcc3a73abf41610695738c1d7b",
        "label": "Real-ESRGAN 4x",
        "desc":  "Klassik renderlar uchun eng yaxshi. 4x kattalashtirish.",
        "scale": 4,
    },
    "real_esrgan_2x": {
        "id":    "nightmareai/real-esrgan:42fed1c4974146d4d2414e2be2c5277c7fcf05fcc3a73abf41610695738c1d7b",
        "label": "Real-ESRGAN 2x",
        "desc":  "Yengil tozalash. Tez ishlaydi.",
        "scale": 2,
    },
    "clarity": {
        "id":    "philz/clarity-upscaler:dfad41707589d68ecdccd1dfa600d55a208f9310748e44bfe35b4a6291453d5e",
        "label": "Clarity Upscaler",
        "desc":  "Interior/exterior uchun maxsus. Detallarni saqlaydi.",
        "scale": 2,
    },
}

# Foydalanuvchi sozlamalari (default)
DEFAULT_SETTINGS = {
    "model":      "clarity",
    "sharpen":    True,
    "contrast":   True,
    "denoise":    False,
    "face_fix":   False,
}


# ─────────────────────────────────────────────────────────────────────────────
#  Yordamchi funksiyalar
# ─────────────────────────────────────────────────────────────────────────────

def get_settings(ctx: ContextTypes.DEFAULT_TYPE) -> dict:
    return {**DEFAULT_SETTINGS, **ctx.user_data.get("settings", {})}


def settings_kb(settings: dict) -> InlineKeyboardMarkup:
    def mark(key):
        return "✅" if settings.get(key) else "⬜"

    model = settings.get("model", "clarity")
    m = MODELS[model]

    return InlineKeyboardMarkup([
        [InlineKeyboardButton(f"🤖 Model: {m['label']}", callback_data="set:model_menu")],
        [
            InlineKeyboardButton(f"{mark('sharpen')} Keskinlashtirish",  callback_data="toggle:sharpen"),
            InlineKeyboardButton(f"{mark('contrast')} Kontrast",         callback_data="toggle:contrast"),
        ],
        [
            InlineKeyboardButton(f"{mark('denoise')} Shovqin tozalash",  callback_data="toggle:denoise"),
            InlineKeyboardButton(f"{mark('face_fix')} Yuz tozalash",     callback_data="toggle:face_fix"),
        ],
        [InlineKeyboardButton("◀️ Menyu", callback_data="menu")],
    ])


def model_select_kb() -> InlineKeyboardMarkup:
    buttons = []
    for key, m in MODELS.items():
        buttons.append([InlineKeyboardButton(
            f"{'⭐ ' if key == 'clarity' else ''}{m['label']} ({m['scale']}x) — {m['desc']}",
            callback_data=f"set:model:{key}",
        )])
    buttons.append([InlineKeyboardButton("◀️ Ortga", callback_data="set:back")])
    return InlineKeyboardMarkup(buttons)


def main_menu_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("⚙️ Sozlamalar",    callback_data="settings"),
         InlineKeyboardButton("ℹ️ Qo'llanma",     callback_data="help")],
        [InlineKeyboardButton("📊 Narxlar",        callback_data="pricing")],
    ])


def post_process(img_bytes: bytes, settings: dict) -> bytes:
    """Qo'shimcha sifat yaxshilash — PIL orqali."""
    img = Image.open(BytesIO(img_bytes)).convert("RGB")

    if settings.get("denoise"):
        img = img.filter(ImageFilter.MedianFilter(size=3))

    if settings.get("sharpen"):
        enhancer = ImageEnhance.Sharpness(img)
        img = enhancer.enhance(1.4)
        img = img.filter(ImageFilter.UnsharpMask(radius=1.2, percent=120, threshold=3))

    if settings.get("contrast"):
        enhancer = ImageEnhance.Contrast(img)
        img = enhancer.enhance(1.15)
        enhancer = ImageEnhance.Color(img)
        img = enhancer.enhance(1.08)

    buf = BytesIO()
    img.save(buf, format="PNG", optimize=True)
    buf.seek(0)
    return buf.read()


async def download_image(url: str) -> bytes:
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            return await resp.read()


async def run_replicate(model_id: str, input_data: dict) -> str:
    """Replicate modelini ishga tushirib, natija URL qaytaradi."""
    loop = asyncio.get_event_loop()

    def _run():
        output = replicate.run(model_id, input=input_data)
        if isinstance(output, list):
            return output[0]
        return output

    result = await loop.run_in_executor(None, _run)
    return str(result)


# ─────────────────────────────────────────────────────────────────────────────
#  Handlerlar
# ─────────────────────────────────────────────────────────────────────────────

async def cmd_start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    name = update.effective_user.first_name
    text = (
        f"Salom, *{name}*! 👋\n\n"
        "🏠 *Render Sifat Oshirish Boti*\n\n"
        "Men sizning xira yoki past sifatli interior/exterior render rasmlaringizni "
        "AI yordamida *professional sifatga* olib chiqaman.\n\n"
        "📸 *Qanday ishlash kerak:*\n"
        "1. Rasmingizni yuboring\n"
        "2. Bot avtomatik qayta ishlaydi\n"
        "3. Yuqori sifatli natijani oling\n\n"
        "⚙️ Sozlamalar orqali model va effektlarni o'zgartiring."
    )
    await update.message.reply_text(text, parse_mode="Markdown",
                                     reply_markup=main_menu_kb())


async def cmd_menu(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📋 Asosiy menyu:", reply_markup=main_menu_kb())


async def cb_handler(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data  = query.data

    if data == "menu":
        await query.edit_message_text("📋 Asosiy menyu:", reply_markup=main_menu_kb())

    elif data == "settings":
        settings = get_settings(ctx)
        await query.edit_message_text(
            "⚙️ *Sozlamalar*\n\nQuyidagi parametrlarni o'zgartiring:",
            parse_mode="Markdown",
            reply_markup=settings_kb(settings),
        )

    elif data == "set:model_menu":
        await query.edit_message_text(
            "🤖 *Model tanlang:*\n\n"
            "• *Real-ESRGAN* — tez, klassik renderlar uchun\n"
            "• *Clarity* — interior/exterior, detallar aniq chiqadi",
            parse_mode="Markdown",
            reply_markup=model_select_kb(),
        )

    elif data.startswith("set:model:"):
        key = data.split(":")[-1]
        if "settings" not in ctx.user_data:
            ctx.user_data["settings"] = {}
        ctx.user_data["settings"]["model"] = key
        settings = get_settings(ctx)
        m = MODELS[key]
        await query.edit_message_text(
            f"✅ *{m['label']}* tanlandi.\n\n_{m['desc']}_",
            parse_mode="Markdown",
            reply_markup=settings_kb(settings),
        )

    elif data == "set:back":
        settings = get_settings(ctx)
        await query.edit_message_text(
            "⚙️ *Sozlamalar*",
            parse_mode="Markdown",
            reply_markup=settings_kb(settings),
        )

    elif data.startswith("toggle:"):
        key = data.split(":")[1]
        if "settings" not in ctx.user_data:
            ctx.user_data["settings"] = {}
        current = get_settings(ctx).get(key, False)
        ctx.user_data["settings"][key] = not current
        settings = get_settings(ctx)
        await query.edit_message_reply_markup(reply_markup=settings_kb(settings))

    elif data == "help":
        text = (
            "📖 *Qo'llanma*\n\n"
            "*1. Rasm yuborish:*\n"
            "Rasmni to'g'ridan-to'g'ri chatga yuboring. "
            "Bot avtomatik qayta ishlaydi.\n\n"
            "*2. Modellar:*\n"
            "• *Clarity* — interior/exterior uchun tavsiya. "
            "Teksturalar, devorlar, mebel detallarini saqlaydi.\n"
            "• *Real-ESRGAN 4x* — 4 marta kattalashtirish. "
            "Kichik rasmlar uchun.\n"
            "• *Real-ESRGAN 2x* — tez ishlaydi, 2 marta.\n\n"
            "*3. Effektlar:*\n"
            "• Keskinlashtirish — chiziqlarni aniqlashtiradi\n"
            "• Kontrast — rang va yorug'likni yaxshilaydi\n"
            "• Shovqin tozalash — donador rasmlarni yumshatadi\n"
            "• Yuz tozalash — odamlar bo'lsa yuzlarni tiklaydi\n\n"
            "*4. Tavsiya:*\n"
            "Interior uchun → Clarity + Keskinlashtirish + Kontrast\n"
            "Exterior uchun → Clarity + Kontrast\n"
            "Tunda olingan render → Real-ESRGAN 4x + Shovqin tozalash"
        )
        await query.edit_message_text(text, parse_mode="Markdown",
                                       reply_markup=InlineKeyboardMarkup([
                                           [InlineKeyboardButton("◀️ Menyu", callback_data="menu")]
                                       ]))

    elif data == "pricing":
        text = (
            "💰 *Replicate narxlari*\n\n"
            "• Clarity Upscaler — ~$0.002 / rasm\n"
            "• Real-ESRGAN — ~$0.001 / rasm\n\n"
            "Ro'yxatdan o'tganda *$5 bepul kredit* beriladi.\n"
            "Bu taxminan *2500–5000 ta rasm* demak!\n\n"
            "🔗 replicate.com"
        )
        await query.edit_message_text(text, parse_mode="Markdown",
                                       reply_markup=InlineKeyboardMarkup([
                                           [InlineKeyboardButton("◀️ Menyu", callback_data="menu")]
                                       ]))


async def photo_handler(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """Foydalanuvchi rasm yuborganida ishga tushadi."""
    msg      = update.message
    settings = get_settings(ctx)
    model_key = settings.get("model", "clarity")
    model     = MODELS[model_key]

    # Statusni ko'rsatish
    status_msg = await msg.reply_text(
        f"⏳ Rasm qabul qilindi...\n"
        f"🤖 Model: *{model['label']}*\n"
        f"⚙️ Qayta ishlanmoqda, kuting...",
        parse_mode="Markdown",
    )

    try:
        # Rasmni yuklab olish
        photo   = msg.photo[-1]  # Eng katta o'lcham
        file    = await ctx.bot.get_file(photo.file_id)
        img_url = file.file_path

        await status_msg.edit_text(
            f"📥 Rasm yuklandi\n"
            f"🤖 *{model['label']}* modeli ishlamoqda...\n"
            f"⏱ 30-60 soniya kuting...",
            parse_mode="Markdown",
        )

        start_time = time.time()

        # Model input parametrlari
        if model_key in ("real_esrgan_4x", "real_esrgan_2x"):
            input_data = {
                "image":       img_url,
                "scale":       model["scale"],
                "face_enhance": settings.get("face_fix", False),
            }
        else:  # clarity
            input_data = {
                "image":          img_url,
                "scale_factor":   2,
                "sharpen_amount": 1.2 if settings.get("sharpen") else 0,
                "creativity":     0.25,
                "resemblance":    1.2,
            }

        # Replicate chaqirish
        result_url = await run_replicate(model["id"], input_data)

        # Natijani yuklab olish
        result_bytes = await download_image(result_url)

        # PIL bilan qo'shimcha qayta ishlash
        if settings.get("sharpen") or settings.get("contrast") or settings.get("denoise"):
            await status_msg.edit_text("✨ Effektlar qo'shilmoqda...", parse_mode="Markdown")
            result_bytes = post_process(result_bytes, settings)

        elapsed = time.time() - start_time

        # Natija haqida ma'lumot
        orig_img    = Image.open(BytesIO(await download_image(img_url)))
        result_img  = Image.open(BytesIO(result_bytes))
        orig_w, orig_h   = orig_img.size
        result_w, result_h = result_img.size

        caption = (
            f"✅ *Tayyor!* ({elapsed:.0f} soniya)\n\n"
            f"📐 *O'lcham:* {orig_w}×{orig_h} → {result_w}×{result_h}\n"
            f"🤖 *Model:* {model['label']}\n"
        )
        effects = []
        if settings.get("sharpen"):    effects.append("Keskinlashtirish")
        if settings.get("contrast"):   effects.append("Kontrast")
        if settings.get("denoise"):    effects.append("Shovqin tozalash")
        if settings.get("face_fix"):   effects.append("Yuz tiklash")
        if effects:
            caption += f"✨ *Effektlar:* {', '.join(effects)}\n"

        kb = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("🔄 Yana yuborish", callback_data="menu"),
                InlineKeyboardButton("⚙️ Sozlamalar",    callback_data="settings"),
            ],
        ])

        await msg.reply_photo(
            photo=BytesIO(result_bytes),
            caption=caption,
            parse_mode="Markdown",
            reply_markup=kb,
        )
        await status_msg.delete()

    except replicate.exceptions.ReplicateError as e:
        logger.error(f"Replicate xato: {e}")
        await status_msg.edit_text(
            f"❌ *Replicate xatosi:*\n`{str(e)[:200]}`\n\n"
            "API tokenini tekshiring yoki keyinroq urinib ko'ring.",
            parse_mode="Markdown",
            reply_markup=main_menu_kb(),
        )
    except Exception as e:
        logger.error(f"Umumiy xato: {e}", exc_info=True)
        await status_msg.edit_text(
            f"❌ Xatolik yuz berdi.\n`{str(e)[:200]}`\n\nKeyinroq urinib ko'ring.",
            parse_mode="Markdown",
            reply_markup=main_menu_kb(),
        )


async def doc_handler(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """Fayl sifatida yuborilgan rasmlar uchun."""
    doc = update.message.document
    if not doc.mime_type or not doc.mime_type.startswith("image/"):
        await update.message.reply_text(
            "❌ Faqat rasm fayllarini yuborin (JPG, PNG, WEBP)."
        )
        return

    # Faylni photo sifatida qayta yo'naltirish
    # Telegram file_id orqali yuklab olamiz
    settings  = get_settings(ctx)
    model_key = settings.get("model", "clarity")
    model     = MODELS[model_key]

    status_msg = await update.message.reply_text(
        f"⏳ Fayl qabul qilindi...\n🤖 *{model['label']}* qayta ishlaydi...",
        parse_mode="Markdown",
    )

    try:
        file     = await ctx.bot.get_file(doc.file_id)
        img_url  = file.file_path

        start_time = time.time()

        if model_key in ("real_esrgan_4x", "real_esrgan_2x"):
            input_data = {
                "image":        img_url,
                "scale":        model["scale"],
                "face_enhance": settings.get("face_fix", False),
            }
        else:
            input_data = {
                "image":          img_url,
                "scale_factor":   2,
                "sharpen_amount": 1.2 if settings.get("sharpen") else 0,
                "creativity":     0.25,
                "resemblance":    1.2,
            }

        result_url   = await run_replicate(model["id"], input_data)
        result_bytes = await download_image(result_url)

        if settings.get("sharpen") or settings.get("contrast") or settings.get("denoise"):
            result_bytes = post_process(result_bytes, settings)

        elapsed = time.time() - start_time

        await update.message.reply_document(
            document=BytesIO(result_bytes),
            filename="enhanced_render.png",
            caption=(
                f"✅ *Tayyor!* ({elapsed:.0f} soniya)\n"
                f"🤖 Model: {model['label']}"
            ),
            parse_mode="Markdown",
        )
        await status_msg.delete()

    except Exception as e:
        logger.error(f"Doc handler xato: {e}", exc_info=True)
        await status_msg.edit_text(
            f"❌ Xatolik: `{str(e)[:200]}`",
            parse_mode="Markdown",
        )


async def text_handler(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📸 Iltimos, sifatini oshirmoqchi bo'lgan rasmingizni yuboring.",
        reply_markup=main_menu_kb(),
    )


# ─────────────────────────────────────────────────────────────────────────────
#  Ishga tushirish
# ─────────────────────────────────────────────────────────────────────────────

def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("menu",  cmd_menu))

    app.add_handler(CallbackQueryHandler(cb_handler))

    # Rasmlar (compressed va fayl)
    app.add_handler(MessageHandler(filters.PHOTO,    photo_handler))
    app.add_handler(MessageHandler(filters.Document.IMAGE, doc_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_handler))

    logger.info("✅ Render bot ishga tushdi!")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
