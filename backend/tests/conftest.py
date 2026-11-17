import os

# Tests must never invoke a live provider, even if a shell key is present.
os.environ["ANTHROPIC_API_KEY"] = ""
os.environ["CLAUDE_MODEL"] = ""
