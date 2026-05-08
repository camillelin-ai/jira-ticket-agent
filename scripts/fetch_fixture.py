"""
One-time script: fetch a sprint section from the live Google Doc and save it
as a fixture file for use in tests.

Usage:
    python scripts/fetch_fixture.py --doc-id DOC_ID --tab-id TAB_ID --section 2026.19

Requires Google Application Default Credentials:
    gcloud auth application-default login
"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.doc_reader import fetch_doc_text, find_section

FIXTURES_DIR = Path(__file__).parent.parent / "tests" / "fixtures"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--doc-id",  required=True)
    parser.add_argument("--tab-id",  default=None)
    parser.add_argument("--section", required=True, help="e.g. 2026.19")
    parser.add_argument("--out",     default=None,  help="Output filename (default: sprint_SECTION.txt)")
    args = parser.parse_args()

    print(f"Fetching doc {args.doc_id}...")
    content = fetch_doc_text(args.doc_id, tab_id=args.tab_id)

    print(f"Finding section '{args.section}'...")
    section_text, start, end = find_section(content, args.section)
    print(f"  Found at lines {start}–{end} ({len(section_text.splitlines())} lines)")

    out_name = args.out or f"sprint_{args.section.replace('.', '_')}.txt"
    out_path = FIXTURES_DIR / out_name
    out_path.write_text(section_text)
    print(f"Saved to {out_path}")


if __name__ == "__main__":
    main()
