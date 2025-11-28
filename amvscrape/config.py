"""
Zentrale Konfiguration für amvscrape
"""

import os
from pathlib import Path

# Projekt-Root (Parent von amvscrape/)
PROJECT_ROOT = Path(__file__).parent.parent

# URLs
BASE_URL = "https://amvnews.ru"
NEWS_URL = f"{BASE_URL}/index.php?go=News&in=cat&id=1"

# Pfade
DB_PATH = PROJECT_ROOT / "amvscrape.db"
TORRENT_DIR = PROJECT_ROOT / "torrent-files"

# HTTP Settings
USER_AGENT = "Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/115.0"
REQUEST_TIMEOUT = 30  # Sekunden
REQUEST_DELAY = 1.0  # Sekunden zwischen Requests

# Torrent Client
TORRENT_CLIENT_CMD = "deluge-gtk"  # Muss auf System installiert sein
