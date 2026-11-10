# gnome-monitor

gnome-monitor guarda la disposición de tus pantallas en GNOME y cambia de una
disposición guardada a otra. Una disposición recoge la resolución, la
frecuencia de actualización (incluida la frecuencia variable, VRR), la
posición y la escala de cada monitor, y cuál es la pantalla principal.
gnome-monitor también puede **apagar y encender** un monitor concreto, algo
útil cuando ese monitor está conectado también a otro ordenador que lo
necesita. Tiene una herramienta de línea de comandos y un panel GTK4.

- Repositorio: [derlocke-ng/gnome-monitor](https://github.com/derlocke-ng/gnome-monitor), GPL-3.0-or-later
- Última versión: **v0.3.2**. Está en el [catálogo de Kiwi](catalogs.md), en el ámbito de usuario.

Un caso típico es un escritorio con dos ordenadores y tres pantallas. Cuando el
otro ordenador también necesita el monitor 4K, lo apagas en este ordenador y
sigues trabajando con las demás pantallas. Al volver a encenderlo, recupera la
posición y el modo que tenía, y vuelve a ser la pantalla principal si lo era
antes. También puedes guardar cada disposición una vez como perfil y aplicarla
con un clic o con un atajo de teclado.

```bash
kiwi install gnome-monitor          # o ./install.sh
```

```bash
gnome-monitor show                  # qué hay conectado, encendido, dónde, en qué modo, con un mapa
gnome-monitor save desk             # la disposición actual como perfil "desk"
gnome-monitor list                  # perfiles; * marca el que está en uso
gnome-monitor apply desk
gnome-monitor off rog               # una pantalla por conector, parte de su nombre, número o "main"
gnome-monitor on rog
gnome-monitor only odyssey hp       # exactamente estas encendidas, todas las demás apagadas
gnome-monitor main odyssey
gnome-monitor mode rog 2560x1440@165
gnome-monitor shortcut desk super+1 # un atajo de GNOME que aplica "desk"
gnome-monitor-panel                 # "Gnome Monitor" en la cuadrícula de aplicaciones
```

gnome-monitor usa la API de D-Bus `DisplayConfig` de Mutter, el gestor de
ventanas de GNOME. Funciona en Wayland y en X11, y no necesita permisos de root
ni ninguna extensión de GNOME. Los perfiles son archivos JSON en
`~/.config/gnome-monitor/profiles/`. Cada monitor se reconoce por su EDID, los
datos de identificación que el propio monitor comunica. Los cambios de
disposición se aplican sin ningún diálogo de confirmación. Si lo prefieres,
puedes activar una opción que te pregunta si quieres conservar la nueva
disposición. Al iniciar sesión se restaura la disposición. Con `--dry-run`,
gnome-monitor pregunta a Mutter si una disposición es válida, pero no la
aplica.
