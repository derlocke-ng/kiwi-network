# gnome-monitor

Save and switch display layouts on GNOME (resolution, refresh rate with VRR,
position, scale and main screen per monitor), and turn single monitors **off
and on** when another computer uses them. A CLI plus a GTK4 panel.

- Repository: [derlocke-ng/gnome-monitor](https://github.com/derlocke-ng/gnome-monitor), GPL-3.0-or-later
- Latest release: **v0.3.2**. It is in the [Kiwi catalog](catalogs.md), user scope.

Two computers, three screens, one desk. When the other machine needs the 4K
too, switch it off here, work, and switch it back on. It comes back where it
was, at the mode it had, as the main screen if it was one. Or save each
arrangement once and apply it with one click or a keyboard shortcut.

```bash
kiwi install gnome-monitor          # or ./install.sh
```

```bash
gnome-monitor show                  # what is connected, on, where, at what mode, with a map
gnome-monitor save desk             # the current layout as profile "desk"
gnome-monitor list                  # profiles; * marks the one in use
gnome-monitor apply desk
gnome-monitor off rog               # a screen by connector, part of its name, number or "main"
gnome-monitor on rog
gnome-monitor only odyssey hp       # exactly these on, every other off
gnome-monitor main odyssey
gnome-monitor mode rog 2560x1440@165
gnome-monitor shortcut desk super+1 # a GNOME shortcut that applies "desk"
gnome-monitor-panel                 # "Gnome Monitor" in the app grid
```

It talks to Mutter's `DisplayConfig` D-Bus API, on Wayland and X11, with no root
and no extension. Profiles are JSON in `~/.config/gnome-monitor/profiles/`, and
monitors are matched by their EDID. Changes apply quietly (or ask to keep
them, if you like), and the layout is restored at login. `--dry-run` asks
Mutter whether a layout is valid without applying it.
