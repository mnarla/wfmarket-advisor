import os
import json
import argparse
from dotenv import load_dotenv
from ingest.build_db import build_database
from agents.graph import create_advisor_graph

# Load environment variables
load_dotenv()

def run_pipeline(item_slug: str):
    """
    Runs the advisor LangGraph over a specific item slug.
    Loads data context from SQLite, runs graph nodes, and persists recommendation.
    """
    print(f"Running advisor pipeline for: {item_slug}")
    graph = create_advisor_graph()
    
    # Mock inputs matching state for skeleton execution
    initial_state = {
        "item_id": "mock_id",
        "url_slug": item_slug,
        "item_name": item_slug.replace('_', ' ').title(),
        "frame_name": "Saryn Prime",
        "component_type": "set",
        "price_history": [],
        "vault_info": {},
        "patchlogs": [],
        "trend_signal": {},
        "vault_signal": {},
        "patch_signal": {},
        "recommendation": "",
        "reasoning": ""
    }
    
    result = graph.invoke(initial_state)
    print(f"Final Recommendation for {item_slug}: {result.get('recommendation')}")
    print(f"Reasoning: {result.get('reasoning')}")

def main():
    parser = argparse.ArgumentParser(description="WFM Sell-Timing Advisor CLI")
    parser.add_argument('--ingest', action='store_true', help="Fetch data and rebuild SQLite database")
    parser.add_argument('--run', type=str, help="Run advisor pipeline for a specific item slug")
    args = parser.parse_args()
    
    if args.ingest:
        print("Starting data ingestion process...")
        build_database()
        
    if args.run:
        run_pipeline(args.run)
        
    if not args.ingest and not args.run:
        parser.print_help()

if __name__ == '__main__':
    main()
