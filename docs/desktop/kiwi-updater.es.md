# kiwi-updater

kiwi-updater instala apps de código abierto en tu ordenador y las mantiene al
día. Su comando es `kiwi`. Obtiene las apps de **catálogos de git**. Un
catálogo es un repositorio git con una lista de apps, y una app es un
repositorio git con un archivo `kiwi.manifest` y un script `install.sh`. kiwi
clona la app, se sitúa en su etiqueta de versión más reciente y ejecuta su
instalador. A partir de ahí actualiza la app en segundo plano, y se actualiza a
sí mismo de la misma manera.

No necesitas ninguna cuenta, y no hay tienda de apps ni ningún fabricante de
por medio. Un catálogo es un repositorio que puedes leer, del que puedes hacer
un fork y al que puedes enviar un pull request. Todas las apps de escritorio de
Kiwi se instalan así.

- Repositorio: [derlocke-ng/kiwi-updater](https://github.com/derlocke-ng/kiwi-updater), GPL-3.0-or-later
- Última versión: **v2.5.1**
- **`kiwi`** es la herramienta de línea de comandos. **Kiwi Apps** (`kiwi-gui`)
  es la app de escritorio. Con ella puedes explorar y buscar las apps,
  instalarlas y leer el instalador de una app antes de que se ejecute.

## Dónde funciona { #where-it-runs }

kiwi-updater se creó para los escritorios Fedora Atomic, y ahora funciona
también en otras distribuciones de Linux. Cada cambio en kiwi-updater se comprueba
en estos sistemas con todas las pruebas automáticas y con una instalación
real:

| Sistema | Qué funciona |
|---|---|
| Fedora Silverblue, Bluefin, Fedora, Debian 13, Ubuntu 24.04, Arch, openSUSE Tumbleweed | todo |
| Alpine | todo, una vez instaladas las herramientas de GNU |
| Debian 12, Ubuntu 22.04 (probados, pero no en cada cambio) | `kiwi` y las apps de línea de comandos. La libadwaita de estos sistemas es demasiado antigua para las apps de escritorio |

## Instalación { #install }

Este comando instala la parte de usuario en tu carpeta personal y la parte de
root para las apps que necesitan root. Solo te pide la contraseña una vez:

```bash
curl -fsSL https://raw.githubusercontent.com/derlocke-ng/kiwi-updater/main/get-kiwi.sh | bash
```

Si no quieres nada fuera de tu carpeta personal, ni que se te pida nunca la
contraseña, instala solo la parte de usuario:

```bash
curl -fsSL https://raw.githubusercontent.com/derlocke-ng/kiwi-updater/main/get-kiwi.sh | bash -s -- --minimal
```

El instalador comprueba que la versión que va a instalar esté firmada con la
clave con la que kiwi-updater firma sus versiones, y rechaza cualquier versión
que no lo esté. Durante la instalación se registra el catálogo de Kiwi. Después
puedes empezar:

```bash
kiwi list                    # todas las apps que puedes instalar
kiwi install <app>           # instala una
kiwi info --installer <app>  # lee su instalador antes de que se ejecute
kiwi-gui                     # la app de escritorio
```

## Partes de root y versiones firmadas { #root-parts-and-signed-releases }

Algunas apps necesitan root, por ejemplo kiwi-killswitch, que incluye un daemon
de cortafuegos. Su parte de root la instala una copia de kiwi que pertenece a
root, y solo desde fuentes que figuran en las listas del propio root. Instalar
o desinstalar una app así siempre pide tu contraseña. En el modo
predeterminado, una actualización solo se hace sin contraseña si la versión
está firmada con la clave que root ha guardado para esa app.

## La documentación completa { #the-full-documentation }

kiwi-updater tiene su propia documentación en su repositorio:

| Página | De qué trata |
|---|---|
| [Instalación](https://github.com/derlocke-ng/kiwi-updater/blob/main/docs/install.md) | sistemas compatibles, paquetes para cada distribución, modos de instalación, desinstalación |
| [Usar kiwi](https://github.com/derlocke-ng/kiwi-updater/blob/main/docs/usage.md) | todos los comandos, Kiwi Apps, actualizaciones en segundo plano, ajustes |
| [Catálogos](https://github.com/derlocke-ng/kiwi-updater/blob/main/docs/catalogs.md) | añadir catálogos, `apps.list`, fijar versiones, sustituir entradas de un catálogo |
| [Seguridad](https://github.com/derlocke-ng/kiwi-updater/blob/main/docs/security.md) | qué se ejecuta como root, cuándo escribes una contraseña, qué comprueba kiwi |
| [Escribir una app](https://github.com/derlocke-ng/kiwi-updater/blob/main/docs/app-authors.md) | `kiwi.manifest`, `install.sh`, dependencias, iconos, versiones |
| [Versiones firmadas](https://github.com/derlocke-ng/kiwi-updater/blob/main/docs/signing.md) | firmar las versiones de tu app con `kiwi-release` |
| [Desarrollo](https://github.com/derlocke-ng/kiwi-updater/blob/main/docs/development.md) | pruebas, CI, publicar una versión de kiwi-updater |

A partir de la próxima versión de kiwi-updater, estas páginas también
aparecerán aquí, en el menú, debajo de kiwi-updater.

Para publicar tu propia app, consulta [Catálogos y publicación](catalogs.md).
