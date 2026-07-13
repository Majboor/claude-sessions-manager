# Session search (design)

Add a search field to the viewer app toolbar.

- Index: launcher name + project + the preview text already extracted by the
  refresh daemon (persist alongside the icon hash cache as `search-index.json`).
- Match: simple subsequence fuzzy scoring, rank by (score, recency).
- UX: results filter the grid live; Enter launches the top hit; Esc clears.
- Stretch: full-transcript grep via `rg` over ~/.claude/projects (read-only).
