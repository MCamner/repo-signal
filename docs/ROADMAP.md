# Roadmap

repo-signal is a local-first repository intelligence tool for turning rough
prototypes into clear, documented, publishable GitHub projects.

## Current focus

Prepare v0.1.7 as a publish checklist CI threshold release.

## v0.1.7 - Publish Checklist CI Threshold

### Quality Gate

- [x] Add `repo-signal publish-checklist . --fail-under <score>`.
- [x] Preserve report output for passing and failing thresholds.
- [x] Support JSON output with fail-under exit codes.
- [x] Cover pass, fail, and invalid threshold values in tests.

## v0.1.6 - Wiki Generator

### Phase 3 - Wiki Generator (mostly done)

- [x] Add `repo-signal wiki plan .`.
- [x] Add `repo-signal wiki export . --output docs/wiki-export`.
- [x] Generate reviewable wiki Markdown files.
- [ ] Add safer refresh/diff behavior for existing wiki pages.
- [ ] Document manual publish flow for copying exports into GitHub Wiki.

## v0.1.4 - Publish Readiness Hardening

### Publish Checklist

- [x] Add `publish-checklist` command.
- [x] Add grouped scoring output.
- [x] Add recommended next action per missing area.
- [x] Add JSON output mode.
- [x] Add Markdown output mode.
- [x] Add examples from real repos.

### Documentation

- [ ] Document `publish-checklist` in README.
- [x] Add example output for `design-prototyp`.
- [x] Add example output for `macos-scripts`.
- [ ] Add command reference page.
- [ ] Add screenshots or terminal output captures.

### Repo Quality

- [x] Add issue templates.
- [x] Add screenshots folder.
- [x] Add roadmap link from README.
- [x] Ensure tests cover publish checklist behavior.

## Later Ideas

- GitHub Pages detection improvements.
- Project type detection.
- Script/tool discovery.
- Wiki suggestion generator.
- Roadmap suggestion generator.
- Positioning report.
- Safe patch suggestions.
