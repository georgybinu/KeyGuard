"""
Logging utility for KeyGuard backend
"""
import logging
import os
from datetime import datetime

LOG_DIR = "./logs"
os.makedirs(LOG_DIR, exist_ok=True)

# Create logger
logger = logging.getLogger("keyguard_backend")
logger.setLevel(logging.DEBUG)

# File handler
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
fh = logging.FileHandler(f"{LOG_DIR}/keyguard_{timestamp}.log")
fh.setLevel(logging.DEBUG)

# Console handler
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)

# Formatter
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
ch.setFormatter(formatter)

# Add handlers
logger.addHandler(fh)
logger.addHandler(ch)

def get_logger():
    return logger
