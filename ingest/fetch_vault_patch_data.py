import sqlite3
import json
import logging
import requests
from datetime import datetime, timezone
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

WARFRAMES_JSON_URL = "https://raw.githubusercontent.com/WFCD/warframe-items/master/data/json/Warframes.json"
PATCHLOGS_JSON_URL = "https://raw.githubusercontent.com/WFCD/warframe-patchlogs/master/data/patchlogs.json"
DB_PATH = "db/wfm.db"
WATCHLIST_PATH = "config/watchlist.json"


def fetch_warframe_vault_patch_data() -> Dict[str, Any]:
    """
    GETs the WFCD Warframes.json dataset and returns a dict keyed by frame name
    (e.g. 'Saryn Prime') for O(1) lookup. Each value contains:
      - vaulted: bool
      - vaultDate: str | None
      - estimatedVaultDate: str | None
    """
    logger.info(f"Fetching WFCD Warframes dataset from {WARFRAMES_JSON_URL}...")
    response = requests.get(WARFRAMES_JSON_URL, timeout=30)
    response.raise_for_status()
    raw = response.json()

    data = {}
    for entry in raw:
        name = entry.get("name", "").strip()
        if not name:
            continue
        data[name] = {
            "vaulted": entry.get("vaulted", False),
            "vaultDate": entry.get("vaultDate"),
            "estimatedVaultDate": entry.get("estimatedVaultDate"),
        }

    logger.info(f"Loaded {len(data)} Warframe entries from WFCD dataset.")
    return data


def fetch_live_patchlogs() -> List[Dict[str, Any]]:
    """
    GETs the raw patchlogs.json URL from @wfcd/patchlogs repo.
    Returns the full list of raw patchlogs.
    """
    logger.info(f"Fetching live patchlogs from {PATCHLOGS_JSON_URL}...")
    response = requests.get(PATCHLOGS_JSON_URL, timeout=30)
    response.raise_for_status()
    raw_patchlogs = response.json()
    logger.info(f"Loaded {len(raw_patchlogs)} total patchlogs from live source.")
    return raw_patchlogs


def match_patchlogs_to_frame(all_patchlogs: List[Dict[str, Any]], frame_name: str) -> List[Dict[str, Any]]:
    """
    Filters all patchlogs to entries where frame_name (or its base name without 'Prime')
    appears in name/additions/changes/fixes.
    """
    matched = []
    base_name = frame_name.replace(" Prime", "").strip()
    base_lower = base_name.lower()
    frame_lower = frame_name.lower()

    for p in all_patchlogs:
        name_txt = p.get("name") or ""
        add_txt = p.get("additions") or ""
        chg_txt = p.get("changes") or ""
        fix_txt = p.get("fixes") or ""

        combined_txt = f"{name_txt}\n{add_txt}\n{chg_txt}\n{fix_txt}".lower()
        if frame_lower in combined_txt or base_lower in combined_txt:
            matched.append(p)

    return matched


def update_items_vault_status(conn: sqlite3.Connection, watchlist: list, source_data: Dict[str, Any]) -> int:
    """
    For each frame in the watchlist, looks up its vault info in source_data and
    UPDATEs all 5 component rows in `items` WHERE frame_name = ?.
    """
    cursor = conn.cursor()
    total_updated = 0

    for frame_name in watchlist:
        if frame_name not in source_data:
            logger.warning(f"Frame '{frame_name}' not found in WFCD dataset — skipping vault status update.")
            continue

        info = source_data[frame_name]
        vault_status = "vaulted" if info["vaulted"] else "unvaulted"
        vault_date = info["vaultDate"]
        estimated_vault_date = info["estimatedVaultDate"]

        cursor.execute(
            """
            UPDATE items
            SET vault_status = ?, vault_date = ?, estimated_vault_date = ?
            WHERE frame_name = ?
            """,
            (vault_status, vault_date, estimated_vault_date, frame_name),
        )
        total_updated += cursor.rowcount

    conn.commit()
    return total_updated


def insert_patchlogs(conn: sqlite3.Connection, watchlist: list, all_patchlogs: List[Dict[str, Any]]) -> int:
    """
    Filters and inserts matched patchlogs for each frame on the watchlist.
    De-duplicates by checking (frame_name, patch_name) pairs.
    """
    cursor = conn.cursor()

    # Load existing (frame_name, patch_name) pairs to avoid duplicates
    cursor.execute("SELECT frame_name, patch_name FROM patchlogs")
    existing = set(cursor.fetchall())

    total_inserted = 0

    for frame_name in watchlist:
        matched_logs = match_patchlogs_to_frame(all_patchlogs, frame_name)
        logger.info(f"Matched {len(matched_logs)} patchlogs for frame '{frame_name}'")

        for patch in matched_logs:
            patch_name = patch.get("name", "")
            patch_date = patch.get("date", "")

            if not patch_name or not patch_date:
                continue

            if (frame_name, patch_name) in existing:
                continue

            cursor.execute(
                """
                INSERT INTO patchlogs (frame_name, patch_name, patch_date, patch_url, additions, changes, fixes)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    frame_name,
                    patch_name,
                    patch_date,
                    patch.get("url"),
                    patch.get("additions"),
                    patch.get("changes"),
                    patch.get("fixes"),
                ),
            )
            existing.add((frame_name, patch_name))
            total_inserted += 1

    conn.commit()
    return total_inserted


def main():
    """
    Orchestrates the ingestion pipeline.
    """
    with open(WATCHLIST_PATH) as f:
        watchlist = json.load(f)

    # 1. Fetch source data
    vault_data = fetch_warframe_vault_patch_data()
    live_patchlogs = fetch_live_patchlogs()

    # 2. Update DB
    conn = sqlite3.connect(DB_PATH)
    try:
        items_updated = update_items_vault_status(conn, watchlist, vault_data)
        patchlogs_inserted = insert_patchlogs(conn, watchlist, live_patchlogs)
    finally:
        conn.close()

    print(f"\n=== Vault & Live Patch Ingestion Summary ===")
    print(f"  Items rows updated (vault status): {items_updated}")
    print(f"  Patchlog rows inserted:            {patchlogs_inserted}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
