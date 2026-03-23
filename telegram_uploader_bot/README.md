# Telegram Video Uploader

Bu alohida loyiha bo'lib, katta hajmdagi videolarni (2GB gacha) Telegram kanalga yuklash uchun ishlatiladi. Django loyihangizdagi "File is too big" xatosini aylanib o'tish uchun mo'ljallangan.

## O'rnatish

1.  Python o'rnatilganligiga ishonch hosil qiling.
2.  Kutubxonalarni o'rnating:
    ```bash
    pip install -r requirements.txt
    ```

## Sozlash

1.  `.env.example` faylidan nusxa olib `.env` fayl yarating.
2.  Ichidagi ma'lumotlarni to'ldiring:
    *   `TELEGRAM_API_ID` va `TELEGRAM_API_HASH`: [my.telegram.org](https://my.telegram.org) saytidan olinadi.
    *   `TELEGRAM_BOT_TOKEN`: [@BotFather](https://t.me/BotFather) dan olingan bot tokeni.
    *   `TELEGRAM_CHANNEL_ID`: Video yuklanadigan kanal ID si (masalan, -100123456789). Bot bu kanalda admin bo'lishi kerak.

## API ID va Hash olish bo'yicha qo'llanma

1.  Brauzerda [my.telegram.org](https://my.telegram.org) saytiga kiring.
2.  Telefon raqamingizni kiritib, Telegramga kelgan kod orqali kiring.
3.  **"API development tools"** bo'limiga o'ting.
4.  Formani to'ldiring:
    *   **App title:** Istalgan nom (masalan, `MyUploaderBot`)
    *   **Short name:** Istalgan qisqa nom (masalan, `uploader`)
    *   Qolgan joylarni bo'sh qoldirsa ham bo'ladi.
5.  **"Create application"** tugmasini bosing.
6.  Sizga **App api_id** va **App api_hash** beriladi. Ularni nusxalab `.env` faylga qo'ying.

## Ishlatish

Terminalda quyidagi buyruqni yozing:

```bash
python uploader.py "video.mp4" "Kino nomi - 1 qism"
```

*   `"video.mp4"`: Video faylga yo'l.
*   `"Kino nomi..."`: Video tagiga yoziladigan izoh (caption).

## Natija

Video yuklangandan so'ng, dastur sizga `Message ID` qaytaradi. Bu ID ni Django admin panelidagi Episode (qism) sozlamalarida `Telegram Message ID` maydoniga yozib qo'yishingiz kerak (agar shunday maydon bo'lsa) yoki shunchaki baza yangilanganda ishlatiladi.
