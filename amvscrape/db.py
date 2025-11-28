"""Database module for AMV metadata management."""

import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import List, Optional, Tuple

from . import config


def init_db() -> None:
    """Initialize database and create table if not exists."""
    db_path = Path(config.DB_PATH)
    db_path.parent.mkdir(parents=True, exist_ok=True)

    with sqlite3.connect(config.DB_PATH) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS amvs (
                id TEXT PRIMARY KEY,
                article_url TEXT NOT NULL,
                torrentfile TEXT,
                state INTEGER NOT NULL DEFAULT 0
            )
        """)
        conn.commit()


@contextmanager
def get_connection():
    """Context manager for database connections."""
    conn = sqlite3.connect(config.DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def insert_amv(amv_id: str, article_url: str) -> bool:
    """
    Insert new AMV entry into database.

    Args:
        amv_id: AMV ID (exact format from website, with or without leading zeros)
        article_url: Full URL to the article page

    Returns:
        True if inserted, False if already exists
    """
    with get_connection() as conn:
        cursor = conn.execute(
            "INSERT OR IGNORE INTO amvs (id, article_url, state) VALUES (?, ?, 0)",
            (amv_id, article_url),
        )
        return cursor.rowcount > 0


def update_state(amv_id: str, state: int) -> None:
    """
    Update state for an AMV.

    Args:
        amv_id: AMV ID
        state: New state (0=not collected, 1=torrent available, 2=sent to client, 3=in collection)
    """
    with get_connection() as conn:
        conn.execute("UPDATE amvs SET state = ? WHERE id = ?", (state, amv_id))


def update_torrentfile(amv_id: str, filename: str) -> None:
    """
    Update torrent filename for an AMV.

    Args:
        amv_id: AMV ID
        filename: Name of the .torrent file
    """
    with get_connection() as conn:
        conn.execute("UPDATE amvs SET torrentfile = ? WHERE id = ?", (filename, amv_id))


def get_by_state(state: int) -> List[sqlite3.Row]:
    """
    Get all AMVs with a specific state.

    Args:
        state: State to filter by

    Returns:
        List of Row objects with columns: id, article_url, torrentfile, state
    """
    with get_connection() as conn:
        cursor = conn.execute(
            "SELECT id, article_url, torrentfile, state FROM amvs WHERE state = ?",
            (state,),
        )
        return cursor.fetchall()


def get_by_id(amv_id: str) -> Optional[sqlite3.Row]:
    """
    Get single AMV by ID.

    Args:
        amv_id: AMV ID

    Returns:
        Row object or None if not found
    """
    with get_connection() as conn:
        cursor = conn.execute(
            "SELECT id, article_url, torrentfile, state FROM amvs WHERE id = ?",
            (amv_id,),
        )
        return cursor.fetchone()


def id_exists(amv_id: str) -> bool:
    """
    Check if AMV ID exists in database.

    Args:
        amv_id: AMV ID

    Returns:
        True if exists, False otherwise
    """
    with get_connection() as conn:
        cursor = conn.execute("SELECT 1 FROM amvs WHERE id = ? LIMIT 1", (amv_id,))
        return cursor.fetchone() is not None
