"""
Slice 1.5: Given parsed ActionItems, use Claude to plan each ticket.

For each item determines:
  - action: CREATE | SKIP | ALREADY_TICKETED
  - Jira fields: project, parent epic, clean title, description, priority, assignees
  - Doc inline text: what gets written back next to the line in the doc

No Jira or Google API calls happen here. Pure planning.
"""

import os
import json
from pathlib import Path
from typing import Optional

import anthropic
from dotenv import load_dotenv

try:
    from src.models import ActionItem, ParseResult, TicketPlan
except ImportError:
    from models import ActionItem, ParseResult, TicketPlan

load_dotenv()

_client: Optional[anthropic.Anthropic] = None

TICKET_LOGIC   = (Path(__file__).parent.parent / "ticket_logic.md").read_text()
TEAM_CONTEXT   = (Path(__file__).parent.parent / "team_context.md").read_text()

_SYSTEM = f"""You are a Jira ticket planning agent for the Obsidian Program at Applied Intuition.
You have deep knowledge of how the team organises their work.

{TICKET_LOGIC}

---

{TEAM_CONTEXT}
"""

_PLANNER_PROMPT = """
Sprint: {sprint} ({date_range})

Below are all action items extracted from the sprint planning doc, grouped by feature.
For each item, decide what to do and return a JSON array — one object per item in the SAME ORDER.

## Action items

{items_block}

---

## Output format

Return a JSON array. One object per item, same order as above. Schema:

{{
  "id": <int, 1-based index matching the item list>,
  "action": "CREATE" | "SKIP" | "ALREADY_TICKETED",
  "skip_reason": "<short reason if SKIP>",

  // Populate only when action == "CREATE":
  "project": "EC" | "AVP",
  "parent_epic_key": "<e.g. EC-16104>",
  "parent_epic_summary": "<Jira summary of that epic>",
  "summary": "<clean, verb-led, single-sentence title — max 80 chars>",
  "description": "<1-3 sentence description of the work + Definition of done>",
  "priority": "P0" | "P1" | "P2",
  "assignees": ["<name>"],
  "inline_text": "<KEY Assignee>" // placeholder KEY until real ticket exists
}}

## Title rules
- Start with a verb (Add, Fix, Implement, Scope, Plan, Design, Document, Verify, Integrate…)
- Exception: "Plan for X" is acceptable as-is — it implies scoping and sign-off
- Single sentence, max 80 chars, no run-on
- If the raw task is a bare noun or unclear fragment, make it explicit using the feature + subsection context
- Never include the assignee name in the title

## Description rules
- 1-3 sentences of context explaining the work
- End with a clear "Definition of done:" line
- Pull context from sibling tasks and feature name where helpful
- Higher standard than title — complete sentences, specific

## SKIP rules
Skip an item if:
- It is a pure status note ("Done with scoping and designing", "after-May^")
- It is scheduling logistics with no deliverable
- It is a sub-note that is already fully captured by a sibling item's description
- It is explicitly marked as not scheduled

## ALREADY_TICKETED rules
- Any item with an existing EC-XXXXX or AVP-XXXXX key → ALREADY_TICKETED
- inline_text: leave null (ticket already in the doc line)

## inline_text format (for CREATE)
- Format: "KEY Name" where KEY is a placeholder (e.g. "EC-???? Avi Agarwal")
- Use "AVP-????" or "EC-????" depending on project
- Include assignee name only if NOT already present in the doc line
- This is what gets inserted before the line in the doc

Return ONLY the JSON array, no markdown, no explanation.
"""


def _build_items_block(items: list[ActionItem]) -> str:
    lines = []
    current_feature = None
    for idx, item in enumerate(items, start=1):
        if item.feature != current_feature:
            current_feature = item.feature
            lines.append(f"\n### {item.subsection} › {item.feature}")
        assignees = ", ".join(item.assignees) if item.assignees else "unassigned"
        ticket_note = f" [EXISTING: {item.existing_ticket}]" if item.existing_ticket else ""
        prio_note   = f" [{item.priority_tag}]" if item.priority_tag else ""
        new_note    = " [NEW]" if item.is_new else ""
        sibling_note = ""
        if item.sibling_context:
            siblings = "; ".join(item.sibling_context[:3])
            sibling_note = f"\n     siblings: {siblings}"
        lines.append(
            f"  {idx}. task={item.task!r}  assignees=[{assignees}]"
            f"{ticket_note}{prio_note}{new_note}{sibling_note}"
        )
    return "\n".join(lines)


def plan_sprint(result: ParseResult) -> list[TicketPlan]:
    """
    Plan tickets for all items in a ParseResult.
    Makes a single batched Claude call for efficiency.
    Returns a TicketPlan for every ActionItem.
    """
    global _client
    if _client is None:
        _client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

    items_block = _build_items_block(result.items)
    prompt = _PLANNER_PROMPT.format(
        sprint=result.sprint,
        date_range=result.date_range,
        items_block=items_block,
    )

    response = _client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=8096,
        system=[{"type": "text", "text": _SYSTEM, "cache_control": {"type": "ephemeral"}}],
        messages=[{"role": "user", "content": prompt}],
    )

    raw = response.content[0].text.strip()
    # Strip markdown code fences if present
    if raw.startswith("```"):
        raw = raw.split("\n", 1)[1].rsplit("```", 1)[0].strip()

    plans_raw: list[dict] = json.loads(raw)

    plans: list[TicketPlan] = []
    for i, item in enumerate(result.items):
        plan_data = next((p for p in plans_raw if p.get("id") == i + 1), {})
        action = plan_data.get("action", "SKIP")

        plan = TicketPlan(
            item=item,
            action=action,
            skip_reason=plan_data.get("skip_reason"),
            project=plan_data.get("project"),
            parent_epic_key=plan_data.get("parent_epic_key"),
            parent_epic_summary=plan_data.get("parent_epic_summary"),
            summary=plan_data.get("summary"),
            description=plan_data.get("description"),
            priority=plan_data.get("priority", item.priority_tag or "P1"),
            assignees=plan_data.get("assignees", item.assignees),
            inline_text=plan_data.get("inline_text"),
        )
        plans.append(plan)

    return plans
