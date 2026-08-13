-- SQLite Database Schema for wfm-sell-timing-advisor

-- Table for tracking individual items (e.g., saryn_prime_set, saryn_prime_blueprint, etc.)
CREATE TABLE IF NOT EXISTS items (
    item_id TEXT PRIMARY KEY,               -- WFM item unique ID
    url_slug TEXT NOT NULL UNIQUE,          -- WFM URL slug (e.g. saryn_prime_set)
    item_name TEXT NOT NULL,                -- Plain English item name
    frame_name TEXT NOT NULL,               -- The Warframe this belongs to (e.g. Saryn Prime)
    component_type TEXT NOT NULL,           -- 'set', 'blueprint', 'neuroptics', 'chassis', 'systems'
    vault_status TEXT DEFAULT 'unvaulted',  -- 'vaulted', 'unvaulted'
    vault_date TEXT,                       -- ISO date string when vaulted
    estimated_vault_date TEXT               -- ISO date string of estimated vaulting
);

-- Table for historical price & volume statistics (48hr and 90day intervals)
CREATE TABLE IF NOT EXISTS price_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    item_id TEXT NOT NULL,
    recorded_at TEXT NOT NULL,              -- ISO timestamp from the statistic entry
    avg_price REAL,
    median_price REAL,
    volume INTEGER,
    moving_avg REAL,
    stat_window TEXT NOT NULL,              -- '90day' or '48hr'
    UNIQUE(item_id, recorded_at, stat_window),
    FOREIGN KEY(item_id) REFERENCES items(item_id)
);

-- Table for component patchlogs parsed/extracted from warframe-items
CREATE TABLE IF NOT EXISTS patchlogs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    frame_name TEXT NOT NULL,
    patch_name TEXT NOT NULL,
    patch_date TEXT NOT NULL,
    patch_url TEXT,
    additions TEXT,
    changes TEXT,
    fixes TEXT
);

-- Table for generated sell-or-hold recommendations from the LangGraph pipeline
CREATE TABLE IF NOT EXISTS recommendations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    item_id TEXT NOT NULL,
    generated_at TEXT NOT NULL,             -- ISO timestamp
    recommendation TEXT NOT NULL,           -- 'SELL', 'HOLD'
    confidence TEXT,                        -- 'low', 'medium', 'high'
    primary_driver TEXT,                    -- 'trend', 'vault', 'patch', 'combined'
    trend_signal REAL,                      -- Numeric signal from trend node
    vault_signal TEXT,                      -- Signal from vault node
    patch_signal TEXT,                      -- Signal/analysis from patch node
    reasoning TEXT NOT NULL,                -- Plain-English synthesis explanation
    FOREIGN KEY(item_id) REFERENCES items(item_id)
);
