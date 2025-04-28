"""
Discord Age Verification Bot
A comprehensive bot for age verification and management.
"""

import os
import sys

# Add the project root directory to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Package metadata
__version__ = "1.0.0"
__author__ = "Your Name"
__license__ = "MIT"

# Import main components
from src.bot import AgeVerificationBot
from src.utils.database import Database
from src.utils.face_detection import FaceDetector
from src.cogs import get_all_cog_paths, AVAILABLE_COGS

# Export main components
__all__ = [
    'AgeVerificationBot',
    'Database',
    'FaceDetector',
    'get_all_cog_paths',
    'AVAILABLE_COGS',
]

# Initialize logging
import logging
logging.getLogger('age-verify-bot').addHandler(logging.NullHandler())

# Load configuration
import json
config_path = os.path.join(project_root, 'config', 'config.json')
try:
    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)
except (FileNotFoundError, json.JSONDecodeError) as e:
    config = {}
    logging.getLogger('age-verify-bot').warning(f"Could not load config: {e}")

# Make config available at package level
__config__ = config
