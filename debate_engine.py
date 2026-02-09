"""Debate engine that orchestrates the multi-agent debate."""
from pathlib import Path
from typing import Any

from agent import Agent
from utils import ensure_dir, write_file, read_file, parse_objective


class DebateEngine:
    """Orchestrates the multi-agent debate."""

    def __init__(self, objective_path: str = "OBJECTIVE.md", base_path: str = "."):
        """Initialize the debate engine.

        Args:
            objective_path: Path to the OBJECTIVE.md file
            base_path: Base directory for the project
        """
        self.base_path = Path(base_path)
        self.objective_path = Path(objective_path)

        # Parse objective
        objective_content = read_file(self.objective_path)
        if not objective_content:
            raise FileNotFoundError(f"Objective file not found: {self.objective_path}")

        self.config = parse_objective(objective_content)
        print(f"📋 Loaded objective: {self.config['topic'][:60]}...")
        print(f"   Debaters: {', '.join(d['alias'] for d in self.config['debaters'])}")
        print(f"   Rounds: {self.config['num_rounds']}")
        print(f"   Research rounds: {self.config['research_rounds']}")

        # Setup directories
        self.agents_dir = self.base_path / "agents"
        self.speeches_dir = self.base_path / "speeches"
        ensure_dir(self.agents_dir)
        ensure_dir(self.speeches_dir)

        # Initialize agents
        self.agents: dict[str, Agent] = {}
        for debater_config in self.config["debaters"]:
            agent = Agent(
                alias=debater_config["alias"],
                model=debater_config["model"],
                language=debater_config["language"],
                role=debater_config["role"],
                base_path=str(self.base_path),
            )
            self.agents[debater_config["alias"]] = agent

        # Validate speaker sequence
        self.speaker_sequence = self.config["speaker_sequence"]
        for speaker in self.speaker_sequence:
            if speaker not in self.agents:
                raise ValueError(f"Speaker '{speaker}' in sequence not found in debaters")

    def run_research_phase(self) -> None:
        """Run the research phase for all agents."""
        print(f"\n🔍 RESEARCH PHASE")
        print("=" * 50)

        topic = self.config["topic"]
        total_rounds = self.config["research_rounds"]

        for round_num in range(1, total_rounds + 1):
            print(f"\n📚 Research Round {round_num}/{total_rounds}")
            print("-" * 30)

            for alias in self.speaker_sequence:
                agent = self.agents[alias]
                agent.research(
                    topic=topic,
                    round_num=round_num,
                    total_rounds=total_rounds,
                )

        print(f"\n✅ Research phase complete!")

    def run_debate_phase(self) -> None:
        """Run the debate phase."""
        print(f"\n🎤 DEBATE PHASE")
        print("=" * 50)

        topic = self.config["topic"]
        total_rounds = self.config["num_rounds"]

        for round_num in range(1, total_rounds + 1):
            print(f"\n🗣️  Debate Round {round_num}/{total_rounds}")
            print("-" * 30)

            # Create round directory
            round_dir = self.speeches_dir / f"round_{round_num}"
            ensure_dir(round_dir)

            for alias in self.speaker_sequence:
                agent = self.agents[alias]

                # Get agent's research
                research = agent.get_all_research()

                # Generate speech
                speech = agent.speak(
                    topic=topic,
                    round_num=round_num,
                    total_rounds=total_rounds,
                    speeches_dir=self.speeches_dir,
                    all_research=research,
                )

                # Save speech
                speech_file = round_dir / f"{alias}_speech.md"
                speech_content = f"""# {alias}'s Speech - Round {round_num}

**Role**: {agent.role}
**Model**: {agent.model}

---

{speech}
"""
                write_file(speech_file, speech_content)
                print(f"     💾 Saved to: {speech_file}")

        print(f"\n✅ Debate phase complete!")

    def generate_summary(self) -> None:
        """Generate a summary of the debate."""
        print(f"\n📝 Generating debate summary...")

        summary_path = self.base_path / "DEBATE_SUMMARY.md"

        content = f"""# Debate Summary: {self.config['topic']}

## Configuration

| Setting | Value |
|---------|-------|
| Topic | {self.config['topic']} |
| Total Rounds | {self.config['num_rounds']} |
| Research Rounds | {self.config['research_rounds']} |
| Words per Speech | {self.config['words_per_speech']} |

## Debaters

"""

        for debater in self.config["debaters"]:
            content += f"""### {debater['alias']}
- **Model**: {debater['model']}
- **Role**: {debater['role']}
- **Language**: {debater['language']}

"""

        content += """## Speeches

"""

        for round_num in range(1, self.config['num_rounds'] + 1):
            content += f"### Round {round_num}\n\n"
            round_dir = self.speeches_dir / f"round_{round_num}"
            if round_dir.exists():
                for speech_file in sorted(round_dir.glob("*_speech.md")):
                    alias = speech_file.stem.replace("_speech", "")
                    content += f"- [{alias}](speeches/round_{round_num}/{speech_file.name})\n"
            content += "\n"

        content += """## Research Materials

"""

        for alias in self.speaker_sequence:
            agent = self.agents[alias]
            research_dir = agent.research_dir
            if research_dir.exists():
                content += f"### {alias}\n\n"
                for research_file in sorted(research_dir.glob("*.md")):
                    content += f"- [{research_file.stem}](agents/{alias}/research/{research_file.name})\n"
                content += "\n"

        write_file(summary_path, content)
        print(f"     💾 Summary saved to: {summary_path}")

    def run(self) -> None:
        """Run the complete debate workflow."""
        print("\n" + "=" * 60)
        print("   🏛️  MULTI-AGENT DEBATE SYSTEM")
        print("=" * 60)

        # Phase 1: Research
        self.run_research_phase()

        # Phase 2: Debate
        self.run_debate_phase()

        # Generate summary
        self.generate_summary()

        print("\n" + "=" * 60)
        print("   ✅ DEBATE COMPLETE!")
        print("=" * 60)
        print(f"\nCheck the following locations:")
        print(f"   - Speeches: {self.speeches_dir}/")
        print(f"   - Research: {self.agents_dir}/<agent>/research/")
        print(f"   - Summary: {self.base_path}/DEBATE_SUMMARY.md")
