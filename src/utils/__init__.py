"""
Utility modules for the bot.
Contains database and face detection utilities.
"""

import os
import sys

# Add the project root directory to Python path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Import utilities
from src.utils.database import Database
from src.utils.face_detection import FaceDetector

# Make utilities available at package level
__all__ = ['Database', 'FaceDetector']

# Initialize logging
import logging
logger = logging.getLogger('age-verify-bot.utils')
logger.addHandler(logging.NullHandler())

# Load configuration if needed
import json
config_path = os.path.join(project_root, 'config', 'config.json')
try:
    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)
except (FileNotFoundError, json.JSONDecodeError) as e:
    config = {}
    logger.warning(f"Could not load config in utils: {e}")

# Make config available at package level
__config__ = config

# Version of the utils package
__version__ = "1.0.0"

# Expose main classes
Database = Database
FaceDetector = FaceDetector
