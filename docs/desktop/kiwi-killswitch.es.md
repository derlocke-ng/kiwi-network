# kiwi-killswitch

kiwi-killswitch es un **kill switch de VPN** para GNOME en Fedora Silverblue y
Bluefin. Un kill switch garantiza que tu ordenador no envíe tráfico fuera de la
VPN, por ejemplo cuando se cae la conexión VPN o cuando cambias a otra red.
Este es **fail-closed**: el cortafuegos bloquea todo lo que no esté permitido
de forma explícita, así que, si algo falla, el tráfico se queda bloqueado en
lugar de pasar.

El cortafuegos lo gestiona únicamente un daemon con permisos de root. Tú lo
controlas con un interruptor en los ajustes rápidos de GNOME (Quick Settings),
con una app GTK4 o con una herramienta de línea de comandos (CLI). Las tres
envían sus peticiones al daemon por el bus de sistema de D-Bus, y ninguna te
pide nunca la contraseña.

Protege **una** sola conexión VPN a la vez, de WireGuard o de OpenVPN. No
conecta la VPN por ti. Tus conexiones las inicias en la Configuración de GNOME,
y el kill switch adapta sus reglas de cortafuegos a la conexión que está
activa de verdad, de modo que ningún tráfico pueda salir del ordenador por
fuera de esa conexión.

- Repositorio: [derlocke-ng/kiwi-killswitch](https://github.com/derlocke-ng/kiwi-killswitch), GPL-3.0-or-later
- Última versión: **v0.2.3**. Está en el [catálogo de Kiwi](catalogs.md) y
  tiene dos ámbitos, de usuario y del sistema: una mitad se instala en tu
  carpeta personal y la otra pertenece a root.
- Funciona con GNOME Shell de la 45 a la 50.

```
┌─ your session (unprivileged) ─────────────┐   ┌─ root ──────────────────────┐
│  GNOME Quick Settings toggle              │   │  kiwi-killswitchd           │
│  kiwi-killswitch-settings (GTK4)          │──▶│   nftables  (inet + netdev) │
│  kiwi-killswitch (CLI)                    │   │   systemd-resolved steering │
└───────────────────────────────────────────┘   │   NM + kernel event watcher │
             D-Bus system bus, group `wheel`    └─────────────────────────────┘
```

Una extensión de GNOME es un proceso sin permisos de root. No puede modificar
el cortafuegos, y tampoco debe poder hacerlo. Por eso todo el bloqueo lo hace
el daemon, y la interfaz de usuario se limita a enviarle peticiones.

## Qué hace { #what-it-does }

- **Es fail-closed.** El cortafuegos usa `policy drop` para el tráfico
  saliente, el entrante y el reenviado, en IPv4 y en IPv6. Es decir, se
  descarta cualquier paquete que ninguna regla permita. Cada nuevo
  conjunto de reglas sustituye al anterior en un solo paso atómico. El tráfico
  solo puede salir por el túnel protegido. Si se cae la VPN, si reinicias o si
  pasas de la wifi a compartir la conexión del móvil, todo sigue bloqueado
  hasta que vuelve a haber un camino permitido.
- **Las interfaces de red nuevas quedan bloqueadas.** Si conectas el móvil por
  USB para compartir su conexión o activas la wifi mientras el kill switch está
  armado, es decir, activado, la nueva interfaz queda bloqueada por defecto. No
  se permite solo porque ninguna regla la mencione.
- **Hay tres niveles de filtrado.** *Standard* filtra el tráfico saliente y el
  entrante. *Strict* es el nivel por defecto y filtra además el tráfico
  **reenviado**. Esto hace falta porque los contenedores, las máquinas
  virtuales y Waydroid envían su tráfico a través del host, y los paquetes
  reenviados nunca pasan por el hook de salida. *Paranoid* añade una cadena
  **netdev egress** en cada tarjeta de red (NIC). Es la única capa que ve el
  tráfico de los sockets raw.
- **Las consultas DNS no pueden saltarse el túnel.** Tú eliges qué resolvedor
  DNS se usa mientras el kill switch está armado: puedes enviar las consultas
  DNS por la VPN, usar el resolvedor de la red en la que estás o usar uno que
  elijas tú. El resolvedor propio de la red solo se usa en la red de un
  kiwi-node de confianza. El kill switch aplica tu elección mediante los
  ajustes por enlace de systemd-resolved. Como segunda protección, una regla de
  nftables descarta cualquier otra consulta DNS.
- **Si el servidor VPN se indica con un nombre de host, el daemon no se fía
  del DNS normal.** Resuelve él mismo el nombre del servidor VPN. Para ello usa
  DNS sobre HTTPS, se conecta a una dirección IP fijada de antemano y verifica
  el certificado. Guarda en caché todas las respuestas.
- **Primero eliges una conexión y después aplicas.** Los cambios quedan
  preparados, es decir, se van acumulando y solo surten efecto cuando los
  aplicas. Así puedes pasar de «red local de casa + kiwi-node» a «tethering +
  VPN» *cuando ya estás usando el tethering*. Al aplicar, todos los cambios se
  hacen en una sola transacción atómica, y el kill switch no se desarma en
  ningún momento entre medias.
- **Kiwi-nodes de confianza.** Puede que tu red tenga una puerta de enlace que
  ya envía tu tráfico por un túnel. En una red Kiwi, eso es un
  [node gateway](../server/roles.md#node). En su propia red, una puerta de
  enlace así puede ocupar el lugar de la VPN. El kill switch la reconoce por su
  dirección IP **y** por su dirección MAC. Esto lo tienes que activar tú: el
  kill switch nunca decide por su cuenta que una puerta de enlace es de
  confianza.
- **Solo se puede conectar una VPN.** Solo se puede llegar al servidor de la
  conexión elegida. Cualquier otro túnel que inicies no podrá conectarse, y la
  interfaz de usuario te indica de qué túnel se trata.
- **Las reglas se mantienen.** Siguen ahí después de un reinicio, después de
  cerrar sesión y volver a entrar, y después de que NetworkManager se
  reinicie. Una unidad aparte carga reglas de bloqueo *antes de que se active
  la red*.

## Instalación { #install }

kiwi-killswitch necesita `nftables`, `NetworkManager` y `python3-gobject`, y
para WireGuard también `wireguard-tools`. Todo eso ya está en Silverblue y en
Bluefin. No se escribe nada en el `/usr` inmutable. Tu usuario tiene que estar
en el grupo `wheel`.

```bash
kiwi install kiwi-killswitch   # las dos mitades; prepara el ámbito del sistema de kiwi si hace falta
```

También puedes instalarlo desde un clon del repositorio. Ejecuta primero
`sudo ./install.sh install`, que instala el daemon, la CLI, la política de
D-Bus y las unidades de systemd. Después ejecuta `./install.sh install`, que
instala la extensión de GNOME y la app de ajustes. Cierra sesión y vuelve a
entrar para que GNOME cargue la extensión. Al desinstalarlo, primero se
desarma el kill switch, así que la desinstalación no puede dejarte con la red
bloqueada.

## Uso { #use }

En **Quick Settings → Kill Switch** (los ajustes rápidos de GNOME) armas y
desarmas el kill switch y eliges qué VPN se protege. Para todo lo demás, abre
**Kiwi Kill Switch** en la cuadrícula de aplicaciones. La CLI tiene estos
comandos:

```bash
kiwi-killswitch status                   # qué se está aplicando ahora mismo
kiwi-killswitch list                     # las conexiones VPN que conoce NetworkManager
kiwi-killswitch vpn <name>               # preparar cuál se protege
kiwi-killswitch set dns_mode tunnel
kiwi-killswitch apply                    # una sola transacción atómica
kiwi-killswitch arm                      # o: arm <vpn>
kiwi-killswitch disarm
kiwi-killswitch pending                  # qué está preparado; revert lo descarta
```

!!! warning "Armar el kill switch por SSH"
    Al armar el kill switch se corta cualquier sesión SSH que venga de una
    subred que no esté en `mgmt_subnets`. Es lo que debe hacer un kill switch.
    Si trabajas por SSH, define antes estos valores:
    ```bash
    kiwi-killswitch set mgmt_subnets 192.168.0.0/16
    kiwi-killswitch set allow_in_ports 22
    kiwi-killswitch apply
    ```

**Recuperación.** La CLI no necesita red, así que para ejecutar
`kiwi-killswitch disarm` siempre basta con una consola de texto (TTY). Si el
propio daemon ha desaparecido, borra sus tablas del cortafuegos con
`sudo nft delete table inet kiwi_ks` y
`sudo nft delete table netdev kiwi_ks_egress`.

**Máquinas virtuales.** Una máquina virtual en modo puente (bridge) nunca envía
su tráfico a través del host, así que el kill switch no le afecta. En ese caso,
evita `paranoid`, porque ese nivel filtra en la tarjeta de red física. Una
máquina virtual con NAT sí envía su tráfico a través del host. Con `strict`,
ese tráfico sale por el túnel y se bloquea cuando el túnel está caído. Añade la
subred de la máquina virtual a `mgmt_subnets` para que sus peticiones DHCP y
DNS lleguen al host. La tabla muestra qué permite cada ajuste:

| Ajuste | Saliente | Entrante | Fuera del túnel |
|---|---|---|---|
| `allow_lan` | sí (automático) | no | no |
| `bypass_subnets` | sí | no | no |
| `mgmt_subnets` | sí | sí | sí |

**Comprobar que funciona.** Arma el kill switch y después desactiva la VPN con
`nmcli connection down …`. Ahora, `curl --max-time 5 ifconfig.me` tiene que
**agotar el tiempo de espera**. No debe mostrar tu dirección IP real. No
juzgues el resultado comparando las direcciones IP públicas que ves. Para
demostrar que el tráfico pasa por el túnel, ejecuta `wg show <iface> transfer`
o `ip route get 1.1.1.1`.

## Otros cortafuegos y limitaciones conocidas { #coexistence-and-known-limits }

- **firewalld puede seguir activo.** Sus cadenas se ejecutan con prioridad 10,
  y las del kill switch, con −10.
- **No** lo uses junto con otro kill switch que tenga su propia tabla para
  descartar el tráfico saliente.
- No toques `nftables.service` si no lo usas. Cuando ese servicio se detiene,
  borra todas las tablas de nftables. El daemon vuelve a cargar sus reglas en
  unos segundos, pero durante esos segundos las reglas no están, y no hay
  ningún motivo para provocarlo.
- Una VPN cuyo servidor se indica con un **nombre de host** no puede volver a
  conectarse mientras el kill switch está armado, salvo que el DNS esté
  configurado como *un resolvedor que elijo yo*. El motivo es que
  NetworkManager y OpenVPN resuelven el nombre con el resolvedor del sistema,
  y ese resolvedor está bloqueado mientras no hay ningún túnel activo. Las
  conexiones cuyo servidor se indica con una dirección IP no se ven afectadas.
- **Un resolvedor que elijas tú es accesible por fuera del túnel** mientras el
  túnel está caído. Activa DNS sobre TLS para él.
- **Un node de confianza que se guardó sin dirección MAC** se reconoce solo
  por la dirección de su puerta de enlace.
- **El control sin contraseña** funciona gracias a la política de D-Bus para el
  grupo `wheel`. Eso también significa que cualquier programa que se ejecute
  con tu usuario puede desactivar el kill switch sin preguntarte.
- kiwi-killswitch evita las fugas a nivel de red, pero no es Tails ni Whonix. No hace nada contra
  el fingerprinting del navegador, contra WebRTC ni contra una app que envíe
  datos a su fabricante a través del túnel.
- Es una herramienta personal y no ha pasado ninguna auditoría independiente.
  `tests/run.sh` prueba el daemon real con nftables real. Cada grupo de pruebas
  se ejecuta en su propio namespace, y las pruebas no necesitan root.
- Sus etiquetas de versión todavía no están firmadas. Por eso, con
  kiwi-updater 2.4, su mitad de root te pide la contraseña cuando se actualiza.

kiwi-killswitch se basa en tres herramientas anteriores del mismo autor. El
orden de arranque viene de `gnome-vpn-killswitch`, la detección de la puerta de
enlace de `kiwi-vpn-monitor` y la arquitectura del daemon de
`nova-killswitch`.
