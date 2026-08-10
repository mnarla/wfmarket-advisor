# WFM Sell-Timing Advisor

A portfolio project focused on agent orchestration for Warframe Market selling recommendations. It implements a LangGraph multi-signal pipeline balancing quantitative price trends, deterministic vaulting schedules, and qualitative patch note analysis to form structured reasoning on whether to SELL or HOLD.

## Project Structure

```
wfm-sell-timing-advisor/
├── README.md                  # Project overview and architecture
├── requirements.txt           # Python dependencies
├── .env.example               # Environment variables template
├── .gitignore
├── config/
│   └── watchlist.json         # Watched Prime frames
├── db/
│   └── schema.sql             # Database definition
├── ingest/
│   ├── slug_utils.py          # WFM Slug parser
│   ├── fetch_wfm.py           # WFM v2 scraper (stub)
│   ├── fetch_vault_patch_data.py # WFCD dataset downloader (stub)
│   └── build_db.py            # SQLite pipeline build orchestrator
├── agents/
│   ├── state.py               # TypedDict LangGraph state
│   ├── graph.py               # LangGraph compile workflow
│   ├── trend_node.py          # Linear Regression trend analyzer
│   ├── vault_node.py          # Scarcity tracker
│   ├── patch_node.py          # LLM patch note evaluator
│   └── synthesis_node.py      # Core decider node
├── tests/
│   └── test_slug_utils.py     # Parser unit tests
└── main.py                    # CLI CLI controller
```

## Getting Started

1. Set up a virtual environment and install requirements:
   ```bash
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

2. Copy the environment template and fill in keys:
   ```bash
   cp .env.example .env
   ```

3. Run the ingest command to initialize DB:
   ```bash
   python main.py --ingest
   ```

4. Run tests:
   ```bash
   pytest
   ```
