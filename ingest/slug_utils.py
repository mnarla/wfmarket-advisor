import re
from typing import Dict, List, Optional, Tuple


def parse_slug(url_slug: str, tags: Optional[List[str]] = None) -> Tuple[Optional[str], Optional[str]]:
    """
    Parses a WFM item slug into (item_name, component_type) for Prime Warframes and Weapons.

    Rule:
      component_type = the slug suffix remaining after stripping the base name,
      with a trailing "_blueprint" removed UNLESS the suffix is exactly "blueprint"
      (in which case leave it as "blueprint").

    Examples:
      - rhino_prime_neuroptics_blueprint -> ('Rhino Prime', 'neuroptics')
      - rhino_prime_blueprint            -> ('Rhino Prime', 'blueprint')
      - rhino_prime_set                  -> ('Rhino Prime', 'set')
      - soma_prime_barrel                -> ('Soma Prime', 'barrel')
      - soma_prime_receiver              -> ('Soma Prime', 'receiver')
      - soma_prime_stock                 -> ('Soma Prime', 'stock')
      - soma_prime_blueprint             -> ('Soma Prime', 'blueprint')
      - cernos_prime_upper_limb          -> ('Cernos Prime', 'upper_limb')

    Returns:
        (item_name, component_type) or (None, None) if it cannot be parsed.
    """
    if not url_slug or not isinstance(url_slug, str):
        return None, None

    match = re.match(r"^([a-z0-9_]+_prime)_(.*)$", url_slug)
    if not match:
        if url_slug.endswith("_prime"):
            base_slug = url_slug
            suffix = "set"
        else:
            return None, None
    else:
        base_slug = match.group(1)
        suffix = match.group(2)

    item_name = " ".join([word.capitalize() for word in base_slug.split("_")])

    if suffix == "blueprint":
        component_type = "blueprint"
    elif suffix.endswith("_blueprint"):
        component_type = suffix[:-10]
    else:
        component_type = suffix

    return item_name, component_type


def parse_item(item: dict) -> Tuple[Optional[str], Optional[str]]:
    """
    Convenience wrapper around parse_slug accepting an item dictionary from WFM API v2.
    Expects keys 'slug' (or 'url_slug') and 'tags'.
    """
    slug = item.get("slug") or item.get("url_slug") or ""
    tags = item.get("tags") or []
    return parse_slug(slug, tags)
