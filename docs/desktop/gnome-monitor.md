# gnome-monitor

gnome-monitor saves the arrangement of your monitors on GNOME as a layout and
switches between saved layouts. A layout records the resolution, the refresh
rate (including variable refresh rate, VRR), the position and the scale of
each monitor, and which monitor is the main screen. gnome-monitor can also
turn a single monitor **off and on**, which is useful when another computer is
connected to the same monitor and needs it. It has a command-line tool and a
GTK4 panel.

- Repository: [derlocke-ng/gnome-monitor](https://github.com/derlocke-ng/gnome-monitor), GPL-3.0-or-later
- Latest release: **v0.3.2**. It is in the [Kiwi catalog](catalogs.md), user scope.

A typical case is a desk with two computers and three screens. When the other
computer needs the 4K monitor as well, you turn that monitor off on this
computer and work on the remaining screens. When you turn it on again, it
returns to the position and the mode it had before, and it is the main screen
again if it was the main screen before. You can also save each arrangement
once as a profile and apply it with one click or with a keyboard shortcut.

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

gnome-monitor uses the `DisplayConfig` D-Bus API of Mutter, the window manager
of GNOME. It works on Wayland and on X11, and it needs neither root rights nor
a GNOME extension. Profiles are JSON files in `~/.config/gnome-monitor/profiles/`.
A monitor is recognised by its EDID, the identification data that the monitor
reports about itself. A change of layout is applied without a confirmation
dialog. If you prefer, you can turn on an option that asks whether you want to
keep the new layout. The layout is restored when you log in. With `--dry-run`,
gnome-monitor asks Mutter whether a layout is valid and does not apply it.
