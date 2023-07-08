"""
researchassistant

Find what you're looking for
"""

__version__ = "0.1.8"
__author__ = "Moon (https://github.com/lalalune)"
__credits__ = "https://github.com/lalalune/researchassistant"

from .research import research
from .archive import import_archive, export_archive
from .search import search

__all__ = [
    "create_memory",
    "get_memories",
    "search_memory",
    "get_memory",
    "update_memory",
    "delete_memory",
    "count_memories",
    "wipe_category",
    "wipe_all_memories",
]
