# Developer - @usrhtff009
# Channel - https://t.me/usrht01
# Purpose - Advanced Logging System for VPS/Cloud Deployment

import logging
from logging.handlers import RotatingFileHandler

# ==========================================
# 📊 𝐋𝐨𝐠𝐠𝐢𝐧𝐠 𝐂𝐨𝐧𝐟𝐢𝐠𝐮𝐫𝐚𝐭𝐢𝐨𝐧
# ==========================================

# Standard format for clean console output
SHORT_LOG_FORMAT = "[%(asctime)s - %(levelname)s] - %(name)s - %(message)s"

# Detailed format for deep debugging (if needed)
FULL_LOG_FORMAT = "%(asctime)s - [%(levelname)s] - %(name)s - %(message)s (%(filename)s:%(lineno)d)"

# Configure logging system
logging.basicConfig(
    level=logging.INFO,
    format=SHORT_LOG_FORMAT,
    handlers=[
        # Auto-rotate: Max 5MB per file, keeps up to 10 historical logs
        RotatingFileHandler("logs.txt", maxBytes=5 * 1024 * 1024, backupCount=10),
        
        # Stream logs to terminal/cloud console
        logging.StreamHandler()
    ]
)

# Suppress unnecessary noise from external libraries
logging.getLogger("pyrogram").setLevel(logging.WARNING)
logging.getLogger("motor").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)

def LOGGER(name: str) -> logging.Logger:
    """
    Returns a professional configured logger instance.
    """
    return logging.getLogger(name)

# Developer - @usrhtff009
