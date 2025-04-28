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

__version__ = "1.0.0"
__author__ = "Your Name"
__license__ = "MIT"

# Import main components for easier access
from src.bot import AgeVerificationBot
from src.utils.database import Database
from src.utils.face_detection import FaceDetector

# Make sure cogs directory is treated as a package
import src.cogs

__all__ = ['AgeVerificationBot', 'Database', 'FaceDetector']
