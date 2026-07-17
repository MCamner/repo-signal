# Suggested Repository Structure

`repo-signal` encourages a clear, discoverable repository structure. Here is a
recommended layout for a CLI project:

```text
repo-signal/
├── README.md
├── LICENSE
├── .gitignore
├── bin/
│   └── repo-signal
├── repo_signal/
│   ├── __init__.py
│   ├── cli.py
│   ├── scanner.py
│   ├── rules.py
│   ├── report.py
│   ├── prompts.py
│   └── patcher.py
├── examples/
│   └── sample-report.md
└── docs/
    └── index.html
```

## Why this structure?

1. **Top-level clarity:** README and LICENSE are at the front door.
2. **Executable bin:** A dedicated `bin/` folder for the main entry point.
3. **Namespaced code:** All library code lives in a folder named after the project.
4. **Evidence:** `examples/` show what the tool actually does.
5. **Documentation:** `docs/` for deeper manuals or GitHub Pages.
