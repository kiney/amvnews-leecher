"""CLI argument parsing and command dispatch for amvscrape."""

import argparse
import sys
from pathlib import Path

from . import config, db, downloader, scraper


def cmd_scrape(args):
    """Scrape amvnews.ru for new AMVs."""
    max_pages = args.n
    try:
        new_count = scraper.scrape_all(max_pages=max_pages)
    except KeyboardInterrupt:
        print("\n\nScraping interrupted by user.")
        sys.exit(0)
    except Exception as e:
        print(f"\n\nError during scraping: {e}", file=sys.stderr)
        sys.exit(1)


def cmd_download(args):
    """Download torrent files for AMVs."""
    if args.id:
        print(f"Downloading torrent for AMV ID: {args.id}")
        if downloader.download_for_amv(args.id):
            print(f"\n✓ Torrent for AMV {args.id} downloaded successfully")
        else:
            print(f"\n✗ Failed to download torrent for AMV {args.id}")
            sys.exit(1)
    else:
        print("Downloading torrents for all pending AMVs...")
        count = downloader.download_all_pending()
        print(f"\n✓ Done! {count} torrents downloaded.")


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

    # Scan directory for video files starting with 5-digit IDs
    import re

    pattern = re.compile(r"^(\d{5})\.")
    found_ids = []

    for file_path in path.iterdir():
        if file_path.is_file():
            match = pattern.match(file_path.name)
            if match:
                amv_id = match.group(1)
                found_ids.append(amv_id)

    if not found_ids:
        print("No AMV files found in library (no files starting with 5-digit ID)")
        return

    print(f"Found {len(found_ids)} AMV files in library")

    # Mark them as collected (state=3) in database
    marked_count = 0
    for amv_id in found_ids:
        if db.id_exists(amv_id):
            db.update_state(amv_id, 3)
            marked_count += 1
            print(f"  {amv_id} → marked as collected")
        else:
            print(f"  {amv_id} → not in database (skipped)")

    print(f"\n✓ Marked {marked_count}/{len(found_ids)} AMVs as collected (state=3)")


def cmd_list(args):
    """List all AMVs in database."""
    # Get filter state if specified
    state_filter = (
        args.state if hasattr(args, "state") and args.state is not None else None
    )

    # Fetch from database
    if state_filter is not None:
        rows = db.get_by_state(state_filter)
        print(f"AMVs with state={state_filter}:")
    else:
        with db.get_connection() as conn:
            cursor = conn.execute(
                "SELECT id, article_url, torrentfile, state FROM amvs ORDER BY CAST(id AS INTEGER) DESC"
            )
            rows = cursor.fetchall()
        print("All AMVs in database:")

    if not rows:
        print("  (no entries)")
        return

    # State names for readability
    state_names = {
        0: "not collected",
        1: "torrent ready",
        2: "sent to client",
        3: "in collection",
    }

    # Print each row
    for row in rows:
        amv_id = row["id"]
        article_url = row["article_url"]
        state = row["state"]
        state_name = state_names.get(state, f"unknown({state})")
        torrentfile = row["torrentfile"] or "(none)"

        # Extract ID from URL for verification (id=XXXXX)
        url_id = "(no url)"
        if article_url:
            import re

            match = re.search(r"id=(\d+)", article_url)
            if match:
                url_id = match.group(1)

        print(
            f"  {amv_id:>8} | url_id={url_id:>8} | state={state} ({state_name:15s}) | torrent={torrentfile}"
        )

    print(f"\nTotal: {len(rows)} AMVs")


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

    # list command
    parser_list = subparsers.add_parser("list", help="List all AMVs in database")
    parser_list.add_argument(
        "--state",
        type=int,
        choices=[0, 1, 2, 3],
        help="Filter by state (0=not collected, 1=torrent ready, 2=sent to client, 3=in collection)",
    )
    parser_list.set_defaults(func=cmd_list)

    # Parse arguments
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    # Dispatch to command handler
    args.func(args)


if __name__ == "__main__":
    main()
