import time
import logging
import requests
from typing import List, Dict, Any, Optional
from ingest.slug_utils import parse_item

logger = logging.getLogger(__name__)

WFM_V2_ITEMS_URL = "https://api.warframe.market/v2/items"
WFM_V1_STATS_URL = "https://api.warframe.market/v1/items/{slug}/statistics"


def fetch_all_items() -> List[Dict[str, Any]]:
    """
    GETs https://api.warframe.market/v2/items once and returns the full raw 'data' list.
    """
    headers = {"Accept": "application/json", "User-Agent": "wfm-sell-timing-advisor/1.0"}
    try:
        response = requests.get(WFM_V2_ITEMS_URL, headers=headers, timeout=10)
        response.raise_for_status()
        payload = response.json()
        return payload.get("data", [])
    except Exception as e:
        logger.error(f"Failed to fetch item list from WFM API v2: {e}")
        raise


def filter_to_watchlist(all_items: List[Dict[str, Any]], watchlist: List[str]) -> List[Dict[str, Any]]:
    """
    Filters raw WFM item dicts against a watchlist of Warframe names (e.g. ['Saryn Prime', 'Wisp Prime']).
    Uses parse_item() from ingest/slug_utils.py to match slug + tags to a frame_name.
    
    Returns a list of items belonging to frames in the watchlist (~5 components per frame:
    set, blueprint, neuroptics, chassis, systems).
    """
    watchlist_set = set(watchlist)
    matched_items = []
    
    for item in all_items:
        frame_name, component_type = parse_item(item)
        if frame_name and frame_name in watchlist_set:
            item_copy = dict(item)
            item_copy["frame_name"] = frame_name
            item_copy["component_type"] = component_type
            
            i18n = item.get("i18n", {})
            en_info = i18n.get("en", {})
            item_copy["item_name"] = en_info.get("name", item.get("slug", "").replace("_", " ").title())
            
            matched_items.append(item_copy)
            
    return matched_items


def fetch_item_statistics(slug: str) -> Dict[str, List[Dict[str, Any]]]:
    """
    Fetches 48hr and 90day price/volume statistics for a single item slug using WFM v1.
    
    # v2 API has no statistics endpoint yet as of Aug 2026 (WFM v2 rollout is 
    # incomplete); falling back to v1 for price/volume history only.
    """
    url = WFM_V1_STATS_URL.format(slug=slug)
    headers = {"Accept": "application/json", "User-Agent": "wfm-sell-timing-advisor/1.0"}
    
    response = requests.get(url, headers=headers, timeout=10)
    response.raise_for_status()
    payload = response.json()
    
    stats_closed = payload.get("payload", {}).get("statistics_closed", {}) if payload else {}
    
    def parse_entries(entries: Optional[List[Dict[str, Any]]], stat_window: str) -> List[Dict[str, Any]]:
        if not entries:
            return []
        parsed = []
        for entry in entries:
            # Filter statistics_closed entries to order_type == "sell" only (or None if unassigned in closed trades)
            if entry.get("order_type") in (None, "sell"):
                parsed.append({
                    "timestamp": entry.get("datetime"),
                    "avg_price": entry.get("avg_price"),
                    "median_price": entry.get("median"),
                    "volume": entry.get("volume"),
                    "moving_avg": entry.get("moving_avg"),
                    "stat_window": stat_window
                })
        return parsed

    raw_90d = stats_closed.get("90days") if isinstance(stats_closed, dict) else []
    raw_48h = stats_closed.get("48hours") if isinstance(stats_closed, dict) else []

    return {
        "price_history_90day": parse_entries(raw_90d, "90day"),
        "price_history_48hr": parse_entries(raw_48h, "48hr")
    }


def fetch_watchlist_data(watchlist: List[str]) -> List[Dict[str, Any]]:
    """
    Orchestrates the fetch flow:
    1. fetch_all_items() -> GET full items catalog from WFM v2
    2. filter_to_watchlist(...) -> Keep only items matching watched frames
    3. For each matched item, calls fetch_item_statistics(...) respecting a rate limit of 3 req/sec across ALL calls.
    4. Catches single-item errors gracefully (logs warning and skips), returning valid item records.
    
    Returns:
        List of dicts formatted for database insertion into `items` and `price_history` tables.
    """
    rate_limit_delay = 1.0 / 3.0  # 3 requests per second limit across ALL calls

    logger.info("Fetching raw item list from WFM v2...")
    all_items = fetch_all_items()
    time.sleep(rate_limit_delay)
    
    filtered_items = filter_to_watchlist(all_items, watchlist)
    logger.info(f"Filtered {len(all_items)} total items down to {len(filtered_items)} items for watchlist.")
    
    results = []
    
    for item in filtered_items:
        slug = item.get("slug")
        item_id = item.get("id")
        
        stats = {"price_history_90day": [], "price_history_48hr": []}
        if slug:
            try:
                stats = fetch_item_statistics(slug)
            except Exception as e:
                logger.warning(f"Failed to fetch statistics for item slug '{slug}': {e}. Skipping statistics.")
                stats = {"price_history_90day": [], "price_history_48hr": []}
                
            time.sleep(rate_limit_delay)
            
        record = {
            "id": item_id,
            "item_id": item_id,
            "slug": slug,
            "url_slug": slug,
            "item_name": item.get("item_name"),
            "frame_name": item.get("frame_name"),
            "component_type": item.get("component_type"),
            "price_history_90day": stats.get("price_history_90day", []),
            "price_history_48hr": stats.get("price_history_48hr", [])
        }
        results.append(record)
        
    return results
