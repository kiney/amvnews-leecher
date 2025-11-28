# TESTING.md - Testanleitung für amvscrape

## Phase 5: Torrent-Client Integration Testing

### Vorbereitung

Stelle sicher dass deluge-gtk installiert ist:
```bash
which deluge-gtk
```

### Test 1: Dry-Run (ohne deluge-gtk zu starten)

```bash
# Test mit spezifischen IDs
python3 /tmp/test_torrent_dry.py 12807 12806 12805

# Test mit allen state=1 AMVs
python3 /tmp/test_torrent_dry.py
```

Zeigt was der Command machen würde ohne tatsächlich deluge-gtk zu starten.

### Test 2: Einzelne ID

**WARNUNG:** Startet deluge-gtk und zeigt GUI-Dialog!

```bash
# State vor dem Test prüfen
python -m amvscrape list | grep 12807

# Torrent senden
python -m amvscrape torrent 12807

# State nach dem Test prüfen (sollte 2 sein)
python -m amvscrape list | grep 12807
```

**Erwartetes Verhalten:**
- deluge-gtk öffnet sich mit einem Dialog zum Hinzufügen des Torrents
- Nach Bestätigung: State 1 → 2 in der Datenbank

### Test 3: Mehrere IDs gleichzeitig (EMPFOHLEN)

**WARNUNG:** Startet deluge-gtk mit GUI-Dialog für ALLE Torrents!

```bash
# Mehrere IDs auf einmal (nur EIN Dialog!)
python -m amvscrape torrent 12807 12806 12805

# States prüfen
python -m amvscrape list | grep -E "12807|12806|12805"
```

**Erwartetes Verhalten:**
- deluge-gtk öffnet sich EINMAL mit Dialog für alle 3 Torrents
- Deutlich besser als 3 separate Aufrufe!
- Alle 3 AMVs haben danach state=2

### Test 4: Alle pending Torrents (state=1)

**WARNUNG:** Sendet ALLE AMVs mit state=1 auf einmal!

```bash
# Wie viele würden gesendet?
python -m amvscrape list --state 1

# Alle senden (NUR wenn du das wirklich willst!)
python -m amvscrape torrent

# Prüfen ob alle jetzt state=2 haben
python -m amvscrape list --state 2
```

### Test 5: Error-Cases

```bash
# ID existiert nicht
python -m amvscrape torrent 99999

# ID hat kein Torrent-File
sqlite3 amvscrape.db "INSERT INTO amvs (id, article_url, state) VALUES ('00001', 'http://test', 1);"
python -m amvscrape torrent 00001
```

### Test 6: State wird ignoriert bei händischer ID-Angabe

```bash
# AMV mit state=0 oder state=3 explizit senden
python -m amvscrape torrent 05289  # Hat state=3 (in collection)

# Sollte trotzdem funktionieren!
```

## Kompletter Workflow-Test

```bash
# 1. Scrapen
python -m amvscrape scrape 1

# 2. Downloads
python -m amvscrape download

# 3. Liste prüfen
python -m amvscrape list --state 1

# 4. An deluge-gtk senden (3 IDs zum Test)
python -m amvscrape torrent 12807 12806 12805

# 5. Status prüfen
python -m amvscrape list | head -15
```

## Cleanup nach Tests

```bash
# States zurücksetzen für erneutes Testen
sqlite3 amvscrape.db "UPDATE amvs SET state=1 WHERE id IN ('12807', '12806', '12805');"
```

## Bekannte Limitierungen

- **GUI-Dialoge:** deluge-gtk zeigt immer Dialoge, kann nicht vermieden werden
- **Batch-Modus:** Mehrere Torrents auf einmal = nur EIN Dialog (viel besser!)
- **Kein Feedback:** deluge-gtk gibt keinen Exit-Code bei Abbruch, State wird trotzdem auf 2 gesetzt

## Troubleshooting

### "deluge-gtk not found"
```bash
# Debian/Ubuntu
sudo apt install deluge-gtk

# Arch
sudo pacman -S deluge
```

### Torrent-Datei nicht gefunden
```bash
# Prüfen ob Datei existiert
ls -lh torrent-files/*.torrent

# Neu herunterladen
python -m amvscrape download <id>
```

### State wird nicht aktualisiert
```bash
# DB-Connection prüfen
sqlite3 amvscrape.db "SELECT * FROM amvs WHERE id='12807';"

# Manuell setzen
sqlite3 amvscrape.db "UPDATE amvs SET state=1 WHERE id='12807';"
```
