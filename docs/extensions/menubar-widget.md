# Menu-bar widget (design)

NSStatusItem showing "⚡2 🟢3" counts, sourced from
~/.claude/active-sessions-state.txt (already written every 60s by the daemon).

- Dropdown lists active sessions with project + last-output snippet.
- Click an entry -> focus its Terminal window (match by tty via lsof) or
  relaunch if the window is gone.
- Optional notification when a ⚡ session flips to 🟢 (Claude finished).
