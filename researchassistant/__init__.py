"""
researchassistant

Find what you're looking for
"""

__version__ = "0.1.8"
__author__ = "Moon (https://github.com/lalalune)"
__credits__ = "https://github.com/lalalune/researchassistant"

from .extract import extract_from_file_or_url, extract
from .crawl import crawl

__all__ = [
    "crawl",
    "extract_from_file_or_url",
    "extract",
]
