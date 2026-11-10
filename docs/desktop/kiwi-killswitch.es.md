# kiwi-killswitch

Un **kill switch de VPN que falla cerrado** para GNOME en Fedora Silverblue y
Bluefin. Un único demonio de root controla el cortafuegos. Un interruptor en los
Ajustes rápidos de GNOME, una app GTK4 y una CLI lo manejan a través del bus de
sistema D-Bus, sin pedir nunca una contraseña.

Protege **una** conexión VPN cada vez, WireGuard u OpenVPN. No conecta tu VPN por
ti: levantas las conexiones en la Configuración de GNOME, y el kill switch
construye un cortafuegos sin fugas alrededor de lo que realmente está activo.

- Repositorio: [derlocke-ng/kiwi-killswitch](https://github.com/derlocke-ng/kiwi-killswitch), GPL-3.0-or-later
- Última versión: **v0.2.3**. Está en el [catálogo de Kiwi](catalogs.md), ámbitos de usuario + sistema.
- GNOME Shell 45 a 50.

```
┌─ your session (unprivileged) ─────────────┐   ┌─ root ──────────────────────┐
│  GNOME Quick Settings toggle              │   │  kiwi-killswitchd           │
│  kiwi-killswitch-settings (GTK4)          │──▶│   nftables  (inet + netdev) │
│  kiwi-killswitch (CLI)                    │   │   systemd-resolved steering │
└───────────────────────────────────────────┘   │   NM + kernel event watcher │
             D-Bus system bus, group `wheel`    └─────────────────────────────┘
```

Una extensión de GNOME es un proceso sin privilegios. No puede ni debe tocar el
cortafuegos, así que la aplicación de las reglas vive en el demonio y la
interfaz solo pide.

## Qué hace { #what-it-does }

- **Falla cerrado.** `policy drop` en salida, entrada y reenvío, IPv4 e IPv6,
  cambiado de forma atómica. El tráfico solo sale por el túnel protegido. Si la
  VPN se cae, reinicias o pasas de Wi-Fi a compartir conexión, todo sigue
  bloqueado hasta que vuelve un camino permitido.
- **Las interfaces nuevas no pueden filtrar.** Conecta la compartición de
  conexión por USB o activa el Wi-Fi con el kill switch armado, y la interfaz
  nueva queda bloqueada por defecto, no permitida por omisión.
- **Tres niveles de aplicación.** *Standard* filtra la salida y la entrada.
  *Strict* (el valor por defecto) filtra además el tráfico **reenviado**, porque
  los contenedores, las VM y Waydroid enrutan a través del host y los paquetes
  reenviados nunca pasan por el hook de salida. *Paranoid* añade una cadena
  **netdev egress** en cada tarjeta de red, la única capa que ve el tráfico de
  raw sockets.
- **El DNS no puede escaparse.** Elige a través de la VPN, el propio de la red
  (solo kiwi-nodes de confianza) o un resolvedor que tú elijas. Se aplica
  mediante los ajustes por enlace de systemd-resolved, con una red de seguridad
  de nftables que descarta cualquier otra consulta.
- **Los endpoints por nombre de host se fijan, no se confían al DNS.** El demonio
  resuelve él mismo el nombre de host de un servidor VPN, por DNS-over-HTTPS
  hacia una IP fijada con un certificado verificado, y guarda en caché cada
  respuesta.
- **Elige una conexión y luego aplica (Apply).** Los cambios se preparan antes,
  así que puedes pasar de «LAN de casa + kiwi-node» a «compartir conexión + VPN»
  *estando ya en la conexión compartida*, y aplicarlo como una sola transacción
  atómica sin ningún intervalo desarmado entre medias.
- **kiwi-nodes de confianza.** Una puerta de enlace que ya hace de túnel por ti
  (un [node gateway](../server/roles.md#node)), identificada por IP **y** MAC,
  puede sustituir a la VPN en su propia red. Hay que activarlo expresamente y
  nunca se deduce.
- **Una VPN, aplicada.** Solo se puede llegar al servidor de la conexión
  seleccionada. Cualquier otro túnel que inicies no puede conectarse, y la
  interfaz lo nombra.
- **Lo aguanta todo.** Reinicios, cerrar e iniciar sesión, reinicios de
  NetworkManager: las reglas se quedan. Una unidad aparte instala un bloqueo
  total *antes de que la red se levante*.

## Instalación { #install }

Requiere `nftables`, `NetworkManager`, `python3-gobject` y, para WireGuard,
`wireguard-tools`, todos presentes en Silverblue y Bluefin. No se escribe nada
en el `/usr` inmutable. Tu usuario debe estar en `wheel`.

```bash
kiwi install kiwi-killswitch   # both halves; sets up kiwi's system scope if needed
```

O desde un clon: `sudo ./install.sh install` (el demonio, la CLI, la política del
bus y las unidades systemd) y luego `./install.sh install` (la extensión de GNOME
y la app de ajustes). Cierra sesión y vuelve a entrar para que GNOME cargue la
extensión. Al desinstalar, primero se desarma, así que no puede dejarte sin
conexión.

## Uso { #use }

Abre **Ajustes rápidos → Kill Switch** para armar, desarmar y elegir qué VPN se
protege, o **Kiwi Kill Switch** en la cuadrícula de aplicaciones para todo lo
demás.

```bash
kiwi-killswitch status                   # qué se aplica ahora mismo
kiwi-killswitch list                     # conexiones VPN que conoce NetworkManager
kiwi-killswitch vpn <name>               # prepara cuál se protege
kiwi-killswitch set dns_mode tunnel
kiwi-killswitch apply                    # una sola transacción atómica
kiwi-killswitch arm                      # o: arm <vpn>
kiwi-killswitch disarm
kiwi-killswitch pending                  # lo que está preparado; revert lo descarta
```

!!! warning "Armar por SSH"
    Armar corta una sesión desde una subred que no está en `mgmt_subnets`. Es el
    comportamiento correcto de un kill switch. Fíjala antes:
    ```bash
    kiwi-killswitch set mgmt_subnets 192.168.0.0/16
    kiwi-killswitch set allow_in_ports 22
    kiwi-killswitch apply
    ```

**Recuperación.** La CLI no necesita red, así que una TTY siempre basta:
`kiwi-killswitch disarm`. Si el propio demonio ha desaparecido:
`sudo nft delete table inet kiwi_ks` y `sudo nft delete table netdev kiwi_ks_egress`.

**Máquinas virtuales.** Una VM en modo puente nunca enruta a través del host, así
que el kill switch la deja en paz (evita `paranoid`, que filtra en la tarjeta
física). Una VM con NAT enruta a través del host. `strict` la saca por el túnel
y la bloquea cuando el túnel está caído. Añade su subred a `mgmt_subnets` para
que su DHCP y su DNS lleguen al host:

| Ajuste | Saliente | Entrante | Fijada fuera del túnel |
|---|---|---|---|
| `allow_lan` | sí (auto) | no | no |
| `bypass_subnets` | sí | no | no |
| `mgmt_subnets` | sí | sí | sí |

**Verificación.** Ármalo y luego baja la VPN (`nmcli connection down …`).
`curl --max-time 5 ifconfig.me` debe **agotar el tiempo de espera**, no mostrar
tu IP real. No lo juzgues comparando IPs de salida: demuestra el uso del túnel
con `wg show <iface> transfer` o `ip route get 1.1.1.1`.

## Convivencia y límites conocidos { #coexistence-and-known-limits }

- **firewalld puede seguir activo.** Sus cadenas funcionan con prioridad 10 y las
  nuestras con −10.
- **No** lo ejecutes junto a otro kill switch que controle una tabla de descarte
  de salida.
- Deja en paz `nftables.service` si no lo usas. Detenerlo vacía todas las
  tablas. El demonio vuelve a imponer sus reglas en segundos, pero no hay motivo
  para abrir ese intervalo.
- Una VPN con un endpoint por **nombre de host** no puede reconectarse mientras
  está armado, salvo que el DNS esté en *un resolvedor que yo elija*.
  NetworkManager y OpenVPN buscan el nombre a través del resolvedor del sistema,
  que está bloqueado mientras no hay ningún túnel levantado. Las conexiones con
  una IP literal no se ven afectadas.
- **Un resolvedor que tú elijas es accesible fuera del túnel** mientras el túnel
  está caído. Activa DNS-over-TLS para él.
- **Un node de confianza guardado sin MAC** se identifica solo por su dirección
  de puerta de enlace.
- **El control sin contraseña** es la política del bus D-Bus para el grupo
  `wheel`. Eso también significa que cualquier programa que se ejecute con tu
  usuario puede apagar el interruptor sin preguntar.
- Detiene las fugas a nivel de red. No es Tails ni Whonix y no hace nada contra
  el fingerprinting del navegador, WebRTC o una app que llama a casa a través del
  túnel.
- Es una herramienta personal y no ha sido auditada de forma independiente.
  `tests/run.sh` pone a prueba el demonio real con nftables real, cada grupo de
  pruebas en su propio espacio de nombres, sin root.
- Sus tags de versión aún no están firmados, así que con kiwi-updater 2.4 su
  mitad de root te pide la contraseña cuando se actualiza.

Desciende de `gnome-vpn-killswitch` (orden de arranque), `kiwi-vpn-monitor`
(detección de la puerta de enlace) y `nova-killswitch` (la arquitectura del
demonio), del mismo autor.
