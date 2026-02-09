#!/usr/bin/env python3
"""Main entry point for the multi-agent debate system."""

import sys
from pathlib import Path

# Add current directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from debate_engine import DebateEngine


def main():
    """Run the debate."""
    try:
        engine = DebateEngine(
            objective_path="OBJECTIVE.md",
            base_path=".",
        )
        engine.run()
    except FileNotFoundError as e:
        print(f"❌ Error: {e}")
        print("Please ensure OBJECTIVE.md exists in the current directory.")
        sys.exit(1)
    except ValueError as e:
        print(f"❌ Configuration Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected Error: {e}")
        raise


if __name__ == "__main__":
    main()
