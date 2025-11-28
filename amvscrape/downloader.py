"""Torrent file download module."""

import re
from pathlib import Path
from typing import List, Optional, Tuple

import requests
from bs4 import BeautifulSoup

from . import config, db


def parse_download_options(article_url: str) -> List[Tuple[str, float]]:
    """
    Parse article page for torrent download links.

    Args:
        article_url: URL to AMV article page

    Returns:
        List of (torrent_url, size_mb) tuples
    """
    headers = {
        "User-Agent": config.USER_AGENT,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
    }

    try:
        response = requests.get(
            article_url, headers=headers, timeout=config.REQUEST_TIMEOUT
        )
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Error fetching article {article_url}: {e}")
        return []

    soup = BeautifulSoup(response.content, "lxml")
    options = []

    # Look for torrent download links
    # The size is in a separate <span class="rating-text"> after the [Torrent] link
    all_links = soup.find_all("a", href=True)

    for link in all_links:
        href = link.get("href", "")
        text = link.get_text(strip=True)

        # Check if this is a torrent download link
        if "torrent" in text.lower() and "go=Files&file=downtorrent" in href:
            # Look for the next span with class="rating-text" which contains the size
            size_mb = 0.0

            # Navigate up to parent and find the rating-text span
            parent = link.parent
            if parent:
                # Look for span.rating-text in the parent's siblings or children
                size_span = parent.find_next_sibling("span", class_="rating-text")
                if not size_span:
                    # Try looking in the parent's parent
                    grandparent = parent.parent
                    if grandparent:
                        size_span = grandparent.find("span", class_="rating-text")

                if size_span:
                    size_text = size_span.get_text(strip=True)
                    size_mb = extract_size_mb(size_text)

            # Construct full URL
            if href.startswith("http"):
                torrent_url = href
            else:
                torrent_url = f"{config.BASE_URL}/{href.lstrip('/')}"

            options.append((torrent_url, size_mb))

    return options


def extract_size_mb(text: str) -> float:
    """
    Extract file size in MB from text.

    Args:
        text: Text containing size info (e.g., "140.99 Mb", "1.5 Gb", "394.2 Мб")

    Returns:
        Size in megabytes (float), or 0.0 if not found
    """
    # Pattern: number followed by Mb, Gb, Мб (Russian), Гб (Russian)
    # Examples: "140.99 Mb", "1.5 Gb", "86.54 Mb", "394.2 Мб"
    match = re.search(r"(\d+\.?\d*)\s*(Mb|Gb|MB|GB|Мб|Гб)", text, re.IGNORECASE)

    if not match:
        return 0.0

    size = float(match.group(1))
    unit = match.group(2).lower()

    # Convert to MB
    if unit in ["gb", "гб"]:
        size *= 1024

    return size


def select_best_torrent(
    options: List[Tuple[str, float]],
) -> Optional[Tuple[str, float]]:
    """
    Select largest torrent file (heuristic: best quality).

    Args:
        options: List of (torrent_url, size_mb) tuples

    Returns:
        Selected (torrent_url, size_mb) tuple, or None if no options
    """
    if not options:
        return None

    # Sort by size (descending) and return the largest
    return max(options, key=lambda x: x[1])


def download_torrent(torrent_url: str, amv_id: str) -> Optional[str]:
    """
    Download .torrent file and save to torrent-files/.

    Args:
        torrent_url: URL to .torrent file
        amv_id: AMV ID for filename

    Returns:
        Filename of saved torrent file, or None on error
    """
    headers = {
        "User-Agent": config.USER_AGENT,
    }

    try:
        response = requests.get(
            torrent_url, headers=headers, timeout=config.REQUEST_TIMEOUT
        )
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Error downloading torrent for AMV {amv_id}: {e}")
        return None

    # Ensure torrent directory exists
    config.TORRENT_DIR.mkdir(parents=True, exist_ok=True)

    # Save as {id}.torrent
    filename = f"{amv_id}.torrent"
    filepath = config.TORRENT_DIR / filename

    try:
        with open(filepath, "wb") as f:
            f.write(response.content)
    except IOError as e:
        print(f"Error saving torrent file {filename}: {e}")
        return None

    return filename


def download_for_amv(amv_id: str) -> bool:
    """
    Download torrent for a single AMV by ID.

    Args:
        amv_id: AMV ID

    Returns:
        True if successful, False otherwise
    """
    # Get AMV from database
    entry = db.get_by_id(amv_id)
    if not entry:
        print(f"AMV {amv_id} not found in database")
        return False

    article_url = entry["article_url"]

    # Parse download options
    options = parse_download_options(article_url)

    if not options:
        print(f"No torrent downloads found for AMV {amv_id}")
        return False

    # Select best (largest) torrent
    best = select_best_torrent(options)
    if not best:
        print(f"Could not select torrent for AMV {amv_id}")
        return False

    torrent_url, size_mb = best
    print(f"  Downloading {size_mb:.2f} MB torrent...", end=" ", flush=True)

    # Download
    filename = download_torrent(torrent_url, amv_id)

    if not filename:
        print("FAILED")
        return False

    # Update database
    db.update_torrentfile(amv_id, filename)
    db.update_state(amv_id, 1)  # State 1 = torrent ready

    print("OK")
    return True


def download_all_pending() -> int:
    """
    Download all torrents for AMVs with state=0.

    Returns:
        Number of torrents downloaded
    """
    pending = db.get_by_state(0)

    if not pending:
        print("No pending AMVs to download")
        return 0

    print(f"Found {len(pending)} AMVs to download\n")

    success_count = 0
    for entry in pending:
        amv_id = entry["id"]
        print(f"AMV {amv_id}:", end=" ", flush=True)

        if download_for_amv(amv_id):
            success_count += 1

    print(f"\nDownloaded {success_count}/{len(pending)} torrents successfully")
    return success_count
