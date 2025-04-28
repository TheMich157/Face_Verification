"""
Bot cogs package containing all command modules.
"""

import os
import importlib
import pkgutil

def init_cogs():
    """Initialize all cogs in the package"""
    cogs = []
    cogs_dir = os.path.dirname(__file__)
    
    # Import all modules in this package
    for _, module_name, _ in pkgutil.iter_modules([cogs_dir]):
        if not module_name.startswith('__'):
            cogs.append(f"src.cogs.{module_name}")
    
    return cogs

# List of available cogs for the bot to load
AVAILABLE_COGS = init_cogs()

def get_all_cog_paths():
    """Get a list of all available cog paths"""
    return AVAILABLE_COGS

# Make cogs available at package level
__all__ = ['get_all_cog_paths', 'AVAILABLE_COGS']
