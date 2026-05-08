import os
import json
import requests
import anthropic
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()

client     = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
JIRA_AUTH  = (os.environ["JIRA_EMAIL"], os.environ["JIRA_API_TOKEN"])
JIRA_HDRS  = {"Accept": "application/json", "Content-Type": "application/json"}
SYSTEM_PROMPT = Path("system_prompt.md").read_text()

def load_config(project_key: str) -> dict:
    path = Path(f"config/{project_key.lower()}.json")
    return json.loads(path.read_text())


# ---------- Jira API helpers ----------

def create_ticket(project_key: str, summary: str, description: str, fields: dict) -> dict:
    """Create a single Jira issue and return the created issue data."""
    config   = load_config(project_key)
    base_url = config["jira_base_url"]

    body = {
        "fields": {
            "project":     {"key": project_key},
            "summary":     summary,
            "description": {"type": "doc", "version": 1, "content": [
                {"type": "paragraph", "content": [{"type": "text", "text": description}]}
            ]},
            "issuetype":   {"name": fields.get("issue_type", "Story")},
        }
    }

    field_map = config["fields"]
    for generic_name, value in fields.items():
        if generic_name == "issue_type":
            continue
        jira_field_id = field_map.get(generic_name)
        if jira_field_id and jira_field_id != "FETCH_FIELD_ID":
            body["fields"][jira_field_id] = value

    response = requests.post(
        f"{base_url}/rest/api/3/issue",
        auth=JIRA_AUTH, headers=JIRA_HDRS, json=body
    )
    response.raise_for_status()
    return response.json()


def get_transition_id(issue_key: str, transition_name: str) -> str:
    """Look up the transition ID for a given status name on a specific issue."""
    base_url = "https://appliedintuition.atlassian.net"
    response = requests.get(
        f"{base_url}/rest/api/3/issue/{issue_key}/transitions",
        auth=JIRA_AUTH, headers=JIRA_HDRS
    )
    response.raise_for_status()
    for t in response.json()["transitions"]:
        if t["name"].lower() == transition_name.lower():
            return t["id"]
    raise ValueError(f"Transition '{transition_name}' not found for {issue_key}")


def bulk_transition(issue_keys: list[str], project_key: str) -> dict:
    """Move a list of issues to the To Do status without sending notifications."""
    config          = load_config(project_key)
    base_url        = config["jira_base_url"]
    transition_name = config["todo_transition_name"]
    transition_id   = get_transition_id(issue_keys[0], transition_name)

    body = {
        "issueIdsOrKeys":    issue_keys,
        "transition":        {"id": transition_id},
        "sendBulkNotification": False,
    }
    response = requests.post(
        f"{base_url}/rest/api/3/bulk/issues/transitions",
        auth=JIRA_AUTH, headers=JIRA_HDRS, json=body
    )
    response.raise_for_status()
    return response.json()


# ---------- Claude tool definitions ----------

TOOLS = [
    {
        "name": "create_jira_ticket",
        "description": (
            "Create a single Jira ticket. Use this for each ticket that needs to be created. "
            "Load the correct config for the project to know which fields are required."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "project_key": {"type": "string", "description": "EC or AVP"},
                "summary":     {"type": "string", "description": "Short, action-oriented ticket title"},
                "description": {"type": "string", "description": "Full ticket description with enough context for an engineer"},
                "fields": {
                    "type": "object",
                    "description": (
                        "Additional field values keyed by generic name. "
                        "Possible keys: issue_type, priority, assignee, parent, components, "
                        "due_date, sprint, acceptance_criteria, engagement"
                    )
                }
            },
            "required": ["project_key", "summary", "description", "fields"]
        }
    },
    {
        "name": "bulk_transition_to_todo",
        "description": (
            "Move a list of issues to 'To Do' status without sending email notifications. "
            "Confirm the issue key list with the user before calling this."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "issue_keys":  {"type": "array", "items": {"type": "string"}, "description": "e.g. ['EC-123', 'EC-124']"},
                "project_key": {"type": "string", "description": "EC or AVP"}
            },
            "required": ["issue_keys", "project_key"]
        }
    }
]


# ---------- Tool execution ----------

def execute_tool(name: str, inputs: dict) -> str:
    if name == "create_jira_ticket":
        result = create_ticket(inputs["project_key"], inputs["summary"], inputs["description"], inputs["fields"])
        return json.dumps({"created": result.get("key"), "url": f"https://appliedintuition.atlassian.net/browse/{result.get('key')}"})

    if name == "bulk_transition_to_todo":
        result = bulk_transition(inputs["issue_keys"], inputs["project_key"])
        return json.dumps({"transitioned": inputs["issue_keys"], "result": result})

    return json.dumps({"error": f"Unknown tool: {name}"})


# ---------- Agent loop ----------

def run(task: str) -> str:
    messages = [{"role": "user", "content": task}]

    while True:
        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=8096,
            system=[{"type": "text", "text": SYSTEM_PROMPT, "cache_control": {"type": "ephemeral"}}],
            tools=TOOLS,
            messages=messages,
        )

        if response.stop_reason == "end_turn":
            return next(b.text for b in response.content if hasattr(b, "text"))

        if response.stop_reason == "tool_use":
            messages.append({"role": "assistant", "content": response.content})
            tool_results = []
            for block in response.content:
                if block.type == "tool_use":
                    print(f"  [calling {block.name}]")
                    output = execute_tool(block.name, block.input)
                    tool_results.append({"type": "tool_result", "tool_use_id": block.id, "content": output})
            messages.append({"role": "user", "content": tool_results})
            continue

        break

    return ""


if __name__ == "__main__":
    print("Jira Ticket Agent — Obsidian Program")
    print("Type your request (e.g. 'Create a ticket in EC to add retry logic to the sensor pipeline')")
    print()
    task   = input("Task: ")
    result = run(task)
    print("\n--- Agent Output ---")
    print(result)
