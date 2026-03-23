import json
import os
import time
from pathlib import Path

import requests
from dotenv import load_dotenv


load_dotenv()

BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "").strip()
CHANNEL_ID = os.environ.get("TELEGRAM_CHANNEL_ID", "").strip()
CHANNEL_USERNAME = os.environ.get("TELEGRAM_CHANNEL_USERNAME", "").strip().lstrip("@")
ADMIN_IDS_RAW = os.environ.get("TELEGRAM_ADMIN_IDS", "").strip()
STATE_FILE = Path(os.environ.get("TELEGRAM_BOT_STATE_FILE", "telegram_bot_state.json"))

if not BOT_TOKEN:
    raise RuntimeError("TELEGRAM_BOT_TOKEN topilmadi")
if not CHANNEL_ID:
    raise RuntimeError("TELEGRAM_CHANNEL_ID topilmadi")

ADMIN_IDS = set()
if ADMIN_IDS_RAW:
    for item in ADMIN_IDS_RAW.split(","):
        item = item.strip()
        if item:
            ADMIN_IDS.add(int(item))

API_BASE = f"https://api.telegram.org/bot{BOT_TOKEN}"


def load_state():
    if STATE_FILE.exists():
        return json.loads(STATE_FILE.read_text(encoding="utf-8"))
    return {
        "offset": 0,
        "last_channel_file_id": "",
        "last_channel_message_id": None,
        "last_channel_seen_update": "",
    }


def save_state(state):
    STATE_FILE.write_text(json.dumps(state, ensure_ascii=True, indent=2), encoding="utf-8")


def tg_call(method, params=None):
    url = f"{API_BASE}/{method}"
    response = requests.post(url, data=params or {}, timeout=90)
    response.raise_for_status()
    payload = response.json()
    if not payload.get("ok"):
        raise RuntimeError(f"Telegram API xato: {payload}")
    return payload["result"]


def send_message(chat_id, text):
    return tg_call("sendMessage", {"chat_id": chat_id, "text": text})


def send_document(chat_id, file_id, caption=""):
    return tg_call("sendDocument", {"chat_id": chat_id, "document": file_id, "caption": caption})


def safe_send_message(chat_id, text):
    try:
        send_message(chat_id, text)
    except Exception:
        pass


def get_updates(offset):
    return tg_call("getUpdates", {"offset": offset, "timeout": 30})


def extract_media(msg):
    if msg.get("document"):
        media = msg["document"]
        return media.get("file_id"), media.get("file_name", "document")
    if msg.get("video"):
        media = msg["video"]
        return media.get("file_id"), "video.mp4"
    if msg.get("animation"):
        media = msg["animation"]
        return media.get("file_id"), "animation.mp4"
    if msg.get("video_note"):
        media = msg["video_note"]
        return media.get("file_id"), "video_note.mp4"
    return "", ""


def is_target_channel(chat):
    chat_id = str(chat.get("id", ""))
    if chat_id == str(CHANNEL_ID):
        return True

    chat_username = (chat.get("username") or "").strip().lstrip("@")
    if CHANNEL_USERNAME and chat_username and chat_username.lower() == CHANNEL_USERNAME.lower():
        return True

    return False


def is_allowed_user(user_id):
    if not ADMIN_IDS:
        return True
    return user_id in ADMIN_IDS


def channel_post_url(message_id):
    if CHANNEL_USERNAME and message_id:
        return f"https://t.me/{CHANNEL_USERNAME}/{message_id}"
    return "(private kanal: public link yo'q)"


def build_diag_text():
    state = load_state()
    lines = []

    try:
        me = tg_call("getMe")
        bot_id = me.get("id")
        lines.append(f"Bot: @{me.get('username', 'unknown')} (id={bot_id})")
    except Exception as exc:
        return f"DIAG ERROR: getMe ishlamadi: {exc}"

    lines.append(f"CHANNEL_ID env: {CHANNEL_ID}")
    lines.append(f"CHANNEL_USERNAME env: @{CHANNEL_USERNAME if CHANNEL_USERNAME else '(berilmagan)'}")

    try:
        chat = tg_call("getChat", {"chat_id": CHANNEL_ID})
        lines.append(
            "Target chat: "
            f"id={chat.get('id')} | type={chat.get('type')} | title={chat.get('title', '-') } | "
            f"username=@{chat.get('username') if chat.get('username') else '-'}"
        )

        try:
            member = tg_call("getChatMember", {"chat_id": CHANNEL_ID, "user_id": bot_id})
            lines.append(f"Bot channel status: {member.get('status')}")
        except Exception as exc:
            lines.append(f"Bot channel status xato: {exc}")
    except Exception as exc:
        lines.append(f"getChat xato: {exc}")

    lines.append(f"State file: {STATE_FILE}")
    lines.append(f"Last file_id: {state.get('last_channel_file_id') or 'topilmadi'}")
    lines.append(f"Last message_id: {state.get('last_channel_message_id') or 'topilmadi'}")
    lines.append(f"Last channel update seen: {state.get('last_channel_seen_update') or 'topilmadi'}")

    return "\n".join(lines)


def handle_private_message(msg):
    chat_id = msg["chat"]["id"]
    user = msg.get("from", {})
    user_id = user.get("id")

    if not is_allowed_user(user_id):
        send_message(chat_id, "Sizga ruxsat yo'q.")
        return

    text = (msg.get("text") or "").strip().lower()
    if text in {"/start", "/help"}:
        send_message(
            chat_id,
            "Video yoki hujjat yuboring: bot uni kanalga joylaydi va file_id qaytaradi.\n"
            "Buyruqlar:\n"
            "- /last : kanaldagi oxirgi media file_id\n"
            "- /where : bot qaysi kanalga qarayotgani\n"
            "- /diag : kanal/bot ulanish diagnostikasi\n"
            "- /help : yordam",
        )
        return

    if text == "/diag":
        send_message(chat_id, build_diag_text())
        return

    if text == "/where":
        send_message(
            chat_id,
            f"CHANNEL_ID: {CHANNEL_ID}\n"
            f"CHANNEL_USERNAME: @{CHANNEL_USERNAME if CHANNEL_USERNAME else '(berilmagan)'}",
        )
        return

    if text == "/last":
        state = load_state()
        file_id = state.get("last_channel_file_id") or "topilmadi"
        message_id = state.get("last_channel_message_id")
        send_message(
            chat_id,
            f"Oxirgi channel file_id: {file_id}\n"
            f"Post: {channel_post_url(message_id)}",
        )
        return

    file_id, file_name = extract_media(msg)
    if not file_id:
        send_message(chat_id, "Video yoki document yuboring.")
        return

    caption = f"Uploaded by bot: {file_name}"
    try:
        posted = send_document(CHANNEL_ID, file_id, caption=caption)
    except Exception as exc:
        send_message(
            chat_id,
            "Kanalga yuborishda xato bo'ldi. CHANNEL_ID/bot admin huquqini tekshiring.\n"
            f"Xato: {exc}",
        )
        return

    posted_doc = posted.get("document") or posted.get("video") or {}
    channel_file_id = posted_doc.get("file_id", file_id)
    message_id = posted.get("message_id")

    state = load_state()
    state["last_channel_file_id"] = channel_file_id
    state["last_channel_message_id"] = message_id
    save_state(state)

    send_message(
        chat_id,
        "Kanalga joylandi.\n"
        f"file_id: {channel_file_id}\n"
        f"post: {channel_post_url(message_id)}",
    )


def handle_channel_post(msg):
    chat = msg.get("chat", {})
    if not is_target_channel(chat):
        return

    file_id, _ = extract_media(msg)
    state = load_state()
    state["last_channel_seen_update"] = (
        f"message_id={msg.get('message_id')} keys={','.join(sorted(msg.keys()))}"
    )

    if not file_id:
        save_state(state)
        return

    message_id = msg.get("message_id")
    state["last_channel_file_id"] = file_id
    state["last_channel_message_id"] = message_id
    save_state(state)

    for admin_id in ADMIN_IDS:
        safe_send_message(
            admin_id,
            "Kanalga yangi media tushdi.\n"
            f"file_id: {file_id}\n"
            f"post: {channel_post_url(message_id)}",
        )


def main():
    offset = int(load_state().get("offset", 0))

    print("Telegram bridge bot ishga tushdi...")

    while True:
        try:
            updates = get_updates(offset)
            for update in updates:
                offset = update["update_id"] + 1
                # Har safar eng so'nggi state'ni o'qib, faqat offsetni yangilab yozamiz.
                # Aks holda boshqa joyda saqlangan last_channel_file_id ustidan yozilib ketadi.
                current_state = load_state()
                current_state["offset"] = offset
                save_state(current_state)

                if update.get("message"):
                    msg = update["message"]
                    if msg.get("chat", {}).get("type") == "private":
                        handle_private_message(msg)

                if update.get("channel_post"):
                    ch_msg = update["channel_post"]
                    handle_channel_post(ch_msg)

                if update.get("edited_channel_post"):
                    ch_msg = update["edited_channel_post"]
                    handle_channel_post(ch_msg)

        except KeyboardInterrupt:
            print("To'xtatildi")
            break
        except Exception as exc:
            print(f"Xato: {exc}")
            time.sleep(3)


if __name__ == "__main__":
    main()

