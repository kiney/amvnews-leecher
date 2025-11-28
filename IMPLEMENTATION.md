# IMPLEMENTATION.md - amvscrape Architektur & Roadmap

## Übersicht

Dieses Dokument beschreibt die geplante Architektur und Implementierungsreihenfolge für `amvscrape`.

---

## 1. Projektstruktur

```
amvnews-leecher/
├── .venv/                      # Python virtual environment
├── torrent-files/              # Zielordner für heruntergeladene .torrent files
├── amvscrape/                  # Haupt-Package
│   ├── __init__.py
│   ├── __main__.py             # Entry point für `python -m amvscrape`
│   ├── cli.py                  # CLI Argument Parsing + Command-Dispatch
│   ├── db.py                   # SQLite Datenbank-Modul
│   ├── scraper.py              # Scraping-Logik (Seitennavigation, Parsing)
│   ├── downloader.py           # Torrent-Download-Logik
│   └── config.py               # Konfiguration (Pfade, URLs, etc.)
├── amvscrape.db                # SQLite Datenbank (wird zur Laufzeit erstellt)
├── pyproject.toml              # Project config & dependencies
├── README.md
├── scrape-hints.md
└── IMPLEMENTATION.md
```

---

## 2. Datenbank-Schema

### Tabelle: `amvs`

| Spalte       | Typ     | Beschreibung                                           |
|--------------|---------|--------------------------------------------------------|
| `id`         | TEXT    | PRIMARY KEY - AMV ID exakt wie im Original (z.B. "07399" oder "5") |
| `article_url`| TEXT    | Vollständige URL zum Artikel                           |
| `torrentfile`| TEXT    | Dateiname des .torrent files (NULL wenn noch nicht geladen) |
| `state`      | INTEGER | Status-Flag (siehe unten)                              |

### State-Werte

| Wert | Bedeutung                    |
|------|------------------------------|
| 0    | Noch nicht in der Sammlung   |
| 1    | Torrent file vorhanden       |
| 2    | An Torrent Client übergeben  |
| 3    | Bereits in der Sammlung      |

---

## 3. Modul-Architektur

### 3.1 `config.py`
- Zentrale Konfigurationswerte
- `BASE_URL`, `NEWS_URL`
- `DB_PATH`, `TORRENT_DIR`
- User-Agent, Timeouts, Request-Delay

### 3.2 `db.py`
- `init_db()` - Erstellt DB/Tabelle falls nicht vorhanden
- `insert_amv(id, article_url)` - INSERT OR IGNORE
- `update_state(id, state)`
- `update_torrentfile(id, filename)`
- `get_by_state(state)` - Alle Einträge mit State
- `get_by_id(id)` - Einzelner Eintrag

### 3.3 `scraper.py`
- `scrape_listing_page(page_num)` - Extrahiert AMV-Links einer Seite
- `scrape_all(max_pages=None)` - Iteriert durch Pagination

### 3.4 `downloader.py`
- `parse_download_options(article_url)` - Findet Torrent-Links + Größen
- `select_best_torrent(options)` - Wählt größte Datei
- `download_torrent(torrent_url, amv_id)` - Speichert als `{id}.torrent`
- `download_all_pending()` - Alle mit state=0

### 3.5 `cli.py`
- Subcommands: `scrape`, `download`, `torrent`, `checklib`, `list`
- `torrent`: Ruft `deluge-gtk {torrent_path}` per subprocess auf
- `checklib`: Scannt Verzeichnis mit Regex `^(\d{5})\.`
- `list`: Zeigt alle AMVs aus DB (optional filterbar nach state)

### 3.6 `__main__.py`
- Entry point: `cli.main()`

---

## 4. Implementierungs-Phasen

### Phase 1: Grundgerüst
**Ziel:** Lauffähiges Skelett

1. `pyproject.toml` mit dependencies
2. `config.py` mit Konstanten
3. `db.py` mit DB-Funktionen
4. `cli.py` Subcommand-Struktur (Stubs)
5. `__main__.py`

**Test:** `python -m amvscrape --help`

---

### Phase 2: Scraping
**Ziel:** `amvscrape scrape [n]` funktioniert

1. `scraper.py` implementieren
2. CLI verdrahten
3. ~1s Delay zwischen Requests

**Test:** `amvscrape scrape 1` → DB hat Einträge mit state=0

---

### Phase 3: Download
**Ziel:** `amvscrape download [id]` funktioniert

1. `downloader.py` implementieren
2. CLI verdrahten

**Test:** `.torrent` Dateien in `torrent-files/`, state=1

---

### Phase 4: Library Check
**Ziel:** `amvscrape checklib [path]` funktioniert

- Regex-Scan, state=3 setzen
- Direkt in `cli.py` (klein genug)

---

### Phase 5: Torrent Client
**Ziel:** `amvscrape torrent [id]` funktioniert

- `subprocess.run(["deluge-gtk", torrent_path])`
- Kein Rückkanal, state=2 nach Aufruf
- Direkt in `cli.py` (klein genug)

---

## 5. Entscheidungen

| Thema | Entscheidung |
|-------|--------------|
| Torrent-Client | `deluge-gtk` via CLI (`subprocess.run`) |
| Torrent-Dateiname | `{id}.torrent` |
| Rate-Limiting | ~1s Delay zwischen Requests |
| ID-Format | Original behalten (mit/ohne führende Nullen) |
| Duplikate | `INSERT OR IGNORE` |

---

## 6. Abhängigkeiten

### pyproject.toml
```toml
[project]
name = "amvscrape"
version = "0.1.0"
dependencies = [
    "requests",
    "beautifulsoup4",
    "lxml",
]

[project.scripts]
amvscrape = "amvscrape.cli:main"
```

Keine externen Dependencies für Torrent-Client (nur subprocess + deluge-gtk auf System).

---

## 7. Beispiel-Workflows

### Erstmaliges Setup
```bash
cd amvnews-leecher
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

### Typischer Workflow
```bash
# Neue AMVs scrapen (erste 5 Seiten)
amvscrape scrape 5

# Vorhandene Sammlung markieren
amvscrape checklib /pfad/zur/sammlung

# Torrents für fehlende AMVs laden
amvscrape download

# An Deluge übergeben
amvscrape torrent
```

---

## 8. Status

### Phase 1: ✅ ABGESCHLOSSEN

Implementiert:
- `pyproject.toml` mit Dependencies
- `amvscrape/` Package-Struktur
- `config.py` - Alle Konstanten definiert
- `db.py` - Vollständige DB-Funktionalität
- `cli.py` - CLI mit allen 4 Subcommands (Stubs)
- `__main__.py` - Entry Point
- `scraper.py`, `downloader.py` - Stubs für spätere Phasen

Getestet:
- ✅ `python -m amvscrape --help` funktioniert
- ✅ Alle Subcommands zeigen Help
- ✅ Datenbank wird initialisiert
- ✅ DB-Funktionen (insert, update, get) arbeiten korrekt

### Phase 2: ✅ ABGESCHLOSSEN

Implementiert:
- `scraper.py` komplett
  - `scrape_listing_page()` - Parsed Pagination und extrahiert AMV-Links
  - `get_total_pages()` - Ermittelt Gesamtzahl der Seiten
  - `scrape_all()` - Hauptschleife mit Rate-Limiting
- `cli.py` - `cmd_scrape()` verdrahtet
- BeautifulSoup + lxml HTML-Parsing
- Regex für URL-Extraktion (IDs mit/ohne führende Nullen)
- Duplikat-Handling (INSERT OR IGNORE)
- 1s Delay zwischen Requests

Getestet:
- ✅ `amvscrape scrape 1` - Scraped erste Seite (31 AMVs gefunden)
- ✅ `amvscrape scrape 3` - Scraped 3 Seiten (32 neue AMVs)
- ✅ Datenbank enthält Einträge mit state=0
- ✅ IDs in verschiedenen Formaten korrekt gespeichert
- ✅ Bereits bekannte AMVs werden übersprungen

### Bonus: List-Command

Implementiert:
- `amvscrape list` - Zeigt alle DB-Einträge sortiert nach ID
- `amvscrape list --state N` - Filtert nach State
- Human-readable Output mit State-Namen
- Sortierung nach ID (numerisch)

Getestet:
- ✅ `amvscrape list` zeigt alle 64 Einträge
- ✅ `amvscrape list --state 0` zeigt nur 63 AMVs mit state=0
- ✅ `amvscrape list --state 1` zeigt 1 AMV mit state=1

### Nächste Schritte

Phase 3: Download-Funktionalität implementieren

---

*Version 1.4 - Phase 2 Complete + List Command*