import os
import anthropic
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()

client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

SYSTEM_PROMPT = Path("system_prompt.md").read_text()

# TODO: add tools here if this agent needs to take actions
# (e.g., read files, call APIs, search the web)
TOOLS = []


def run(task: str) -> str:
    """Run the agent on a single task and return its final response."""
    messages = [{"role": "user", "content": task}]

    while True:
        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=8096,
            system=[
                {
                    "type": "text",
                    "text": SYSTEM_PROMPT,
                    "cache_control": {"type": "ephemeral"},  # caches the system prompt
                }
            ],
            tools=TOOLS if TOOLS else [],
            messages=messages,
        )

        # If no tool calls, the agent is done — return its text response
        if response.stop_reason == "end_turn":
            return next(b.text for b in response.content if hasattr(b, "text"))

        # TODO: handle tool calls here when you add tools
        # For now, append the response and break
        messages.append({"role": "assistant", "content": response.content})
        break

    return ""


if __name__ == "__main__":
    # TODO: replace this with however you want to feed tasks to the agent
    # (e.g., read from a file, accept a CLI argument, pull from a queue)
    task = input("Task: ")
    result = run(task)
    print("\n--- Agent Output ---")
    print(result)
