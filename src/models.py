from dataclasses import dataclass, field
from typing import Optional


@dataclass
class ActionItem:
    task: str                            # cleaned task description
    raw_line: str                        # original line verbatim from doc
    subsection: str                      # FMS / Stack / Development
    feature: str                         # parent feature grouping (e.g. "Bench Loading")
    assignees: list[str] = field(default_factory=list)
    existing_ticket: Optional[str] = None   # EC-XXXXX or AVP-XXXXX if already in the line
    priority_tag: Optional[str] = None      # "P0" / "P1" / "P2" if explicitly tagged
    is_new: bool = False                    # has [New] or [New – XX.XX] tag
    indent_level: int = 0
    line_number: int = 0                    # 1-based line number within the section text

    def needs_ticket(self) -> bool:
        """True if this item appears to need a new Jira ticket."""
        return self.existing_ticket is None and bool(self.task.strip())

    def to_dict(self) -> dict:
        return {
            "task":            self.task,
            "subsection":      self.subsection,
            "feature":         self.feature,
            "assignees":       self.assignees,
            "existing_ticket": self.existing_ticket,
            "priority_tag":    self.priority_tag,
            "is_new":          self.is_new,
            "needs_ticket":    self.needs_ticket(),
            "indent_level":    self.indent_level,
            "line_number":     self.line_number,
            "raw_line":        self.raw_line,
        }


@dataclass
class ParseResult:
    sprint:       str
    date_range:   str
    items:        list[ActionItem] = field(default_factory=list)
    raw_section:  str = ""

    def needs_tickets(self) -> list[ActionItem]:
        return [i for i in self.items if i.needs_ticket()]

    def already_ticketed(self) -> list[ActionItem]:
        return [i for i in self.items if i.existing_ticket]
