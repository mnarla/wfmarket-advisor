import requests

def fetch_watchlist_items(watchlist: list) -> list:
    """
    Fetches the live list of items matching the watchlist frames from WFM API v2.
    For each frame, looks for: set, blueprint, neuroptics, chassis, systems.
    
    API: https://api.warframe.market/v2/items
    
    Returns:
        List of dicts containing item details.
    """
    # TODO: Implement full query to /v2/items, filter based on watchlist and slugs
    return []

def fetch_price_history(item_slug: str) -> dict:
    """
    Pulls price and volume history (48hr and 90day statistics) for the given item slug.
    
    Returns:
        Dict with average prices and volumes, or None if fetch fails.
    """
    # TODO: Fetch from WFM price history endpoints and extract 48hr / 90day stats
    return {}
