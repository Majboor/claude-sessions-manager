#!/bin/bash
# Installer for claude-sessions-manager.
# Copies the scripts into ~/bin, builds the viewer app, installs the
# launchd agents, and adds the sessions stack + viewer to the Dock.
set -euo pipefail

REPO="$(cd "$(dirname "$0")" && pwd)"
USER_ID="$(id -un)"
PY3="$(command -v python3)"

echo "==> checking dependencies"
"$PY3" -c "import PIL, objc" 2>/dev/null || {
  echo "python3 needs Pillow and pyobjc:  pip3 install Pillow pyobjc"; exit 1; }

echo "==> installing scripts to ~/bin"
mkdir -p "$HOME/bin"
cp "$REPO/bin/claude-sessions-refresh" "$REPO/bin/claude-restore" "$REPO/bin/claude-respawn" "$REPO/bin/claude-session-edit" "$HOME/bin/"
chmod +x "$HOME/bin/claude-sessions-refresh" "$HOME/bin/claude-restore" "$HOME/bin/claude-respawn" "$HOME/bin/claude-session-edit"

echo "==> building viewer app"
APP="$HOME/Applications/Claude Sessions.app"
mkdir -p "$APP/Contents/MacOS" "$APP/Contents/Resources"
cp "$REPO/viewer/viewer.py" "$APP/Contents/Resources/"
sips -s format icns "$REPO/assets/spark.png" --out "$APP/Contents/Resources/icon.icns" >/dev/null
cat > "$APP/Contents/MacOS/run" <<EOF
#!/bin/bash
DIR="\$(cd "\$(dirname "\$0")/.." && pwd)"
exec "$PY3" "\$DIR/Resources/viewer.py"
EOF
chmod +x "$APP/Contents/MacOS/run"
cat > "$APP/Contents/Info.plist" <<'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
	<key>CFBundlePackageType</key><string>APPL</string>
	<key>CFBundleExecutable</key><string>run</string>
	<key>CFBundleIconFile</key><string>icon</string>
	<key>CFBundleIdentifier</key><string>com.claude-sessions.viewer</string>
	<key>CFBundleName</key><string>Claude Sessions</string>
	<key>NSHighResolutionCapable</key><true/>
</dict>
</plist>
EOF

echo "==> installing launchd agents"
mkdir -p "$HOME/Library/LaunchAgents"
for t in "$REPO"/launchd/*.template; do
  name="$(basename "$t" .plist.template)"
  name="${name/USER/$USER_ID}"
  dest="$HOME/Library/LaunchAgents/$name.plist"
  sed -e "s|__HOME__|$HOME|g" -e "s|__USER__|$USER_ID|g" "$t" > "$dest"
  launchctl unload "$dest" 2>/dev/null || true
  launchctl load "$dest"
done

echo "==> first refresh (builds ~/ClaudeSessions)"
"$HOME/bin/claude-sessions-refresh"

echo "==> adding to Dock"
if ! defaults read com.apple.dock persistent-others 2>/dev/null | grep -q ClaudeSessions; then
  defaults write com.apple.dock persistent-others -array-add "<dict><key>tile-data</key><dict><key>file-data</key><dict><key>_CFURLString</key><string>file://$HOME/ClaudeSessions/</string><key>_CFURLStringType</key><integer>15</integer></dict><key>file-label</key><string>Claude Sessions</string><key>file-type</key><integer>2</integer><key>displayas</key><integer>1</integer><key>showas</key><integer>2</integer><key>arrangement</key><integer>1</integer></dict><key>tile-type</key><string>directory-tile</string></dict>"
  killall Dock
fi

echo "done — click the Claude Sessions stack in your Dock."
