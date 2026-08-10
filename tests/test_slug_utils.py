from ingest.slug_utils import parse_slug

def test_parse_slug_set():
    frame, comp = parse_slug("saryn_prime_set", ["set", "prime"])
    assert frame == "Saryn Prime"
    assert comp == "set"

def test_parse_slug_blueprint():
    frame, comp = parse_slug("saryn_prime_blueprint", ["blueprint", "prime"])
    assert frame == "Saryn Prime"
    assert comp == "blueprint"

def test_parse_slug_component():
    frame, comp = parse_slug("saryn_prime_neuroptics_blueprint", ["blueprint", "component", "prime"])
    assert frame == "Saryn Prime"
    assert comp == "neuroptics"

def test_parse_slug_invalid():
    frame, comp = parse_slug("invalid_slug_pattern")
    assert frame is None
    assert comp is None
