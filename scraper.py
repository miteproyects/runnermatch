"""
RunnerMatch - Race Results Scraper
Scrapes participant/results data from Sportmaniacs, UTMB World, and ITRA.
"""

import re
import time
import unicodedata
import requests
from bs4 import BeautifulSoup
from typing import Optional


HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept-Language": "es-ES,es;q=0.9,en;q=0.8",
}


def normalize_name(name: str) -> str:
    """
    Normalize a name for matching:
    - Lowercase, strip accents, remove extra whitespace, remove special chars.
    """
    if not name:
        return ""
    name = name.strip().lower()
    # Remove accents
    name = unicodedata.normalize("NFD", name)
    name = "".join(c for c in name if unicodedata.category(c) != "Mn")
    # Remove non-alphanumeric (keep spaces)
    name = re.sub(r"[^a-z0-9\s]", "", name)
    # Collapse whitespace
    name = re.sub(r"\s+", " ", name).strip()
    return name


# =============================================================================
# SPORTMANIACS SCRAPER
# =============================================================================

def scrape_sportmaniacs(url: str) -> list[dict]:
    """
    Scrape results from Sportmaniacs.
    URL format: https://sportmaniacs.com/en/races/race-slug
    Returns list of {"full_name": ..., "bib_number": ..., "category": ..., "finish_time": ...}
    """
    participants = []
    page = 1
    max_pages = 50

    while page <= max_pages:
        try:
            page_url = f"{url}?page={page}" if page > 1 else url
            resp = requests.get(page_url, headers=HEADERS, timeout=15)
            resp.raise_for_status()
            soup = BeautifulSoup(resp.text, "html.parser")

            # Sportmaniacs uses table rows for results
            rows = soup.select("table tbody tr")
            if not rows:
                # Try alternative selectors
                rows = soup.select(".results-table tr, .ranking-table tr")

            if not rows:
                break

            found_any = False
            for row in rows:
                cells = row.find_all("td")
                if len(cells) >= 2:
                    # Try to extract name (usually 2nd or 3rd column)
                    name_cell = None
                    bib = ""
                    category = ""
                    finish_time = ""

                    for i, cell in enumerate(cells):
                        text = cell.get_text(strip=True)
                        # Bib number is usually first and numeric
                        if i == 0 and text.isdigit():
                            bib = text
                        # Name is usually the longest text cell
                        elif len(text) > 3 and not text.replace(":", "").replace(".", "").isdigit():
                            if not name_cell:
                                name_cell = text
                            elif len(text) < len(name_cell):
                                category = text
                        # Time pattern HH:MM:SS or MM:SS
                        elif re.match(r"\d{1,2}:\d{2}(:\d{2})?", text):
                            finish_time = text

                    if name_cell:
                        participants.append({
                            "full_name": name_cell,
                            "full_name_normalized": normalize_name(name_cell),
                            "bib_number": bib,
                            "category": category,
                            "finish_time": finish_time,
                            "source": "sportmaniacs",
                        })
                        found_any = True

            if not found_any:
                break

            page += 1
            time.sleep(1)  # Be polite

        except Exception as e:
            print(f"Sportmaniacs scraper error (page {page}): {e}")
            break

    return participants


# =============================================================================
# UTMB WORLD SCRAPER
# =============================================================================

def scrape_utmb_world(race_url: str) -> list[dict]:
    """
    Scrape results from UTMB World.
    URL format: https://utmb.world/utmb-index/races/12345.race-slug.year
    Returns list of participant dicts.
    """
    participants = []

    try:
        resp = requests.get(race_url, headers=HEADERS, timeout=15)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")

        # UTMB World renders results in table or card format
        result_rows = soup.select(".results-row, .runner-row, table.results tbody tr")

        for row in result_rows:
            name_el = row.select_one(".runner-name, .athlete-name, td:nth-child(2)")
            bib_el = row.select_one(".bib, td:nth-child(1)")
            time_el = row.select_one(".time, .finish-time, td:nth-child(4)")
            nat_el = row.select_one(".nationality, .country, td:nth-child(3)")

            name = name_el.get_text(strip=True) if name_el else ""
            if name:
                participants.append({
                    "full_name": name,
                    "full_name_normalized": normalize_name(name),
                    "bib_number": bib_el.get_text(strip=True) if bib_el else "",
                    "category": "",
                    "finish_time": time_el.get_text(strip=True) if time_el else "",
                    "nationality": nat_el.get_text(strip=True) if nat_el else "",
                    "source": "utmb_world",
                })

        # Check if there's a JSON API endpoint
        if not participants:
            # UTMB sometimes has API endpoints in script tags
            scripts = soup.find_all("script")
            for script in scripts:
                if script.string and "results" in (script.string or "").lower():
                    # Try to extract JSON data
                    import json
                    json_match = re.search(r'\[.*?"name".*?\]', script.string, re.DOTALL)
                    if json_match:
                        try:
                            data = json.loads(json_match.group())
                            for item in data:
                                name = item.get("name", item.get("runner_name", ""))
                                if name:
                                    participants.append({
                                        "full_name": name,
                                        "full_name_normalized": normalize_name(name),
                                        "bib_number": str(item.get("bib", "")),
                                        "category": item.get("category", ""),
                                        "finish_time": item.get("time", ""),
                                        "nationality": item.get("nationality", ""),
                                        "source": "utmb_world",
                                    })
                        except json.JSONDecodeError:
                            pass

    except Exception as e:
        print(f"UTMB World scraper error: {e}")

    return participants


# =============================================================================
# ITRA SCRAPER
# =============================================================================

def scrape_itra(race_url: str) -> list[dict]:
    """
    Scrape results from ITRA (International Trail Running Association).
    URL format: https://itra.run/Races/RaceDetails/...
    """
    participants = []

    try:
        resp = requests.get(race_url, headers=HEADERS, timeout=15)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")

        # ITRA uses various table formats
        rows = soup.select("table tbody tr, .result-line, .runner-result")

        for row in rows:
            cells = row.find_all("td") if row.name == "tr" else [row]
            name = ""
            bib = ""
            finish_time = ""

            for cell in cells:
                text = cell.get_text(strip=True)
                if len(text) > 3 and not text.replace(":", "").replace(".", "").isdigit():
                    if not name:
                        name = text
                elif text.isdigit() and not bib:
                    bib = text
                elif re.match(r"\d{1,2}:\d{2}", text):
                    finish_time = text

            if name:
                participants.append({
                    "full_name": name,
                    "full_name_normalized": normalize_name(name),
                    "bib_number": bib,
                    "category": "",
                    "finish_time": finish_time,
                    "source": "itra",
                })

    except Exception as e:
        print(f"ITRA scraper error: {e}")

    return participants


# =============================================================================
# CSV / EXCEL PARSER (for manual uploads)
# =============================================================================

def parse_participant_file(file_content, file_type: str = "csv") -> list[dict]:
    """
    Parse uploaded participant list (CSV or Excel).
    Expects columns: name (or full_name), bib (or bib_number), category (optional)
    """
    import pandas as pd
    import io

    try:
        if file_type == "csv":
            df = pd.read_csv(io.BytesIO(file_content))
        else:
            df = pd.read_excel(io.BytesIO(file_content))

        # Normalize column names
        df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]

        # Find the name column
        name_col = None
        for candidate in ["full_name", "name", "nombre", "nombre_completo", "runner", "corredor", "atleta"]:
            if candidate in df.columns:
                name_col = candidate
                break

        if not name_col:
            # Use first non-numeric column
            for col in df.columns:
                if df[col].dtype == object:
                    name_col = col
                    break

        if not name_col:
            return []

        # Find bib column
        bib_col = None
        for candidate in ["bib", "bib_number", "dorsal", "numero", "pumero", "no"]:
            if candidate in df.columns:
                bib_col = candidate
                break

        # Find category column
        cat_col = None
        for candidate in ["category", "categoria", "distance", "distancia"]:
            if candidate in df.columns:
                cat_col = candidate
                break

        participants = []
        for _, row in df.iterrows():
            name = str(row[name_col]).strip()
            if name and name.lower() != "nan":
                participants.append({
                    "full_name": name,
                    "full_name_normalized": normalize_name(name),
                    "bib_number": str(row[bib_col]).strip() if bib_col and str(row[bib_col]) != "nan" else "",
                    "category": str(row[cat_col]).strip() if cat_col and str(row[cat_col]) != "nan" else "",
                    "finish_time": "",
                    "source": "manual_upload",
                })

        return participants

    except Exception as e:
        print(f"File parse error: {e}")
        return []


# =============================================================================
# UNIFIED SCRAPE FUNCTION
# =============================================================================

def scrape_race(url: str) -> list[dict]:
    """
    Auto-detect source and scrape.
    """
    url_lower = url.lower()

    if "sportmaniacs" in url_lower:
        return scrape_sportmaniacs(url)
    elif "utmb.world" in url_lower:
        return scrape_utmb_world(url)
    elif "itra.run" in url_lower:
        return scrape_itra(url)
    else:
        # Generic scraper: try to find tables with names
        return _scrape_generic(url)


def _scrape_generic(url: str) -> list[dict]:
    """Fallback generic scraper for unknown sites."""
    participants = []
    try:
        resp = requests.get(url, headers=HEADERS, timeout=15)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")

        for table in soup.find_all("table"):
            rows = table.find_all("tr")
            for row in rows[1:]:  # Skip header
                cells = row.find_all("td")
                if len(cells) >= 2:
                    name = ""
                    bib = ""
                    for cell in cells:
                        text = cell.get_text(strip=True)
                        if text.isdigit() and not bib:
                            bib = text
                        elif len(text) > 3 and not name:
                            name = text
                    if name:
                        participants.append({
                            "full_name": name,
                            "full_name_normalized": normalize_name(name),
                            "bib_number": bib,
                            "category": "",
                            "finish_time": "",
                            "source": "generic_scrape",
                        })

    except Exception as e:
        print(f"Generic scraper error: {e}")

    return participants
