import pytest
from datetime import datetime, timezone, timedelta
from nodes.vault_node import compute_vault_signal


def test_rhino_prime_resurgence_recently_vaulted():
    now = datetime.now(tz=timezone.utc)
    resurgence_end = (now - timedelta(days=65)).strftime("%Y-%m-%d")

    signal = compute_vault_signal(
        vault_status="vaulted",
        vault_date="2016-02-16",
        estimated_vault_date=None,
        last_resurgence_end=resurgence_end,
        is_resurgence_active=False,
    )
    print(f"\n[Test] Rhino Prime Resurgence Vault Signal: {signal}")
    assert signal["signal"] == "recently_vaulted"
    assert signal["days_since_vaulted"] == 65
    assert "Prime Resurgence rotation" in signal["reasoning"]


def test_active_resurgence_frame():
    now = datetime.now(tz=timezone.utc)
    resurgence_expiry = (now + timedelta(days=20)).strftime("%Y-%m-%d")

    signal = compute_vault_signal(
        vault_status="unvaulted",
        vault_date="2025-01-01",
        estimated_vault_date=None,
        is_resurgence_active=True,
        resurgence_end_date=resurgence_expiry,
    )
    print(f"\n[Test] Active Resurgence Frame Signal: {signal}")
    assert signal["signal"] == "vaulting_soon"
    assert signal["is_resurgence_active"] is True
    assert signal["days_until_vault"] == 20
    assert "Currently unvaulted in Prime Resurgence" in signal["reasoning"]


def test_long_vaulted_frame():
    now = datetime.now(tz=timezone.utc)
    resurgence_end = (now - timedelta(days=400)).strftime("%Y-%m-%d")

    signal = compute_vault_signal(
        vault_status="vaulted",
        vault_date="2016-05-17",
        estimated_vault_date=None,
        last_resurgence_end=resurgence_end,
    )
    print(f"\n[Test] Long Vaulted Frame Signal: {signal}")
    assert signal["signal"] == "long_vaulted"
    assert signal["days_since_vaulted"] == 400
    assert "price likely stabilized" in signal["reasoning"]
