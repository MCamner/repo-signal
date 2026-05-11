# Wiki Generator Spec

## Goal

The wiki generator should turn repository state into useful GitHub Wiki pages.

It should help answer:

- What wiki pages should this repo have?
- Which pages already exist?
- Which pages are missing?
- Which pages need refresh?
- What content should be generated safely?

## Target Commands

```bash
repo-signal wiki plan .
repo-signal wiki export . --output docs/wiki-export
```

## Phase 3 Target Pages

Minimum generated pages:

- `Home.md`
- `Getting-Started.md`
- `Command-Reference.md`
- `Architecture.md`
- `Roadmap.md`
- `Release-Flow.md`
- `Skills.md`
- `Troubleshooting.md`

## Wiki Plan Output

`repo-signal wiki plan .` should print:

- detected project type
- recommended wiki pages
- existing wiki/doc pages if available
- missing pages
- recommended next page to create

## Wiki Export Output

`repo-signal wiki export . --output docs/wiki-export` should write Markdown
files:

```text
docs/wiki-export/
├── Home.md
├── Getting-Started.md
├── Command-Reference.md
├── Architecture.md
├── Roadmap.md
├── Release-Flow.md
├── Skills.md
└── Troubleshooting.md
```

## Safety Rules

The generator must not:

- push to GitHub automatically
- overwrite wiki pages without explicit action
- include API keys
- include local secrets
- include private paths unless already present in public docs

## Done When

- [ ] `repo-signal wiki plan .` works
- [ ] `repo-signal wiki export . --output docs/wiki-export` works
- [ ] generated files are safe to review before publishing
- [ ] README mentions wiki generator commands
- [ ] Roadmap marks Phase 3 as done or mostly done
