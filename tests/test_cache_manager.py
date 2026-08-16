import os
import sqlite3
from datetime import datetime, timezone, timedelta
from unittest.mock import patch, MagicMock
import pytest

from ingest.cache_manager import (
    ensure_fresh_data,
    get_recommendation,
    get_cache_metadata,
    update_cache_timestamp,
    init_cache_table,
    is_stale,
    PRICE_STALENESS_THRESHOLD,
    VAULT_STALENESS_THRESHOLD,
    PATCH_STALENESS_THRESHOLD,
)

TEST_DB = "db/test_cache_manager.db"


@pytest.fixture
def clean_test_db():
    if os.path.exists(TEST_DB):
        os.remove(TEST_DB)

    # Initialize schema
    schema_path = "db/schema.sql"
    with open(schema_path, "r") as f:
        schema_sql = f.read()

    conn = sqlite3.connect(TEST_DB)
    conn.executescript(schema_sql)

    # Seed an item for testing
    conn.execute(
        """
        INSERT INTO items (item_id, url_slug, item_name, frame_name, component_type, vault_status, vault_date, estimated_vault_date)
        VALUES ('test_rhino_neuro', 'rhino_prime_neuroptics_blueprint', 'Rhino Prime Neuroptics Blueprint', 'Rhino Prime', 'neuroptics', 'vaulted', '2016-02-16', NULL)
        """
    )
    conn.commit()
    conn.close()

    yield TEST_DB

    if os.path.exists(TEST_DB):
        os.remove(TEST_DB)


def test_missing_cache_row_fetches_all_three(clean_test_db):
    slug = "rhino_prime_neuroptics_blueprint"

    with patch("ingest.cache_manager.fetch_item_statistics") as mock_price, \
         patch("ingest.cache_manager.fetch_warframe_vault_patch_data") as mock_vault, \
         patch("ingest.cache_manager.fetch_live_patchlogs") as mock_patch, \
         patch("ingest.cache_manager.insert_patchlogs") as mock_insert_patch:

        mock_price.return_value = {"price_history_90day": [], "price_history_48hr": []}
        mock_vault.return_value = {"Rhino Prime": {"vaulted": True, "vaultDate": "2016-02-16", "estimatedVaultDate": None}}
        mock_patch.return_value = []

        print(f"\n[Test 1] Missing cache row for '{slug}' -> ensuring fresh data...")
        ensure_fresh_data([slug], db_path=clean_test_db)

        # Confirm all 3 fetched
        assert mock_price.called, "Price fetch should be called"
        assert mock_vault.called, "Vault fetch should be called"
        assert mock_patch.called, "Patch fetch should be called"

        conn = sqlite3.connect(clean_test_db)
        meta = get_cache_metadata(slug, conn)
        conn.close()

        print(f"  -> Cache row created: {meta}")
        assert meta["price_last_updated"] is not None
        assert meta["vault_last_updated"] is not None
        assert meta["patch_last_updated"] is not None


def test_fresh_cache_makes_zero_fetches(clean_test_db):
    slug = "rhino_prime_neuroptics_blueprint"
    now_iso = datetime.now(tz=timezone.utc).isoformat()

    conn = sqlite3.connect(clean_test_db)
    init_cache_table(conn)
    conn.execute(
        """
        INSERT INTO cache_metadata (slug, price_last_updated, vault_last_updated, patch_last_updated)
        VALUES (?, ?, ?, ?)
        """,
        (slug, now_iso, now_iso, now_iso),
    )
    conn.commit()
    conn.close()

    with patch("ingest.cache_manager.fetch_item_statistics") as mock_price, \
         patch("ingest.cache_manager.fetch_warframe_vault_patch_data") as mock_vault, \
         patch("ingest.cache_manager.fetch_live_patchlogs") as mock_patch:

        print(f"\n[Test 2] All 3 fields fresh for '{slug}' -> ensuring fresh data...")
        ensure_fresh_data([slug], db_path=clean_test_db)

        assert not mock_price.called, "Price fetch should NOT be called"
        assert not mock_vault.called, "Vault fetch should NOT be called"
        assert not mock_patch.called, "Patch fetch should NOT be called"
        print("  -> Confirmed 0 fetch calls made.")


def test_stale_price_only_refetches_price(clean_test_db):
    slug = "rhino_prime_neuroptics_blueprint"
    now = datetime.now(tz=timezone.utc)
    stale_price_time = (now - timedelta(hours=26)).isoformat()
    fresh_time = now.isoformat()

    conn = sqlite3.connect(clean_test_db)
    init_cache_table(conn)
    conn.execute(
        """
        INSERT INTO cache_metadata (slug, price_last_updated, vault_last_updated, patch_last_updated)
        VALUES (?, ?, ?, ?)
        """,
        (slug, stale_price_time, fresh_time, fresh_time),
    )
    conn.commit()
    conn.close()

    with patch("ingest.cache_manager.fetch_item_statistics") as mock_price, \
         patch("ingest.cache_manager.fetch_warframe_vault_patch_data") as mock_vault, \
         patch("ingest.cache_manager.fetch_live_patchlogs") as mock_patch:

        mock_price.return_value = {"price_history_90day": [], "price_history_48hr": []}

        print(f"\n[Test 3] Only price stale for '{slug}' -> ensuring fresh data...")
        ensure_fresh_data([slug], db_path=clean_test_db)

        assert mock_price.called, "Price fetch should be called"
        assert not mock_vault.called, "Vault fetch should NOT be called"
        assert not mock_patch.called, "Patch fetch should NOT be called"
        print("  -> Confirmed only price was refetched, vault/patch skipped.")


def test_fetch_failure_handles_gracefully_without_crashing(clean_test_db):
    slug = "rhino_prime_neuroptics_blueprint"

    with patch("ingest.cache_manager.fetch_item_statistics", side_effect=Exception("Simulated Network 500 Error")) as mock_price:
        print(f"\n[Test 4] Simulating fetch failure for '{slug}'...")
        # Should not raise exception
        ensure_fresh_data([slug], db_path=clean_test_db)
        print("  -> Handled network error gracefully without crashing.")


def test_get_recommendation_short_circuits_on_nonsense(clean_test_db):
    print(f"\n[Test 5] get_recommendation('xyz nonsense')...")
    with patch("ingest.cache_manager.ensure_fresh_data") as mock_ensure, \
         patch("ingest.cache_manager.create_advisor_graph") as mock_graph:

        res = get_recommendation("xyz nonsense", db_path=clean_test_db)
        print(f"  -> Result: {res}")
        assert res["status"] in ("not_found", "ambiguous")
        assert not mock_ensure.called
        assert not mock_graph.called


def test_get_recommendation_end_to_end_real():
    print(f"\n[Test 6] Real End-to-End: get_recommendation('rhino prime neuroptics')...")
    res = get_recommendation("rhino prime neuroptics")
    print(f"  -> Status: {res.get('status')}")
    print(f"  -> Item: {res.get('item_name')}")
    print(f"  -> Recommendation: {res.get('recommendation')}")
    print(f"  -> Reasoning: {res.get('reasoning')}")
    print(f"  -> Trend Signal: {res.get('trend_signal')}")
    print(f"  -> Vault Signal: {res.get('vault_signal')}")
    print(f"  -> Patch Signal: {res.get('patch_signal')}")

    assert res["status"] == "resolved"
    assert res["recommendation"] in ("SELL", "HOLD")
    assert res["frame_name"] == "Rhino Prime"
    assert res["component"] == "neuroptics"
