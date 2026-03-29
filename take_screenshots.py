#!/usr/bin/env python3
"""Render Quran Radio UI screenshots for the Flathub metainfo.

Uses Gtk.OffscreenWindow — no screen capture, works on Wayland.
Outputs:
  screenshots/tray-menu.png   — dropdown menu (station list + play/stop)
  screenshots/volume-popup.png — volume controls popup window
"""

import math, os, gi
gi.require_version('Gtk', '3.0')
gi.require_version('Gdk', '3.0')
gi.require_version('GdkPixbuf', '2.0')
from gi.repository import Gtk, Gdk, GdkPixbuf, GLib

APP_DIR = os.path.dirname(os.path.abspath(__file__))
OUT_DIR = os.path.join(APP_DIR, "screenshots")
os.makedirs(OUT_DIR, exist_ok=True)

ICON_PATH = os.path.join(APP_DIR, "icon.png")

# ── Shared CSS ─────────────────────────────────────────────────────────────────
CSS = b"""
* { font-family: "Cantarell", "Noto Sans", sans-serif; }
window, .menu-box, .popup-box {
    background-color: #1e1e1e;
}
label.title {
    color: #2da05a;
    font-weight: bold;
    font-size: 15px;
}
button.play-btn {
    background: #1B6B3A;
    color: white;
    border-radius: 5px;
    font-weight: bold;
    padding: 4px 0;
    border: none;
    box-shadow: none;
}
label, checkbutton label, radiobutton label {
    color: #d8d8d8;
}
label.status {
    color: #888888;
    font-style: italic;
    font-size: 11px;
}
label.menu-item {
    color: #d8d8d8;
    font-size: 13px;
    padding: 2px 0;
}
label.menu-item.active {
    color: #2da05a;
    font-weight: bold;
}
label.sep-label {
    color: #444444;
    font-size: 8px;
}
scale trough   { background-color: #3a3a3a; }
scale highlight { background-color: #1B6B3A; }
"""

def apply_css():
    p = Gtk.CssProvider()
    p.load_from_data(CSS)
    Gtk.StyleContext.add_provider_for_screen(
        Gdk.Screen.get_default(), p,
        Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION,
    )

def flush():
    """Process pending GTK events so widgets fully render."""
    for _ in range(20):
        while Gtk.events_pending():
            Gtk.main_iteration_do(False)

def save_offscreen(widget, path, padding=0):
    """Wrap widget in an OffscreenWindow, render, save PNG."""
    if padding:
        outer = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        outer.set_border_width(padding)
        outer.pack_start(widget, True, True, 0)
        widget = outer

    win = Gtk.OffscreenWindow()
    win.add(widget)
    win.show_all()
    flush()

    pb = win.get_pixbuf()
    if pb:
        pb.savev(path, "png", [], [])
        print(f"  saved → {path}  ({pb.get_width()}×{pb.get_height()})")
    else:
        print(f"  WARNING: could not render {path}")

    win.destroy()


# ── Screenshot 1: Tray dropdown menu ──────────────────────────────────────────
def make_tray_menu() -> Gtk.Widget:
    """Simulate the SNI dbusmenu as a GTK widget."""

    STATIONS = [
        ("Quran Kareem — Beirut",           True),   # selected
        ("Quran Kareem — Cairo (ERTU 98.2 FM)", False),
    ]

    frame = Gtk.Frame()
    frame.set_shadow_type(Gtk.ShadowType.ETCHED_IN)

    vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
    vbox.set_border_width(6)
    frame.add(vbox)

    def add_sep():
        sep = Gtk.Separator()
        vbox.pack_start(sep, False, False, 4)

    def add_row(label_text, is_active=False, indent=False, bold=False):
        row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        row.set_border_width(2)

        # Radio bullet
        dot = Gtk.Label(label="●" if is_active else "○")
        dot.get_style_context().add_class("menu-item")
        if is_active:
            dot.get_style_context().add_class("active")
        row.pack_start(dot, False, False, 4 if indent else 2)

        lbl = Gtk.Label(label=label_text)
        lbl.set_halign(Gtk.Align.START)
        lbl.get_style_context().add_class("menu-item")
        if is_active:
            lbl.get_style_context().add_class("active")
        row.pack_start(lbl, True, True, 0)
        vbox.pack_start(row, False, False, 2)

    def add_action(label_text, icon=""):
        row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        row.set_border_width(2)
        if icon:
            ico = Gtk.Label(label=icon)
            ico.get_style_context().add_class("menu-item")
            row.pack_start(ico, False, False, 6)
        lbl = Gtk.Label(label=label_text)
        lbl.set_halign(Gtk.Align.START)
        lbl.get_style_context().add_class("menu-item")
        row.pack_start(lbl, True, True, 0)
        vbox.pack_start(row, False, False, 2)

    # Stations
    for name, active in STATIONS:
        add_row(name, is_active=active)

    add_sep()
    add_action("▶  Play", "")
    add_sep()
    add_action("Volume Controls…")
    add_sep()
    add_action("Quit")

    return frame


# ── Screenshot 2: Volume popup window ─────────────────────────────────────────
def make_volume_popup() -> Gtk.Widget:
    vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
    vbox.set_border_width(14)

    title = Gtk.Label(label="Quran Radio 📻")
    title.get_style_context().add_class("title")
    title.set_halign(Gtk.Align.CENTER)
    vbox.pack_start(title, False, False, 4)

    vbox.pack_start(Gtk.Separator(), False, False, 2)

    # Station radio buttons
    group = None
    for i, (name, active) in enumerate([
        ("Quran Kareem — Beirut",                True),
        ("Quran Kareem — Cairo (ERTU 98.2 FM)",  False),
    ]):
        btn = Gtk.RadioButton.new_with_label_from_widget(group, name)
        if group is None:
            group = btn
        btn.set_active(active)
        vbox.pack_start(btn, False, False, 0)

    vbox.pack_start(Gtk.Separator(), False, False, 2)

    # Volume row
    vol_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
    vol_row.pack_start(Gtk.Label(label="Vol:"), False, False, 0)

    slider = Gtk.Scale.new_with_range(Gtk.Orientation.HORIZONTAL, 0, 100, 1)
    slider.set_value(80)
    slider.set_hexpand(True)
    slider.set_draw_value(False)
    vol_row.pack_start(slider, True, True, 0)

    vol_row.pack_start(Gtk.Label(label="80%"), False, False, 0)
    vbox.pack_start(vol_row, False, False, 0)

    # Play button
    play_btn = Gtk.Button(label="▶  Play")
    play_btn.get_style_context().add_class("play-btn")
    vbox.pack_start(play_btn, False, False, 4)

    # Status
    status = Gtk.Label(label="Stopped")
    status.get_style_context().add_class("status")
    status.set_halign(Gtk.Align.CENTER)
    vbox.pack_start(status, False, False, 0)

    # Wrap in a frame to show the window border
    frame = Gtk.Frame()
    frame.set_shadow_type(Gtk.ShadowType.ETCHED_IN)
    frame.set_size_request(300, -1)
    frame.add(vbox)
    return frame


# ── Main ───────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    apply_css()

    print("Rendering screenshots…")

    save_offscreen(make_tray_menu(),     os.path.join(OUT_DIR, "tray-menu.png"),    padding=8)
    save_offscreen(make_volume_popup(),  os.path.join(OUT_DIR, "volume-popup.png"), padding=8)

    print("Done.")
