# [Agent Name]

[One sentence describing what this agent does.]

## What it does

[2-3 sentences. What task does it handle? What does it produce?]

## Setup

1. Clone this repo
2. Copy `.env.example` to `.env` and add your Anthropic API key
3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

## Run

```
python main.py
```

## Customize

- **Behavior and standards**: edit `system_prompt.md`
- **Tools / actions the agent can take**: edit the `TOOLS` list in `main.py`
- **How tasks are fed in**: edit the `__main__` block at the bottom of `main.py`
