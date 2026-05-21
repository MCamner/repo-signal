# RepoAware

RepoAware builds high-signal context exports for AI systems by combining:

- repo structure
- git state
- semantic relevance
- file ranking
- focused snippets

The important part is not more context. It is better context.

## Signal Ranking Engine

RepoAware ranks files with a small transparent signal model:

| Signal | Purpose |
| --- | --- |
| filename and path matches | favor files that are likely about the question |
| keyword frequency | keep obvious textual relevance |
| git modified and recent commit signals | surface active work when useful |
| launcher/menu/core path bonuses | prioritize operational entry points |
| shell entrypoint detection | find runnable command surfaces |
| docs and file-size penalties | reduce low-signal bulk |

## Usage

<!-- markdownlint-disable MD013 -->
```bash
repo-signal repoaware --mode explain "how does dispatch work"
repo-signal repoaware --mode architect --format markdown "where is this coupled"
repo-signal repoaware --mode review --format claude "what are the risks"
repo-signal repoaware --copy "how does routing work"
```
<!-- markdownlint-enable MD013 -->

## Modes

Modes tune the context instructions without adding agent complexity:

| Mode | Focus |
| --- | --- |
| `debug` | errors, routing, stack flow, modified files |
| `explain` | clear grounded explanation |
| `architect` | structure, modularity, coupling, roadmap |
| `review` | risks, maintainability, shell pitfalls, test gaps |

## Ask

`ask` is the first AI-backed workflow:

```text
repo scan
→ ranking
→ signal selection
→ context shrinking
→ AI answer
```

```bash
repo-signal ask "how does routing work"
repo-signal ask --dry-run "how does routing work"
```

AI providers are optional adapters. The core architecture still works without
API keys, embeddings, or a vector database. Vector stores should accelerate
semantic recall later, not replace ranking and signal selection.

Install optional AI dependencies when needed:

```bash
pip install "repo-signal[ai]"
```

`repo-signal ask` reads `OPENAI_API_KEY` from the process environment or an
ignored local env file if `python-dotenv` is installed. Do not commit API keys.
