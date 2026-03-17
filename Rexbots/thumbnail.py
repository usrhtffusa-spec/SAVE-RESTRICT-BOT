# Developer - @usrhtff009
# Channel - https://t.me/usrht01

from pyrogram import Client, filters, enums
from pyrogram.types import Message
from database.db import db

# ======================================================
# /set_thumb - Set Custom Thumbnail (Reply to Photo)
# ======================================================
@Client.on_message(filters.command("set_thumb") & filters.private)
async def set_custom_thumbnail(client: Client, message: Message):
    user_id = message.from_user.id

    # 1. Ensure User Exists
    if not await db.is_user_exist(user_id):
        await db.add_user(user_id, message.from_user.first_name)

    # 2. Validate Reply
    if not message.reply_to_message or not message.reply_to_message.photo:
        return await message.reply_text(
            "🖼 Set Custom Thumbnail\n\n"
            "Reply to any photo with /set_thumb to use it as your default thumbnail.\n\n"
            "Usage: Reply to a photo -> /set_thumb"
        )

    # 3. Save File ID to Database (NOT Path)
    # This ensures it works even if the bot restarts
    file_id = message.reply_to_message.photo.file_id
    await db.set_thumbnail(user_id, file_id)

    await message.reply_photo(
        photo=file_id,
        caption=(
            "✅ Custom Thumbnail Set Successfully!\n\n"
            "This thumbnail will be used for all your future uploads.\n"
            "Use /view_thumb to preview • /del_thumb to remove"
        )
    )

# ======================================================
# /view_thumb - Preview Current Thumbnail
# ======================================================
@Client.on_message(filters.command(["view_thumb", "see_thumb"]) & filters.private)
async def view_custom_thumbnail(client: Client, message: Message):
    user_id = message.from_user.id

    if not await db.is_user_exist(user_id):
        await db.add_user(user_id, message.from_user.first_name)

    thumb_id = await db.get_thumbnail(user_id)

    if thumb_id:
        try:
            await message.reply_photo(
                photo=thumb_id,
                caption=(
                    "🖼 Your Current Custom Thumbnail\n\n"
                    "This is applied to all uploads.\n"
                    "To delete, use /del_thumb"
                )
            )
        except Exception as e:
            # If file_id is invalid/old
            await message.reply_text(f"❌ Error loading thumbnail: {e}\nPlease set a new one.")
    else:
        await message.reply_text(
            "❌ No Custom Thumbnail Found\n\n"
            "Reply to a photo with /set_thumb to add one."
        )

# ======================================================
# /del_thumb - Remove Custom Thumbnail
# ======================================================
@Client.on_message(filters.command(["del_thumb", "delete_thumb"]) & filters.private)
async def delete_custom_thumbnail(client: Client, message: Message):
    user_id = message.from_user.id

    if not await db.is_user_exist(user_id):
        await db.add_user(user_id, message.from_user.first_name)

    thumb_id = await db.get_thumbnail(user_id)

    if not thumb_id:
        return await message.reply_text(
            "ℹ️ You don't have a custom thumbnail set."
        )

    # Remove from DB
    await db.del_thumbnail(user_id)

    await message.reply_text(
        "🗑 Custom Thumbnail Deleted\n\n"
        "Your uploads will now use the default video/file thumbnail."
    )

# ======================================================
# /thumb_mode - Check Status
# ======================================================
@Client.on_message(filters.command("thumb_mode") & filters.private)
async def thumbnail_status(client: Client, message: Message):
    user_id = message.from_user.id
    if not await db.is_user_exist(user_id):
        await db.add_user(user_id, message.from_user.first_name)

    thumb_id = await db.get_thumbnail(user_id)

    if thumb_id:
        status = "🟢 Custom Thumbnail Active"
        extra = "Use /view_thumb to preview"
    else:
        status = "🔴 No Custom Thumbnail"
        extra = "Use /set_thumb (reply to photo) to enable"

    await message.reply_text(
        f"🖼 Thumbnail Status\n\n"
        f"{status}\n"
        f"{extra}"
    )

# Developer - @usrhtff009
# Channel - https://t.me/usrht01
