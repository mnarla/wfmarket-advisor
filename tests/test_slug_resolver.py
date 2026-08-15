import pytest
from ingest.slug_resolver import resolve_item_query, ResolvedQuery


def test_rhino_prime_whole_set():
    result = resolve_item_query("rhino prime")
    print(f"\n[Test] 'rhino prime' -> {result}")
    assert result.status == "resolved"
    assert result.frame_name == "Rhino Prime"
    assert result.component is None
    assert len(result.slugs) == 5
    assert "rhino_prime_set" in result.slugs
    assert "rhino_prime_blueprint" in result.slugs
    assert "rhino_prime_neuroptics_blueprint" in result.slugs
    assert "rhino_prime_chassis_blueprint" in result.slugs
    assert "rhino_prime_systems_blueprint" in result.slugs


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
    assert len(result.slugs) == 5


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
