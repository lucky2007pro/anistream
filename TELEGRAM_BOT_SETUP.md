# Telegram Bot Setup

## 1) Bot yaratish
1. Telegram'da `@BotFather` oching.
2. `/newbot` yuboring.
3. Nom va username bering (username `bot` bilan tugasin).
4. Olingan token'ni `TELEGRAM_BOT_TOKEN` sifatida saqlang.

## 2) Kanal sozlash
1. Private kanal yarating.
2. Botni kanalga admin qiling (`Post messages` ruxsati bilan).
3. Kanal ID (`-100...`) ni `TELEGRAM_CHANNEL_ID` ga yozing.

## 3) Env misol
```env
TELEGRAM_BOT_TOKEN=123456:ABC...
TELEGRAM_CHANNEL_ID=-1001234567890
TELEGRAM_CHANNEL_USERNAME=ani_stream_uz
TELEGRAM_ADMIN_IDS=111111111,222222222
```

## 4) Botni ishga tushirish
```bash
python telegram_bridge_bot.py
```

## 4.1) Render'da alohida worker sifatida
- `render.yaml` ichida `anistream-telegram-bot` worker qo'shilgan.
- Worker uchun Render Environment'da quyidagilarni kiriting:
  - `TELEGRAM_BOT_TOKEN`
  - `TELEGRAM_CHANNEL_ID`
  - `TELEGRAM_CHANNEL_USERNAME` (ixtiyoriy)
  - `TELEGRAM_ADMIN_IDS` (ixtiyoriy)

## 5) Foydalanish
- Botga private chatda video/document yuboring.
- Bot faylni kanalga joylaydi va `file_id` qaytaradi.
- Saytda Episode formga `telegram_file_id` ni kiriting yoki upload checkboxdan foydalaning.

## 6) Xavfsizlik
- Token'ni hech qayerga oshkor qilmang.
- Agar token tarqalgan bo'lsa, `@BotFather` orqali qayta yarating.

