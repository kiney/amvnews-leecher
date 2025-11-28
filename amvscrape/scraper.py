"""Scraping logic for amvnews.ru."""

from typing import List, Optional, Tuple

from . import config


def scrape_listing_page(page_num: int) -> List[Tuple[str, str]]:
    """
    Scrape a single page of the news listing.

    Args:
        page_num: Page number to scrape (1-based)

    Returns:
        List of (amv_id, article_url) tuples
    """
    # TODO: Implement in Phase 2
    raise NotImplementedError("scrape_listing_page not yet implemented")


def scrape_all(max_pages: Optional[int] = None) -> int:
    """
    Scrape all (or max_pages) listing pages and insert into database.

    Args:
        max_pages: Maximum number of pages to scrape, None for all

    Returns:
        Number of new AMVs found
    """
    # TODO: Implement in Phase 2
    raise NotImplementedError("scrape_all not yet implemented")
