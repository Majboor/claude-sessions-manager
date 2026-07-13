# Roadmap

## In progress (feature branches)

- **`feature/session-search`** — fuzzy search bar in the viewer app: type to filter
  by project, prompt text, or transcript content; Enter resumes the top hit.
- **`feature/menubar-widget`** — menu-bar item showing a live count of ⚡ generating /
  🟢 waiting sessions, with a dropdown to jump to any of them.
- **`feature/raycast-extension`** — Raycast command listing sessions with the same
  previews, resume on Enter.

## Planned

- **Quick Look plugin** — press Space on a launcher in Finder and get the scrollable
  full transcript, not just the icon.
- **iCloud-synced tags** — share `session-projects.json` across Macs.
- **Session archiving** — move old launchers into an Archive folder after N days
  (transcripts are of course untouched).
- **Multi-terminal support** — iTerm2 / Ghostty / Warp as resume targets, not just
  Terminal.app.
- **Preview themes** — light mode, custom fonts, and accent colors for the rendered
  terminal icons.

## Done

- ✅ Dock stack of resumable session launchers
- ✅ Terminal-preview icons rendered from live transcripts
- ✅ ⚡/🟢 live status detection
- ✅ Hover-to-enlarge viewer app
- ✅ Rule-based project categorization
- ✅ Respawn running sessions after reboot
- ✅ Two-level layout (All Sessions + Projects) with custom folder icons
- ✅ In-grid actions: New Session, Resume Active, Edit Sessions (re-tagging)
