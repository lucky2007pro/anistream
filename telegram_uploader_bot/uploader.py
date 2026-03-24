import os
import asyncio
import json
import logging
import sys
from pathlib import Path
from dotenv import load_dotenv
from telethon import TelegramClient, events, Button, utils
# Logging sozlamalari
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
# .env yuklash
env_path = Path(__file__).resolve().parent / '.env'
parent_env_path = Path(__file__).resolve().parent.parent / '.env'

if env_path.exists():
    load_dotenv(dotenv_path=env_path)
elif parent_env_path.exists():
    load_dotenv(dotenv_path=parent_env_path)
else:
    load_dotenv() # Fallback to default behavior
# Konfiguratsiya
API_ID = os.getenv("TELEGRAM_API_ID")
API_HASH = os.getenv("TELEGRAM_API_HASH")
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHANNEL_ID = os.getenv("TELEGRAM_CHANNEL_ID")
CHANNEL_USERNAME = os.getenv("TELEGRAM_CHANNEL_USERNAME", "").replace("@", "")
ADMIN_IDS_RAW = os.getenv("TELEGRAM_ADMIN_IDS", "")
STATE_FILE = Path(os.getenv("TELEGRAM_BOT_STATE_FILE", "telegram_bot_state.json"))
# Validatsiya
if not all([API_ID, API_HASH, BOT_TOKEN, CHANNEL_ID]):
    logger.error("XATO: .env faylida TELEGRAM_API_ID, TELEGRAM_API_HASH, TELEGRAM_BOT_TOKEN, TELEGRAM_CHANNEL_ID bo'lishi shart.")
    sys.exit(1)
try:
    CHANNEL_ID_INT = int(CHANNEL_ID)
except ValueError:
    logger.error("XATO: TELEGRAM_CHANNEL_ID raqam bo'lishi kerak (masalan -100123...)")
    sys.exit(1)
# Adminlar
ADMIN_IDS = set()
if ADMIN_IDS_RAW:
    for x in ADMIN_IDS_RAW.split(","):
        if x.strip():
            try:
                ADMIN_IDS.add(int(x.strip()))
            except:
                pass

# Telethon Client - biz uni main() ichida yoki loop yaratilgandan keyin yaratamiz
client = None

def load_state_data():
    if STATE_FILE.exists():
        try:
            return json.loads(STATE_FILE.read_text(encoding='utf-8'))
        except:
            pass
    return {}
def save_state_data(key, value):
    try:
        current = load_state_data()
        current[key] = value
        STATE_FILE.write_text(json.dumps(current, indent=2), encoding='utf-8')
    except Exception as e:
        logger.error(f"State save error: {e}")
# --- Handlers ---
async def start_handler(event):
    sender = await event.get_sender()
    if not sender: return
    user_id = sender.id
    if ADMIN_IDS and user_id not in ADMIN_IDS:
        await event.respond("⛔️ Sizga bu botdan foydalanishga ruxsat yo'q.")
        return
    # Menyu
    markup = [
        [Button.text("📹 Qisqa Video (Lavha) Yuklash", resize=True)],
        [Button.text("📊 Statistika"), Button.text("❓ Yordam")]
    ]
    await event.respond(
        f"👋 Assalomu alaykum, {sender.first_name}!\n\n"
        "Qisqa video (Lavha) yoki treyler yuklash uchun quyidagi tugmani bosing va videoni yuboring:",
        buttons=markup
    )

async def mode_short(event):
    await event.respond("✅ **Qisqa Video** rejimi tayyor.\nVideoni yuboring (Lavha).")

async def stats_handler(event):
    st = load_state_data()
    last_fid = st.get('last_channel_file_id', 'mavjud emas')
    last_mid = st.get('last_channel_message_id', 'mavjud emas')
    await event.respond(
        f"📊 **Bot Statistikasi**:\n"
        f"🔹 Target Kanal: {CHANNEL_ID}\n"
        f"🔹 So'nggi yuklangan File ID: {last_fid}\n"
        f"🔹 So'nggi Message ID: {last_mid}"
    )

async def help_handler(event):
    await event.respond(
        "📚 **Yordam:**\n"
        "1. Menyudan turni tanlang.\n"
        "2. Media faylni yuboring.\n"
        "3. Bot uni kanalga joylab, ID qaytaradi."
    )

async def upload_main(event):
    # Only process media if it's NOT a command/text button
    txt = (event.message.text or "")
    if txt.startswith('/') or txt in ['📹 Qisqa Video (Lavha) Yuklash', '📊 Statistika', '❓ Yordam']:
        return
    user_id = event.sender_id
    if ADMIN_IDS and user_id not in ADMIN_IDS:
        return
    if not event.message.media:
        await event.respond("👇 Iltimos, video yuboring.")
        return
    
    status_msg = await event.respond("⏳ **Kanalga yuklanmoqda...**")
    try:
        final_caption = event.message.text or ""
        # Progress bar funksiyasi (agar qayta yuklash kerak bo'lsa ishlaydi)
        async def progress_cb(current, total):
            # Juda ko'p update qilmaslik uchun (flood wait oldini olish)
            pass
        # MUHIM O'ZGARISH: 
        # event.message.media ni to'g'ridan-to'g'ri ishlatish Telegram serverida 
        # faylni qayta yuklamasdan nusxalash imkonini beradi (agar mumkin bo'lsa).
        # supports_streaming=True muhim!
        target_media = event.message.media
        uploaded_msg = await client.send_file(
            CHANNEL_ID_INT,
            target_media,
            caption=final_caption,
            supports_streaming=True, # Video stream bo'lishi uchun
            progress_callback=progress_cb
        )
        # File ID ni aniqlash (Universal Bot API formati)
        f_id = "unknown"
        if uploaded_msg.media:
            f_id = utils.pack_bot_file_id(uploaded_msg.media)
        # Link yaratish
        chan_post_id = uploaded_msg.id
        link_url = f"https://t.me/{CHANNEL_USERNAME}/{chan_post_id}" if CHANNEL_USERNAME else f"ID: {chan_post_id}"
        # State faylga yozish
        save_state_data('last_channel_file_id', f_id)
        save_state_data('last_channel_message_id', chan_post_id)
        response_text = (
            f"✅ **Muvaffaqiyatli Yuklandi!**\n\n"
            f"📂 **File ID (Lavhalar uchun)**: `{f_id}`\n" 
            f"🔗 **Link**: [Postga o'tish]({link_url})\n\n"
            f"⚠️ Ushbu File ID ni saytingizdagi Lavhalar qismiga joylang."
        )
        await status_msg.edit(response_text, link_preview=False)
    except Exception as e:
        logger.error(f"Error: {e}")
        await status_msg.edit(f"❌ Xatolik yuz berdi: {e}")

async def main():
    global client
    client = TelegramClient('bot_session', int(API_ID), API_HASH)
    
    # Handlers ro'yxatdan o'tkazish
    client.add_event_handler(start_handler, events.NewMessage(pattern='/start'))
    client.add_event_handler(mode_short, events.NewMessage(pattern=r'📹 Qisqa Video \(Lavha\) Yuklash'))
    client.add_event_handler(stats_handler, events.NewMessage(pattern='📊 Statistika'))
    client.add_event_handler(help_handler, events.NewMessage(pattern='❓ Yordam'))
    client.add_event_handler(upload_main, events.NewMessage())

    print("🤖 Bot ishga tushdi (Telethon)...")
    await client.start(bot_token=BOT_TOKEN)
    print("✅ Bot onlayn. Telegram orqali /start bosing.")
    await client.run_until_disconnected()

if __name__ == '__main__':
    try:
        # Telethon logs noise kamaytirish
        logging.getLogger("telethon").setLevel(logging.WARNING)
        
        # Loop borligini tekshiramiz (Windows uchun muhim)
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 Bot to'xtatildi.")
    except Exception as e:
        logger.exception("Kutilmagan xatolik yuz berdi:")
        print(f"\nXATOLIK: {e}")
        input("\nChiqish uchun Enter tugmasini bosing...")
