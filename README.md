# WFM Sell-Timing Advisor

An on-demand sell/hold recommendation pipeline for **Warframe Market** built using **LangGraph**, **SQLite**, and **Gemini / LLM synthesis**.

---

## Architecture & Capabilities

1. **On-Demand Free-Text Query Engine ([`slug_resolver.py`](slug_resolver.py))**:
   - Accepts colloquial item queries (e.g. `"rhino prime"`, `"wisp prime sys"`, `"excal p bp"`).
   - Dynamically parses component aliases (`set`, `bp`/`blueprint`, `neuroptics`/`neuro`, `chassis`/`chass`, `systems`/`sys`).
   - Uses `RapidFuzz` token sorting with alias normalization against live Warframe Market catalogs.

2. **Conditional Cache & Ingestion Layer ([`cache_manager.py`](cache_manager.py))**:
   - Independent staleness tracking in SQLite:
     - **Price History**: Stale if $> 24\text{ hours}$
     - **Vault Status**: Stale if $> 7\text{ days}$
     - **Patchlogs**: Stale if $> 24\text{ hours}$
   - Only refetches missing or stale data on-demand, keeping cached entries intact if network/API calls fail.

3. **Live Prime Resurgence & Vault Tracking ([`ingest/fetch_vault_patch_data.py`](ingest/fetch_vault_patch_data.py))**:
   - Integrates live Warframe WorldState API (`vaultTrader`) to track active Prime Resurgence rotations (Varzia Dax).
   - Computes effective vault dates ($\max(\text{Original Vault Date}, \text{Latest Resurgence End Date})$) to prevent mislabeling recently unvaulted frames as long-vaulted.

4. **Multi-Agent LangGraph Pipeline ([`agents/graph.py`](agents/graph.py))**:
   - **Trend Node ([`agents/trend_node.py`](agents/trend_node.py))**: Linear regression over 90-day price history with scale-independent thresholding ($\pm 10\%$).
   - **Vault Node ([`agents/vault_node.py`](agents/vault_node.py))**: Calendar-math reasoning for vaulting and resurgence states (`recently_vaulted`, `vaulting_soon`, `long_vaulted`, `not_vaulted`).
   - **Patch Node ([`agents/patch_node.py`](agents/patch_node.py))**: LLM semantic filter discerning genuine balance changes (buffs/nerfs) from noise/bugfixes.
   - **Synthesis Node ([`agents/synthesis_node.py`](agents/synthesis_node.py))**: Weighs conflicting signals and outputs final `SELL` / `HOLD` recommendation, confidence, primary driver, and plain-English justification.

---

## Quickstart

Still developing so I will update soon. 

