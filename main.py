import os
import sys
import argparse
from dotenv import load_dotenv

from ingest.build_db import build_database
from ingest.cache_manager import get_recommendation

# Load environment variables
load_dotenv()


def query_item(user_input: str):
    """
    Executes on-demand recommendation query and prints the formatted card.
    """
    print(f"\nProcessing on-demand query: '{user_input}'...")
    res = get_recommendation(user_input)

    status = res.get("status")
    if status == "not_found":
        print(f"\n[Error] Item not found for query: '{user_input}'. Please check spelling.")
        return

    if status == "ambiguous":
        candidates = res.get("candidates", [])
        cand_str = ", ".join(candidates)
        print(f"\n[Ambiguous] Multiple candidates found for '{user_input}': {cand_str}")
        print("Please refine your search query (e.g. specify the full frame name).")
        return

    formatted_card = res.get("formatted_card")
    if formatted_card:
        print("\n" + formatted_card + "\n")
    else:
        print(res)


def interactive_mode():
    """
    Interactive prompt loop for asking sell-timing advice.
    """
    print("\n================================================================================")
    print("WARFRAME MARKET SELL-TIMING ADVISOR (On-Demand Query Engine)")
    print("Type any Prime item name (e.g. 'rhino prime', 'excal p bp', 'wisp prime sys')")
    print("Type 'exit' or 'quit' to exit.")
    print("================================================================================\n")

    while True:
        try:
            query = input("Query item > ").strip()
            if not query:
                continue
            if query.lower() in ("exit", "quit", "q"):
                print("Exiting WFM Sell-Timing Advisor. Good luck with your trades!")
                break
            query_item(query)
        except (KeyboardInterrupt, EOFError):
            print("\nExiting.")
            break


def main():
    parser = argparse.ArgumentParser(description="Warframe Market Sell-Timing Advisor CLI")
    parser.add_argument(
        "-q", "--query", type=str, help="Free-text item query (e.g. 'rhino prime neuroptics', 'wisp prime sys')"
    )
    parser.add_argument(
        "-i", "--interactive", action="store_true", help="Start interactive query prompt"
    )
    parser.add_argument(
        "--ingest", action="store_true", help="Fetch watchlist data and rebuild SQLite database"
    )
    parser.add_argument(
        "--batch", action="store_true", help="Run full pipeline batch run on watchlist"
    )
    args = parser.parse_args()

    if args.query:
        query_item(args.query)
        return

    if args.interactive:
        interactive_mode()
        return

    if args.ingest:
        print("Starting data ingestion process...")
        build_database()
        return

    if args.batch:
        from run_pipeline import run_full_pipeline, print_summary_and_full_table
        run_full_pipeline()
        print_summary_and_full_table()
        return

    # Default to interactive mode if no arguments provided
    interactive_mode()


if __name__ == "__main__":
    main()
