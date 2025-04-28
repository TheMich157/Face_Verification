"""
Bot cogs package containing all command modules.
"""

import os
import importlib
import pkgutil

# Import all modules in this package
__all__ = []
for loader, module_name, is_pkg in pkgutil.walk_packages([os.path.dirname(__file__)]):
    __all__.append(module_name)
    module = importlib.import_module(f"{__package__}.{module_name}")
    
# List of available cogs for the bot to load
AVAILABLE_COGS = [
    'verification',
    'admin',
    'moderation',
    'statistics',
    'appeals',
    'automod',
    'admin_control',
    'privacy',
    'advanced_features'
]

# Function to get full cog path
def get_cog_path(cog_name):
    """Get the full import path for a cog"""
    return f"src.cogs.{cog_name}"

# Function to get all cog paths
def get_all_cog_paths():
    """Get a list of all available cog paths"""
    return [get_cog_path(cog) for cog in AVAILABLE_COGS]
