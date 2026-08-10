import sqlite3
import os
import json
from ingest.fetch_wfm import fetch_watchlist_items, fetch_price_history
from ingest.fetch_vault_patch_data import fetch_vault_status, fetch_patchlogs

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'db', 'wfm_advisor.db')

def init_db():
    """Initializes the SQLite database with the schema."""
    schema_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'db', 'schema.sql')
    with open(schema_path, 'r') as f:
        schema_sql = f.read()
        
    conn = sqlite3.connect(DB_PATH)
    conn.executescript(schema_sql)
    conn.commit()
    conn.close()

def build_database():
    """
    Orchestrates the fetching, parsing, and writing of WFM and WFCD data into SQLite.
    """
    init_db()
    
    # Load watchlist
    watchlist_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config', 'watchlist.json')
    with open(watchlist_path, 'r') as f:
        watchlist = json.load(f)
        
    # TODO: Perform ingestion flow:
    # 1. Fetch live watchlist items from WFM
    # 2. Fetch price history for each item and insert to price_history
    # 3. Fetch vault status & patchlogs from WFCD and populate items & patchlogs tables
    
    print("Database built successfully skeleton executed.")

if __name__ == '__main__':
    build_database()
