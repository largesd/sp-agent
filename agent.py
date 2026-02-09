"""Agent class for debate participants."""
import os
from pathlib import Path
from typing import Iterator
from openai import OpenAI
from dotenv import load_dotenv

from utils import read_file, write_file, list_files, ensure_dir

# Load environment variables
load_dotenv()


class Agent:
    """A debate agent that can research and speak."""

    def __init__(self, alias: str, model: str, language: str, role: str,
                 base_path: str = "."):
        """Initialize an agent.

        Args:
            alias: The agent's name/identifier
            model: The LLM model name on OpenRouter
            language: Language for responses
            role: The agent's expertise/role
            base_path: Base directory for agent files
        """
        self.alias = alias
        self.model = model
        self.language = language
        self.role = role
        self.base_path = Path(base_path)

        # Setup paths
        self.agent_dir = self.base_path / "agents" / alias
        self.research_dir = self.agent_dir / "research"
        ensure_dir(self.research_dir)

        # Initialize OpenAI client (configured for OpenRouter)
        api_key = os.getenv("OPENROUTER_API_KEY")
        base_url = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")

        if not api_key:
            raise ValueError("OPENROUTER_API_KEY not found in environment variables")

        self.client = OpenAI(
            base_url=base_url,
            api_key=api_key,
        )

        # Optional: Site info for OpenRouter rankings
        self.site_url = os.getenv("SITE_URL", "")
        self.site_name = os.getenv("SITE_NAME", "Multi-Agent Debate System")

    def _call_llm(self, prompt: str, system_prompt: str = "") -> str:
        """Call the LLM with the given prompt."""
        messages = []

        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})

        messages.append({"role": "user", "content": prompt})

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                extra_headers={
                    "HTTP-Referer": self.site_url,
                    "X-Title": self.site_name,
                },
                temperature=0.7,
                max_tokens=4000,
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Error calling LLM: {str(e)}"

    def research(self, topic: str, round_num: int, total_rounds: int) -> str:
        """Conduct research on the debate topic.

        Args:
            topic: The debate topic
            round_num: Current research round
            total_rounds: Total number of research rounds

        Returns:
            The research content
        """
        # Read previous research if exists
        previous_research = ""
        if round_num > 1:
            prev_files = list_files(self.research_dir, f"round_{round_num - 1}_*.md")
            if prev_files:
                previous_research = read_file(prev_files[-1])

        # Generate research prompt
        system_prompt = f"""You are {self.alias}, a {self.role}.
You are conducting research for an upcoming debate.
Respond in {self.language}.
Be thorough, analytical, and organize information clearly with markdown formatting."""

        from utils import format_research_prompt
        prompt = format_research_prompt(topic, round_num, total_rounds, previous_research)

        print(f"  [Research] {self.alias} - Round {round_num}/{total_rounds}")

        # Call LLM
        research_content = self._call_llm(prompt, system_prompt)

        # Save research
        filename = f"round_{round_num}_research.md"
        filepath = self.research_dir / filename
        write_file(filepath, research_content)

        return research_content

    def speak(self, topic: str, round_num: int, total_rounds: int,
              speeches_dir: Path, all_research: str = "") -> str:
        """Deliver a speech in the debate.

        Args:
            topic: The debate topic
            round_num: Current debate round
            total_rounds: Total number of debate rounds
            speeches_dir: Directory containing all speeches
            all_research: Combined research materials

        Returns:
            The speech content
        """
        # Read previous speeches
        previous_speeches = []
        for r in range(1, round_num + 1):
            round_dir = speeches_dir / f"round_{r}"
            if round_dir.exists():
                for speech_file in sorted(round_dir.glob("*_speech.md")):
                    if speech_file.stem != f"{self.alias}_speech":
                        speaker = speech_file.stem.replace("_speech", "")
                        content = read_file(speech_file)
                        previous_speeches.append({
                            "round": f"Round {r}",
                            "speaker": speaker,
                            "content": content,
                        })

        # Generate debate prompt
        system_prompt = f"""You are {self.alias}, a {self.role}.
You are participating in a formal debate.
Respond in {self.language}.
Be persuasive, logical, and respectful. Use markdown formatting for your speech."""

        from utils import format_debate_prompt
        prompt = format_debate_prompt(
            topic=topic,
            debater_alias=self.alias,
            debater_role=self.role,
            round_num=round_num,
            total_rounds=total_rounds,
            previous_speeches=previous_speeches,
            research_materials=all_research,
            target_words=1000,
        )

        print(f"  [Speech] {self.alias} - Round {round_num}/{total_rounds}")

        # Call LLM
        speech_content = self._call_llm(prompt, system_prompt)

        return speech_content

    def get_all_research(self) -> str:
        """Get all research materials as a single string."""
        research_files = list_files(self.research_dir, "*.md")
        contents = []
        for f in research_files:
            content = read_file(f)
            contents.append(f"## {f.stem}\n\n{content}")
        return "\n\n".join(contents)
