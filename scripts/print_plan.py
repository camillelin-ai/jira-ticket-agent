"""
Print a human-readable audit of every line item in a sprint section.

For each item shows:
  - What the agent would do (CREATE / SKIP / ALREADY_TICKETED)
  - If CREATE: all proposed Jira fields
  - Doc inline: what gets written back into the doc

Usage (dry-run, no writes):
    python scripts/print_plan.py --from-file tests/fixtures/sprint_2026_19.txt --section 2026.19
    python scripts/print_plan.py --from-file tests/fixtures/sprint_2026_19.txt --section 2026.19 --needs-tickets-only
"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.doc_reader import find_section, parse_section
from src.ticket_planner import plan_sprint
from src.models import TicketPlan

# ── ANSI colours ──────────────────────────────────────────────────────────────
GREEN  = "\033[92m"
YELLOW = "\033[93m"
CYAN   = "\033[96m"
RED    = "\033[91m"
GREY   = "\033[90m"
BOLD   = "\033[1m"
RESET  = "\033[0m"

W = 72   # line width


def bar(char="─"):
    return char * W


def header(text: str, colour: str) -> str:
    return f"{colour}{BOLD}{text}{RESET}"


def field(label: str, value: str, colour: str = "") -> str:
    pad = 18
    return f"  {GREY}{label:<{pad}}{RESET}{colour}{value}{RESET}"


def print_plan(plan: TicketPlan, idx: int, total: int):
    item = plan.item

    action_colours = {
        "CREATE":           GREEN,
        "SKIP":             GREY,
        "ALREADY_TICKETED": CYAN,
    }
    colour = action_colours.get(plan.action, RESET)

    print(f"\n{bar()}")
    label = f" {idx}/{total}  [{plan.action}]  {item.subsection} › {item.feature}"
    print(header(label, colour))
    print(bar())

    print(field("Raw line:", item.raw_line.strip(), GREY))
    print(field("Assignees:", ", ".join(item.assignees) if item.assignees else "—"))

    if plan.action == "SKIP":
        reason = plan.skip_reason or "no reason given"
        print(field("Skip reason:", reason, GREY))

    elif plan.action == "ALREADY_TICKETED":
        print(field("Existing ticket:", item.existing_ticket or "—", CYAN))
        print(field("Doc inline:", "✓ ticket key already present in line", CYAN))

    elif plan.action == "CREATE":
        print()
        print(field("Project:",      plan.project or "—",             GREEN))
        print(field("Parent epic:",  f"{plan.parent_epic_key}  {plan.parent_epic_summary or ''}", ""))
        print(field("Title:",        plan.summary or "—",             BOLD))
        print(field("Priority:",     plan.priority,                   YELLOW if plan.priority == "P0" else ""))
        print(field("Assignees:",    ", ".join(plan.assignees) if plan.assignees else "unassigned"))
        print(field("Sprint:",       plan.sprint or "Eng Sprint v2 (current)"))

        if plan.description:
            print()
            print(f"  {GREY}Description:{RESET}")
            for line in plan.description.split("\n"):
                print(f"    {line}")

        if plan.inline_text:
            print()
            print(field("Doc inline:", f"→ insert  \"{plan.inline_text} \"  before line", GREEN))


def main():
    parser = argparse.ArgumentParser(description="Dry-run: print planned actions for a sprint section")
    src = parser.add_mutually_exclusive_group(required=True)
    src.add_argument("--from-file", metavar="PATH")
    src.add_argument("--doc-id",    metavar="ID")
    parser.add_argument("--section",           required=True)
    parser.add_argument("--tab-id",            default=None)
    parser.add_argument("--needs-tickets-only", action="store_true",
                        help="Only show CREATE items (hide SKIP and ALREADY_TICKETED)")
    args = parser.parse_args()

    if args.from_file:
        content = Path(args.from_file).read_text()
    else:
        from src.doc_reader import fetch_doc_text
        content = fetch_doc_text(args.doc_id, tab_id=args.tab_id)

    print(f"\n{BOLD}Parsing section '{args.section}'...{RESET}")
    section_text, start, _ = find_section(content, args.section)
    result = parse_section(section_text, section_start_line=start)

    print(f"Found {len(result.items)} items  "
          f"({len(result.needs_tickets())} need tickets, "
          f"{len(result.already_ticketed())} already ticketed)")

    print(f"\n{BOLD}Planning tickets via Claude...{RESET}")
    plans = plan_sprint(result)

    creates   = sum(1 for p in plans if p.action == "CREATE")
    skips     = sum(1 for p in plans if p.action == "SKIP")
    ticketed  = sum(1 for p in plans if p.action == "ALREADY_TICKETED")

    if args.needs_tickets_only:
        plans = [p for p in plans if p.action == "CREATE"]

    print(f"\n{bar('═')}")
    print(f"{BOLD}  Sprint {result.sprint}  ·  {result.date_range}{RESET}")
    print(f"  {GREEN}CREATE {creates}{RESET}   "
          f"{CYAN}ALREADY_TICKETED {ticketed}{RESET}   "
          f"{GREY}SKIP {skips}{RESET}")
    print(f"{bar('═')}")

    for i, plan in enumerate(plans, start=1):
        print_plan(plan, i, len(plans))

    print(f"\n{bar()}")
    print(f"{BOLD}  Done.  No changes were made to the doc or Jira.{RESET}")
    print(bar())


if __name__ == "__main__":
    main()
