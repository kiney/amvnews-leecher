Tool to scrape torrent files for AMVs from amvnews.ru

vibe coded for personal use, docs if you can call it that are in german for now.

# Intro
die Seite amvnews.ru stellt regelmässig AMVs (Anime Music Videos) zur Verfügung. Die AMVs haben
eindeutige fünfstellige numerische IDs.
Zur Stuktur der Seite siehe @scrape-hints.md.


# Architecture
command line tool das eine sqlite database für metadaten nutzt.
Die datenbank enthält eine einzelne Tabelle:
  id (primary key) # dies entspricht der amvnew id. speichern wir als text EXAKT wie im original, weil es mit und ohne führende nullen zu geben scheint
  article url
  torrentfile # der Dateiname des .torrent files, NICHT der fertigen Dateien
  state # ein flag mit drei zuständen:
    0: noch nicht in der Sammlung
    1: torrent file vorhanden
    2: an torrent client übergeben
    3: bereits in der sammlung

Das tool soll mehrere "Phasen" oder subcommands bieten die relativ unabhängig voneinander
arbeiten. Ihre Funktion wird im usage abschnitt weiter erläutert.

Libraries wie beautifulsoup4, requests, sqlite3 dürfen natürlich verwendet werden.
Bedingung: im venv ohne global install auf dem host nutzbar


# Tool usage
das CLI Tool heißt "amvscrape"

amvscrape scrape [n]
  scrape amvnews.ru for new AMVs
  durchsucht nacheinander die paginierte new videos section von amvnews.ru
  Der optionale parameter n gibt die maximale Anzahl der zu scrapenden Seiten an, fehlt er
  wird ALLES gescraped.
  Es wird jeweils nur die article URL in die sqlite datenbank geschrieben.

amvscrape download [id]
  download torrent files for new AMVs
  lädt das .torrent file für die angegebene AMV ID herunter und legt es in @torrent-files ab
  wenn keine id angegeben wird, werden alle .torrent files mit state 0 heruntergeladen

amvscrape torrent [id]
  send torrent file to torrent client
  sendet das .torrent file für die angegebene AMV ID an den torrent client
  wenn keine id angegeben wird, werden alle .torrent files mit state 1 an den client gesendet

amvscrape checklib [path]
  list den directory content vom angegebenen path
  Alle dateien darin die mit einer fünfstelligen zahl und dann einem punk beginnen
  werden als AMV mit dieser Zahl als ID interpretiert und in der Datenbank als state 3 eingetragen
  (beispiel: 07399.Satsumayu-Between.Dogs.and.Wolves.amvnews.ru.mp4 entspricht id 07399)
  Der angegebene path kann noch weitere videodateien oder anderen Inhalt haben - ignorieren!

amvscrape list [--state N]
  list database contents
  zeigt alle AMVs aus der Datenbank in human-readable Format
  optional: --state N filtert nach einem bestimmten State (0, 1, 2, oder 3)
  Output: eine Zeile pro AMV mit ID, State und Torrent-Dateiname
