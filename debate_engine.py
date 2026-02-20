"""Debate engine that orchestrates the multi-agent debate."""
from pathlib import Path
from typing import Any

from agent import Agent
from utils import ensure_dir, write_file, read_file, parse_objective, list_files


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

        # Initialize proposal agent if configured
        self.proposal_agent: Agent | None = None
        if self.config.get("proposal_agent"):
            proposal_config = self.config["proposal_agent"]
            self.proposal_agent = Agent(
                alias=proposal_config["alias"],
                model=proposal_config["model"],
                language=proposal_config["language"],
                role=proposal_config["role"],
                base_path=str(self.base_path),
            )
            self.proposal_words_limit = proposal_config.get("words_limit", 3000)
            print(f"   Proposal Agent: {proposal_config['alias']} ({proposal_config['model']})")

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

    def run_proposal_phase(self) -> None:
        """Run the proposal phase to synthesize the debate outcomes."""
        if not self.proposal_agent:
            print("\n⏭️  No proposal agent configured. Skipping proposal phase.")
            return

        print(f"\n📄 PROPOSAL PHASE")
        print("=" * 50)
        print(f"   Proposal Agent: {self.proposal_agent.alias}")
        print(f"   Model: {self.proposal_agent.model}")

        # Collect all research materials from all debaters
        all_research = []
        for alias in self.speaker_sequence:
            agent = self.agents[alias]
            research_files = list_files(agent.research_dir, "*.md")
            for research_file in research_files:
                content = read_file(research_file)
                all_research.append(f"## Research by {alias}: {research_file.stem}\n\n{content}")

        # Collect all speeches from all rounds
        all_speeches = []
        for round_num in range(1, self.config["num_rounds"] + 1):
            round_dir = self.speeches_dir / f"round_{round_num}"
            if round_dir.exists():
                for speech_file in sorted(round_dir.glob("*_speech.md")):
                    alias = speech_file.stem.replace("_speech", "")
                    content = read_file(speech_file)
                    all_speeches.append(f"## {alias}'s Speech - Round {round_num}\n\n{content}")

        # Generate proposal
        from utils import format_proposal_prompt
        prompt = format_proposal_prompt(
            topic=self.config["topic"],
            research_materials="\n\n".join(all_research),
            speeches="\n\n".join(all_speeches),
            words_limit=self.proposal_words_limit,
        )

        system_prompt = f"""You are {self.proposal_agent.alias}, a {self.proposal_agent.role}.
You must synthesize all the research and debate speeches into a comprehensive, objective proposal.
Respond in {self.proposal_agent.language}.
Be neutral, balanced, and base your proposal solely on the evidence presented."""

        print(f"\n📝 Generating proposal...")
        proposal_content = self.proposal_agent._call_llm(prompt, system_prompt)

        # Save proposal
        proposal_dir = self.agents_dir / "Proposal"
        ensure_dir(proposal_dir)
        proposal_file = proposal_dir / "proposal.md"
        
        full_proposal = f"""# {self.config["topic"]}

**Proposal by**: {self.proposal_agent.alias}
**Role**: {self.proposal_agent.role}
**Model**: {self.proposal_agent.model}

---

{proposal_content}
"""
        write_file(proposal_file, full_proposal)
        print(f"     💾 Proposal saved to: {proposal_file}")
        print(f"\n✅ Proposal phase complete!")

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

        # Add proposal section if exists
        if self.proposal_agent:
            proposal_file = self.agents_dir / "Proposal" / "proposal.md"
            if proposal_file.exists():
                content += """## Final Proposal

"""
                content += f"- [Proposal by {self.proposal_agent.alias}](agents/Proposal/proposal.md)\n\n"

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

        # Phase 3: Proposal
        self.run_proposal_phase()

        # Generate summary
        self.generate_summary()

        print("\n" + "=" * 60)
        print("   ✅ DEBATE COMPLETE!")
        print("=" * 60)
        print(f"\nCheck the following locations:")
        print(f"   - Speeches: {self.speeches_dir}/")
        print(f"   - Research: {self.agents_dir}/<agent>/research/")
        if self.proposal_agent:
            print(f"   - Proposal: {self.agents_dir}/Proposal/proposal.md")
        print(f"   - Summary: {self.base_path}/DEBATE_SUMMARY.md")
