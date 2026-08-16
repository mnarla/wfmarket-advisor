# WFM Sell-Timing Advisor 📈⚔️

An on-demand sell/hold intelligence engine for **Warframe Market** built using **LangGraph**, **SQLite**, and **Gemini / LLM synthesis**.

Instead of guessing when to sell your vaulted parts or sets, this tool evaluates 90-day price momentum, live Prime Resurgence rotations (Varzia Dax), and patch balance changes to give you clear **SELL**, **HOLD**, or **WAIT** signals with numerical breakdowns and reasoning.

> 🎥 **Note**: Video demo coming soon!

---

## What It Does

1. **Colloquial On-Demand Querying**:
   - Accepts typos, shorthand, and aliases (e.g., `"rhino prime"`, `"wisp prime sys"`, `"soma prime bld"`, `"excal p bp"`).
   - Dynamically resolves variable component counts for Warframes and Prime weapons (rifles, bows, melee, etc.).

2. **Smart Caching Layer**:
   - SQLite cache with independent staleness tracking (price: 24h, vault: 7d, patches: 24h).
   - Only fetches what is stale or missing on-demand.

3. **Prime Resurgence & Vault Tracking**:
   - Live integration with Warframe WorldState API (`vaultTrader`).
   - Calculates effective vault dates (`max(original vaultDate, latest resurgence expiry)`) to ensure recently returned items aren't misclassified as long-vaulted.
   - Resurgence dates automatically propagate to companion Prime weapons via Prime Access grouping.

4. **Multi-Agent LangGraph Pipeline**:
   - **Trend Node**: Linear regression over 90-day price history with confidence metrics ($R^2$, slope %).
   - **Vault Node**: Calendar-math reasoning for vault states (`recently_vaulted`, `vaulting_soon`, `long_vaulted`, `not_vaulted`).
   - **Patch Node**: Semantic LLM filter that weeds out cosmetic/noise patch notes and identifies genuine gameplay buffs/nerfs.
   - **Synthesis Node**: Evaluates conflicting signals and outputs a high-confidence recommendation card.

---

## Sample Output

```text
================================================================================
ITEM: Soma Prime Set (soma_prime_set)
CURRENT PRICE: 59p (88d Avg: 54.1p)
--------------------------------------------------------------------------------
SIGNALS:
  • Trend:        +19.5% (R² = 0.66)
  • Vault Status: Active (Recently Vaulted, 122d ago)
  • Patch Impact: None
ACTION: SELL
--------------------------------------------------------------------------------
REASONING:
The Soma Prime Set has demonstrated a steady upward price movement over the last
90 days with high statistical confidence. Combined with stabilized supply after its
resurgence rotation, this sustained momentum creates an optimal selling window.
================================================================================
```

---

## Getting Started / Running Locally

### 1. Clone the Repo
```bash
git clone https://github.com/mnarla/wfmarket-scout.git
cd wfmarket-scout
```

### 2. Set Up Virtual Environment & Dependencies
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Bring Your Own API Keys 🔑
Create a `.env` file in the root directory:
```bash
cp .env.example .env
```

Add your API keys to `.env`:
```env
# Required: Google Gemini API Key (for patch reasoning and synthesis)
GEMINI_API_KEY=your_gemini_api_key_here

# Optional: OpenRouter API Key (automatic fallback if Gemini hits rate limits)
OPENROUTER_API_KEY=your_openrouter_api_key_here
```

> **Note on API Keys**: You will need to bring your own API keys. You can get a free Gemini API key from [Google AI Studio](https://aistudio.google.com/). OpenRouter is optional and only used as a fallback if Gemini is overloaded.

---

## Usage

### Interactive Mode (Default)
Search for any Prime Warframe or Weapon interactively:
```bash
python main.py
```
```text
Query item > rhino prime
Query item > soma prime barrel
Query item > wisp prime sys
```

### One-Shot Query Mode
Query a specific item directly from the command line:
```bash
# Query an entire set (returns breakdown for set + all components)
python main.py -q "soma prime"

# Query a single component
python main.py -q "fang prime blade"
```

### Run Tests
```bash
pytest -v
```

---

## License & Disclaimer
This is an unofficial community project and is not affiliated with or endorsed by Digital Extremes. Warframe and Warframe Market data belong to their respective creators.
