"""
Utility modules for the bot.
Contains database and face detection utilities.
"""

from src.utils.database import Database
from src.utils.face_detection import FaceDetector

__all__ = ['Database', 'FaceDetector']

# Version of the utils package
__version__ = "1.0.0"

# Expose main classes for easier imports
Database = Database
FaceDetector = FaceDetector
