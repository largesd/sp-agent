"""Utility functions for the debate system."""
import os
import re
from pathlib import Path
from typing import Any


def ensure_dir(path: str | Path) -> Path:
    """Create directory if it doesn't exist."""
    path = Path(path)
    path.mkdir(parents=True, exist_ok=True)
    return path


def read_file(path: str | Path, default: str = "") -> str:
    """Read file content, return default if not exists."""
    try:
        return Path(path).read_text(encoding="utf-8")
    except FileNotFoundError:
        return default


def write_file(path: str | Path, content: str) -> None:
    """Write content to file, creating parent directories if needed."""
    path = Path(path)
    ensure_dir(path.parent)
    path.write_text(content, encoding="utf-8")


def list_files(directory: str | Path, pattern: str = "*.md") -> list[Path]:
    """List files matching pattern in directory."""
    path = Path(directory)
    if not path.exists():
        return []
    return sorted(path.glob(pattern))


def parse_objective(content: str) -> dict[str, Any]:
    """Parse OBJECTIVE.md content into structured data."""
    result = {
        "topic": "",
        "debaters": [],
        "num_rounds": 3,
        "speaker_sequence": [],
        "words_per_speech": 1000,
        "research_rounds": 2,
    }
    
    # Extract topic
    topic_match = re.search(r"## Topic\s*\n+(.+?)(?=\n##|$)", content, re.DOTALL)
    if topic_match:
        result["topic"] = topic_match.group(1).strip()
    
    # Extract debaters from table
    # Look for table rows after "| Alias" header
    debater_pattern = r"\|\s*(\w+)\s*\|\s*([^|]+)\|\s*(\w+)\s*\|\s*([^|]+)\|"
    matches = re.findall(debater_pattern, content)
    for match in matches:
        alias, model, language, role = match
        # Skip header row if present
        if alias.lower() not in ["alias", "---", "-"]:
            result["debaters"].append({
                "alias": alias.strip(),
                "model": model.strip(),
                "language": language.strip(),
                "role": role.strip(),
            })
    
    # Extract number of rounds
    rounds_match = re.search(r"\*\*Number of Rounds\*\*:\s*(\d+)", content)
    if rounds_match:
        result["num_rounds"] = int(rounds_match.group(1))
    
    # Extract speaker sequence
    sequence_match = re.search(r"\*\*Speaker Sequence\*\*:\s*(.+)", content)
    if sequence_match:
        sequence_str = sequence_match.group(1)
        result["speaker_sequence"] = [
            s.strip() for s in re.split(r"[→,]", sequence_str)
        ]
    else:
        # Default to order of debaters
        result["speaker_sequence"] = [d["alias"] for d in result["debaters"]]
    
    # Extract words per speech
    words_match = re.search(r"\*\*Words per Speech\*\*:\s*(\d+)", content)
    if words_match:
        result["words_per_speech"] = int(words_match.group(1))
    
    # Extract research rounds
    research_match = re.search(r"\*\*Research Rounds\*\*:\s*(\d+)", content)
    if research_match:
        result["research_rounds"] = int(research_match.group(1))
    
    return result


def format_research_prompt(topic: str, round_num: int, total_rounds: int, 
                           previous_research: str = "") -> str:
    """Generate research prompt for a debater."""
    base_prompt = f"""You are conducting research for a debate on: "{topic}"

This is research round {round_num} of {total_rounds}.

Your task is to gather information, insights, and arguments that will help you 
debate this topic effectively. Focus on finding:

1. Key facts and statistics
2. Historical precedents and case studies
3. Expert opinions and research findings
4. Potential counter-arguments
5. Policy recommendations or solutions

Please organize your research in a clear, structured format with headings and bullet points.
Be thorough and cite specific examples where possible.
"""
    
    if previous_research:
        base_prompt += f"\n\n---\nYour previous research:\n{previous_research}\n---\n"
        base_prompt += "\nBuild upon your previous research. Explore new angles or dive deeper into existing areas."
    
    return base_prompt


def format_debate_prompt(topic: str, debater_alias: str, debater_role: str,
                         round_num: int, total_rounds: int, 
                         previous_speeches: list[dict], 
                         research_materials: str,
                         target_words: int = 1000) -> str:
    """Generate debate speech prompt for a debater."""
    prompt = f"""You are {debater_alias}, a {debater_role}.

DEBATE TOPIC: "{topic}"

CURRENT ROUND: {round_num} of {total_rounds}

YOUR TASK: Deliver a persuasive speech of approximately {target_words} words.

"""
    
    if research_materials:
        prompt += f"""---
YOUR RESEARCH MATERIALS:
{research_materials}
---

"""
    
    if previous_speeches:
        prompt += "PREVIOUS SPEECHES IN THIS DEBATE:\n\n"
        for speech in previous_speeches:
            prompt += f"--- {speech['round']} | {speech['speaker']} ---\n"
            prompt += f"{speech['content'][:2000]}...\n\n"  # Truncate for context
    
    prompt += f"""
SPEECH GUIDELINES:
1. Length: Approximately {target_words} words
2. Reference your research materials to support your arguments
3. Address points raised by other debaters (if applicable)
4. Present clear, logical arguments with supporting evidence
5. Maintain your character as {debater_role}
6. Be respectful but persuasive in your arguments
7. End with a strong conclusion or call to action

Write your complete speech now:
"""
    
    return prompt
