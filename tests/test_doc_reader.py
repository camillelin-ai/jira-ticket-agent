"""
Sanity tests for Slice 1: doc_reader.py

All tests run against local fixture files — no Google API calls, no Jira calls.
"""

import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.doc_reader import find_section, parse_section
from src.models import ActionItem, ParseResult


# ---------------------------------------------------------------------------
# Section detection
# ---------------------------------------------------------------------------

class TestFindSection:
    def test_finds_structural_heading(self, sprint_2026_19_text):
        section, start, end = find_section(sprint_2026_19_text, "2026.19")
        assert "2026.19" in section
        assert start == 1

    def test_extracts_correct_date_range(self, sprint_2026_19_text):
        section, _, _ = find_section(sprint_2026_19_text, "2026.19")
        result = parse_section(section)
        assert result.sprint == "2026.19"
        assert "May 4" in result.date_range or "May 4, 2026" in result.date_range

    def test_finds_section_in_multi_sprint_doc(self, full_doc_text):
        section, _, _ = find_section(full_doc_text, "2026.17")
        assert "2026.17" in section

    def test_raises_if_section_not_found(self, sprint_2026_19_text):
        with pytest.raises(ValueError, match="not found"):
            find_section(sprint_2026_19_text, "2026.99")

    def test_section_stops_at_next_sprint(self, full_doc_text):
        section, _, _ = find_section(full_doc_text, "2026.19")
        # Should not bleed into 2026.17 content
        assert "2026.17" not in section


# ---------------------------------------------------------------------------
# Subsection parsing
# ---------------------------------------------------------------------------

class TestSubsectionParsing:
    def test_all_three_subsections_present(self, sprint_2026_19_text):
        section, start, _ = find_section(sprint_2026_19_text, "2026.19")
        result = parse_section(section, start)
        subsections = {item.subsection for item in result.items}
        assert "FMS" in subsections
        assert "Stack" in subsections
        assert "Development" in subsections

    def test_items_assigned_to_correct_subsection(self, sprint_2026_19_text):
        section, start, _ = find_section(sprint_2026_19_text, "2026.19")
        result = parse_section(section, start)
        # Bench Loading is Stack
        bench_items = [i for i in result.items if i.feature == "Bench Loading"]
        assert all(i.subsection == "Stack" for i in bench_items)
        # Dump script is FMS
        dump_items = [i for i in result.items if "Dump script" in i.feature or "dump script" in i.task.lower()]
        assert all(i.subsection == "FMS" for i in dump_items)


# ---------------------------------------------------------------------------
# Action item extraction
# ---------------------------------------------------------------------------

class TestActionItemExtraction:
    def test_extracts_items_from_all_subsections(self, sprint_2026_19_text):
        section, start, _ = find_section(sprint_2026_19_text, "2026.19")
        result = parse_section(section, start)
        assert len(result.items) > 10

    def test_task_text_is_not_empty(self, sprint_2026_19_text):
        section, start, _ = find_section(sprint_2026_19_text, "2026.19")
        result = parse_section(section, start)
        for item in result.items:
            assert item.task.strip(), f"Empty task in item: {item.raw_line!r}"

    def test_rockwell_items_extracted(self, sprint_2026_19_text):
        section, start, _ = find_section(sprint_2026_19_text, "2026.19")
        result = parse_section(section, start)
        rockwell_items = [i for i in result.items if i.feature == "Rockwell Bringup"]
        assert len(rockwell_items) >= 3
        tasks = [i.task for i in rockwell_items]
        assert any("Hopper" in t for t in tasks)

    def test_scoping_items_extracted(self, sprint_2026_19_text):
        section, start, _ = find_section(sprint_2026_19_text, "2026.19")
        result = parse_section(section, start)
        triple_lf = [i for i in result.items if i.feature == "Triple Leader Follower"]
        assert len(triple_lf) >= 1
        assert any("Scoping" in i.task for i in triple_lf)


# ---------------------------------------------------------------------------
# Assignee extraction
# ---------------------------------------------------------------------------

class TestAssigneeExtraction:
    def test_feature_level_assignee_inherited(self, sprint_2026_19_text):
        section, start, _ = find_section(sprint_2026_19_text, "2026.19")
        result = parse_section(section, start)
        bench = [i for i in result.items if i.feature == "Bench Loading"]
        assert all("Wenkai Ren" in i.assignees for i in bench), \
            f"Expected Wenkai Ren in all Bench Loading items: {[i.assignees for i in bench]}"

    def test_multiple_assignees_on_single_task(self, sprint_2026_19_text):
        section, start, _ = find_section(sprint_2026_19_text, "2026.19")
        result = parse_section(section, start)
        # "Amber Chau, Jensen Solar: implement mvp of autonomy accumulated metrics dashboard"
        dashboard_items = [
            i for i in result.items
            if "metrics dashboard" in i.task.lower() or "accumulated metrics" in i.task.lower()
        ]
        assert dashboard_items, "Dashboard metrics item not found"
        item = dashboard_items[0]
        assert "Amber Chau" in item.assignees
        assert "Jensen Solar" in item.assignees

    def test_name_after_dash_extracted(self, sprint_2026_19_text):
        section, start, _ = find_section(sprint_2026_19_text, "2026.19")
        result = parse_section(section, start)
        # "Pankaj Saini – need plan doc"
        heidelberg = [i for i in result.items if "plan doc" in i.task.lower() and i.feature == "Heidelberg customer cluster"]
        assert heidelberg, "Heidelberg plan doc item not found"
        assert "Pankaj Saini" in heidelberg[0].assignees

    def test_assignee_at_task_end(self, sprint_2026_19_text):
        section, start, _ = find_section(sprint_2026_19_text, "2026.19")
        result = parse_section(section, start)
        # "[EC-16668]: Revive hill start assist — Peter Redman"
        hill_start = [i for i in result.items if "hill start" in i.task.lower()]
        assert hill_start, "Hill start assist item not found"
        assert "Peter Redman" in hill_start[0].assignees

    def test_standalone_name_not_emitted_as_task(self, sprint_2026_19_text):
        section, start, _ = find_section(sprint_2026_19_text, "2026.19")
        result = parse_section(section, start)
        # "Kamil Nocon" appears as a standalone line under Fuel Bay — should not be its own task
        pure_name_tasks = [i for i in result.items if i.task.strip() in (
            "Kamil Nocon", "Walter Wang", "Wenkai Ren", "Jensen Solar"
        )]
        assert not pure_name_tasks, f"Standalone names emitted as tasks: {pure_name_tasks}"


# ---------------------------------------------------------------------------
# Existing ticket detection
# ---------------------------------------------------------------------------

class TestTicketDetection:
    def test_existing_ec_ticket_detected(self, sprint_2026_19_text):
        section, start, _ = find_section(sprint_2026_19_text, "2026.19")
        result = parse_section(section, start)
        ticketed = result.already_ticketed()
        keys = [i.existing_ticket for i in ticketed]
        assert "EC-16482" in keys
        assert "EC-16498" in keys
        assert "EC-16514" in keys

    def test_existing_avp_ticket_detected(self, sprint_2026_19_text):
        section, start, _ = find_section(sprint_2026_19_text, "2026.19")
        result = parse_section(section, start)
        keys = [i.existing_ticket for i in result.already_ticketed()]
        assert "AVP-57547" in keys

    def test_items_without_tickets_need_tickets(self, sprint_2026_19_text):
        section, start, _ = find_section(sprint_2026_19_text, "2026.19")
        result = parse_section(section, start)
        needs = result.needs_tickets()
        assert len(needs) > 0
        # "Scoping out Hopper" has no ticket
        assert any("Hopper" in i.task or "Scoping" in i.task for i in needs)

    def test_ticketed_items_do_not_need_tickets(self, sprint_2026_19_text):
        section, start, _ = find_section(sprint_2026_19_text, "2026.19")
        result = parse_section(section, start)
        for item in result.already_ticketed():
            assert not item.needs_ticket()

    def test_counts_are_consistent(self, sprint_2026_19_text):
        section, start, _ = find_section(sprint_2026_19_text, "2026.19")
        result = parse_section(section, start)
        assert len(result.needs_tickets()) + len(result.already_ticketed()) == len(result.items)


# ---------------------------------------------------------------------------
# Priority and flags
# ---------------------------------------------------------------------------

class TestFlags:
    def test_p2_tag_parsed(self, sprint_2026_19_text):
        section, start, _ = find_section(sprint_2026_19_text, "2026.19")
        result = parse_section(section, start)
        p2_items = [i for i in result.items if i.priority_tag == "P2"]
        assert len(p2_items) >= 2  # "[P2] integrates with stack" and "[P2] smoke tests"

    def test_new_tag_parsed(self, sprint_2026_19_text):
        section, start, _ = find_section(sprint_2026_19_text, "2026.19")
        result = parse_section(section, start)
        new_items = [i for i in result.items if i.is_new]
        assert len(new_items) >= 2  # [New – 26.19-21] EC-16600, [New] HIL bench doc

    def test_tags_stripped_from_task_text(self, sprint_2026_19_text):
        section, start, _ = find_section(sprint_2026_19_text, "2026.19")
        result = parse_section(section, start)
        for item in result.items:
            assert "[P0]" not in item.task
            assert "[P1]" not in item.task
            assert "[P2]" not in item.task
            assert "[New]" not in item.task
