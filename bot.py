# -*- coding: utf-8 -*-
"""
Namoz vaqtlari Telegram boti.

Ishlash tartibi:
1. /start bosilganda foydalanuvchidan viloyatini tanlashi so'raladi
   (inline tugmalar orqali, barcha O'zbekiston viloyatlari).
2. Viloyat tanlangan zahoti - o'sha yerning o'zida (bir necha soniya
   ichida) o'sha kungi namoz vaqtlari avtomatik chiqariladi, so'ng
   pastki (reply) klaviaturada 2 ta tugma chiqadi:
      🕌 Bugungi namoz vaqti
      🔄 Viloyatni o'zgartirish
3. "Bugungi namoz vaqti" bosilganda namozapi.uz dan tanlangan viloyat
   uchun ma'lumot olinadi va chiroyli formatda (faqat lotin alifbosida)
   yuboriladi, shu jumladan boshqa hududlar bilan vaqt farqi jadvali.
4. "Viloyatni o'zgartirish" bosilganda qaytadan viloyat tanlash
   klaviaturasi chiqariladi.
"""
import logging
import os

import requests
from dotenv import load_dotenv
from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ReplyKeyboardMarkup,
    Update,
)
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

from data import REGIONS, REGION_API_MAP
from utils import build_prayer_message

# ------------------------------------------------------------------
# Sozlamalar
# ------------------------------------------------------------------
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
API_BASE_URL = os.getenv("API_BASE_URL", "https://namozapi.uz/namoz")

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

BTN_PRAYER_TIME = "🕌 Bugungi namoz vaqti"
BTN_CHANGE_REGION = "🔄 Viloyatni o'zgartirish"

MAIN_KEYBOARD = ReplyKeyboardMarkup(
    [[BTN_PRAYER_TIME], [BTN_CHANGE_REGION]],
    resize_keyboard=True,
)


# ------------------------------------------------------------------
# Klaviatura quruvchi
# ------------------------------------------------------------------
def build_region_keyboard() -> InlineKeyboardMarkup:
    """Barcha viloyatlarni ko'rsatadigan inline klaviaturani quradi."""
    buttons = [
        [InlineKeyboardButton(name, callback_data=f"region:{name}")]
        for name, _ in REGIONS
    ]
    return InlineKeyboardMarkup(buttons)


# ------------------------------------------------------------------
# Yordamchi: API'dan namoz vaqtini olib, chat'ga yuborish
# ------------------------------------------------------------------
async def fetch_and_send_prayer_time(
    context: ContextTypes.DEFAULT_TYPE,
    chat_id: int,
    region_name: str,
    reply_markup=None,
) -> None:
    """Berilgan viloyat uchun namoz vaqtini olib, chat'ga xabar yuboradi."""
    api_param = REGION_API_MAP.get(region_name, region_name)
    url = f"{API_BASE_URL}/{api_param}"

    try:
        response = requests.get(url, timeout=10)
    except requests.RequestException as exc:
        logger.error("API so'rovida xatolik: %s", exc)
        await context.bot.send_message(
            chat_id=chat_id,
            text="⚠️ Namoz vaqtlarini olishda xatolik yuz berdi. Birozdan so'ng qayta urinib ko'ring.",
            reply_markup=reply_markup,
        )
        return

    if response.status_code != 200:
        await context.bot.send_message(
            chat_id=chat_id,
            text=f"⚠️ Xatolik: server {response.status_code} kodini qaytardi.",
            reply_markup=reply_markup,
        )
        return

    try:
        data = response.json()
    except ValueError:
        await context.bot.send_message(
            chat_id=chat_id,
            text="⚠️ Serverdan noto'g'ri javob keldi.",
            reply_markup=reply_markup,
        )
        return

    message = build_prayer_message(region_name, data)
    await context.bot.send_message(chat_id=chat_id, text=message, reply_markup=reply_markup)


# ------------------------------------------------------------------
# Handlerlar
# ------------------------------------------------------------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """/start buyrug'i - viloyat tanlashni so'raydi."""
    await update.message.reply_text(
        "Assalomu alaykum! 👋\n\nIltimos, qaysi viloyatdan ekanligingizni tanlang:",
        reply_markup=build_region_keyboard(),
    )


async def region_selected(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Foydalanuvchi inline tugma orqali viloyat tanlaganda ishlaydi.

    Viloyat tanlangan zahoti o'sha kungi namoz vaqti darhol yuboriladi.
    """
    query = update.callback_query
    await query.answer()

    region_name = query.data.split("region:", 1)[1]
    context.user_data["region"] = region_name

    # Inline klaviaturali xabarni tasdiqqa o'zgartiramiz
    await query.edit_message_text(f"✅ Siz tanladingiz: <b>{region_name}</b>", parse_mode="HTML")

    # Darhol namoz vaqtini olib yuboramiz, pastiga asosiy klaviaturani biriktiramiz
    await fetch_and_send_prayer_time(
        context=context,
        chat_id=query.message.chat_id,
        region_name=region_name,
        reply_markup=MAIN_KEYBOARD,
    )


async def change_region(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """'Viloyatni o'zgartirish' tugmasi bosilganda ishlaydi."""
    await update.message.reply_text(
        "Iltimos, qaysi viloyatdan ekanligingizni tanlang:",
        reply_markup=build_region_keyboard(),
    )


async def send_prayer_time(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """'Bugungi namoz vaqti' tugmasi bosilganda API'dan ma'lumot olib yuboradi."""
    region_name = context.user_data.get("region")

    if not region_name:
        await update.message.reply_text(
            "Avval viloyatingizni tanlang 🙂",
            reply_markup=build_region_keyboard(),
        )
        return

    await fetch_and_send_prayer_time(
        context=context,
        chat_id=update.message.chat_id,
        region_name=region_name,
        reply_markup=MAIN_KEYBOARD,
    )


async def unknown_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Tanilmagan matnli xabarlar uchun yordamchi javob."""
    await update.message.reply_text(
        "Tugmalardan foydalaning yoki /start buyrug'ini yuboring.",
        reply_markup=MAIN_KEYBOARD if context.user_data.get("region") else build_region_keyboard(),
    )


# ------------------------------------------------------------------
# Ilovani ishga tushirish
# ------------------------------------------------------------------
def main() -> None:
    if not BOT_TOKEN:
        raise RuntimeError(
            "BOT_TOKEN topilmadi. .env faylida BOT_TOKEN=... qiymatini kiriting."
        )

    application = Application.builder().token(BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(region_selected, pattern=r"^region:"))
    application.add_handler(MessageHandler(filters.Regex(f"^{BTN_PRAYER_TIME}$"), send_prayer_time))
    application.add_handler(MessageHandler(filters.Regex(f"^{BTN_CHANGE_REGION}$"), change_region))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, unknown_text))

    logger.info("Bot ishga tushdi...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()