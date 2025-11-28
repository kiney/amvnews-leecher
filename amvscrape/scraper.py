"""Scraping logic for amvnews.ru."""

import re
import time
from typing import List, Optional, Tuple
from urllib.parse import parse_qs, urlparse

import requests
from bs4 import BeautifulSoup

from . import config, db


def scrape_listing_page(page_num: int) -> List[Tuple[str, str]]:
    """
    Scrape a single page of the news listing.

    Args:
        page_num: Page number to scrape (1-based)

    Returns:
        List of (amv_id, article_url) tuples
    """
    # Construct paginated URL
    # Pagination works in steps of 10: no param for page 1, page=10 for page 2, page=20 for page 3, etc.
    if page_num == 1:
        url = config.NEWS_URL
    else:
        page_param = (page_num - 1) * 10
        url = f"{config.NEWS_URL}&page={page_param}"

    headers = {
        "User-Agent": config.USER_AGENT,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
    }

    try:
        response = requests.get(url, headers=headers, timeout=config.REQUEST_TIMEOUT)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Error fetching page {page_num}: {e}")
        return []

    soup = BeautifulSoup(response.content, "lxml")
    results = []

    # Find only the actual news article "More ->" links, not header/featured AMVs
    # The real articles have class="more-news-simple-a"
    links = soup.find_all("a", class_="more-news-simple-a")

    for link in links:
        href = link.get("href")
        if not href:
            continue

        # Parse URL to extract ID
        parsed = urlparse(href)
        params = parse_qs(parsed.query)

        if "id" not in params:
            continue

        amv_id = params["id"][0]

        # Construct full article URL
        if href.startswith("http"):
            article_url = href
        else:
            article_url = f"{config.BASE_URL}/{href.lstrip('/')}"

        results.append((amv_id, article_url))

    # Deduplicate (same AMV might appear multiple times on page)
    seen = set()
    unique_results = []
    for amv_id, article_url in results:
        if amv_id not in seen:
            seen.add(amv_id)
            unique_results.append((amv_id, article_url))

    return unique_results


def get_total_pages() -> Optional[int]:
    """
    Get total number of pages from pagination.

    Returns:
        Total page count or None if unable to determine
    """
    headers = {
        "User-Agent": config.USER_AGENT,
    }

    try:
        response = requests.get(
            config.NEWS_URL, headers=headers, timeout=config.REQUEST_TIMEOUT
        )
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Error fetching pagination info: {e}")
        return None

    soup = BeautifulSoup(response.content, "lxml")

    # Look for pagination links
    # Pagination uses page=10, page=20, etc. (steps of 10)
    page_links = soup.find_all("a", href=re.compile(r"page=\d+"))

    if not page_links:
        return 1  # Only one page

    # Extract highest page number and convert to page count
    # page=4220 means page 423 (4220/10 + 1)
    max_page_param = 0
    for link in page_links:
        href = link.get("href", "")
        match = re.search(r"page=(\d+)", href)
        if match:
            page_param = int(match.group(1))
            max_page_param = max(max_page_param, page_param)

    if max_page_param > 0:
        return (max_page_param // 10) + 1
    return 1


def scrape_all(max_pages: Optional[int] = None) -> int:
    """
    Scrape all (or max_pages) listing pages and insert into database.

    Args:
        max_pages: Maximum number of pages to scrape, None for all

    Returns:
        Number of new AMVs found
    """
    new_count = 0
    page = 1

    # If max_pages not specified, try to determine total
    if max_pages is None:
        total = get_total_pages()
        if total:
            print(f"Found {total} total pages")
            max_pages = total
        else:
            print("Could not determine total pages, will scrape until empty")
            max_pages = 9999  # Arbitrary large number

    print(f"Starting scrape (max {max_pages} pages)...")

    while page <= max_pages:
        print(f"Scraping page {page}...", end=" ", flush=True)

        results = scrape_listing_page(page)

        if not results:
            print("no results, stopping.")
            break

        page_new = 0
        for amv_id, article_url in results:
            if db.insert_amv(amv_id, article_url):
                page_new += 1
                new_count += 1

        print(f"found {len(results)} AMVs ({page_new} new)")

        page += 1

        # Rate limiting - be nice to the server
        if page <= max_pages:
            time.sleep(config.REQUEST_DELAY)

    print(f"\nScraping complete. {new_count} new AMVs added to database.")
    return new_count
