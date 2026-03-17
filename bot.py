
# Developer - @usrhtff009
# Channel - https://t.me/usrht01

import asyncio
import datetime
import sys
import os
from datetime import timezone, timedelta
from pyrogram import Client, filters, enums, __version__ as pyrogram_version
from pyrogram.types import Message, BotCommand
from pyrogram.errors import FloodWait, RPCError
from config import API_ID, API_HASH, BOT_TOKEN, LOG_CHANNEL, ADMINS
from database.db import db
from logger import LOGGER

# Keep-alive server for Render / Cloud
try:
    from keep_alive import keep_alive
except ImportError:
    keep_alive = None

logger = LOGGER(__name__)
IST = timezone(timedelta(hours=5, minutes=30))

# User Cache to prevent DB lag on high traffic
USER_CACHE = set()

LOGO = r"""
  ██████╗  ██╗  ██╗  █████╗  ███╗   ██╗ ██████╗   █████╗  ██╗      
  ██╔══██╗ ██║  ██║ ██╔══██╗ ████╗  ██║ ██╔══██╗ ██╔══██╗ ██║      
  ██║  ██║ ███████║ ███████║ ██╔██╗ ██║ ██████╔╝ ███████║ ██║      
  ██║  ██║ ██╔══██║ ██╔══██║ ██║╚██╗██║ ██╔═══╝  ██╔══██║ ██║      
  ██████╔╝ ██║  ██║ ██║  ██║ ██║ ╚████║ ██║      ██║  ██║ ███████
    𝚂𝚈𝚂𝚃𝙴𝙼 𝙾𝙽𝙻𝙸𝙽𝙴 & 𝚁𝙴𝙰𝙳𝚈....
"""

class Bot(Client):
    def __init__(self):
        super().__init__(
            name="Restricted_Saver_Bot",
            api_id=API_ID,
            api_hash=API_HASH,
            bot_token=BOT_TOKEN,
            plugins=dict(root="plugins"), # Auto-loads files from plugins folder
            workers=20, 
            sleep_threshold=15,
            max_concurrent_transmissions=5,
            ipv6=False,
            in_memory=True,
        )
        self._keep_alive_started = False

    async def start(self):
        print(LOGO)

        # 1. Start keep-alive (Crucial for Render/Cloud)
        if keep_alive and not self._keep_alive_started:
            try:
                loop = asyncio.get_running_loop()
                keep_alive(loop)
                self._keep_alive_started = True
                logger.info("Keep-alive server operational.")
            except Exception as e:
                logger.warning(f"Keep-alive warning: {e}")

        # 2. Resilient Login Loop (Fix for FloodWait)
        while True:
            try:
                await super().start()
                break 
            except FloodWait as e:
                wait_time = int(e.value) + 10
                logger.warning(f"Flood Wait: Sleeping for {wait_time}s...")
                await asyncio.sleep(wait_time)
            except Exception as e:
                logger.error(f"Startup Crash: {e}")
                await asyncio.sleep(15)

        me = await self.get_me()

        # 3. Database Statistics
        try:
            user_count = await db.total_users_count()
            logger.info(f"DB Connected: {user_count} Users found.")
        except Exception as e:
            logger.error(f"DB Error: {e}")
            user_count = "N/A"

        # 4. Startup Notification
        now = datetime.datetime.now(IST)
        startup_text = (
            f"<b>🚀 𝐒𝐲𝐬𝐭𝐞𝐦 𝐔𝐩𝐝𝐚𝐭𝐞: 𝐎𝐧𝐥𝐢𝐧𝐞</b>\n\n"
            f"<b>🤖 Bot:</b> @{me.username}\n"
            f"<b>👤 Users:</b> <code>{user_count}</code>\n"
            f"<b>🕒 Time:</b> <code>{now.strftime('%I:%M %p')} IST</code>\n\n"
            f"<b>Developed by: @usrhtff009</b>"
        )

        try:
            await self.send_message(LOG_CHANNEL, startup_text)
            logger.info("Startup log dispatched to channel.")
        except Exception as e:
            logger.error(f"Logging Error: {e}")

        await self.set_bot_commands_list()

    async def stop(self, *args):
        try:
            await self.send_message(LOG_CHANNEL, "<b>❌ System going Offline...</b>")
        except:
            pass
        await asyncio.shield(super().stop())
        logger.info("Bot terminated cleanly.")

    async def set_bot_commands_list(self):
        commands = [
            BotCommand("start", "🏠 Home"),
            BotCommand("help", "📖 User Guide"),
            BotCommand("login", "🔑 Authenticate Session"),
            BotCommand("logout", "🚪 Terminate Session"),
            BotCommand("cancel", "🛑 Stop Task"),
            BotCommand("myplan", "📊 Plan Details"),
            BotCommand("premium", "💎 Upgrade Tier"),
            BotCommand("settings", "⚙️ Bot Settings"),
            BotCommand("setchat", "🎯 Set Dump Chat"),
            BotCommand("set_thumb", "🖼 Set Thumbnail"),
            BotCommand("set_caption", "📝 Set Caption"),
        ]
        await self.set_bot_commands(commands)

BotInstance = Bot()

@BotInstance.on_message(filters.private & filters.incoming, group=-1)
async def new_user_log(bot: Client, message: Message):
    user = message.from_user
    if not user or user.id in USER_CACHE:
        return

    if not await db.is_user_exist(user.id):
        await db.add_user(user.id, user.first_name)
        now = datetime.datetime.now(IST)
        log_text = (
            f"<b>#NewUser 👤</b>\n"
            f"<b>User:</b> {user.mention}\n"
            f"<b>ID:</b> <code>{user.id}</code>\n"
            f"<b>Time:</b> {now.strftime('%I:%M %p')} IST"
        )
        try:
            await bot.send_message(LOG_CHANNEL, log_text)
        except:
            pass

    USER_CACHE.add(user.id)

if __name__ == "__main__":
    BotInstance.run()

