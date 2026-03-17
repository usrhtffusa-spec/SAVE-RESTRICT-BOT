# Developer - @usrhtff009
# Channel - https://t.me/usrht01

from pyrogram import Client, filters, enums
from pyrogram.types import Message
from database.db import db

# ======================================================
# /set_caption - Set Professional Custom Caption
# ======================================================
@Client.on_message(filters.command("set_caption") & filters.private)
async def set_caption(client: Client, message: Message):
    user_id = message.from_user.id

    # 1. Ensure User Exists
    if not await db.is_user_exist(user_id):
        await db.add_user(user_id, message.from_user.first_name)

    # 2. Validate Input
    if len(message.command) < 2:
        return await message.reply_text(
            "✍️ 𝐒𝐞𝐭 𝐂𝐮𝐬𝐭𝐨𝐦 𝐂𝐚𝐩𝐭𝐢𝐨𝐧\n\n"
            "Please provide the caption text after the command.\n\n"
            "📥 𝐅𝐨𝐫𝐦𝐚𝐭:\n"
            "/set_caption Your Caption Here\n\n"
            "🧩 𝐒𝐮𝐩𝐩𝐨𝐫𝐭𝐞𝐝 𝐏𝐥𝐚𝐜𝐞𝐡𝐨𝐥𝐝𝐞𝐫𝐬:\n"
            "‣ {filename} : Original File Name\n"
            "‣ {size} : Processed File Size\n\n"
            "💡 𝐄𝐱𝐚𝐦𝐩𝐥𝐞:\n"
            "File: {filename} | Size: {size}"
        )

    # 3. Save to Database
    caption = message.text.split(" ", 1)[1].strip()
    await db.set_caption(user_id, caption)

    await message.reply_text(
        "✅ 𝐂𝐮𝐬𝐭𝐨𝐦 𝐂𝐚𝐩𝐭𝐢𝐨𝐧 𝐒𝐚𝐯𝐞𝐝!\n\n"
        f"📝 𝐏𝐫𝐞𝐯𝐢𝐞𝐰:\n{caption}\n\n"
        "This layout will be applied to all your future downloads."
    )

# ======================================================
# /see_caption - View Current Active Caption
# ======================================================
@Client.on_message(filters.command("see_caption") & filters.private)
async def see_caption(client: Client, message: Message):
    user_id = message.from_user.id

    # 1. Ensure User Exists
    if not await db.is_user_exist(user_id):
        await db.add_user(user_id, message.from_user.first_name)

    # 2. Fetch Caption
    caption = await db.get_caption(user_id)

    if caption:
        await message.reply_text(
            "📋 𝐘𝐨𝐮𝐫 𝐀𝐜𝐭𝐢𝐯𝐞 𝐂𝐮𝐬𝐭𝐨𝐦 𝐂𝐚𝐩𝐭𝐢𝐨𝐧\n\n"
            f"{caption}\n\n"
            "To reset this, use /del_caption"
        )
    else:
        await message.reply_text(
            "❌ 𝐍𝐨 𝐂𝐮𝐬𝐭𝐨𝐦 𝐂𝐚𝐩𝐭𝐢𝐨𝐧 𝐒𝐞𝐭\n\n"
            "You are currently using the default system caption.\n"
            "Use /set_caption to personalize your files."
        )

# ======================================================
# /del_caption - Remove Custom Caption
# ======================================================
@Client.on_message(filters.command("del_caption") & filters.private)
async def del_caption(client: Client, message: Message):
    user_id = message.from_user.id

    # 1. Ensure User Exists
    if not await db.is_user_exist(user_id):
        await db.add_user(user_id, message.from_user.first_name)

    # 2. Check if caption exists
    caption = await db.get_caption(user_id)

    if not caption:
        return await message.reply_text(
            "⚠️ 𝐍𝐨 𝐂𝐚𝐩𝐭𝐢𝐨𝐧 𝐅𝐨𝐮𝐧𝐝\n\n"
            "You don't have any custom caption set to delete."
        )

    # 3. Delete from Database
    await db.del_caption(user_id)

    await message.reply_text(
        "🗑 𝐂𝐮𝐬𝐭𝐨𝐦 𝐂𝐚𝐩𝐭𝐢𝐨𝐧 𝐑𝐞𝐦𝐨𝐯𝐞𝐝\n\n"
        "Your uploads will now revert to the default bot caption."
    )

# Developer - @usrhtff009
# Channel - https://t.me/usrht01
