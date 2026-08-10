import re

def parse_slug(url_slug: str, tags: list = None) -> tuple:
    """
    Parses a WFM item slug and its associated tags into (frame_name, component_type).
    
    WFM slugs follow patterns like:
      - saryn_prime_set
      - saryn_prime_blueprint
      - saryn_prime_neuroptics_blueprint
      
    WFM tags are used to distinguish components:
      - 'set' -> set
      - 'blueprint' without 'component' -> blueprint (the frame's main blueprint)
      - 'blueprint' with 'component' -> component name (neuroptics, chassis, systems)
    
    Returns:
        (frame_name, component_type) or (None, None) if it cannot be parsed.
        frame_name: Clean capitalized name (e.g. 'Saryn Prime')
        component_type: 'set', 'blueprint', 'neuroptics', 'chassis', 'systems'
    """
    if not url_slug:
        return None, None
        
    tags = tags or []
    
    # Standardize tags
    tags_lower = [t.lower() for t in tags]
    
    # Try to extract the prime frame name from the slug
    # We look for something like '<name>_prime'
    match = re.match(r'^([a-z_]+_prime)_(.*)$', url_slug)
    if not match:
        # Check if it is a prime set/blueprint directly, e.g. "saryn_prime"
        if url_slug.endswith('_prime'):
            frame_slug = url_slug
            rest = ""
        else:
            return None, None
    else:
        frame_slug = match.group(1)
        rest = match.group(2)
        
    # Clean frame name (e.g., saryn_prime -> Saryn Prime)
    frame_name = " ".join([word.capitalize() for word in frame_slug.split('_')])
    
    # Determine component type using rest of slug and tags
    if 'set' in tags_lower or rest == 'set':
        return frame_name, 'set'
    
    if 'blueprint' in tags_lower:
        if 'component' in tags_lower or rest in ['neuroptics_blueprint', 'chassis_blueprint', 'systems_blueprint']:
            # It's one of the parts
            for part in ['neuroptics', 'chassis', 'systems']:
                if part in rest:
                    return frame_name, part
        else:
            return frame_name, 'blueprint'
            
    # Fallbacks based on string matching
    if rest == 'blueprint':
        return frame_name, 'blueprint'
    for part in ['neuroptics', 'chassis', 'systems']:
        if part in rest:
            return frame_name, part
            
    return frame_name, 'set' if 'set' in rest else 'blueprint'
