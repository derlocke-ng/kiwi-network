# Módulos de proveedores

Un módulo de proveedor da a [kiwi-proxy](kiwi-proxy.md) una salida que produce él
mismo, en lugar de un SOCKS5 que te dieron. Cada uno vive en su propio
repositorio, se instala mediante kiwi-updater en el directorio de módulos de
kiwi-proxy y lo gestiona kiwi-proxy: construye la imagen del módulo, lo levanta
cuando una salida lo necesita y lo derriba cuando ya no lo usa ningún gateway.

| Módulo | Repositorio | Versión | Salida | Necesita |
|---|---|---|---|---|
| `tor` | [kiwi-plugin-tor](https://github.com/derlocke-ng/kiwi-plugin-tor) | v0.3.0 | la red Tor, un circuito por salida, cualquier país de salida | nada (gratis) |
| `vpn` | [kiwi-plugin-vpn](https://github.com/derlocke-ng/kiwi-plugin-vpn) | v0.2.2 | un túnel WireGuard u OpenVPN a través de [gluetun](https://github.com/qdm12/gluetun) | una suscripción VPN |
| `9proxy` | [kiwi-plugin-9proxy](https://github.com/derlocke-ng/kiwi-plugin-9proxy) | v0.2.0 | una salida residencial de [9proxy](https://9proxy.com/) | una cuenta de 9proxy y su cliente propietario (no se redistribuye) |
| `mysterium` | [kiwi-plugin-myst](https://github.com/derlocke-ng/kiwi-plugin-myst) | v0.5.2 | la dVPN [Mysterium](https://mysterium.network/), con un selector de nodos por país y tipo de IP | una identidad de consumidor registrada con saldo de MYST |

Los cuatro son GPL-3.0-or-later, están en el
[catálogo de Kiwi](../desktop/catalogs.md) y declaran `DEPENDS=kiwi-proxy`, así
que kiwi instala primero kiwi-proxy. Tor y Mysterium son la forma rápida de tener
más IPs de salida, por ejemplo para pruebas.

## Instalación y uso { #install-and-use }

```bash
kiwi install kiwi-plugin-tor
kiwi-proxy module setup tor                      # construye su imagen (kiwi-proxy setup lo hace todo)
kiwi-proxy module list
kiwi-proxy module countries tor                  # por dónde puede salir Tor
kiwi-proxy add tor-de --module tor --country de  # una salida de él
kiwi-custodia new test --exit tor-de             # una box en ella, o:
kiwi-fox new test --exit tor-de                  # un perfil de navegador en ella
```

Con Tor, el país se mantiene con `StrictNodes`, así que el circuito falla antes
que salir por otro sitio. Las salidas del módulo tor dejan pasar por defecto las
credenciales SOCKS por sitio de Tor Browser (`--socks-auth passthrough`).

## Cómo está conectado { #how-it-is-wired }

**Todo proveedor expone SOCKS5 y nada más.** Un contenedor de proveedor necesita
su propia salida, así que no puede vivir en el espacio de nombres de un gateway,
donde se descarta todo salvo un destino. Los dos se encuentran en un bridge de
Podman sin root, `kf-providers`, donde cada módulo recibe una dirección fija:

```
provider container ──── kf-providers bridge ──── gateway ──── box / browser / tool
(its own way out)                                permits only <provider-ip>:port
SOCKS5 only
```

- **Tor** ya habla SOCKS5. kiwi-proxy envía una credencial por salida, y el
  `IsolateSOCKSAuth` de Tor da a cada salida su propio circuito.
- **VPN y Mysterium** van sobre un túnel que no habla SOCKS5, así que un pequeño
  adaptador microsocks se une al espacio de nombres de red del túnel y ofrece un
  SOCKS5 que va por el túnel.
- **9proxy** ejecuta el cliente de 9proxy, que abre un puerto SOCKS5 en una
  salida residencial.

Un contenedor de proveedor sirve a todas las salidas del mismo módulo y lease. Un
túnel que pierde su sesión falla cerrado y se reinicia.

## Configuración { #configuration }

El estado de cada módulo vive en
`~/.local/share/kiwi-proxy/modules-state/<module>/`, fuera de cualquier
repositorio:

- **vpn**: `vpn.json` con los ajustes de gluetun (`VPN_SERVICE_PROVIDER`,
  `VPN_TYPE`, `WIREGUARD_ADDRESSES`, …; cada clave en mayúsculas va a gluetun tal
  cual), una lista `leases` opcional y un directorio `gluetun/` opcional (por
  ejemplo, un `wireguard.conf` para el proveedor `custom` de gluetun). Es una
  sola configuración por máquina: las salidas sobre ella se diferencian por el
  país del servidor.
- **9proxy**: `config/account.conf`. Pon el cliente propietario en
  `module/containers/vendor/` del plugin y añade `COPY vendor/ /opt/9proxy/` a su
  `Containerfile` antes de `kiwi-proxy module setup 9proxy`. Sin él, la imagen se
  construye, pero el proveedor se niega a levantarse en lugar de abrir un
  puerto.
- **mysterium**: `kiwi-proxy module config mysterium keystore=/path/to/0x….json
  --ask passphrase`, o *Configure…* en la app Kiwi Proxy. La frase de contraseña
  se convierte en un secreto de Podman. Una identidad mantiene una sola conexión
  cada vez.

## Estado { #status }

Tor no necesita cuenta. Mysterium se verificó de principio a fin el 2026-11-07.
Los módulos VPN y 9proxy están completos y tienen pruebas unitarias, pero no se
han ejecutado de principio a fin contra una suscripción o cuenta reales, como
dicen sus README.
