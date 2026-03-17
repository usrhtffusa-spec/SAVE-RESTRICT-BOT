# Developer - @usrhtff009
# Channel - https://t.me/usrht01

from pyrogram.errors import InputUserDeactivated, UserNotParticipant, FloodWait, UserIsBlocked, PeerIdInvalid
from database.db import db
from pyrogram import Client, filters, enums
from config import ADMINS
import asyncio
import datetime
import time
from pyrogram.types import Message
import json
import os
from logger import LOGGER

logger = LOGGER(__name__)

# ---------------------------------------------------
# Professional Broadcast Helper
# ---------------------------------------------------
async def broadcast_messages(user_id, message):
    try:
        await message.copy(chat_id=user_id)
        return True, "Success"
    except FloodWait as e:
        await asyncio.sleep(e.value)
        return await broadcast_messages(user_id, message)
    except InputUserDeactivated:
        await db.delete_user(int(user_id))
        return False, "Deleted"
    except UserIsBlocked:
        await db.delete_user(int(user_id))
        return False, "Blocked"
    except PeerIdInvalid:
        await db.delete_user(int(user_id))
        return False, "Error"
    except Exception as e:
        logger.error(f"[!] Broadcast error for {user_id}: {e}")
        return False, "Error"

# ---------------------------------------------------
# /broadcast - Admin Mass Messaging
# ---------------------------------------------------
@Client.on_message(filters.command("broadcast") & filters.user(ADMINS))
async def broadcast_command(bot: Client, message: Message):
    b_msg = message.reply_to_message
    if not b_msg:
        return await message.reply_text(
            "📝 Reply to this command with the message you want to broadcast.",
            quote=True
        )

    users = await db.get_all_users()
    sts = await message.reply_text(
        text='📡 Initializing global broadcast...',
        quote=True
    )

    start_time = time.time()
    total_users = await db.total_users_count()
    done = 0
    blocked = 0
    deleted = 0
    failed = 0
    success = 0

    async for user in users:
        user_id = user.get('id')
        if user_id:
            pti, sh = await broadcast_messages(int(user_id), b_msg)
            if pti:
                success += 1
            else:
                if sh == "Blocked":
                    blocked += 1
                elif sh == "Deleted":
                    deleted += 1
                elif sh == "Error":
                    failed += 1
            done += 1

            if done % 20 == 0:
                await sts.edit(
                    f"🛰 𝐁𝐫𝐨𝐚𝐝𝐜𝐚𝐬𝐭 𝐈𝐧 𝐏𝐫𝐨𝐠𝐫𝐞𝐬𝐬\n\n"
                    f"👥 𝐓𝐨𝐭𝐚𝐥 𝐔𝐬𝐞𝐫𝐬: {total_users}\n"
                    f"🌀 𝐂𝐨𝐦𝐩𝐥𝐞𝐭𝐞𝐝: {done} / {total_users}\n"
                    f"✅ 𝐒𝐮𝐜𝐜𝐞𝐬𝐬: {success}\n"
                    f"🚫 𝐁𝐥𝐨𝐜𝐤𝐞𝐝: {blocked}\n"
                    f"🚮 𝐃𝐞𝐥𝐞𝐭𝐞𝐝: {deleted}"
                )
        else:
            done += 1
            failed += 1

    time_taken = datetime.timedelta(seconds=int(time.time() - start_time))
    await sts.edit(
        f"🎊 𝐁𝐫𝐨𝐚𝐝𝐜𝐚𝐬𝐭 𝐂𝐨𝐦𝐩𝐥𝐞𝐭𝐞𝐝\n"
        f"⏱️ 𝐓𝐢𝐦𝐞 𝐓𝐚𝐤𝐞𝐧: {time_taken}\n\n"
        f"📊 𝐒𝐮𝐦𝐦𝐚𝐫𝐲:\n"
        f"‣ Total Users: {total_users}\n"
        f"‣ Success: {success}\n"
        f"‣ Blocked: {blocked}\n"
        f"‣ Deleted: {deleted}"
    )

# ---------------------------------------------------
# /users - Advanced Analytics & JSON Export
# ---------------------------------------------------
@Client.on_message(filters.command("users") & filters.user(ADMINS))
async def users_count(bot: Client, message: Message):
    msg = await message.reply_text("⏳ Processing user analytics...", quote=True)
    try:
        total = await db.total_users_count()
        await msg.edit_text(
            f"📊 𝐒𝐲𝐬𝐭𝐞𝐦 𝐔𝐬𝐞𝐫 𝐀𝐧𝐚𝐥𝐲𝐭𝐢𝐜𝐬\n\n"
            f"👥 Total Registered: {total}\n"
            f"📡 Server Status: Active ✅\n"
            f"🧠 Database: MongoDB (Async Mode)\n\n"
            f"<i>Generating full user list for export...</i>",
            parse_mode=enums.ParseMode.HTML
        )

        users_cursor = await db.get_all_users()
        users_list = []
        async for user in users_cursor:
            users_list.append({
                "name": user.get("name", "None"),
                "username": user.get("username", "None"),
                "id": user.get("id")
            })

        tmp_path = "User_Database.json"
        with open(tmp_path, "w", encoding="utf-8") as f:
            json.dump(users_list, f, indent=2, ensure_ascii=False)

        await message.reply_document(
            document=tmp_path,
            caption=f"📄 User database backup recorded.\n👥 Total: {len(users_list)} Users"
        )

        try:
            os.remove(tmp_path)
        except Exception as e:
            logger.error(f"[!] Failed to Delete File {tmp_path}: {e}")

    except Exception as e:
        await msg.edit_text(f"❌ Error fetching user data: {e}")
        logger.error(f"[!] /users error: {e}")

# Developer - @usrhtff009
# Channel - https://t.me/usrht01
