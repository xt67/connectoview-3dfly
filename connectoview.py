"""Backward-compatible entry point — canonical implementation lives in src/connectoview.py."""
from src.connectoview import cli

if __name__ == "__main__":
    raise SystemExit(cli())
