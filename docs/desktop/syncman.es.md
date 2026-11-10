# syncman

syncman mantiene sincronizados, en ambos sentidos, pares de carpetas de una
máquina Linux. Cuando aparece un archivo nuevo o modificado en una de las dos
carpetas de un par, se copia a la otra. syncman se hizo para las partidas guardadas de
los juegos, pero sirve para cualquier carpeta. **Su única dependencia es
rsync**, e inotify-tools es opcional. syncman se instala y funciona solo en el
ámbito de usuario, es decir, para tu propia cuenta de usuario.

- Repositorio: [derlocke-ng/syncman](https://github.com/derlocke-ng/syncman), GPL-3.0-or-later
- Última versión: **v0.4.1**. Está en el [catálogo de Kiwi](catalogs.md), en el ámbito de usuario.

Lo que hay que sincronizar se describe en un **job**. Un job es un archivo de
texto con un par de carpetas en cada línea. El formato no es YAML y no hace
falta poner comillas, así que una ruta con espacios se escribe tal cual:

```
# ~/.config/syncman/jobs/game-saves.job
~/Games/SomeGame/saves :: ~/Nextcloud/saves/SomeGame
```

Cada job funciona como un servicio de usuario de systemd llamado
`syncjob@<name>.service`. Cada `INTERVAL`, que por defecto son 30 segundos, el
servicio ejecuta `rsync -a --update` en los dos sentidos. Si un archivo existe
en los dos lados, el más reciente sustituye al más antiguo, y **nunca se borra
nada**. Si está instalado `inotifywait`, los cambios se sincronizan en cuanto
se producen.

```bash
kiwi install syncman            # o ./install.sh
syncman add game-saves          # crear y editar un job
syncman start game-saves        # un servicio en segundo plano que sobrevive a los reinicios
syncman list                    # los jobs y el estado de su servicio
syncman sync all                # una sola vez, sin servicio
syncman stop all
syncman log game-saves
syncman-panel                   # panel GTK4: un interruptor por job, botones de sincronizar ahora
```

Los ajustes están en `~/.config/syncman/syncman.conf`. Ese archivo define
`INTERVAL` y, si quieres, `JOBS_DIR`. Al desinstalar syncman, tus jobs se
conservan, salvo que añadas `--purge`.
