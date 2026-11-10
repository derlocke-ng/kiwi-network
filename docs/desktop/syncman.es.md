# syncman

Sincronización de carpetas en ambos sentidos y por pares para Linux. Se hizo para
partidas guardadas y sirve para cualquier carpeta. **rsync es la única
dependencia** (inotify-tools es opcional), y funciona solo en tu ámbito de
usuario.

- Repositorio: [derlocke-ng/syncman](https://github.com/derlocke-ng/syncman), GPL-3.0-or-later
- Última versión: **v0.4.1**. Está en el [catálogo de Kiwi](catalogs.md), ámbito de usuario.

Un **trabajo** es un archivo de texto simple con un par por línea. No hay YAML ni
comillas, y los espacios en las rutas simplemente funcionan:

```
# ~/.config/syncman/jobs/game-saves.job
~/Games/SomeGame/saves :: ~/Nextcloud/saves/SomeGame
```

Cada trabajo se ejecuta como un servicio de usuario de systemd,
`syncjob@<name>.service`. Cada `INTERVAL` (30 segundos por defecto) ejecuta
`rsync -a --update` en ambos sentidos: gana el archivo más reciente, y **nunca se
borra nada**. Con `inotifywait` instalado, los cambios se sincronizan al
momento.

```bash
kiwi install syncman            # o ./install.sh
syncman add game-saves          # crea y edita un trabajo
syncman start game-saves        # un servicio en segundo plano que sobrevive a los reinicios
syncman list                    # los trabajos y el estado de su servicio
syncman sync all                # una sola vez, sin servicio
syncman stop all
syncman log game-saves
syncman-panel                   # panel GTK4: un interruptor por trabajo, botones de sincronizar ahora
```

Los ajustes están en `~/.config/syncman/syncman.conf` (`INTERVAL` y,
opcionalmente, `JOBS_DIR`). Al desinstalar se conservan tus trabajos, salvo que
pases `--purge`.
