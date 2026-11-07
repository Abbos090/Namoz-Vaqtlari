# -*- coding: utf-8 -*-
"""
Namoz vaqtlari Telegram boti.

Ishlash tartibi:
1. /start bosilganda foydalanuvchidan davlatini tanlashi so'raladi
   (O'zbekiston, Qozog'iston, Qirg'iziston, Tojikiston, Turkmaniston,
   Afg'oniston, Rossiya).
2. Agar O'zbekiston tanlansa - viloyat tanlash klaviaturasi chiqadi
   (namozapi.uz manbasi ishlatiladi).
   Agar boshqa davlat tanlansa - o'sha davlatning yirik shaharlari
   ro'yxati chiqadi (AlAdhan API manbasi ishlatiladi).
3. Viloyat/shahar tanlangan zahoti o'sha kungi namoz vaqtlari darhol
   yuboriladi, so'ng pastki (reply) klaviaturada 3 ta tugma chiqadi:
      🕌 Bugungi namoz vaqti
      🔄 Viloyatni o'zgartirish
      🌍 Davlatni o'zgartirish
4. "Bugungi namoz vaqti" bosilganda saqlangan viloyat/shahar uchun
   namoz vaqtlari qayta olib yuboriladi.
5. "Viloyatni o'zgartirish" bosilganda joriy davlat doirasida
   viloyat/shahar tanlash klaviaturasi qaytadan chiqariladi.
6. "Davlatni o'zgartirish" bosilganda davlat tanlash klaviaturasi
   qaytadan chiqariladi.
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

from data import (
    COUNTRIES,
    COUNTRY_API_NAME,
    COUNTRY_NAME_MAP,
    INTL_CALC_METHOD,
    INTL_CITIES,
    REGIONS,
    REGION_API_MAP,
)
from utils import build_intl_prayer_message, build_prayer_message

# ------------------------------------------------------------------
# Sozlamalar
# ------------------------------------------------------------------
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
API_BASE_URL = os.getenv("API_BASE_URL", "https://namozapi.uz/namoz")
INTL_API_URL = "https://api.aladhan.com/v1/timingsByCity"

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

BTN_PRAYER_TIME = "🕌 Bugungi namoz vaqti"
BTN_CHANGE_REGION = "🔄 Viloyatni o'zgartirish"
BTN_CHANGE_COUNTRY = "🌍 Davlatni o'zgartirish"

MAIN_KEYBOARD = ReplyKeyboardMarkup(
    [[BTN_PRAYER_TIME], [BTN_CHANGE_REGION, BTN_CHANGE_COUNTRY]],
    resize_keyboard=True,
)


# ------------------------------------------------------------------
# Klaviatura quruvchilar
# ------------------------------------------------------------------
def build_country_keyboard() -> InlineKeyboardMarkup:
    """Barcha davlatlarni ko'rsatadigan inline klaviaturani quradi."""
    buttons = [
        [InlineKeyboardButton(name, callback_data=f"country:{code}")]
        for name, code in COUNTRIES
    ]
    return InlineKeyboardMarkup(buttons)


def build_region_keyboard() -> InlineKeyboardMarkup:
    """O'zbekiston viloyatlarini ko'rsatadigan inline klaviaturani quradi."""
    buttons = [
        [InlineKeyboardButton(name, callback_data=f"region:{name}")]
        for name, _ in REGIONS
    ]
    return InlineKeyboardMarkup(buttons)


def build_city_keyboard(country_code: str) -> InlineKeyboardMarkup:
    """Tanlangan davlatning yirik shaharlarini ko'rsatadigan klaviaturani quradi."""
    cities = INTL_CITIES.get(country_code, [])
    buttons = [
        [InlineKeyboardButton(display_name, callback_data=f"city:{country_code}:{idx}")]
        for idx, (display_name, _api_name) in enumerate(cities)
    ]
    return InlineKeyboardMarkup(buttons)


# ------------------------------------------------------------------
# Yordamchi: API'lardan namoz vaqtini olib, chat'ga yuborish
# ------------------------------------------------------------------
async def fetch_and_send_prayer_time(
    context: ContextTypes.DEFAULT_TYPE,
    chat_id: int,
    region_name: str,
    reply_markup=None,
) -> None:
    """O'zbekiston viloyati uchun namozapi.uz'dan vaqtni olib, chat'ga yuboradi."""
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

    # namozapi.uz noma'lum hudud uchun ham 200 qaytaradi: {"error": "Region not found"}
    if "error" in data or "bomdod" not in data:
        logger.error("namozapi.uz javobida vaqtlar yo'q (%s): %s", api_param, data)
        await context.bot.send_message(
            chat_id=chat_id,
            text="⚠️ Bu hudud uchun namoz vaqtlari topilmadi.",
            reply_markup=reply_markup,
        )
        return

    message = build_prayer_message(region_name, data)
    await context.bot.send_message(chat_id=chat_id, text=message, reply_markup=reply_markup)


async def fetch_and_send_intl_prayer_time(
    context: ContextTypes.DEFAULT_TYPE,
    chat_id: int,
    country_code: str,
    city_api_name: str,
    city_display_name: str,
    reply_markup=None,
) -> None:
    """Boshqa davlat/shahar uchun AlAdhan API'dan vaqtni olib, chat'ga yuboradi."""
    country_name = COUNTRY_NAME_MAP.get(country_code, country_code)
    api_country_name = COUNTRY_API_NAME.get(country_code, country_code)
    params = {
        "city": city_api_name,
        "country": api_country_name,
        "method": INTL_CALC_METHOD,
    }

    try:
        response = requests.get(INTL_API_URL, params=params, timeout=10)
    except requests.RequestException as exc:
        logger.error("AlAdhan API so'rovida xatolik: %s", exc)
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

    timings = (data.get("data") or {}).get("timings")
    if not timings:
        await context.bot.send_message(
            chat_id=chat_id,
            text="⚠️ Namoz vaqtlari topilmadi.",
            reply_markup=reply_markup,
        )
        return

    message = build_intl_prayer_message(country_name, city_display_name, timings)
    await context.bot.send_message(chat_id=chat_id, text=message, reply_markup=reply_markup)


# ------------------------------------------------------------------
# Handlerlar
# ------------------------------------------------------------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """/start buyrug'i - davlat tanlashni so'raydi."""
    context.user_data.clear()
    await update.message.reply_text(
        "Assalomu alaykum! 👋\n\nIltimos, qaysi davlatdan ekanligingizni tanlang:",
        reply_markup=build_country_keyboard(),
    )


async def country_selected(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Foydalanuvchi davlat tanlaganda ishlaydi."""
    query = update.callback_query
    await query.answer()

    country_code = query.data.split("country:", 1)[1]
    context.user_data["country"] = country_code
    context.user_data.pop("region", None)
    context.user_data.pop("city_api", None)
    context.user_data.pop("city_display", None)

    country_name = COUNTRY_NAME_MAP.get(country_code, country_code)

    if country_code == "UZ":
        await query.edit_message_text(
            f"✅ Siz tanladingiz: <b>{country_name}</b>\n\nEndi viloyatingizni tanlang:",
            parse_mode="HTML",
            reply_markup=build_region_keyboard(),
        )
    else:
        await query.edit_message_text(
            f"✅ Siz tanladingiz: <b>{country_name}</b>\n\nEndi shaharingizni tanlang:",
            parse_mode="HTML",
            reply_markup=build_city_keyboard(country_code),
        )


async def region_selected(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Foydalanuvchi O'zbekiston viloyatini tanlaganda ishlaydi.

    Viloyat tanlangan zahoti o'sha kungi namoz vaqti darhol yuboriladi.
    """
    query = update.callback_query
    await query.answer()

    region_name = query.data.split("region:", 1)[1]
    context.user_data["country"] = "UZ"
    context.user_data["region"] = region_name

    await query.edit_message_text(f"✅ Siz tanladingiz: <b>{region_name}</b>", parse_mode="HTML")

    await fetch_and_send_prayer_time(
        context=context,
        chat_id=query.message.chat_id,
        region_name=region_name,
        reply_markup=MAIN_KEYBOARD,
    )


async def city_selected(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Foydalanuvchi boshqa davlat uchun shahar tanlaganda ishlaydi.

    Shahar tanlangan zahoti o'sha kungi namoz vaqti darhol yuboriladi.
    """
    query = update.callback_query
    await query.answer()

    _, country_code, idx_str = query.data.split(":", 2)
    cities = INTL_CITIES.get(country_code, [])

    try:
        idx = int(idx_str)
        display_name, api_name = cities[idx]
    except (ValueError, IndexError):
        await query.edit_message_text("⚠️ Xatolik yuz berdi, qaytadan /start bosing.")
        return

    context.user_data["country"] = country_code
    context.user_data["city_display"] = display_name
    context.user_data["city_api"] = api_name

    await query.edit_message_text(f"✅ Siz tanladingiz: <b>{display_name}</b>", parse_mode="HTML")

    await fetch_and_send_intl_prayer_time(
        context=context,
        chat_id=query.message.chat_id,
        country_code=country_code,
        city_api_name=api_name,
        city_display_name=display_name,
        reply_markup=MAIN_KEYBOARD,
    )


async def change_region(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """'Viloyatni o'zgartirish' tugmasi bosilganda ishlaydi (joriy davlat doirasida)."""
    country_code = context.user_data.get("country")

    if not country_code:
        await update.message.reply_text(
            "Avval davlatingizni tanlang 🙂",
            reply_markup=build_country_keyboard(),
        )
        return

    if country_code == "UZ":
        await update.message.reply_text(
            "Iltimos, qaysi viloyatdan ekanligingizni tanlang:",
            reply_markup=build_region_keyboard(),
        )
    else:
        await update.message.reply_text(
            "Iltimos, qaysi shahardan ekanligingizni tanlang:",
            reply_markup=build_city_keyboard(country_code),
        )


async def change_country(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """'Davlatni o'zgartirish' tugmasi bosilganda ishlaydi."""
    await update.message.reply_text(
        "Iltimos, qaysi davlatdan ekanligingizni tanlang:",
        reply_markup=build_country_keyboard(),
    )


async def send_prayer_time(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """'Bugungi namoz vaqti' tugmasi bosilganda saqlangan joy uchun ma'lumot yuboradi."""
    country_code = context.user_data.get("country")

    if not country_code:
        await update.message.reply_text(
            "Avval davlatingizni tanlang 🙂",
            reply_markup=build_country_keyboard(),
        )
        return

    if country_code == "UZ":
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
    else:
        city_api_name = context.user_data.get("city_api")
        city_display_name = context.user_data.get("city_display")
        if not city_api_name:
            await update.message.reply_text(
                "Avval shaharingizni tanlang 🙂",
                reply_markup=build_city_keyboard(country_code),
            )
            return
        await fetch_and_send_intl_prayer_time(
            context=context,
            chat_id=update.message.chat_id,
            country_code=country_code,
            city_api_name=city_api_name,
            city_display_name=city_display_name,
            reply_markup=MAIN_KEYBOARD,
        )


async def unknown_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Tanilmagan matnli xabarlar uchun yordamchi javob."""
    has_location = context.user_data.get("region") or context.user_data.get("city_api")
    await update.message.reply_text(
        "Tugmalardan foydalaning yoki /start buyrug'ini yuboring.",
        reply_markup=MAIN_KEYBOARD if has_location else build_country_keyboard(),
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
    application.add_handler(CallbackQueryHandler(country_selected, pattern=r"^country:"))
    application.add_handler(CallbackQueryHandler(region_selected, pattern=r"^region:"))
    application.add_handler(CallbackQueryHandler(city_selected, pattern=r"^city:"))
    application.add_handler(MessageHandler(filters.Regex(f"^{BTN_PRAYER_TIME}$"), send_prayer_time))
    application.add_handler(MessageHandler(filters.Regex(f"^{BTN_CHANGE_REGION}$"), change_region))
    application.add_handler(MessageHandler(filters.Regex(f"^{BTN_CHANGE_COUNTRY}$"), change_country))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, unknown_text))

    logger.info("Bot ishga tushdi...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()  