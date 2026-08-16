from ingest.slug_utils import parse_slug


def test_parse_slug_warframe_cases():
    frame, comp = parse_slug("rhino_prime_neuroptics_blueprint", ["blueprint", "component", "prime"])
    assert frame == "Rhino Prime"
    assert comp == "neuroptics"

    frame, comp = parse_slug("rhino_prime_blueprint", ["blueprint", "prime"])
    assert frame == "Rhino Prime"
    assert comp == "blueprint"

    frame, comp = parse_slug("rhino_prime_set", ["set", "prime"])
    assert frame == "Rhino Prime"
    assert comp == "set"


def test_parse_slug_weapon_cases():
    weapon, comp = parse_slug("soma_prime_barrel", ["component", "prime", "weapon"])
    assert weapon == "Soma Prime"
    assert comp == "barrel"

    weapon, comp = parse_slug("soma_prime_receiver", ["component", "prime", "weapon"])
    assert weapon == "Soma Prime"
    assert comp == "receiver"

    weapon, comp = parse_slug("soma_prime_stock", ["component", "prime", "weapon"])
    assert weapon == "Soma Prime"
    assert comp == "stock"

    weapon, comp = parse_slug("soma_prime_blueprint", ["blueprint", "prime", "weapon"])
    assert weapon == "Soma Prime"
    assert comp == "blueprint"

    weapon, comp = parse_slug("soma_prime_set", ["set", "prime", "weapon"])
    assert weapon == "Soma Prime"
    assert comp == "set"

    weapon, comp = parse_slug("cernos_prime_upper_limb", ["component", "prime", "weapon"])
    assert weapon == "Cernos Prime"
    assert comp == "upper_limb"

    weapon, comp = parse_slug("fang_prime_blade", ["component", "prime", "weapon"])
    assert weapon == "Fang Prime"
    assert comp == "blade"


def test_parse_slug_invalid():
    frame, comp = parse_slug("invalid_slug_pattern")
    assert frame is None
    assert comp is None
