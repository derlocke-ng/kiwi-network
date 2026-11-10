# El escritorio

Las herramientas de escritorio de Kiwi están hechas para los **escritorios Fedora
Atomic**: Fedora Silverblue y [Bluefin](https://projectbluefin.io/) (Bluefin-DX
en particular). Son sistemas basados en imágenes, con un `/usr` inmutable y una
vuelta atrás sencilla. No hay una imagen especial de Kiwi: instalas una estándar
y añades tres capas encima.

1. **[kiwi-updater](kiwi-updater.md)** instala y actualiza apps desde catálogos
   git: todo en tu home, más una parte propiedad de root solo para las apps que
   la necesitan. También se actualiza a sí mismo.
2. **[ensconce](ensconce.md)** configura un Bluefin-DX recién instalado a partir
   de archivos de lista simples: paquetes, Flatpaks, extensiones de GNOME,
   sincronización con Nextcloud, SSH, sysctl y ajustes de energía, la pantalla de
   inicio de sesión y tus apps de Kiwi. `--export` clona una máquina.
3. **Las apps**, del [catálogo de Kiwi](catalogs.md):

| App | Qué hace |
|---|---|
| [kiwi-killswitch](kiwi-killswitch.md) | Un kill switch de VPN que falla cerrado para GNOME |
| [Redes de clientes](../clients/index.md): kiwi-proxy, kiwi-custodia, kiwi-fox | Una salida sellada por cada endpoint VPN o SOCKS, y distro boxes y navegadores que viven dentro de ellas |
| [kiwi-server](../server/index.md) | Construye y gestiona tu propia red |
| [gnome-monitor](gnome-monitor.md) | Guarda y cambia distribuciones de pantallas; apaga y enciende monitores sueltos |
| [syncman](syncman.md) | Sincronización de carpetas en ambos sentidos (partidas guardadas y más) como servicios de usuario |
| [kiwi-cli-tools-desktop](cli-tools.md) | `pweb`, `select-server`, `tethering`, `torlink` |

También aquí: [kiwi-gen](kiwi-gen.md), un gestor de claves y certificados que
funciona sin conexión en el navegador.

## Desde una instalación nueva { #from-a-fresh-install }

```bash
# 1. kiwi-updater: ámbito de usuario y de sistema, una sola petición de contraseña; el catálogo de Kiwi viene incluido
curl -fsSL https://raw.githubusercontent.com/derlocke-ng/kiwi-updater/main/get-kiwi.sh | bash
kiwi list

# 2. configura la máquina
kiwi install ensconce
ensconce --init && $EDITOR "$(ensconce --config-dir)"/settings.sh
ensconce

# 3. las apps que quieras (o enuméralas en el kiwi-apps.list de ensconce)
kiwi install kiwi-killswitch
kiwi install kiwi-custodia && kiwi-custodia setup
```

**Kiwi Apps** (`kiwi-gui`), en la cuadrícula de aplicaciones, hace lo mismo con
un clic.

## Unirse a tu red { #joining-your-network }

Un escritorio se une a la malla como cualquier otro dispositivo: `kiwi-server enroll fleet.yaml
laptop --group devices` escribe una configuración WireGuard, que importas en la
Configuración de GNOME. Importa la CA de la fleet (`kiwiCA.pem`) para que sus
nombres HTTPS sean de confianza. ensconce instala en todo el sistema cada `.pem`
de su directorio `certs/`.

Después, [kiwi-killswitch](kiwi-killswitch.md) mantiene la máquina en modo
fail-closed alrededor de esa conexión. Su ajuste *trusted kiwi-nodes* permite que
un node gateway de tu LAN haga las veces del túnel en casa.
