import sqlite3
import json
import logging
import requests
from typing import Dict, Any

logger = logging.getLogger(__name__)

WARFRAMES_JSON_URL = "https://raw.githubusercontent.com/WFCD/warframe-items/master/data/json/Warframes.json"
DB_PATH = "db/wfm.db"
WATCHLIST_PATH = "config/watchlist.json"


def fetch_warframe_vault_patch_data() -> Dict[str, Any]:
    """
    GETs the WFCD Warframes.json dataset and returns a dict keyed by frame name
    (e.g. 'Saryn Prime') for O(1) lookup. Each value contains:
      - vaulted: bool
      - vaultDate: str | None
      - estimatedVaultDate: str | None
      - patchlogs: list[dict]
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
            "patchlogs": entry.get("patchlogs", []),
        }

    logger.info(f"Loaded {len(data)} Warframe entries from WFCD dataset.")
    return data


def update_items_vault_status(conn: sqlite3.Connection, watchlist: list, source_data: Dict[str, Any]) -> int:
    """
    For each frame in the watchlist, looks up its vault info in source_data and
    UPDATEs all 5 component rows in `items` WHERE frame_name = ?.

    Converts the source JSON boolean `vaulted` field to the schema's TEXT enum:
      True  -> 'vaulted'
      False -> 'unvaulted'

    Returns the total number of item rows updated.
    """
    cursor = conn.cursor()
    total_updated = 0
    failed = []

    for frame_name in watchlist:
        if frame_name not in source_data:
            logger.warning(f"Frame '{frame_name}' not found in WFCD dataset — skipping vault update.")
            failed.append(frame_name)
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
        rows_updated = cursor.rowcount
        total_updated += rows_updated

        if rows_updated == 0:
            logger.warning(f"No rows updated for frame '{frame_name}' — frame_name may not match items table.")

    conn.commit()
    return total_updated


def insert_patchlogs(conn: sqlite3.Connection, watchlist: list, source_data: Dict[str, Any]) -> tuple:
    """
    For each frame in the watchlist, inserts patchlog entries into the `patchlogs` table.
    De-duplicates in Python by checking existing (frame_name, patch_name) pairs before
    inserting, since the patchlogs table has no UNIQUE constraint.

    Returns (rows_inserted, failed_frames).
    """
    cursor = conn.cursor()

    # Load existing (frame_name, patch_name) pairs to avoid duplicates
    cursor.execute("SELECT frame_name, patch_name FROM patchlogs")
    existing = set(cursor.fetchall())

    total_inserted = 0
    failed = []

    for frame_name in watchlist:
        if frame_name not in source_data:
            failed.append(frame_name)
            continue

        patchlogs = source_data[frame_name].get("patchlogs", [])

        for patch in patchlogs:
            patch_name = patch.get("name", "")
            patch_date = patch.get("date", "")

            if not patch_name or not patch_date:
                continue

            if (frame_name, patch_name) in existing:
                continue  # skip duplicate

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
    return total_inserted, failed


def main():
    """
    Orchestrates: connect to db/wfm.db, load watchlist, fetch WFCD data,
    run vault status update and patchlog insertion, print summary.
    """
    with open(WATCHLIST_PATH) as f:
        watchlist = json.load(f)

    source_data = fetch_warframe_vault_patch_data()

    conn = sqlite3.connect(DB_PATH)
    try:
        items_updated = update_items_vault_status(conn, watchlist, source_data)
        patchlogs_inserted, failed = insert_patchlogs(conn, watchlist, source_data)
    finally:
        conn.close()

    print(f"\n=== Vault & Patch Ingestion Summary ===")
    print(f"  Items rows updated (vault status): {items_updated}")
    print(f"  Patchlog rows inserted:            {patchlogs_inserted}")
    if failed:
        print(f"  Frames NOT found in WFCD dataset ({len(failed)}): {failed}")
    else:
        print(f"  All watchlist frames matched successfully.")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
