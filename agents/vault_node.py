"""
agents/vault_node.py — Vault signal node for the LangGraph sell-timing pipeline.

WHY THIS NODE EXISTS:
Vaulting removes an item's relics from the drop tables, which typically causes
prices to rise over time as supply dries up while demand persists. This node
translates raw vault dates into an actionable signal: whether an item is freshly
vaulted (price may still be climbing), long-vaulted (price likely stabilized/
plateaued), soon-to-vault (urgency to decide before supply cuts off), or not
vaulted at all (no vault-driven pressure). Without this node, the synthesis layer
would need to reason over raw date strings — offloading that calendar math here
keeps the synthesis layer focused on weighing signals, not computing them.
"""

import sqlite3
from datetime import datetime, timezone
from typing import Dict, Any

# Tunable thresholds (days)
VAULTING_SOON_THRESHOLD_DAYS = 90   # If estimated vault date is within this many days, flag as vaulting_soon
RECENTLY_VAULTED_THRESHOLD_DAYS = 180  # If vault_date is within this many days, flag as recently_vaulted

DB_PATH = "db/wfm.db"


def _parse_date(date_str: str | None) -> datetime | None:
    """Parse an ISO date string (YYYY-MM-DD or full ISO timestamp) into a UTC datetime."""
    if not date_str:
        return None
    # Handle both 'YYYY-MM-DD' and full ISO timestamps
    for fmt in ("%Y-%m-%d", "%Y-%m-%dT%H:%M:%S.%fZ", "%Y-%m-%dT%H:%M:%SZ"):
        try:
            return datetime.strptime(date_str[:len(fmt.replace('%f', '000000').replace('%', '').replace(fmt[0], ''))], fmt).replace(tzinfo=timezone.utc)
        except ValueError:
            continue
    # Fallback: try splitting on T and taking date part
    try:
        return datetime.strptime(date_str[:10], "%Y-%m-%d").replace(tzinfo=timezone.utc)
    except ValueError:
        return None


def compute_vault_signal(vault_status: str, vault_date: str | None, estimated_vault_date: str | None) -> Dict[str, Any]:
    """
    Core vault signal computation. Accepts raw vault fields and returns a signal dict.
    Extracted as a standalone function so it can be unit-tested without a DB or graph.

    Returns a dict with keys:
        - signal: str — one of 'not_vaulted', 'vaulting_soon', 'recently_vaulted', 'long_vaulted'
        - days_since_vaulted: int | None
        - days_until_vault: int | None
        - reasoning: str — human-readable fragment for synthesis node
    """
    now = datetime.now(tz=timezone.utc)

    if vault_status == "vaulted":
        parsed_vault_date = _parse_date(vault_date)
        if parsed_vault_date:
            days_since = (now - parsed_vault_date).days
            if days_since <= RECENTLY_VAULTED_THRESHOLD_DAYS:
                signal = "recently_vaulted"
                reasoning = (
                    f"Vaulted {days_since} days ago ({vault_date}) — "
                    f"supply may still be declining; price could still be climbing."
                )
            else:
                signal = "long_vaulted"
                reasoning = (
                    f"Vaulted {days_since} days ago ({vault_date}) — "
                    f"price likely stabilized long ago."
                )
            return {
                "signal": signal,
                "days_since_vaulted": days_since,
                "days_until_vault": None,
                "reasoning": reasoning,
            }
        else:
            # vaulted but no vault_date — treat as long_vaulted conservatively
            return {
                "signal": "long_vaulted",
                "days_since_vaulted": None,
                "days_until_vault": None,
                "reasoning": "Item is vaulted but no vault date recorded — treating as long-vaulted.",
            }

    else:  # vault_status == 'unvaulted'
        parsed_est = _parse_date(estimated_vault_date)
        if parsed_est:
            days_until = (parsed_est - now).days
            if days_until <= VAULTING_SOON_THRESHOLD_DAYS:
                return {
                    "signal": "vaulting_soon",
                    "days_since_vaulted": None,
                    "days_until_vault": days_until,
                    "reasoning": (
                        f"Estimated to vault in ~{days_until} days ({estimated_vault_date}) — "
                        f"watch for price movement as relics become unavailable."
                    ),
                }
        # No estimated date, or far-off estimate (> VAULTING_SOON_THRESHOLD_DAYS)
        return {
            "signal": "not_vaulted",
            "days_since_vaulted": None,
            "days_until_vault": days_until if parsed_est else None,
            "reasoning": (
                "Item is not vaulted and no imminent vaulting detected — "
                "no vault-driven supply pressure."
            ),
        }


def vault_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    LangGraph node: reads vault info from state['vault_info'] and produces a vault_signal.

    vault_info dict is expected to carry:
        vault_status: str — 'vaulted' or 'unvaulted'
        vault_date: str | None
        estimated_vault_date: str | None

    Updates state with vault_signal dict containing signal, days, and reasoning.
    """
    vault_info = state.get("vault_info", {})
    vault_status = vault_info.get("vault_status", "unvaulted")
    vault_date = vault_info.get("vault_date")
    estimated_vault_date = vault_info.get("estimated_vault_date")

    signal = compute_vault_signal(vault_status, vault_date, estimated_vault_date)

    return {"vault_signal": signal}


if __name__ == "__main__":
    # Test block: run against Loki Prime and Rhino Prime's real DB rows
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    cur.execute("""
        SELECT item_id, url_slug, frame_name, component_type,
               vault_status, vault_date, estimated_vault_date
        FROM items
        WHERE frame_name IN ('Loki Prime', 'Rhino Prime', 'Xaku Prime', 'Voruna Prime')
        ORDER BY frame_name, component_type
    """)
    rows = cur.fetchall()
    conn.close()

    print(f"{'Slug':<45} {'Signal':<20} {'Reasoning'}")
    print("-" * 120)
    for row in rows:
        signal = compute_vault_signal(
            row["vault_status"],
            row["vault_date"],
            row["estimated_vault_date"],
        )
        print(f"{row['url_slug']:<45} {signal['signal']:<20} {signal['reasoning']}")
