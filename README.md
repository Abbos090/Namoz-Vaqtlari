# Namoz Vaqtlari Telegram Bot

O'zbekiston viloyatlari bo'yicha kunlik namoz vaqtlarini yuboradigan Telegram bot.

## Imkoniyatlari

- `/start` — viloyatni tanlash uchun tugmalar ro'yxatini chiqaradi
- Viloyat tanlangач pastki klaviaturada 2 ta tugma paydo bo'ladi:
  - **🕌 Bugungi namoz vaqti** — tanlangan viloyat uchun bugungi namoz vaqtlarini,
    milodiy/hijriy sanani va boshqa hududlar bilan vaqt farqini yuboradi
  - **🔄 Viloyatni o'zgartirish** — viloyatni qayta tanlash

## O'rnatish

1. Python 3.10+ o'rnatilganligiga ishonch hosil qiling.
2. Loyihani ochib, kerakli kutubxonalarni o'rnating:

   ```bash
   pip install -r requirements.txt
   ```

3. `.env.example` faylidan nusxa olib `.env` nomi bilan saqlang va
   `@BotFather` dan olingan tokeningizni kiriting:

   ```bash
   cp .env.example .env
   ```

   `.env` fayli ichida:

   ```
   BOT_TOKEN=sizning_tokeningiz
   API_BASE_URL=https://namozapi.uz/namoz
   ```

4. Botni ishga tushiring:

   ```bash
   python bot.py
   ```

## Fayllar tuzilishi

```
namoz_bot/
├── bot.py            # Asosiy bot logikasi (handlerlar)
├── data.py           # Viloyatlar ro'yxati, vaqt farqlari, oy/kun nomlari
├── utils.py          # Xabarni formatlash funksiyalari (sana, hijriy sana va h.k.)
├── requirements.txt  # Kerakli Python kutubxonalari
├── .env.example      # .env fayl namunasi
└── README.md
```

## Muhim eslatmalar

- `data.py` faylidagi `REGIONS` ro'yxatidagi ikkinchi element (`api_param`)
  `namozapi.uz` kutayotgan nom bilan mos kelishi kerak. Agar API boshqa
  nomlash formatidan foydalansa, shu yerni moslashtiring.
- Hijriy sana `hijri-converter` kutubxonasi yordamida hisoblanadi (arifmetik
  hisob-kitob asosida), shuning uchun rasmiy e'lon qilingan hijriy sanadan
  ±1 kunga farq qilishi mumkin.
- Viloyatlar orasidagi vaqt farqi (daqiqada) siz bergan namuna xabardagi
  qiymatlar asosida `data.py` ichida qattiq kodlangan (hard-coded). Kerak
  bo'lsa shu yerdan tahrirlashingiz mumkin.
- Bot xotira ichida (`context.user_data`) foydalanuvchi tanlagan viloyatni
  saqlaydi — bot qayta ishga tushirilsa, foydalanuvchilar viloyatni qayta
  tanlashlari kerak bo'ladi. Doimiy saqlash kerak bo'lsa, oddiy JSON fayl
  yoki bazaga yozib qo'yish mumkin.
