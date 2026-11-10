# Módulos de proveedor

En [kiwi-proxy](kiwi-proxy.md), un exit es una conexión a un upstream,
guardada con un nombre y con su propio contenedor, por la que tus boxes y tus
navegadores envían su tráfico. Normalmente es una conexión que te han dado,
como el proxy SOCKS5 que lleva a la red de un cliente. Un módulo de proveedor
sirve para el otro caso: crea él mismo el exit, a través de Tor, de una
suscripción de VPN, de 9proxy o de Mysterium. Tor y Mysterium, en concreto,
están para darte más direcciones IP con las que hacer pruebas.

Cada módulo está en su propio repositorio. kiwi-updater lo instala en el
directorio de módulos de kiwi-proxy, y a partir de ahí lo gestiona kiwi-proxy:
construye la imagen de contenedor del módulo, arranca el módulo cuando un exit
lo necesita y lo detiene cuando ya no lo usa ningún gateway. Un gateway es el
contenedor que kiwi-proxy ejecuta para un exit mientras ese exit está activo.

| Módulo | Repositorio | Versión | Exit | Requisitos |
|---|---|---|---|---|
| `tor` | [kiwi-plugin-tor](https://github.com/derlocke-ng/kiwi-plugin-tor) | v0.3.0 | la red Tor, con un circuito por exit y cualquier país de salida | nada (es gratis) |
| `vpn` | [kiwi-plugin-vpn](https://github.com/derlocke-ng/kiwi-plugin-vpn) | v0.2.2 | un túnel WireGuard u OpenVPN a través de [gluetun](https://github.com/qdm12/gluetun) | una suscripción de VPN |
| `9proxy` | [kiwi-plugin-9proxy](https://github.com/derlocke-ng/kiwi-plugin-9proxy) | v0.2.0 | un exit residencial de [9proxy](https://9proxy.com/) | una cuenta de 9proxy y el cliente propietario de 9proxy, que no se redistribuye |
| `mysterium` | [kiwi-plugin-myst](https://github.com/derlocke-ng/kiwi-plugin-myst) | v0.5.2 | la dVPN de [Mysterium](https://mysterium.network/) (una VPN descentralizada), con una lista de nodos que puedes elegir por país y por tipo de IP | una identidad de consumidor registrada con saldo de MYST |

Los cuatro módulos tienen licencia GPL-3.0-or-later y están en el
[catálogo de Kiwi](../desktop/catalogs.md). Cada uno declara
`DEPENDS=kiwi-proxy`, así que kiwi-updater instala primero kiwi-proxy. Tor y
Mysterium son la forma rápida de conseguir más direcciones IP de salida, por
ejemplo para hacer pruebas.

## Instalación y uso { #install-and-use }

```bash
kiwi install kiwi-plugin-tor
kiwi-proxy module setup tor                      # construir su imagen (kiwi-proxy setup lo hace todo)
kiwi-proxy module list
kiwi-proxy module countries tor                  # en qué países puede salir Tor
kiwi-proxy add tor-de --module tor --country de  # un exit creado con él
kiwi-custodia new test --exit tor-de             # una box que lo usa, o bien:
kiwi-fox new test --exit tor-de                  # un perfil del navegador que lo usa
```

En un exit de Tor, el país se impone con la opción `StrictNodes` de Tor. Un
circuito que no puede salir en ese país falla, y nunca sale por otro país. Los
exits del módulo tor transmiten las credenciales SOCKS que Tor Browser envía
para cada sitio. Es su ajuste por defecto (`--socks-auth passthrough`).

## Cómo se conecta un proveedor a un gateway { #how-it-is-wired }

**Todos los proveedores ofrecen SOCKS5 y nada más.** Un contenedor de
proveedor necesita su propia conexión a Internet. Por eso no puede funcionar en
el namespace de red de un gateway, porque allí se descarta todo lo que no vaya
a un único destino. En su lugar, el proveedor y el gateway se conectan a
través de una red puente de Podman rootless, `kf-providers`, en la que cada
módulo tiene una dirección fija:

```
provider container ──── kf-providers bridge ──── gateway ──── box / browser / tool
(its own way out)                                permits only <provider-ip>:port
SOCKS5 only
```

- **Tor** ofrece SOCKS5 por sí mismo. kiwi-proxy envía unas credenciales
  distintas para cada exit, y la opción `IsolateSOCKSAuth` de Tor da entonces a
  cada exit su propio circuito, es decir, su propio camino por la red Tor.
- **VPN y Mysterium** usan un túnel, y un túnel no ofrece SOCKS5. Por eso, un
  pequeño adaptador, microsocks, entra en el namespace de red del túnel. Ofrece
  SOCKS5 y envía el tráfico por el túnel.
- **9proxy** ejecuta el cliente de 9proxy, que abre un puerto SOCKS5 que lleva
  a un exit residencial.

Un mismo contenedor de proveedor sirve a todos los exits que usan el mismo
módulo y el mismo lease. Un lease es cada una de las opciones de exit que
ofrece un módulo para elegir, por ejemplo el país de un servidor VPN o un nodo
de Mysterium. Si un túnel pierde su sesión, es fail-closed, es decir, no sale
ningún tráfico, y se reinicia.

## Configuración { #configuration }

El estado de cada módulo se guarda en
`~/.local/share/kiwi-proxy/modules-state/<module>/`, fuera de cualquier
repositorio:

- **vpn**: el archivo `vpn.json` contiene los ajustes de gluetun, como
  `VPN_SERVICE_PROVIDER`, `VPN_TYPE` y `WIREGUARD_ADDRESSES`. Todas las claves
  en mayúsculas se pasan a gluetun sin cambios. El archivo también puede
  contener una lista `leases`. Un directorio `gluetun/` opcional contiene más
  archivos, por ejemplo un `wireguard.conf` para el proveedor `custom` de
  gluetun. Hay una sola configuración de este tipo por máquina, y los exits
  que la usan se diferencian por el país del servidor.
- **9proxy**: el archivo de configuración es `config/account.conf`. El cliente
  propietario no está incluido. Antes de ejecutar
  `kiwi-proxy module setup 9proxy`, pon el cliente en el directorio
  `module/containers/vendor/` del plugin y añade `COPY vendor/ /opt/9proxy/` al
  `Containerfile` del plugin. Sin el cliente, la imagen se construye igualmente,
  pero el proveedor se niega a arrancar y no abre ningún puerto.
- **mysterium**: ejecuta `kiwi-proxy module config mysterium keystore=/path/to/0x….json
  --ask passphrase`, o usa *Configure…* en la app Kiwi Proxy. La frase de
  contraseña se guarda como secreto de Podman. Una identidad solo puede tener
  una conexión a la vez.

## Estado { #status }

Tor no necesita cuenta. El módulo de Mysterium se comprobó de principio a fin
el 7 de noviembre de 2026. Según sus README, los módulos de VPN y de 9proxy
están completos y tienen pruebas unitarias, pero no se han probado de principio
a fin con una suscripción o una cuenta reales.
