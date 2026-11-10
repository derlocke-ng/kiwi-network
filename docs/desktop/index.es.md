# El escritorio

La parte de escritorio de Kiwi Network es el ordenador en el que trabajas: una
estación de trabajo Linux que se configura sola y obtiene sus apps de catálogos
de git. Un catálogo es un repositorio git con una lista de apps. No tienes que
configurar la máquina a mano, y la siguiente la puedes configurar exactamente
igual.

Las herramientas de escritorio de Kiwi están hechas para los **escritorios
Fedora Atomic**: Fedora Silverblue y [Bluefin](https://projectbluefin.io/), y
en especial Bluefin-DX. Estos sistemas se instalan y se actualizan como una
imagen completa. Su directorio `/usr` es inmutable, es decir, no se puede
modificar, y una actualización se puede deshacer fácilmente. No existe una
imagen especial de Kiwi: instalas una imagen normal de Silverblue o de Bluefin
y le añades tres cosas.

1. **[kiwi-updater](kiwi-updater.md)** instala apps desde catálogos de git y
   las mantiene actualizadas. Lo instala todo en tu carpeta personal. Solo las
   apps que necesitan permisos de root tienen además una parte que pertenece a
   root. kiwi-updater también se actualiza a sí mismo.
2. **[ensconce](ensconce.md)** configura un Bluefin-DX recién instalado.
   Describes tu configuración en archivos de listas sencillos y ensconce la
   aplica: paquetes, Flatpaks, extensiones de GNOME, sincronización con
   Nextcloud, SSH, ajustes de sysctl y de energía, la pantalla de inicio de
   sesión y tus apps de Kiwi. Con `--export` escribe en esos mismos archivos la
   configuración de una máquina que ya tienes, para que puedas clonarla.
3. **Las apps**, que instalas desde el [catálogo de Kiwi](catalogs.md):

| App | Qué hace |
|---|---|
| [kiwi-killswitch](kiwi-killswitch.md) | Un kill switch de VPN para GNOME. Es fail-closed: mientras la VPN no esté activa, todo el tráfico queda bloqueado |
| [Redes de clientes](../clients/index.md): kiwi-proxy, kiwi-custodia, kiwi-fox | Un exit para cada endpoint de VPN o SOCKS. Un exit es un contenedor aislado que solo puede llegar a ese endpoint. Se le pueden conectar boxes con distribuciones de Linux y navegadores, de modo que todo su tráfico pase por él |
| [kiwi-server](../server/index.md) | La herramienta con la que montas y mantienes tu propia red |
| [gnome-monitor](gnome-monitor.md) | Guarda disposiciones de las pantallas y cambia de una a otra. También apaga y enciende monitores sueltos |
| [syncman](syncman.md) | Sincroniza carpetas en ambos sentidos, por ejemplo partidas guardadas de juegos. La sincronización funciona como servicios de usuario |
| [kiwi-cli-tools-desktop](cli-tools.md) | `pweb`, `select-server`, `tethering`, `torlink` |

En esta sección también se describe [kiwi-gen](kiwi-gen.md), un gestor de
claves y certificados que funciona en el navegador y sin conexión.

## Desde una instalación nueva { #from-a-fresh-install }

Con estos comandos pasas de un sistema recién instalado a un escritorio con las
apps de Kiwi:

```bash
# 1. kiwi-updater: ámbito de usuario y del sistema, una sola petición de contraseña; incluye el catálogo de Kiwi
curl -fsSL https://raw.githubusercontent.com/derlocke-ng/kiwi-updater/main/get-kiwi.sh | bash
kiwi list

# 2. configurar la máquina
kiwi install ensconce
ensconce --init && $EDITOR "$(ensconce --config-dir)"/settings.sh
ensconce

# 3. las apps que quieras (o ponlas en el kiwi-apps.list de ensconce)
kiwi install kiwi-killswitch
kiwi install kiwi-custodia && kiwi-custodia setup
```

También puedes instalar apps sin abrir la terminal. **Kiwi Apps** (`kiwi-gui`),
en la cuadrícula de aplicaciones, instala una app con un clic.

## Conectarse a tu red { #joining-your-network }

Un escritorio entra en la mesh igual que cualquier otro dispositivo. La mesh es
la red WireGuard privada que une tus servidores y tus dispositivos. El comando
`kiwi-server enroll fleet.yaml laptop --group devices` escribe un archivo de
configuración de WireGuard, que luego importas en la Configuración de GNOME.
Importa también la autoridad de certificación (CA) de tu fleet, `kiwiCA.pem`,
para que el escritorio confíe en los certificados HTTPS de los nombres de tu
red. ensconce instala para todo el sistema cada archivo `.pem` que haya en su
directorio `certs/`.

Después, [kiwi-killswitch](kiwi-killswitch.md) protege esa conexión y mantiene
la máquina en modo fail-closed: el tráfico que no pasa por la conexión se
bloquea, también cuando la conexión está caída. En casa, puede que un node
gateway de tu red local ya envíe tu tráfico por un túnel. Con el ajuste
*trusted kiwi-nodes*, el kill switch acepta ese node gateway en lugar del
túnel.
