# Trabajar con muchas redes de clientes

Diez clientes remotos suelen significar diez VPN o endpoints SOCKS, uno para
llegar a la red de cada cliente. Ejecutarlos todos en el host es un lío: diez
túneles a la vez, rutas que se pelean y una red que se filtra en la siguiente.
Las apps de escritorio de Kiwi dan a cada uno una **salida sellada** en su lugar:
un contenedor cuya única ruta es ese upstream. Tus herramientas se unen a la
salida que necesitan, y nada más cambia en el host.

| App | Qué hace |
|---|---|
| [**kiwi-proxy**](kiwi-proxy.md) | El motor. Una **salida** es un upstream con nombre: un SOCKS5 que te dieron, o uno que crea un módulo de proveedor. Levantarla crea un **gateway**, un espacio de nombres de red cuya única ruta es ese upstream. Las apps del host pueden usarla como un puerto SOCKS5 local |
| [**kiwi-custodia**](kiwi-custodia.md) | **Distro boxes en una salida**: Fedora, Ubuntu, Debian, Kali, Arch, openSUSE, Rocky o Alpine en un contenedor sin root con su propio home. *Todo* lo que hay en la box sale por la salida: gestores de paquetes, juegos, binarios estáticos que nunca han oído hablar de un proxy |
| [**kiwi-fox**](kiwi-fox.md) | **Perfiles de navegador en una salida**: Camoufox, Firefox o Tor Browser, cada perfil con su propio almacenamiento |
| [**Módulos de proveedores**](providers.md) | Salidas desde Tor, una VPN (gluetun), 9proxy o Mysterium. Tor y Mysterium son la forma rápida de tener más IPs de salida, útil para pruebas |

```
 client A: socks5://…  ─┐                                   ┌─ box "client-a" (Fedora: ssh, ansible, dnf …)
 client B: socks5://…  ─┼─ kiwi-proxy exits ─▶ gateways ───┼─ browser profile "client-b"
 Tor / Mysterium / VPN ─┘   one per upstream   only route   └─ curl, mail, any app: socks5h://127.0.0.1:1082
                                               is the exit
```

## Cómo se mantiene limpio { #how-it-stays-clean }

- **Falla cerrado.** El cortafuegos de un gateway lo descarta todo salvo su único
  upstream. Si el gateway muere, todo lo que se unió a él pierde su ruta. El kill
  switch es la ausencia de una ruta, no un software que tenga que darse cuenta.
- **No se ejecuta nada que no se use.** Un gateway que levantó una box o un
  navegador desaparece cuando se va el último. Solo las salidas que inicias con
  `kiwi-proxy up` se quedan levantadas.
- **Lo separado sigue separado.** Lo que está en la misma salida la comparte
  (una IP, un espacio de nombres). Los clientes que no deben encontrarse reciben
  salidas distintas, y cada box tiene su propio home, así que las claves SSH y
  los perfiles de navegador no se cruzan.
- **Sin root, sin rutas en el host.** Todo funciona en Podman sin root, y la red
  propia del host no se toca.
- **El DNS también va por la salida.** Por defecto, los nombres se resuelven por
  DoH a través de la salida, con listas de bloqueo de anuncios. Para los
  **nombres de host internos** de un cliente, pasa los nombres al lado del
  cliente con `--dns remote` (también el modo para Tor y los nombres `.onion`).

## Límites { #limits }

Vienen de los repositorios:

- **Solo TCP, solo IPv4.** UDP no sale por ninguna parte (ni QUIC, ni medios
  WebRTC), e IPv6 no tiene ruta.
- **Una configuración VPN por máquina.** El módulo de proveedor VPN guarda una
  configuración de gluetun (un `vpn.json`, una configuración WireGuard
  personalizada), y sus salidas solo se diferencian por el país del servidor.
  Para tener las VPN propias de varios clientes en paralelo, hoy el camino es un
  endpoint SOCKS5 por cliente.
- **Una box es custodia de red, no un sandbox.** Comparte tu pantalla, el bus de
  sesión y el portapapeles, como distrobox. Lo que no puede hacer es llegar a la
  red salvo a través de su salida.
- **Mysterium:** una identidad mantiene una sola conexión cada vez.

## Primeros pasos { #get-started }

```bash
kiwi install kiwi-custodia            # trae consigo kiwi-proxy
kiwi-custodia setup                   # imágenes y datos de DNS

kiwi-proxy add client-a socks5://user:pass@jump.client-a.example:1080 --dns remote
kiwi-custodia new client-a --exit client-a --distro fedora
kiwi-custodia enter client-a          # a shell whose only way out is client A's SOCKS5
```
