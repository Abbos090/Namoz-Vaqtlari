# -*- coding: utf-8 -*-
"""
Bot uchun statik ma'lumotlar:
- Viloyatlar ro'yxati (API'ga yuboriladigan nom)
- Toshkentga nisbatan vaqt farqlari (daqiqada)
- Oy va hafta kunlari nomlari (lotin alifbosida)
"""

# ------------------------------------------------------------------
# Viloyatlar ro'yxati: (foydalanuvchiga ko'rinadigan nom, API parametri)
# Agar namozapi.uz boshqacha nom kutsa, faqat ikkinchi elementni o'zgartiring.
# ------------------------------------------------------------------
REGIONS = [
    ("Toshkent shahri", "Toshkent"),
    ("Toshkent viloyati", "Toshkent"),
    ("Andijon", "Andijon"),
    ("Buxoro", "Buxoro"),
    ("Farg'ona", "Fargona"),
    ("Jizzax", "Jizzax"),
    ("Xorazm", "Xorazm"),
    ("Namangan", "Namangan"),
    ("Navoiy", "Navoiy"),
    ("Qashqadaryo", "Qashqadaryo"),
    ("Qoraqalpog'iston", "Qoraqalpogiston"),
    ("Samarqand", "Samarqand"),
    ("Sirdaryo", "Sirdaryo"),
    ("Surxondaryo", "Surxondaryo"),
]

# Ko'rinadigan nomdan API parametrini topish uchun tezkor lug'at
REGION_API_MAP = {name: api_param for name, api_param in REGIONS}

# ------------------------------------------------------------------
# Toshkentga nisbatan vaqt farqi (daqiqa). Manba: foydalanuvchi bergan
# namuna xabar. Musbat qiymat - Toshkentdan KEYIN, manfiy - Toshkentdan OLDIN.
# Kalit sifatida REGIONS ro'yxatidagi ko'rinadigan nomdan foydalaniladi.
# ------------------------------------------------------------------
REGION_OFFSET_FROM_TASHKENT = {
    "Toshkent shahri": 0,
    "Toshkent viloyati": 0,
    "Andijon": -11,
    "Namangan": -10,
    "Farg'ona": -10,
    "Jizzax": 6,
    "Samarqand": 9,
    "Buxoro": 21,
    "Xorazm": 35,          # Xiva asosida
    "Qoraqalpog'iston": 42,  # Nukus asosida
    "Qashqadaryo": 12,      # Qarshi asosida
    "Sirdaryo": 7,          # Guliston asosida
    "Surxondaryo": 7,       # Denov/Termiz asosida
    "Navoiy": 19,
}

# Namoz vaqtlari jadvalidagi qo'shni shahar/mamlakatlar (Toshkentga nisbatan,
# doim ro'yxatda ko'rsatiladigan qo'shimcha shaharlar - ixtiyoriy, o'chirib
# qo'yish mumkin). Bular tanlangan viloyat ro'yxatida bo'lmagani uchun
# har doim asosiy ro'yxatga qo'shib ko'rsatiladi.
NEIGHBOUR_CITY_OFFSETS = {
    "Chimkent": -1,
    "Konibodom": -5,
    "Xo'jand": -6,
    "Qo'qon": -7,
    "Jambul": -7,
    "Jaloqobod": -15,
    "Bishkek": -21,
    "Olmaota": -21,
    "O'sh": -14,
    "Bekobod": 4,
    "Turkiston": 4,
    "Denov": 7,
    "Jomboy": 7,
    "Shahrisabz": 10,
    "Kattaqo'rg'on": 12,
    "Qarshi": 12,
    "Nurota": 14,
    "Xiva": 35,
    "Nukus": 42,
}

UZ_WEEKDAYS = [
    "Dushanba",
    "Seshanba",
    "Chorshanba",
    "Payshanba",
    "Juma",
    "Shanba",
    "Yakshanba",
]

UZ_MONTHS = [
    "YANVAR", "FEVRAL", "MART", "APREL", "MAY", "IYUN",
    "IYUL", "AVGUST", "SENTABR", "OKTABR", "NOYABR", "DEKABR",
]

HIJRI_MONTHS = [
    "Muharram", "Safar", "Rabi' ul-avval", "Rabi' ul-oxir",
    "Jumad ul-avval", "Jumad ul-oxir", "Rajab", "Sha'bon",
    "Ramazon", "Shavvol", "Zulqa'da", "Zulhijja",
]
