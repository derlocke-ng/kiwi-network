# Trabajar en las redes de muchos clientes

Si trabajas a distancia para muchos clientes, normalmente necesitas una
conexión VPN o SOCKS distinta para llegar a la red de cada uno. Diez clientes
son entonces diez conexiones. Tenerlas todas en el host trae problemas: hay
diez túneles activos a la vez, sus rutas chocan entre sí y el tráfico destinado
a la red de un cliente puede acabar en la de otro.

Las apps de escritorio de Kiwi te permiten trabajar en la red de cada cliente
por separado. El host no se llena de túneles y rutas, y no tienes diez
conexiones VPN funcionando al mismo tiempo. Cada conexión va en su propio
contenedor, y la única ruta que sale de ese contenedor lleva a ese cliente y a
ningún otro. Una conexión así se llama **exit**. Tus herramientas funcionan en
un contenedor o en un perfil del navegador que usa el exit que necesitan, y en
el resto del host no cambia nada.

| App | Qué hace |
|---|---|
| [**kiwi-proxy**](kiwi-proxy.md) | La base sobre la que se construyen las demás apps. Un **exit** es una conexión a un upstream, guardada con un nombre. El upstream es el proxy al que se envía tu tráfico: o bien un proxy SOCKS5 que te han dado, o bien uno que crea un módulo de proveedor. Cuando activas un exit, kiwi-proxy le crea un **gateway**. Un gateway es un namespace de red (un conjunto propio de interfaces, direcciones, rutas y cortafuegos) cuya única ruta lleva a ese upstream. Los programas del host pueden usar un exit a través de un puerto SOCKS5 local |
| [**kiwi-custodia**](kiwi-custodia.md) | **Distribuciones de Linux en boxes que usan un exit.** Una box es un contenedor rootless (que funciona sin permisos de root) con Fedora, Ubuntu, Debian, Kali, Arch, openSUSE, Rocky o Alpine y con su propia carpeta personal. *Todo* el tráfico de red de la box pasa por el exit. Eso incluye los gestores de paquetes, los juegos y los programas enlazados estáticamente que no hacen caso de los ajustes de proxy |
| [**kiwi-fox**](kiwi-fox.md) | **Perfiles del navegador que usan un exit.** Cada perfil ejecuta Camoufox, Firefox o Tor Browser y tiene su propio almacenamiento |
| [**Módulos de proveedor**](providers.md) | Módulos que crean exits a través de Tor, de una VPN (con gluetun), de 9proxy o de Mysterium. Tor y Mysterium son una forma rápida de conseguir más direcciones IP, algo útil para hacer pruebas |

```
 client A: socks5://…  ─┐                                   ┌─ box "client-a" (Fedora: ssh, ansible, dnf …)
 client B: socks5://…  ─┼─ kiwi-proxy exits ─▶ gateways ───┼─ browser profile "client-b"
 Tor / Mysterium / VPN ─┘   one per upstream   only route   └─ curl, mail, any app: socks5h://127.0.0.1:1082
                                               is the exit
```

## Cómo se mantienen separados los exits { #how-it-stays-clean }

- **Un gateway es fail-closed.** Es decir, un fallo corta la conexión y nunca
  abre otro camino. El cortafuegos de un gateway descarta todo lo que no vaya
  dirigido a su único upstream. Si el gateway se detiene, todo lo que depende
  de él se queda sin conexión. Ningún programa tiene que darse cuenta del fallo
  y reaccionar, porque sin el gateway sencillamente no hay ruta.
- **Solo funciona lo que usas.** Cuando una box o un navegador arranca un
  gateway, ese gateway se elimina en cuanto se detiene la última box o el
  último navegador que lo usaba. Solo siguen funcionando los exits que arrancas
  tú mismo con `kiwi-proxy up`.
- **Los clientes se mantienen separados.** Las boxes y los navegadores que
  usan el mismo exit lo comparten, así que tienen la misma dirección IP y el
  mismo namespace de red. Los clientes que no deben verse entre sí usan exits
  distintos. Además, cada box tiene su propia carpeta personal, así que las
  claves SSH y los perfiles del navegador de un cliente no están disponibles
  en la box de otro.
- **Sin permisos de root y sin rutas en el host.** Todo funciona en Podman
  rootless, que ejecuta los contenedores con tu propio usuario. La red del
  propio host no cambia.
- **Las consultas DNS también pasan por el exit.** Por defecto, los nombres se
  resuelven con DNS sobre HTTPS (DoH) a través del exit, y se bloquean listas
  de dominios publicitarios. Para resolver los **nombres de host internos** de
  un cliente, usa `--dns remote`. Así los nombres se pasan al lado del cliente
  y se resuelven allí. Tor y los nombres `.onion` también necesitan este modo.

## Limitaciones { #limits }

Los repositorios indican estas limitaciones:

- **Solo TCP y solo IPv4.** UDP no se reenvía, así que QUIC y los medios de
  WebRTC no funcionan. No hay ruta para IPv6.
- **Una configuración de VPN por máquina.** El módulo de proveedor de VPN tiene
  una única configuración de gluetun, con un `vpn.json` y una configuración de
  WireGuard propia. Sus exits solo se diferencian en el país del servidor. Si
  necesitas las VPN propias de varios clientes a la vez, hoy la forma de
  hacerlo es un endpoint SOCKS5 para cada cliente.
- **Una box limita la red, pero no es un sandbox.** Igual que un contenedor de
  distrobox, comparte tu pantalla, tu bus de sesión y tu portapapeles. Lo que
  no puede es llegar a la red de ninguna otra forma que no sea su exit.
- **Mysterium:** una identidad solo puede tener una conexión a la vez.

## Primeros pasos { #get-started }

Los comandos siguientes instalan las apps, guardan el proxy SOCKS5 de un
cliente como exit y abren una shell en una box de Fedora que usa ese exit:

```bash
kiwi install kiwi-custodia            # instala también kiwi-proxy
kiwi-custodia setup                   # imágenes y datos de DNS

kiwi-proxy add client-a socks5://user:pass@jump.client-a.example:1080 --dns remote
kiwi-custodia new client-a --exit client-a --distro fedora
kiwi-custodia enter client-a          # una shell cuya única salida es el SOCKS5 del cliente A
```
