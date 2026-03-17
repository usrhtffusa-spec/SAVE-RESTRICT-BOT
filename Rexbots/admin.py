# Developer - @usrhtff009
# Channel - https://t.me/usrht01

from pyrogram import Client, filters, enums
from pyrogram.types import Message
from database.db import db
from config import ADMINS, DB_URI

# ======================================================
# /ban - Ban User from System
# ======================================================
@Client.on_message(filters.command("ban") & filters.user(ADMINS))
async def ban(client: Client, message: Message):
    if len(message.command) < 2:
        return await message.reply_text("⚖️ 𝐔𝐬𝐚𝐠𝐞: /ban user_id")
    try:
        user_id = int(message.command[1])
        await db.ban_user(user_id)
        await message.reply_text(f"🚫 𝐔𝐬𝐞𝐫 {user_id} has been banned successfully.")
    except Exception as e:
        await message.reply_text(f"❌ Error during banning: {e}")

# ======================================================
# /unban - Revoke User Ban
# ======================================================
@Client.on_message(filters.command("unban") & filters.user(ADMINS))
async def unban(client: Client, message: Message):
    if len(message.command) < 2:
        return await message.reply_text("⚖️ 𝐔𝐬𝐚𝐠𝐞: /unban user_id")
    try:
        user_id = int(message.command[1])
        await db.unban_user(user_id)
        await message.reply_text(f"✅ 𝐔𝐬𝐞𝐫 {user_id} has been unbanned.")
    except Exception as e:
        await message.reply_text(f"❌ Error during unbanning: {e}")

# ======================================================
# /set_dump - Configure Global Dump Channel
# ======================================================
@Client.on_message(filters.command("set_dump") & filters.user(ADMINS))
async def set_dump(client: Client, message: Message):
    if len(message.command) < 3:
        return await message.reply_text("⚖️ 𝐔𝐬𝐚𝐠𝐞: /set_dump user_id chat_id")
    try:
        user_id = int(message.command[1])
        chat_id = int(message.command[2])
        await db.set_dump_chat(user_id, chat_id)
        await message.reply_text(f"🎯 𝐃𝐮𝐦𝐩 𝐂𝐡𝐚𝐭 configured for UID: {user_id}")
    except Exception as e:
        await message.reply_text(f"❌ Configuration error: {e}")

# ======================================================
# /dblink - View Database Configuration
# ======================================================
@Client.on_message(filters.command("dblink") & filters.user(ADMINS))
async def dblink(client: Client, message: Message):
    await message.reply_text(
        f"🌐 𝐃𝐚𝐭𝐚𝐛𝐚𝐬𝐞 𝐔𝐑𝐈:\n<code>{DB_URI}</code>",
        parse_mode=enums.ParseMode.HTML
    )

# ======================================================
# Subscription Management (Future Update)
# ======================================================
@Client.on_message(filters.command(["add_unsubscribe", "del_unsubscribe"]) & filters.user(ADMINS))
async def manage_force_subscribe(client: Client, message: Message):
    await message.reply_text("🛠 𝐅𝐨𝐫𝐜𝐞 𝐒𝐮𝐛𝐬𝐜𝐫𝐢𝐛𝐞 management is being optimized for the next update.")

# Developer - @usrhtff009
# Channel - https://t.me/usrht01
