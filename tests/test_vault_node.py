import pytest
from datetime import datetime, timezone, timedelta
from agents.vault_node import compute_vault_signal


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


def test_weapon_resurgence_inherited_signal():
    """Verify that a weapon with inherited resurgence date computes correct recently_vaulted signal."""
    now = datetime.now(tz=timezone.utc)
    resurgence_end = (now - timedelta(days=120)).strftime("%Y-%m-%d")

    # Soma Prime inherits Nova Prime's resurgence expiry
    signal = compute_vault_signal(
        vault_status="vaulted",
        vault_date="2016-11-22",
        estimated_vault_date="2016-11-22",
        last_resurgence_end=resurgence_end,
        is_resurgence_active=False,
    )
    assert signal["signal"] == "recently_vaulted"
    assert signal["days_since_vaulted"] == 120
    assert "Prime Resurgence rotation" in signal["reasoning"]


def test_active_resurgence_weapon():
    """Verify that an actively unvaulted resurgence weapon computes vaulting_soon signal."""
    now = datetime.now(tz=timezone.utc)
    resurgence_expiry = (now + timedelta(days=18)).strftime("%Y-%m-%d")

    # Phantasma Prime / Tatsu Prime companion to Revenant Prime
    signal = compute_vault_signal(
        vault_status="unvaulted",
        vault_date="2024-08-21",
        estimated_vault_date=None,
        is_resurgence_active=True,
        resurgence_end_date=resurgence_expiry,
    )
    assert signal["signal"] == "vaulting_soon"
    assert signal["is_resurgence_active"] is True
    assert signal["days_until_vault"] == 18

