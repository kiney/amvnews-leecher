"""CLI argument parsing and command dispatch for amvscrape."""

import argparse
import sys
from pathlib import Path

from . import config, db, downloader, scraper


def cmd_scrape(args):
    """Scrape amvnews.ru for new AMVs."""
    print(f"Scraping amvnews.ru (max pages: {args.n or 'all'})...")
    # TODO: Implement in Phase 2
    print("Not yet implemented")


def cmd_download(args):
    """Download torrent files for AMVs."""
    if args.id:
        print(f"Downloading torrent for AMV ID: {args.id}")
    else:
        print("Downloading torrents for all pending AMVs...")
    # TODO: Implement in Phase 3
    print("Not yet implemented")


def cmd_torrent(args):
    """Send torrent files to deluge-gtk."""
    if args.id:
        print(f"Sending torrent for AMV ID {args.id} to deluge-gtk...")
    else:
        print("Sending all pending torrents to deluge-gtk...")
    # TODO: Implement in Phase 5
    print("Not yet implemented")


def cmd_checklib(args):
    """Scan library directory and mark existing AMVs."""
    if not args.path:
        print("Error: path is required for checklib command", file=sys.stderr)
        sys.exit(1)

    path = Path(args.path)
    if not path.exists() or not path.is_dir():
        print(f"Error: '{args.path}' is not a valid directory", file=sys.stderr)
        sys.exit(1)

    print(f"Scanning library at: {args.path}")
    # TODO: Implement in Phase 4
    print("Not yet implemented")


def main():
    """Main CLI entry point."""
    # Initialize database
    db.init_db()

    parser = argparse.ArgumentParser(
        prog="amvscrape", description="Tool to scrape and manage AMVs from amvnews.ru"
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # scrape command
    parser_scrape = subparsers.add_parser(
        "scrape", help="Scrape amvnews.ru for new AMVs"
    )
    parser_scrape.add_argument(
        "n",
        type=int,
        nargs="?",
        help="Maximum number of pages to scrape (optional, default: all)",
    )
    parser_scrape.set_defaults(func=cmd_scrape)

    # download command
    parser_download = subparsers.add_parser(
        "download", help="Download torrent files for AMVs"
    )
    parser_download.add_argument(
        "id", nargs="?", help="AMV ID to download (optional, default: all pending)"
    )
    parser_download.set_defaults(func=cmd_download)

    # torrent command
    parser_torrent = subparsers.add_parser(
        "torrent", help="Send torrent files to deluge-gtk"
    )
    parser_torrent.add_argument(
        "id", nargs="?", help="AMV ID to send (optional, default: all with state=1)"
    )
    parser_torrent.set_defaults(func=cmd_torrent)

    # checklib command
    parser_checklib = subparsers.add_parser(
        "checklib", help="Scan library directory and mark existing AMVs"
    )
    parser_checklib.add_argument("path", help="Path to library directory")
    parser_checklib.set_defaults(func=cmd_checklib)

    # Parse arguments
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    # Dispatch to command handler
    args.func(args)


if __name__ == "__main__":
    main()
