#!/usr/bin/env python3
"""Claude Sessions viewer — grid of session previews with hover-to-enlarge.

Reads the .app launchers that claude-sessions-refresh maintains in
~/ClaudeSessions; hovering a tile shows the full 512px terminal preview,
clicking launches the session in Terminal.
"""
import subprocess
from pathlib import Path

import objc
from AppKit import (
    NSApplication, NSApplicationActivationPolicyRegular, NSBackingStoreBuffered,
    NSBorderlessWindowMask, NSColor, NSFloatingWindowLevel, NSFont, NSImage,
    NSImageView, NSMakeRect, NSObject, NSPanel, NSScreen, NSScrollView,
    NSTextField, NSTimer, NSTrackingActiveAlways, NSTrackingArea,
    NSTrackingInVisibleRect, NSTrackingMouseEnteredAndExited, NSView, NSWindow,
    NSWindowStyleMaskClosable, NSWindowStyleMaskMiniaturizable,
    NSWindowStyleMaskResizable, NSWindowStyleMaskTitled,
)
from Foundation import NSMakePoint, NSMakeSize

SESSIONS = Path.home() / "ClaudeSessions"
CELL_W, CELL_H, PAD = 150, 176, 14
COLS = 6
PREVIEW = 640


class SessionCell(NSView):
    def initWithFrame_app_owner_(self, frame, app_path, owner):
        self = objc.super(SessionCell, self).initWithFrame_(frame)
        if self is None:
            return None
        self.app_path = app_path
        self.owner = owner
        icns = app_path / "Contents" / "Resources" / "icon.icns"
        self.image = NSImage.alloc().initWithContentsOfFile_(str(icns))
        detail = app_path / "Contents" / "Resources" / "preview.png"
        self.detail = (NSImage.alloc().initWithContentsOfFile_(str(detail))
                       if detail.exists() else None) or self.image
        iv = NSImageView.alloc().initWithFrame_(NSMakeRect(5, 36, CELL_W - 10, CELL_H - 44))
        iv.setImage_(self.image)
        self.addSubview_(iv)
        label = NSTextField.alloc().initWithFrame_(NSMakeRect(2, 0, CELL_W - 4, 34))
        parent = app_path.parent
        prefix = f"[{parent.name}] " if parent != SESSIONS else ""
        label.setStringValue_(prefix + app_path.stem)
        label.setEditable_(False)
        label.setBordered_(False)
        label.setDrawsBackground_(False)
        label.setFont_(NSFont.systemFontOfSize_(10))
        label.setTextColor_(NSColor.secondaryLabelColor())
        label.setLineBreakMode_(5)  # truncate middle
        label.cell().setWraps_(True)
        self.addSubview_(label)
        ta = NSTrackingArea.alloc().initWithRect_options_owner_userInfo_(
            self.bounds(),
            NSTrackingMouseEnteredAndExited | NSTrackingActiveAlways | NSTrackingInVisibleRect,
            self, None)
        self.addTrackingArea_(ta)
        return self

    def mouseEntered_(self, event):
        self.owner.showPreviewFor_(self)

    def mouseExited_(self, event):
        self.owner.hidePreview()

    def mouseDown_(self, event):
        subprocess.Popen(["open", str(self.app_path)])
        self.owner.hidePreview()


class AppDelegate(NSObject):
    def applicationDidFinishLaunching_(self, note):
        mask = (NSWindowStyleMaskTitled | NSWindowStyleMaskClosable |
                NSWindowStyleMaskResizable | NSWindowStyleMaskMiniaturizable)
        w = COLS * (CELL_W + PAD) + PAD + 16
        self.window = NSWindow.alloc().initWithContentRect_styleMask_backing_defer_(
            NSMakeRect(120, 120, w, 660), mask, NSBackingStoreBuffered, False)
        self.window.setTitle_("Claude Sessions")
        self.window.setReleasedWhenClosed_(False)
        self.scroll = NSScrollView.alloc().initWithFrame_(self.window.contentView().bounds())
        self.scroll.setHasVerticalScroller_(True)
        self.scroll.setAutoresizingMask_(18)  # width + height sizable
        self.window.contentView().addSubview_(self.scroll)

        self.preview_panel = NSPanel.alloc().initWithContentRect_styleMask_backing_defer_(
            NSMakeRect(0, 0, PREVIEW, PREVIEW), NSBorderlessWindowMask,
            NSBackingStoreBuffered, False)
        self.preview_panel.setLevel_(NSFloatingWindowLevel)
        self.preview_panel.setOpaque_(False)
        self.preview_panel.setBackgroundColor_(NSColor.clearColor())
        self.preview_panel.setIgnoresMouseEvents_(True)
        self.preview_iv = NSImageView.alloc().initWithFrame_(
            NSMakeRect(0, 0, PREVIEW, PREVIEW))
        self.preview_panel.contentView().addSubview_(self.preview_iv)

        self.known = None
        self.reload_(None)
        NSTimer.scheduledTimerWithTimeInterval_target_selector_userInfo_repeats_(
            30.0, self, "reload:", None, True)
        self.window.makeKeyAndOrderFront_(None)
        NSApplication.sharedApplication().activateIgnoringOtherApps_(True)

    def reload_(self, timer):
        apps = sorted(SESSIONS.glob("*.app")) + sorted(
            SESSIONS.glob("*/*.app"), key=lambda p: (p.parent.name, p.name))
        sig = [(p.name, (p / "Contents" / "Resources" / "icon.icns").stat().st_mtime
                if (p / "Contents" / "Resources" / "icon.icns").exists() else 0)
               for p in apps]
        if sig == self.known:
            return
        self.known = sig
        rows = (len(apps) + COLS - 1) // COLS
        height = max(rows * (CELL_H + PAD) + PAD, 200)
        width = COLS * (CELL_W + PAD) + PAD
        doc = NSView.alloc().initWithFrame_(NSMakeRect(0, 0, width, height))
        for i, app in enumerate(apps):
            r, c = divmod(i, COLS)
            x = PAD + c * (CELL_W + PAD)
            y = height - (r + 1) * (CELL_H + PAD)
            cell = SessionCell.alloc().initWithFrame_app_owner_(
                NSMakeRect(x, y, CELL_W, CELL_H), app, self)
            doc.addSubview_(cell)
        self.scroll.setDocumentView_(doc)

    def showPreviewFor_(self, cell):
        if cell.detail is None:
            return
        self.preview_iv.setImage_(cell.detail)
        rect = cell.window().convertRectToScreen_(
            cell.convertRect_toView_(cell.bounds(), None))
        screen = NSScreen.mainScreen().visibleFrame()
        x = rect.origin.x + CELL_W + 8
        if x + PREVIEW > screen.origin.x + screen.size.width:
            x = rect.origin.x - PREVIEW - 8
        y = min(max(rect.origin.y - PREVIEW / 2, screen.origin.y),
                screen.origin.y + screen.size.height - PREVIEW)
        self.preview_panel.setFrameOrigin_(NSMakePoint(x, y))
        self.preview_panel.orderFront_(None)

    def hidePreview(self):
        self.preview_panel.orderOut_(None)

    def applicationShouldHandleReopen_hasVisibleWindows_(self, app, flag):
        self.window.makeKeyAndOrderFront_(None)
        return True

    def applicationShouldTerminateAfterLastWindowClosed_(self, app):
        return False


def main():
    app = NSApplication.sharedApplication()
    app.setActivationPolicy_(NSApplicationActivationPolicyRegular)
    delegate = AppDelegate.alloc().init()
    app.setDelegate_(delegate)
    app.run()


if __name__ == "__main__":
    main()
