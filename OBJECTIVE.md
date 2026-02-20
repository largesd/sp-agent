# Debate Objective: Post-AI Era Mass Unemployment

## Topic
How to solve the potential problem of mass unemployment in the post-AI era?

## Debate Configuration

### Debaters
| Alias  | Model Name                | Language | Role/Expertise                      |
|--------|---------------------------|----------|-------------------------------------|
| Peter  | deepseek/deepseek-v3.2    | English  | Economist / Policy Maker            |
| Paul   | moonshotai/kimi-k2.5      | English  | Technologist / Entrepreneur         |
| Mary   | qwen/qwen3-max            | English  | Sociologist / Labor Rights Advocate |

### Proposal Agent
| Alias    | Model Name              | Words Limit | Role/Expertise                           |
|----------|-------------------------|-------------|------------------------------------------|
| Proposal | qwen/qwen3-max          | 3000        | Objective Synthesizer / Solution Drafter |

**Proposal Agent Responsibilities:**
- Study all research materials from debaters (`agents/{alias}/research/`)
- Analyze all debate speeches (`speeches/round_{n}/`)
- Synthesize a comprehensive, objective proposal to solve the problem
- Remain neutral without personal preference or bias toward any debater
- Base the proposal solely on the materials presented in the debate

### Debate Structure
- **Number of Rounds**: 3
- **Speaker Sequence**: Peter → Paul → Mary
- **Words per Speech**: 1000 words (approximately)

### Research Phase
- **Research Rounds**: 2 round per debater
- Each debater conducts independent research before the debate begins
- Research materials are stored in each debater's own folder for reference during speeches

## Workflow

### Phase 1: Research (Pre-Debate)
1. Each debater spends 2 rounds researching the topic
2. Research focuses on:
   - Historical precedents of technological unemployment
   - Policy solutions (UBI, retraining programs, etc.)
   - Technological trends and projections
   - Social and ethical implications
3. All research is saved to `agents/{alias}/research/` folder

### Phase 2: Debate (3 Rounds)
1. Each round, debaters speak in sequence: Peter → Paul → Mary
2. Before each speech, the debater can read:
   - All previous speeches from other debaters (`speeches/round_{n}/`)
   - Their own research materials (`agents/{alias}/research/`)
3. Each speech is saved to `speeches/round_{n}/{alias}_speech.md`

### Phase 3: Proposal (Post-Debate)
1. The Proposal agent reviews:
   - All research materials from all debaters (`agents/{alias}/research/`)
   - All debate speeches across all rounds (`speeches/round_{n}/`)
2. The Proposal agent synthesizes an objective proposal that:
   - Addresses the problem based on evidence presented in the debate
   - Incorporates valid points from all debaters
   - Provides concrete, actionable recommendations
   - Maintains neutrality without favoring any particular debater
3. The final proposal is saved to `agents/Proposal/proposal.md`

## Output Structure
```
project/
├── agents/
│   ├── Peter/
│   │   └── research/
│   ├── Paul/
│   │   └── research/
│   ├── Mary/
│   │   └── research/
│   └── Proposal/
│       └── proposal.md
└── speeches/
    ├── round_1/
    ├── round_2/
    └── round_3/
```

## Constraints
- All content must be human-readable and well-organized
- Debaters should reference their research when making arguments
- Debaters should respond to points raised by other debaters
- Keep track of all API calls and token usage
