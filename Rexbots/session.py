# Developer - @usrhtff009
# Channel - https://t.me/usrht01

import asyncio
from pyrogram import Client, filters, enums
from pyrogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from pyrogram.errors import (
    ApiIdInvalid,
    PhoneNumberInvalid,
    PhoneCodeInvalid,
    PhoneCodeExpired,
    SessionPasswordNeeded,
    PasswordHashInvalid
)
from config import API_ID, API_HASH
from database.db import db

LOGIN_STATE = {}
cancel_keyboard = ReplyKeyboardMarkup(
    [[KeyboardButton("❌ Cancel")]],
    resize_keyboard=True
)
remove_keyboard = ReplyKeyboardRemove()

PROGRESS_STEPS = {
    "WAITING_PHONE": "🟢 Phone Number → 🔵 Code → 🔵 Password",
    "WAITING_CODE": "✅ Phone Number → 🟢 Code → 🔵 Password",
    "WAITING_PASSWORD": "✅ Phone Number → ✅ Code → 🟢 Password"
}

LOADING_FRAMES = [
    "🔄 Connecting •••",
    "🔄 Connecting ••○",
    "🔄 Connecting •○○",
    "🔄 Connecting ○○○",
    "🔄 Connecting ○○•",
    "🔄 Connecting ○••",
    "🔄 Connecting •••"
]

async def animate_loading(message: Message, duration: int = 5):
    for _ in range(duration):
        for frame in LOADING_FRAMES:
            try:
                await message.edit_text(f"<b>{frame}</b>", parse_mode=enums.ParseMode.HTML)
                await asyncio.sleep(0.5)
            except:
                return

async def check_login_state(_, __, message):
    return message.from_user.id in LOGIN_STATE

login_state_filter = filters.create(check_login_state)

# ======================================================
# /login - Start the Authentication Process
# ======================================================
@Client.on_message(filters.private & filters.command("login"))
async def login_start(client: Client, message: Message):
    user_id = message.from_user.id

    user_data = await db.get_session(user_id)
    if user_data:
        return await message.reply(
            "✅ <b>You're already logged in!</b> 🎉\n\n"
            "<i>To switch accounts, please use /logout first.</i>",
            parse_mode=enums.ParseMode.HTML
        )

    LOGIN_STATE[user_id] = {"step": "WAITING_PHONE", "data": {}}
    progress = PROGRESS_STEPS["WAITING_PHONE"]
    
    await message.reply(
        f"👋 <b>Welcome to Secure Login</b> 🌟\n\n"
        f"<i>Status: {progress}</i>\n\n"
        "📞 Please send your <b>Telegram Phone Number</b> with your country code.\n\n"
        "📌 <b>Example:</b> <code>+919876543210</code>\n\n"
        "<i>💡 Your number is used only for verification and is kept 100% secure. 🔒</i>\n\n"
        "🛑 Tap the <b>Cancel</b> button below or send /cancel to stop.",
        parse_mode=enums.ParseMode.HTML,
        reply_markup=cancel_keyboard
    )

# ======================================================
# /logout - Terminate Current Session
# ======================================================
@Client.on_message(filters.private & filters.command("logout"))
async def logout(client: Client, message: Message):
    user_id = message.from_user.id

    if user_id in LOGIN_STATE:
        del LOGIN_STATE[user_id]

    await db.set_session(user_id, session=None)
    await message.reply(
        "🚪 <b>Logout Successful!</b> 👋\n\n"
        "<i>Your session has been securely cleared. You can log in again anytime! 🔄</i>",
        parse_mode=enums.ParseMode.HTML,
        reply_markup=remove_keyboard
    )

# ======================================================
# /cancel - Halt Login Process (Smart Filtered)
# ======================================================
@Client.on_message(filters.private & filters.command(["cancel", "cancellogin"]) & login_state_filter)
async def cancel_login(client: Client, message: Message):
    user_id = message.from_user.id

    state = LOGIN_STATE[user_id]
    if "data" in state and "client" in state["data"]:
        try:
            await state["data"]["client"].disconnect()
        except:
            pass

    del LOGIN_STATE[user_id]
    await message.reply(
        "❌ <b>Login process cancelled successfully.</b> 😌",
        parse_mode=enums.ParseMode.HTML,
        reply_markup=remove_keyboard
    )

# ======================================================
# Active Login State Handler
# ======================================================
@Client.on_message(filters.private & filters.text & login_state_filter & ~filters.command(["cancel", "cancellogin"]))
async def login_handler(bot: Client, message: Message):
    user_id = message.from_user.id
    text = message.text
    state = LOGIN_STATE[user_id]
    step = state["step"]
    progress = PROGRESS_STEPS.get(step, "")

    if text.strip().lower() == "❌ cancel":
        if "data" in state and "client" in state["data"]:
            try:
                await state["data"]["client"].disconnect()
            except:
                pass
        del LOGIN_STATE[user_id]
        await message.reply(
            "❌ <b>Login process cancelled.</b> 😌",
            parse_mode=enums.ParseMode.HTML,
            reply_markup=remove_keyboard
        )
        return

    if step == "WAITING_PHONE":
        phone_number = text.replace(" ", "")

        temp_client = Client(
            name=f"session_{user_id}",
            api_id=API_ID,
            api_hash=API_HASH,
            in_memory=True
        )

        status_msg = await message.reply(
            f"🔄 <b>Connecting to Telegram Data Centers...</b> 🌐\n\n<i>Status: {progress}</i>",
            parse_mode=enums.ParseMode.HTML
        )

        animation_task = asyncio.create_task(animate_loading(status_msg))
        await temp_client.connect()
        animation_task.cancel() 

        try:
            code = await temp_client.send_code(phone_number)

            state["data"]["client"] = temp_client
            state["data"]["phone"] = phone_number
            state["data"]["hash"] = code.phone_code_hash
            state["step"] = "WAITING_CODE"
            progress = PROGRESS_STEPS["WAITING_CODE"]

            await status_msg.edit(
                f"📩 <b>OTP Sent Successfully!</b> 📲\n\n"
                f"<i>Status: {progress}</i>\n\n"
                "Please check your official Telegram app for the verification code.\n\n"
                "📌 <b>Send it like this:</b> <code>12 345</code> or <code>1 2 3 4 5</code>\n\n"
                "<i>💡 Adding spaces prevents Telegram from auto-deleting the message.</i>",
                parse_mode=enums.ParseMode.HTML
            )

        except PhoneNumberInvalid:
            await status_msg.edit(
                "❌ <b>Invalid Phone Number Format.</b> 😅\n\n"
                f"<i>Status: {progress}</i>\n\n"
                "Please check your country code and try again (e.g., +919876543210).",
                parse_mode=enums.ParseMode.HTML
            )
            await temp_client.disconnect()
            del LOGIN_STATE[user_id]
        except Exception as e:
            await status_msg.edit(
                f"❌ <b>Connection Error:</b> <code>{e}</code> 🤔\n\n"
                f"<i>Status: {progress}</i>\n\nPlease try /login again.",
                parse_mode=enums.ParseMode.HTML
            )
            await temp_client.disconnect()
            del LOGIN_STATE[user_id]

    elif step == "WAITING_CODE":
        phone_code = text.replace(" ", "")

        temp_client = state["data"]["client"]
        phone_number = state["data"]["phone"]
        phone_hash = state["data"]["hash"]

        status_msg = await message.reply(
            f"🔍 <b>Verifying your code...</b> ⏳\n\n<i>Status: {progress}</i>",
            parse_mode=enums.ParseMode.HTML
        )

        animation_task = asyncio.create_task(animate_loading(status_msg, duration=3))

        try:
            await temp_client.sign_in(phone_number, phone_hash, phone_code)
            animation_task.cancel()
            await finalize_login(status_msg, temp_client, user_id)
            
        except PhoneCodeInvalid:
            animation_task.cancel()
            await status_msg.edit(
                "❌ <b>Incorrect Verification Code.</b> 🔍\n\n"
                f"<i>Status: {progress}</i>\n\nPlease check your Telegram app and send the correct code.",
                parse_mode=enums.ParseMode.HTML
            )
        except PhoneCodeExpired:
            animation_task.cancel()
            await status_msg.edit(
                "⏰ <b>Code Expired.</b> ⏳\n\n"
                f"<i>Status: {progress}</i>\n\nPlease restart the process using /login.",
                parse_mode=enums.ParseMode.HTML
            )
            await temp_client.disconnect()
            del LOGIN_STATE[user_id]
        except SessionPasswordNeeded:
            animation_task.cancel()
            state["step"] = "WAITING_PASSWORD"
            progress = PROGRESS_STEPS["WAITING_PASSWORD"]
            
            await status_msg.edit(
                f"🔐 <b>Two-Step Verification Detected</b> 🔒\n\n"
                f"<i>Status: {progress}</i>\n\n"
                "Your account is protected. Please enter your <b>password</b> to continue.\n\n"
                "<i>🛡️ Take your time — this process is fully encrypted.</i>",
                parse_mode=enums.ParseMode.HTML
            )
        except Exception as e:
            animation_task.cancel()
            await status_msg.edit(
                f"❌ <b>Authentication Error:</b> <code>{e}</code> 🤔\n\n<i>Status: {progress}</i>",
                parse_mode=enums.ParseMode.HTML
            )
            await temp_client.disconnect()
            del LOGIN_STATE[user_id]

    elif step == "WAITING_PASSWORD":
        password = text
        temp_client = state["data"]["client"]

        status_msg = await message.reply(
            f"🔑 <b>Authenticating password...</b> ⏳\n\n<i>Status: {progress}</i>",
            parse_mode=enums.ParseMode.HTML
        )

        animation_task = asyncio.create_task(animate_loading(status_msg, duration=3))

        try:
            await temp_client.check_password(password=password)
            animation_task.cancel()
            await finalize_login(status_msg, temp_client, user_id)
            
        except PasswordHashInvalid:
            animation_task.cancel()
            await status_msg.edit(
                "❌ <b>Incorrect Password.</b> 🔑\n\n"
                f"<i>Status: {progress}</i>\n\nPlease check your password and try again.",
                parse_mode=enums.ParseMode.HTML
            )
        except Exception as e:
            animation_task.cancel()
            await status_msg.edit(
                f"❌ <b>Error:</b> <code>{e}</code> 🤔\n\n<i>Status: {progress}</i>",
                parse_mode=enums.ParseMode.HTML
            )
            await temp_client.disconnect()
            del LOGIN_STATE[user_id]

async def finalize_login(status_msg: Message, temp_client, user_id):
    try:
        session_string = await temp_client.export_session_string()
        await temp_client.disconnect()

        await db.set_session(user_id, session=session_string)

        if user_id in LOGIN_STATE:
            del LOGIN_STATE[user_id]

        await status_msg.edit(
            "🎉 <b>Login Successful!</b> 🌟\n\n"
            "<i>Status: ✅ Phone Number → ✅ Code → ✅ Password</i>\n\n"
            "<i>Your session string has been generated and saved securely. 🔒</i>\n\n"
            "🚀 <b>You are now ready to download restricted content!</b>",
            parse_mode=enums.ParseMode.HTML,
            reply_markup=remove_keyboard
        )
    except Exception as e:
        await status_msg.edit(
            f"❌ <b>Failed to generate session:</b> <code>{e}</code> 😔\n\nPlease try /login again.",
            parse_mode=enums.ParseMode.HTML,
            reply_markup=remove_keyboard
        )
        if user_id in LOGIN_STATE:
            del LOGIN_STATE[user_id]

# Developer - @usrhtff009
# Channel - https://t.me/usrht01
