import pytest
from nodes.synthesis_node import build_synthesis_prompt, call_llm_for_synthesis


def test_patch_buff_overrides_negative_trend():
    """Verify that a confirmed gameplay buff forces a SELL recommendation regardless of trend."""
    trend_signal = {
        "signal": "falling",
        "slope": -0.5,
        "r_squared": 0.85,
        "pct_change_90d": -30.0,
        "reasoning": "Price has fallen 30% over 90 days.",
    }
    vault_signal = {
        "signal": "not_vaulted",
        "days_since_vaulted": None,
        "days_until_vault": None,
        "reasoning": "Item is currently not vaulted.",
    }
    patch_signal = {
        "relevant_patch_found": True,
        "patch_name": "Update 36: Major Frame Buff",
        "expected_impact": "increase",
        "reasoning": "Direct 50% damage buff to all abilities.",
    }

    prompt = build_synthesis_prompt("Test Frame Set", trend_signal, vault_signal, patch_signal)
    res = call_llm_for_synthesis(prompt)

    assert res["recommendation"] == "SELL"
    assert res["primary_driver"] == "patch"


def test_patch_nerf_overrides_positive_trend():
    """Verify that a confirmed gameplay nerf forces a HOLD recommendation regardless of trend."""
    trend_signal = {
        "signal": "rising",
        "slope": 0.8,
        "r_squared": 0.85,
        "pct_change_90d": +45.0,
        "reasoning": "Price has risen 45% over 90 days.",
    }
    vault_signal = {
        "signal": "not_vaulted",
        "days_since_vaulted": None,
        "days_until_vault": None,
        "reasoning": "Item is currently not vaulted.",
    }
    patch_signal = {
        "relevant_patch_found": True,
        "patch_name": "Update 36: Major Frame Nerf",
        "expected_impact": "decrease",
        "reasoning": "Key ability mechanics removed, reducing damage significantly.",
    }

    prompt = build_synthesis_prompt("Test Frame Set", trend_signal, vault_signal, patch_signal)
    res = call_llm_for_synthesis(prompt)

    assert res["recommendation"] == "HOLD"
    assert res["primary_driver"] == "patch"


def test_high_confidence_positive_trend_sells_when_patch_none():
    """Verify that when patch impact is none and R² > 0.45, positive trend recommends SELL."""
    trend_signal = {
        "signal": "rising",
        "slope": 0.35,
        "r_squared": 0.66,
        "pct_change_90d": +18.1,
        "reasoning": "Price has climbed 18.1% with high confidence.",
    }
    vault_signal = {
        "signal": "recently_vaulted",
        "days_since_vaulted": 124,
        "days_until_vault": None,
        "reasoning": "Recently re-entered the vault 124 days ago.",
    }
    patch_signal = {
        "relevant_patch_found": False,
        "patch_name": None,
        "expected_impact": "none",
        "reasoning": "No relevant balance patches.",
    }

    prompt = build_synthesis_prompt("Soma Prime Set", trend_signal, vault_signal, patch_signal)
    res = call_llm_for_synthesis(prompt)

    assert res["recommendation"] == "SELL"
    assert res["primary_driver"] == "trend"


def test_low_confidence_trend_falls_back_to_vault_hold():
    """Verify that when R² <= 0.45, vault status dictates the action (recently_vaulted -> HOLD)."""
    trend_signal = {
        "signal": "falling",
        "slope": -0.05,
        "r_squared": 0.03,
        "pct_change_90d": -11.8,
        "reasoning": "Price has drifted downwards slightly but noisy.",
    }
    vault_signal = {
        "signal": "recently_vaulted",
        "days_since_vaulted": 96,
        "days_until_vault": None,
        "reasoning": "Recently re-entered vault 96 days ago; market absorbing supply.",
    }
    patch_signal = {
        "relevant_patch_found": False,
        "patch_name": None,
        "expected_impact": "none",
        "reasoning": "No relevant balance patches.",
    }

    prompt = build_synthesis_prompt("Gauss Prime Chassis Blueprint", trend_signal, vault_signal, patch_signal)
    res = call_llm_for_synthesis(prompt)

    assert res["recommendation"] == "HOLD"
    assert res["primary_driver"] == "vault"
