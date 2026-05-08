"""
Slice 1: Read a sprint planning section from a Google Doc and extract action items.

Usage:
    python src/doc_reader.py --from-file tests/fixtures/sprint_2026_19.txt --section 2026.19
    python src/doc_reader.py --doc-id DOC_ID --section 2026.19   (requires Google auth)

Output: JSON array of action items to stdout.
"""

import re
import sys
import json
import argparse
from pathlib import Path
from typing import Optional

# src is a package; support both direct run and import
try:
    from src.models import ActionItem, ParseResult
except ImportError:
    from models import ActionItem, ParseResult


# ---------------------------------------------------------------------------
# Regex patterns
# ---------------------------------------------------------------------------

# Sprint heading: ## 2026.19 – May 4, 2026 – May 15, 2026
_SPRINT_HEADING = re.compile(
    r'^#{1,4}\s+(\d{4}\.\d{2})\s*[–\-](.+)$'
)
# Any markdown heading
_HEADING = re.compile(r'^(#{1,6})\s+(.+)$')

# Bullet line: leading spaces + "- " or "• "
_BULLET = re.compile(r'^(\s*)[-•]\s+(.+)$')

# Existing ticket reference anywhere in a line
_TICKET_REF = re.compile(r'\b((?:EC|AVP)-\d+)\b')

# Priority tag: [P0] [P1] [P2]
_PRIORITY = re.compile(r'\[P([0-2])\]')

# [New] or [New – 26.19-21] etc.
_NEW_TAG = re.compile(r'\[New[^\]]*\]', re.IGNORECASE)

# Assignee patterns -------------------------------------------------------
# "FirstName LastName" (single name, title-cased, 2+ words)
_SINGLE_NAME = re.compile(r'^[A-Z][a-z]+(?:\s+[A-Z][a-z]+)+$')

# "Name1, Name2: task" or "Name: task"
_NAMES_COLON_TASK = re.compile(
    r'^([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+(?:,\s*[A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)*)\s*:\s*(.+)$'
)
# "task: Name" (name at end after colon — less common)
_TASK_COLON_NAME = re.compile(
    r'^(.+):\s*([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)$'
)
# "task – Name" (name after em-dash)
_TASK_DASH_NAME = re.compile(
    r'^(.+?)\s*[–—]\s*([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)$'
)

# Subsection headings inside a sprint (#### FMS, #### Stack, etc.)
_KNOWN_SUBSECTIONS = {"FMS", "Stack", "Development", "Non-Autonomy Deliverables"}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _indent_level(line: str) -> int:
    """Return indentation depth: count of leading spaces divided by 2."""
    return (len(line) - len(line.lstrip(' '))) // 2


def _strip_tags(text: str) -> str:
    """Remove [P0]/[P2]/[New...] tags and clean up whitespace."""
    text = _PRIORITY.sub('', text)
    text = _NEW_TAG.sub('', text)
    return text.strip(' -–—:')


def _extract_ticket(text: str) -> Optional[str]:
    m = _TICKET_REF.search(text)
    return m.group(1) if m else None


def _extract_priority(text: str) -> Optional[str]:
    m = _PRIORITY.search(text)
    return f"P{m.group(1)}" if m else None


def _is_name_only(text: str) -> bool:
    """True if the line is just one or more person names (not a task)."""
    # Strip trailing/leading punctuation
    t = text.strip(' -–—:')
    # Each comma-separated part should look like a title-cased name
    parts = [p.strip() for p in t.split(',')]
    return all(_SINGLE_NAME.match(p) for p in parts if p)


def _parse_assignees_and_task(text: str) -> tuple[list[str], str]:
    """
    Given raw bullet text (tags already stripped from ticket/priority),
    return (assignees, task_description).

    Handles:
      "Name: task"
      "Name1, Name2: task"
      "task – Name"
      "task: Name"  (when Name is clearly a person)
      pure name line → (names, "")
    """
    text = text.strip()

    if _is_name_only(text):
        names = [n.strip() for n in text.split(',')]
        return names, ""

    # "Name(s): task"
    m = _NAMES_COLON_TASK.match(text)
    if m:
        names = [n.strip() for n in m.group(1).split(',')]
        return names, m.group(2).strip()

    # "task – Name" (em-dash assignee at end)
    m = _TASK_DASH_NAME.match(text)
    if m:
        task_part = m.group(1).strip()
        name_part = m.group(2).strip()
        if _SINGLE_NAME.match(name_part):
            return [name_part], task_part

    # "task: Name" — only treat as assignee if trailing part is a bare name
    m = _TASK_COLON_NAME.match(text)
    if m:
        name_part = m.group(2).strip()
        if _SINGLE_NAME.match(name_part):
            return [name_part], m.group(1).strip()

    return [], text


def _is_noise(text: str) -> bool:
    """Skip lines that are URLs, empty, or scheduling notes like 'after-May^'."""
    t = text.strip()
    if not t:
        return True
    if t.startswith('http'):
        return True
    if re.match(r'^after-', t, re.IGNORECASE):
        return True
    if t in ('Not scheduled for this sprint',):
        return True
    return False


# ---------------------------------------------------------------------------
# Section finder
# ---------------------------------------------------------------------------

def find_section(content: str, query: str) -> tuple[str, int, int]:
    """
    Locate the sprint section matching `query` (e.g. "2026.19") in `content`.

    Returns (section_text, start_line_1based, end_line_1based).
    Raises ValueError if not found.

    Handles:
      - Structural: ## 2026.19 – ...
      - Semantic: line containing "2026.19" that looks like a header
        (short, standalone, followed by subsection content)
    """
    lines = content.splitlines()
    start_idx = None
    end_idx = None

    for i, line in enumerate(lines):
        # Structural match: markdown heading containing the query
        m = _SPRINT_HEADING.match(line)
        if m and query in m.group(1):
            start_idx = i
            break

        # Semantic match: short line containing the query, no bullet
        if query in line and not _BULLET.match(line):
            stripped = line.strip()
            # Treat as a header if it's short-ish and looks like a heading
            if len(stripped) < 80 and not stripped.startswith('http'):
                start_idx = i
                break

    if start_idx is None:
        raise ValueError(f"Section '{query}' not found in document content")

    # End: next heading at same or higher level, or end of content
    start_hashes = len(lines[start_idx]) - len(lines[start_idx].lstrip('#'))
    start_hashes = max(start_hashes, 1)

    for i in range(start_idx + 1, len(lines)):
        m = _HEADING.match(lines[i])
        if m and len(m.group(1)) <= start_hashes:
            end_idx = i
            break

    if end_idx is None:
        end_idx = len(lines)

    section = '\n'.join(lines[start_idx:end_idx])
    return section, start_idx + 1, end_idx


# ---------------------------------------------------------------------------
# Section parser
# ---------------------------------------------------------------------------

def parse_section(section_text: str, section_start_line: int = 1) -> ParseResult:
    """
    Parse a sprint section into structured ActionItems.

    Args:
        section_text: The raw text of the section.
        section_start_line: 1-based line number of the section heading in the
                            original document (used for write-back references).
    """
    lines = section_text.splitlines()

    # Extract sprint and date range from heading
    sprint = ""
    date_range = ""
    m = _SPRINT_HEADING.match(lines[0].strip())
    if m:
        sprint = m.group(1)
        date_range = m.group(2).strip()

    result = ParseResult(sprint=sprint, date_range=date_range, raw_section=section_text)

    current_subsection = ""
    current_feature = ""
    feature_assignees: list[str] = []
    assignee_stack: list[tuple[int, list[str]]] = []
    # track raw task texts per feature so we can backfill sibling_context after parsing
    feature_item_indices: dict[str, list[int]] = {}   # feature → indices into result.items

    for rel_idx, raw_line in enumerate(lines[1:], start=2):   # skip heading
        line_no = section_start_line + rel_idx - 1

        # Subsection heading (#### FMS, #### Stack, etc.)
        hm = _HEADING.match(raw_line.strip())
        if hm and len(hm.group(1)) >= 3:
            name = hm.group(2).strip()
            if name in _KNOWN_SUBSECTIONS or len(hm.group(1)) >= 3:
                current_subsection = name
                current_feature = ""
                feature_assignees = []
                assignee_stack = []
                continue

        bm = _BULLET.match(raw_line)
        if not bm:
            continue

        indent = _indent_level(raw_line)
        text = bm.group(2).strip()

        if _is_noise(text):
            continue

        # Pop assignee stack entries deeper than current indent
        assignee_stack = [(lvl, a) for lvl, a in assignee_stack if lvl < indent]

        # Detect existing ticket
        ticket = _extract_ticket(text)
        priority = _extract_priority(text)
        is_new = bool(_NEW_TAG.search(text))

        # Clean text for display (remove ticket refs and tags)
        clean = _strip_tags(text)
        clean = _TICKET_REF.sub('', clean).strip(' -–—:[]')

        # Feature-level line (top indentation within subsection, ~1 level)
        if indent <= 1:
            current_feature = ""
            feature_assignees = []
            assignee_stack = []

            assignees, task = _parse_assignees_and_task(clean)

            if not task and not ticket:
                current_feature = clean
                feature_assignees = assignees
                continue
            else:
                if not current_feature:
                    current_feature = clean if not task else ""
                item = ActionItem(
                    task=task or clean,
                    raw_line=raw_line,
                    subsection=current_subsection,
                    feature=current_feature or (task or clean),
                    assignees=assignees or feature_assignees,
                    existing_ticket=ticket,
                    priority_tag=priority,
                    is_new=is_new,
                    indent_level=indent,
                    line_number=line_no,
                )
                feature_item_indices.setdefault(current_feature, []).append(len(result.items))
                result.items.append(item)
            continue

        # Sub-item line
        assignees, task = _parse_assignees_and_task(clean)

        if not task and assignees and not ticket:
            # Standalone name(s) — push onto assignee stack for children
            assignee_stack.append((indent, assignees))
            continue

        # Inherit assignees from stack if none on this line
        inherited = []
        for _, a in reversed(assignee_stack):
            inherited = a
            break
        effective_assignees = assignees or inherited or feature_assignees

        if not task and ticket:
            task = clean or ticket

        if not task:
            continue

        item = ActionItem(
            task=task,
            raw_line=raw_line,
            subsection=current_subsection,
            feature=current_feature,
            assignees=effective_assignees,
            existing_ticket=ticket,
            priority_tag=priority,
            is_new=is_new,
            indent_level=indent,
            line_number=line_no,
        )
        feature_item_indices.setdefault(current_feature, []).append(len(result.items))
        result.items.append(item)

    # Backfill sibling_context: each item gets the task texts of its feature-siblings
    for feature, indices in feature_item_indices.items():
        all_tasks = [result.items[i].task for i in indices]
        for i in indices:
            result.items[i].sibling_context = [t for t in all_tasks if t != result.items[i].task]

    return result


# ---------------------------------------------------------------------------
# Google Docs fetch (live path — requires Application Default Credentials)
# ---------------------------------------------------------------------------

def fetch_doc_text(doc_id: str, tab_id: Optional[str] = None) -> str:
    """
    Fetch a Google Doc as plain text via the Docs API.

    Requires: `gcloud auth application-default login` or a service account.
    Add to .env: GOOGLE_APPLICATION_CREDENTIALS=/path/to/credentials.json
    """
    try:
        from google.auth import default
        from googleapiclient.discovery import build
    except ImportError:
        raise RuntimeError(
            "Google API libraries not installed. Run: "
            "pip install google-api-python-client google-auth-oauthlib"
        )

    creds, _ = default(scopes=["https://www.googleapis.com/auth/documents.readonly"])
    service = build("docs", "v1", credentials=creds)

    params: dict = {"documentId": doc_id}
    if tab_id:
        params["includeTabsContent"] = True

    doc = service.documents().get(**params).execute()

    # Extract text from document body (or specific tab)
    if tab_id and "tabs" in doc:
        for tab in doc.get("tabs", []):
            if tab.get("tabProperties", {}).get("tabId") == tab_id:
                body = tab.get("documentTab", {}).get("body", {})
                return _extract_text_from_body(body)

    body = doc.get("body", {})
    return _extract_text_from_body(body)


def _extract_text_from_body(body: dict) -> str:
    """Convert Google Docs API body JSON to plain text."""
    lines = []
    for element in body.get("content", []):
        para = element.get("paragraph")
        if not para:
            continue
        style = para.get("paragraphStyle", {}).get("namedStyleType", "")
        bullet = para.get("bullet")

        text = "".join(
            r.get("textRun", {}).get("content", "")
            for r in para.get("elements", [])
        ).rstrip("\n")

        if not text.strip():
            continue

        # Heading levels
        heading_map = {
            "HEADING_1": "# ", "HEADING_2": "## ",
            "HEADING_3": "### ", "HEADING_4": "#### ",
        }
        if style in heading_map:
            lines.append(f"{heading_map[style]}{text}")
        elif bullet:
            depth = bullet.get("nestingLevel", 0)
            indent = "  " * depth
            lines.append(f"{indent}- {text}")
        else:
            lines.append(text)

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Extract action items from a sprint planning section")
    src = parser.add_mutually_exclusive_group(required=True)
    src.add_argument("--from-file", metavar="PATH", help="Read doc content from a local text file")
    src.add_argument("--doc-id",    metavar="ID",   help="Fetch live from Google Docs API")

    parser.add_argument("--section",  required=True, metavar="SPRINT", help="Sprint identifier, e.g. 2026.19")
    parser.add_argument("--tab-id",   metavar="TAB",  help="Google Doc tab ID (for --doc-id only)")
    parser.add_argument("--needs-tickets", action="store_true", help="Only show items without existing tickets")
    parser.add_argument("--pretty",   action="store_true", help="Pretty-print JSON output")

    args = parser.parse_args()

    if args.from_file:
        content = Path(args.from_file).read_text()
    else:
        content = fetch_doc_text(args.doc_id, tab_id=args.tab_id)

    section_text, start_line, _ = find_section(content, args.section)
    result = parse_section(section_text, section_start_line=start_line)

    items = result.needs_tickets() if args.needs_tickets else result.items
    output = {
        "sprint":     result.sprint,
        "date_range": result.date_range,
        "total":      len(result.items),
        "needs_ticket": len(result.needs_tickets()),
        "already_ticketed": len(result.already_ticketed()),
        "items":      [i.to_dict() for i in items],
    }

    indent = 2 if args.pretty else None
    print(json.dumps(output, indent=indent))


if __name__ == "__main__":
    main()
