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

### Debate Structure
- **Number of Rounds**: 3
- **Speaker Sequence**: Peter → Paul → Mary (repeats each round)
- **Words per Speech**: 1000 words (approximately)

### Research Phase
- **Research Rounds**: 2 rounds per debater
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

## Output Structure
```
project/
├── agents/
│   ├── Peter/
│   │   └── research/
│   ├── Paul/
│   │   └── research/
│   └── Mary/
│       └── research/
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
