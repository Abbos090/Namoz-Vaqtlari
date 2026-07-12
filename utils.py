# -*- coding: utf-8 -*-
"""
Namoz vaqtlari xabarini formatlash uchun yordamchi funksiyalar.
"""
from datetime import datetime

from hijri_converter import Gregorian

from data import UZ_WEEKDAYS, UZ_MONTHS, HIJRI_MONTHS, REGION_OFFSET_FROM_TASHKENT


def get_gregorian_and_hijri(today: datetime = None):
    """Bugungi milodiy va hijriy sana ma'lumotlarini qaytaradi."""
    if today is None:
        today = datetime.now()

    weekday_name = UZ_WEEKDAYS[today.weekday()]
    month_name = UZ_MONTHS[today.month - 1]

    hijri = Gregorian(today.year, today.month, today.day).to_hijri()
    hijri_month_name = HIJRI_MONTHS[hijri.month - 1]

    return {
        "year": today.year,
        "day": today.day,
        "month_name": month_name,
        "weekday_name": weekday_name,
        "hijri_day": hijri.day,
        "hijri_month_name": hijri_month_name,
        "hijri_year": hijri.year,
    }


def region_display_label(region_name: str) -> str:
    """Sarlavhada ko'rsatiladigan '( ... )' ichidagi nom."""
    if "shahri" in region_name or "viloyati" in region_name:
        return region_name
    return f"{region_name} viloyati"


def build_time_diff_lines(selected_region: str) -> str:
    """
    Tanlangan viloyatga nisbatan boshqa hududlarning vaqt farqini
    'Avval' va 'Keyin' shaklida matn qilib qaytaradi. Tanlangan
    viloyat ro'yxatdan chiqarib tashlanadi, o'rniga kerak bo'lsa
    Toshkent qo'shiladi.
    """
    base_offset = REGION_OFFSET_FROM_TASHKENT.get(selected_region, 0)

    # Barcha ma'lum hududlar (viloyatlar + Toshkent o'zi ham ro'yxatda,
    # chunki u ham boshqa hudud tanlanganda ko'rsatilishi kerak)
    all_offsets = dict(REGION_OFFSET_FROM_TASHKENT)

    diffs = []
    for name, offset in all_offsets.items():
        if name == selected_region:
            continue
        # Toshkent shahri/viloyati ikkalasi ham bir xil "Toshkent" nomi
        # bilan faqat bitta marta chiqishi kerak
        display_name = "Toshkent" if name in ("Toshkent shahri", "Toshkent viloyati") else name
        relative = offset - base_offset
        if relative == 0:
            continue
        # Dublikatlarni oldini olish (Toshkent shahri/viloyati)
        if any(d[0] == display_name for d in diffs):
            continue
        diffs.append((display_name, relative))

    avval = sorted([d for d in diffs if d[1] < 0], key=lambda x: -x[1])
    keyin = sorted([d for d in diffs if d[1] > 0], key=lambda x: x[1])

    avval_str = ", ".join(f"{name} ({v})" for name, v in avval)
    keyin_str = ", ".join(f"{name} (+{v})" for name, v in keyin)

    lines = []
    header_city = "Toshkentdan" if selected_region not in ("Toshkent shahri", "Toshkent viloyati") else "Toshkentdan"
    lines.append(f"{selected_region}dan boshqa hududlardagi vaqtlar farqi (daqiqa)")
    if avval_str:
        lines.append(f"\nAvval: {avval_str}\n")
    if keyin_str:
        lines.append(f"Keyin: {keyin_str}")

    return "\n".join(lines)


def build_prayer_message(selected_region: str, data: dict) -> str:
    """
    API'dan kelgan namoz vaqtlari ma'lumotlari asosida to'liq xabarni
    (foydalanuvchi bergan namunadagi formatda, faqat lotin alifbosida) quradi.
    Bu funksiya faqat O'zbekiston viloyatlari (namozapi.uz) uchun ishlatiladi.
    """
    date_info = get_gregorian_and_hijri()
    label = region_display_label(selected_region)

    msg_lines = [
        "☪️ " + f"{date_info['year']}-yil",
        "🌺 " + f"{date_info['day']}-{date_info['month_name']}",
        "🗓 " + date_info["weekday_name"],
        "🌙 " + f"{date_info['hijri_day']}-{date_info['hijri_month_name']}, {date_info['hijri_year']}\n\n",
        f"( {label} )\n\n",
        f"🏙 TONG - {data.get('bomdod', '—')} 🕰\n",
        f"🌅 QUYOSH - {data.get('quyosh', '—')} 🕰\n",
        f"🏞 PESHIN - {data.get('peshin', '—')} 🕰\n",
        f"🌇 ASR - {data.get('asr', '—')} 🕰\n",
        f"🌆 SHOM - {data.get('shom', '—')} 🕰\n",
        f"🌃 XUFTON - {data.get('xufton', '—')} 🕰\n",
        "",
        build_time_diff_lines(selected_region),
    ]

    return "\n".join(msg_lines)


def clean_time(value: str) -> str:
    """
    AlAdhan API javobidagi '05:12 (+05)' kabi qiymatdan faqat soat:daqiqa
    qismini ajratib oladi.
    """
    if not value:
        return "—"
    return value.split(" ")[0]


def build_intl_prayer_message(country_name: str, city_name: str, timings: dict) -> str:
    """
    AlAdhan API'dan kelgan namoz vaqtlari ma'lumotlari asosida
    O'zbekistondan tashqari davlatlar uchun xabarni quradi.
    """
    date_info = get_gregorian_and_hijri()

    msg_lines = [
        "☪️ " + f"{date_info['year']}-yil",
        "🌺 " + f"{date_info['day']}-{date_info['month_name']}",
        "🗓 " + date_info["weekday_name"],
        "🌙 " + f"{date_info['hijri_day']}-{date_info['hijri_month_name']}, {date_info['hijri_year']}\n\n",
        f"( {city_name}, {country_name} )\n\n",
        f"🏙 TONG - {clean_time(timings.get('Fajr'))} 🕰\n",
        f"🌅 QUYOSH - {clean_time(timings.get('Sunrise'))} 🕰\n",
        f"🏞 PESHIN - {clean_time(timings.get('Dhuhr'))} 🕰\n",
        f"🌇 ASR - {clean_time(timings.get('Asr'))} 🕰\n",
        f"🌆 SHOM - {clean_time(timings.get('Maghrib'))} 🕰\n",
        f"🌃 XUFTON - {clean_time(timings.get('Isha'))} 🕰\n",
    ]

    return "\n".join(msg_lines)