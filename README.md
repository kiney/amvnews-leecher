# amvscrape

CLI tool to scrape and download AMV torrents from amvnews.ru

## What it does

- Scrapes AMV metadata from amvnews.ru (423+ pages, ~4000+ videos)
- Downloads .torrent files
- Tracks your collection status in SQLite
- Integrates with deluge-gtk

## Installation

```bash
git clone <repo>
cd amvnews-leecher
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
pip install -e .
```

## Requirements

- Python 3.8+
- deluge-gtk (for sending torrents to client)

**Note:** Currently only deluge-gtk is supported as torrent client. If you need a different client, you'll have to code it yourself.

## Usage

### Scrape AMV metadata

```bash
# Scrape first 10 pages
amvscrape scrape 10

# Scrape everything (takes a while)
amvscrape scrape
```

### Download torrent files

```bash
# Download specific AMV
amvscrape download 12807

# Download all pending (state=0)
amvscrape download
```

### Send to torrent client

```bash
# Send specific AMVs (recommended: multiple at once = fewer dialogs)
amvscrape torrent 12807 12806 12805

# Send all ready torrents (state=1)
amvscrape torrent
```

### Mark existing collection

```bash
# Scan directory and mark AMVs as collected (state=3)
# Expects files named: 12345.Title.mp4 (5-digit ID at start)
amvscrape checklib /path/to/your/amv/collection
```

### List database

```bash
# Show all AMVs
amvscrape list

# Filter by state
amvscrape list --state 1
```

## States

- `0` - Not collected (scraped, no torrent yet)
- `1` - Torrent ready (downloaded, not sent to client)
- `2` - Sent to client (torrent added to deluge)
- `3` - In collection (video file exists locally)

## Typical workflow

```bash
# 1. Scrape new AMVs
amvscrape scrape 5

# 2. Mark what you already have
amvscrape checklib /path/to/collection

# 3. Download missing torrents
amvscrape download

# 4. Send to deluge
amvscrape torrent

# 5. Check status
amvscrape list
```

## Notes

- AMV IDs may have leading zeros (e.g., "07399" or "12807")
- Stored as-is in database (TEXT, not INTEGER)
- When multiple torrent qualities exist, largest is selected automatically
- Torrent files saved to `torrent-files/` as `{id}.torrent`

## Database

SQLite database (`amvscrape.db`) with single table:

```sql
CREATE TABLE amvs (
    id TEXT PRIMARY KEY,      -- AMV ID from amvnews.ru
    article_url TEXT,          -- Full article URL
    torrentfile TEXT,          -- Filename of .torrent
    state INTEGER              -- 0-3 (see States above)
);
```

## License

WTFPL - See [LICENSE](LICENSE)