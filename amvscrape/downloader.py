"""Torrent file download module - to be implemented in Phase 3."""

from typing import List, Optional, Tuple


def parse_download_options(article_url: str) -> List[Tuple[str, float]]:
    """
    Parse article page for torrent download links.

    Args:
        article_url: URL to AMV article page

    Returns:
        List of (torrent_url, size_mb) tuples
    """
    # TODO: Implement in Phase 3
    raise NotImplementedError("download functionality not yet implemented")


def select_best_torrent(options: List[Tuple[str, float]]) -> Tuple[str, float]:
    """
    Select largest torrent file (heuristic: best quality).

    Args:
        options: List of (torrent_url, size_mb) tuples

    Returns:
        Selected (torrent_url, size_mb) tuple
    """
    # TODO: Implement in Phase 3
    raise NotImplementedError("download functionality not yet implemented")


def download_torrent(torrent_url: str, amv_id: str) -> str:
    """
    Download .torrent file and save to torrent-files/.

    Args:
        torrent_url: URL to .torrent file
        amv_id: AMV ID for filename

    Returns:
        Filename of saved torrent file
    """
    # TODO: Implement in Phase 3
    raise NotImplementedError("download functionality not yet implemented")


def download_all_pending() -> int:
    """
    Download all torrents for AMVs with state=0.

    Returns:
        Number of torrents downloaded
    """
    # TODO: Implement in Phase 3
    raise NotImplementedError("download functionality not yet implemented")
