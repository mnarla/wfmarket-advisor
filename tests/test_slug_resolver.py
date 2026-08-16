import pytest
from ingest.slug_resolver import resolve_item_query, ResolvedQuery


# ==============================================================================
# ORIGINAL 9 TEST CASES (Warframe Regression Suite)
# ==============================================================================

def test_rhino_prime_whole_set():
    result = resolve_item_query("rhino prime")
    print(f"\n[Test] 'rhino prime' -> {result}")
    assert result.status == "resolved"
    assert result.frame_name == "Rhino Prime"
    assert result.component is None
    assert result.slugs == ["rhino_prime_set"]


def test_rhino_prime_neuroptics():
    result = resolve_item_query("rhino prime neuroptics")
    print(f"\n[Test] 'rhino prime neuroptics' -> {result}")
    assert result.status == "resolved"
    assert result.frame_name == "Rhino Prime"
    assert result.component == "neuroptics"
    assert result.slugs == ["rhino_prime_neuroptics_blueprint"]


def test_excal_p_bp():
    result = resolve_item_query("excal p bp")
    print(f"\n[Test] 'excal p bp' -> {result}")
    assert result.status == "resolved"
    assert result.frame_name == "Excalibur Prime"
    assert result.component == "blueprint"
    assert result.slugs == ["excalibur_prime_blueprint"]


def test_wisp_prime_sys():
    result = resolve_item_query("wisp prime sys")
    print(f"\n[Test] 'wisp prime sys' -> {result}")
    assert result.status == "resolved"
    assert result.frame_name == "Wisp Prime"
    assert result.component == "systems"
    assert result.slugs == ["wisp_prime_systems_blueprint"]


def test_rino_prime_typo():
    result = resolve_item_query("rino prime")
    print(f"\n[Test] 'rino prime' -> {result}")
    assert result.status == "resolved"
    assert result.frame_name == "Rhino Prime"
    assert result.component is None
    assert result.slugs == ["rhino_prime_set"]


def test_xyz_nonsense_item():
    result = resolve_item_query("xyz nonsense item")
    print(f"\n[Test] 'xyz nonsense item' -> {result}")
    assert result.status == "not_found"
    assert result.frame_name is None
    assert result.slugs == []
    assert result.candidates == []


def test_empty_string():
    result = resolve_item_query("")
    print(f"\n[Test] '' (empty string) -> {result}")
    assert result.status == "not_found"
    assert result.frame_name is None
    assert result.slugs == []
    assert result.candidates == []


def test_ambiguous_query():
    result = resolve_item_query("tit prime")
    print(f"\n[Test] 'tit prime' (ambiguous) -> {result}")
    assert result.status == "ambiguous"
    assert result.frame_name is None
    assert len(result.candidates) >= 2
    assert "Titania Prime" in result.candidates
    assert "Trinity Prime" in result.candidates


def test_none_and_malformed_inputs():
    for malformed in [None, "   ", "\t\n", "!!!"]:
        res = resolve_item_query(malformed)
        print(f"\n[Test] Malformed input {malformed!r} -> {res}")
        assert res.status == "not_found"


# ==============================================================================
# NEW WEAPON TEST CASES (Phase 3 Generalized Items)
# ==============================================================================

def test_rifle_soma_prime_whole_set():
    result = resolve_item_query("soma prime")
    print(f"\n[Test] 'soma prime' (rifle whole set) -> {result}")
    assert result.status == "resolved"
    assert result.frame_name == "Soma Prime"
    assert result.component is None
    assert result.slugs == ["soma_prime_set"]


def test_rifle_soma_prime_barrel_component():
    result = resolve_item_query("soma prime barrel")
    print(f"\n[Test] 'soma prime barrel' -> {result}")
    assert result.status == "resolved"
    assert result.frame_name == "Soma Prime"
    assert result.component == "barrel"
    assert result.slugs == ["soma_prime_barrel"]


def test_rifle_soma_prime_bp_alias():
    result = resolve_item_query("soma p bp")
    print(f"\n[Test] 'soma p bp' -> {result}")
    assert result.status == "resolved"
    assert result.frame_name == "Soma Prime"
    assert result.component == "blueprint"
    assert result.slugs == ["soma_prime_blueprint"]


def test_bow_cernos_prime_whole_set():
    result = resolve_item_query("cernos prime")
    print(f"\n[Test] 'cernos prime' (bow whole set) -> {result}")
    assert result.status == "resolved"
    assert result.frame_name == "Cernos Prime"
    assert result.component is None
    assert result.slugs == ["cernos_prime_set"]


def test_bow_cernos_prime_upper_limb():
    result = resolve_item_query("cernos prime upper limb")
    print(f"\n[Test] 'cernos prime upper limb' -> {result}")
    assert result.status == "resolved"
    assert result.frame_name == "Cernos Prime"
    assert result.component == "upper_limb"
    assert result.slugs == ["cernos_prime_upper_limb"]


def test_melee_fang_prime_whole_set():
    result = resolve_item_query("fang prime")
    print(f"\n[Test] 'fang prime' (melee whole set) -> {result}")
    assert result.status == "resolved"
    assert result.frame_name == "Fang Prime"
    assert result.component is None
    assert result.slugs == ["fang_prime_set"]


def test_melee_fang_prime_blade_component():
    result = resolve_item_query("fang prime blade")
    print(f"\n[Test] 'fang prime blade' -> {result}")
    assert result.status == "resolved"
    assert result.frame_name == "Fang Prime"
    assert result.component == "blade"
    assert result.slugs == ["fang_prime_blade"]


def test_melee_orthos_prime_handle_component():
    result = resolve_item_query("orthos prime handle")
    print(f"\n[Test] 'orthos prime handle' -> {result}")
    assert result.status == "resolved"
    assert result.frame_name == "Orthos Prime"
    assert result.component == "handle"
    assert result.slugs == ["orthos_prime_handle"]
