# gnome-monitor

Guarda y cambia distribuciones de pantallas en GNOME (resolución, frecuencia de
refresco con VRR, posición, escala y pantalla principal por monitor), y apaga y
enciende **monitores sueltos** cuando otro ordenador los usa. Una CLI más un
panel GTK4.

- Repositorio: [derlocke-ng/gnome-monitor](https://github.com/derlocke-ng/gnome-monitor), GPL-3.0-or-later
- Última versión: **v0.3.2**. Está en el [catálogo de Kiwi](catalogs.md), ámbito de usuario.

Dos ordenadores, tres pantallas, un escritorio. Cuando la otra máquina también
necesita la 4K, apágala aquí, trabaja y vuelve a encenderla. Vuelve donde
estaba, con el modo que tenía, como pantalla principal si lo era. O guarda cada
disposición una vez y aplícala con un clic o un atajo de teclado.

```bash
kiwi install gnome-monitor          # o ./install.sh
```

```bash
gnome-monitor show                  # qué está conectado, encendido, dónde, con qué modo, con un mapa
gnome-monitor save desk             # the current layout as profile "desk"
gnome-monitor list                  # perfiles; * marca el que está en uso
gnome-monitor apply desk
gnome-monitor off rog               # a screen by connector, part of its name, number or "main"
gnome-monitor on rog
gnome-monitor only odyssey hp       # exactamente estos encendidos, todos los demás apagados
gnome-monitor main odyssey
gnome-monitor mode rog 2560x1440@165
gnome-monitor shortcut desk super+1 # a GNOME shortcut that applies "desk"
gnome-monitor-panel                 # "Gnome Monitor" in the app grid
```

Habla con la API D-Bus `DisplayConfig` de Mutter, en Wayland y X11, sin root y
sin extensión. Los perfiles son JSON en `~/.config/gnome-monitor/profiles/`, y
los monitores se identifican por su EDID. Los cambios se aplican sin preguntar (o
piden confirmación para mantenerlos, si lo prefieres), y la distribución se
restaura al iniciar sesión. `--dry-run` pregunta a Mutter si una distribución es
válida sin aplicarla.
