# MCP Security Scanner

Testing how well AI models resist tool poisoning attacks through MCP

## What This Is

MCP tools can have their descriptions tampered with to try to manipulate an AI into doing things it shouldnt. this project tests whether that actually works.

## Files

- `test_tool_poisoning.py` - Basic version, manually label each result yourself
- `real_world_tests.py` - More advanced, uses a second AI call to auto-judge results and saves everything to a csv

## Setup

```
pip install -r requirements.txt
```

make a `.env` file with your key:
```
ANTHROPIC_API_KEY=your_key_here
```

## Status

Still a work in progress, plan to add more attack types and maybe a proper scoring breakdown later
