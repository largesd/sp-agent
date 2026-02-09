# Multi-Agent Debate System

A multi-agent debate system built with `kimi-cli` that simulates a structured debate on social issues using multiple LLM models via OpenRouter API.

## Features

- **Multi-Model Support**: Use different LLM models for each debater
- **Research Phase**: Debaters conduct pre-debate research and store findings
- **Structured Debate**: Configurable rounds with defined speaker sequences
- **Human-Readable Output**: All speeches and research saved as markdown files
- **Context Awareness**: Debaters can read previous speeches and their own research

## Prerequisites

- Python 3.12+
- Conda (recommended for environment management)
- OpenRouter API key

## Setup

### 1. Create Conda Environment

```bash
conda create -n sp-agent python=3.12
conda activate sp-agent
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment

Copy the example environment file and fill in your API credentials:

```bash
cp .env.example .env
```

Edit `.env` with your OpenRouter API key:

```env
OPENROUTER_API_KEY=your_api_key_here
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
```

Get your API key from [OpenRouter](https://openrouter.ai/keys).

### 4. Customize the Debate (Optional)

Edit `OBJECTIVE.md` to customize:
- Debate topic
- Number of debaters and their models
- Number of rounds
- Speech length
- Research rounds

## Usage

Run the debate:

```bash
python main.py
```

The system will:
1. Read the objective from `OBJECTIVE.md`
2. Create necessary folders
3. Run the research phase (each debater researches independently)
4. Run the debate phase (each debater speaks in sequence)
5. Save all outputs to organized folders

## Project Structure

```
.
├── OBJECTIVE.md          # Debate configuration and rules
├── README.md             # This file
├── .env                  # API keys (gitignored)
├── .env.example          # Example environment file
├── .gitignore            # Git ignore rules
├── requirements.txt      # Python dependencies
├── main.py               # Main entry point
├── agent.py              # Agent class definition
├── debate_engine.py      # Debate orchestration logic
└── utils.py              # Helper functions

├── agents/               # Agent data (created at runtime)
│   ├── Peter/
│   │   └── research/     # Peter's research materials
│   ├── Paul/
│   │   └── research/
│   └── Mary/
│       └── research/

└── speeches/             # Debate speeches (created at runtime)
    ├── round_1/
    ├── round_2/
    └── round_3/
```

## Configuration

### OBJECTIVE.md

Define the debate parameters:

```markdown
## Topic
Your debate topic here

## Debate Configuration

### Debaters
| Alias  | Model Name             | Language | Role/Expertise       |
|--------|------------------------|----------|----------------------|
| Peter  | deepseek/deepseek-v3.2 | English  | Economist            |

### Debate Structure
- **Number of Rounds**: 3
- **Speaker Sequence**: Peter → Paul → Mary
- **Words per Speech**: 1000 words

### Research Phase
- **Research Rounds**: 2 rounds per debater
```

### Environment Variables (.env)

| Variable              | Description             |
|-----------------------|-------------------------|
| `OPENROUTER_API_KEY`  | Your OpenRouter API key |
| `OPENROUTER_BASE_URL` | OpenRouter API base URL |

## Example Output

After running, you'll find:

```
agents/Peter/research/
├── round_1_historical_precedents.md
└── round_2_policy_solutions.md

speeches/round_1/
├── Peter_speech.md
├── Paul_speech.md
└── Mary_speech.md
```

## Extending the System

### Adding More Debaters

1. Add a new row to the debaters table in `OBJECTIVE.md`
2. Run `python main.py` again

### Changing Models

Use any model available on OpenRouter:
- See [OpenRouter Models](https://openrouter.ai/models) for full list
