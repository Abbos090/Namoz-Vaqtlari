# -*- coding: utf-8 -*-
"""
Bot uchun statik ma'lumotlar:
- Davlatlar ro'yxati
- Viloyatlar ro'yxati (O'zbekiston, API'ga yuboriladigan nom)
- Boshqa davlatlar uchun yirik shaharlar ro'yxati (AlAdhan API uchun)
- Toshkentga nisbatan vaqt farqlari (daqiqada)
- Oy va hafta kunlari nomlari (lotin alifbosida)
"""

# ------------------------------------------------------------------
# Davlatlar ro'yxati: (foydalanuvchiga ko'rinadigan nom, ichki kod)
# ------------------------------------------------------------------
COUNTRIES = [
    ("🇺🇿 O'zbekiston", "UZ"),
    ("🇰🇿 Qozog'iston", "KZ"),
    ("🇰🇬 Qirg'iziston", "KG"),
    ("🇹🇯 Tojikiston", "TJ"),
    ("🇹🇲 Turkmaniston", "TM"),
    ("🇦🇫 Afg'oniston", "AF"),
    ("🇷🇺 Rossiya", "RU"),
]

COUNTRY_NAME_MAP = {code: name for name, code in COUNTRIES}

# AlAdhan API'ga yuboriladigan `country` parametri (inglizcha nom)
COUNTRY_API_NAME = {
    "KZ": "Kazakhstan",
    "KG": "Kyrgyzstan",
    "TJ": "Tajikistan",
    "TM": "Turkmenistan",
    "AF": "Afghanistan",
    "RU": "Russia",
}

# O'zbekistondan tashqari har bir davlat uchun yirik shaharlar:
# (foydalanuvchiga ko'rinadigan nom, AlAdhan API'ga yuboriladigan shahar nomi)
INTL_CITIES = {
    "KZ": [
        ("Nur-Sultan (Ostona)", "Astana"),
        ("Almati", "Almaty"),
        ("Shimkent", "Shymkent"),
        ("Qarag'andi", "Karaganda"),
        ("Turkiston", "Turkestan"),
    ],
    "KG": [
        ("Bishkek", "Bishkek"),
        ("O'sh", "Osh"),
        ("Jaloqobod", "Jalal-Abad"),
        ("O'zgan", "Uzgen"),
    ],
    "TJ": [
        ("Dushanbe", "Dushanbe"),
        ("Xo'jand", "Khujand"),
        ("Bohtar", "Bokhtar"),
        ("Kulob", "Kulob"),
    ],
    "TM": [
        ("Ashxobod", "Ashgabat"),
        ("Turkmanobod", "Turkmenabat"),
        ("Mari", "Mary"),
        ("Dashog'uz", "Dashoguz"),
    ],
    "AF": [
        ("Kobul", "Kabul"),
        ("Hirot", "Herat"),
        ("Mozori Sharif", "Mazar-i-Sharif"),
        ("Qandahor", "Kandahar"),
    ],
    "RU": [
        ("Moskva", "Moscow"),
        ("Qozon", "Kazan"),
        ("Ufa", "Ufa"),
        ("Mahachqal'a", "Makhachkala"),
        ("Grozniy", "Grozny"),
    ],
}

# AlAdhan API namoz vaqtini hisoblash usuli (method parametri).
# 2 = Islamic Society of North America (ISNA)
INTL_CALC_METHOD = 2

# ------------------------------------------------------------------
# Viloyatlar ro'yxati (O'zbekiston): (foydalanuvchiga ko'rinadigan nom, API parametri)
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