---
hide:
  - toc
---

<div class="kiwi-hero" markdown>

![](assets/logo.svg)

<p class="kiwi-motto">Ex fructu arbor agnoscitur</p>

# Kiwi Network

<p class="kiwi-lede">Un entorno Linux de código abierto que gestionas tú mismo: tus servidores, tus dispositivos y tu escritorio, unidos en una sola red privada. Se instala solo, se mantiene al día, hace una copia de seguridad cada noche y se puede reconstruir cuando algo se estropea.</p>

[Cómo funciona](network/index.md){ .md-button .md-button--primary }
[Monta tu red](server/index.md){ .md-button }

</div>

<div class="kiwi-cards" markdown>

<a href="network/">
<strong>La red</strong>
<span>Tus servidores y dispositivos en una red WireGuard privada. Solo un servidor es accesible desde Internet; los demás se quedan en casa.</span>
<em>Cómo funciona →</em>
</a>

<a href="server/">
<strong>kiwi-server</strong>
<span>La herramienta con la que montas y mantienes la red: un único archivo para todas las máquinas, instalación automática, copias de seguridad y desbloqueo de discos.</span>
<em>Montar una red →</em>
</a>

<a href="server/modules/">
<strong>Módulos</strong>
<span>Los 20 servicios que puede ejecutar una máquina, desde WireGuard y Pi-hole hasta Nextcloud, Vaultwarden, copias de seguridad e Immich.</span>
<em>Qué puede ejecutar un node →</em>
</a>

<a href="people/">
<strong>Hubs</strong>
<span>Con kiwi-framework, una comunidad tiene su propio hub, con un mercado abierto, un feed y chat, y sin ninguna plataforma central.</span>
<em>Hubs para comunidades →</em>
</a>

<a href="desktop/">
<strong>El escritorio</strong>
<span>Una estación de trabajo con Fedora Atomic y apps que llegan directamente de git: un kill switch para la VPN, conexiones aisladas para las redes de tus clientes, configuración inicial y sincronización.</span>
<em>Apps de escritorio →</em>
</a>

<a href="project/status/">
<strong>Estado</strong>
<span>Todos los repositorios, con su versión actual y lo que todavía les falta.</span>
<em>Estado actual →</em>
</a>

</div>

## La idea { #the-idea }

Internet es un lugar hostil, y cuidar de tus propios servidores es un trabajo
que no se acaba nunca. Kiwi Network te lo quita de encima. Describes tus
máquinas en un solo archivo y las tareas rutinarias se hacen solas. El diseño
cuenta desde el principio con intrusiones, discos que fallan y máquinas que se
pierden.

- **Instalación automática.** Cada máquina se instala sin que nadie tenga que
  estar delante del teclado: desde su propia imagen de instalación o
  directamente en un servidor alquilado, mediante la API del proveedor de
  hosting. Hoy funciona con netcup, y están
  [previstos](server/roadmap.md#more-hosters-and-network-boot) más proveedores.
- **Actualizaciones automáticas.** Las actualizaciones se instalan solas. Una
  máquina solo se reinicia en las horas que tú hayas permitido.
- **Una copia de seguridad cada noche.** Cada máquina envía una copia de
  seguridad cifrada a un servidor de copias de seguridad que es tuyo. Puede
  añadir a sus copias, pero no borrarlas, así que un intruso no puede
  destruirlas. También se hace copia de seguridad del archivo fleet (el archivo
  que describe tus máquinas) y de sus secretos.
- **Recuperación cuando hace falta.** Los discos están cifrados. Las máquinas
  los desbloquean solas al arrancar, o los desbloqueas tú a distancia. Si hay
  que reconstruir una máquina, su configuración sale del archivo fleet y sus
  datos, de la copia de seguridad.

## Las máquinas { #the-machines }

Cada máquina tiene un rol, que determina qué hace en la red.

| Rol | Qué hace la máquina |
|---|---|
| `master` | Es la única máquina accesible desde Internet. En ella funciona el servidor de WireGuard. Envía el tráfico saliente por un proveedor de VPN o directamente a Internet, y ofrece DNS con Pi-hole, Tor y las páginas de administración. También puede alojar un relay de nostr y un hub. |
| `node` · `gateway` | Envía toda una red doméstica o de oficina por la VPN, con Pi-hole como servidor DNS y DHCP, una estación de descargas y SFTP. |
| `node` · `cloud` | Ejecuta Nextcloud con Collabora, y también Vaultwarden. |
| `node` · `minimal` | Solo tiene la conexión a la red y nginx. Los módulos los añades tú, por ejemplo copias de seguridad, Tang, Immich, Paperless-ngx u OpenCloud. |
| `bare` | Solo tiene el sistema base. |

Los masters llevan nombres de postres de fruta (sorbet, crumble, compote) y los
nodes, nombres de frutas (papaya, lychee, quince). El master es la única máquina
que tiene que ser accesible desde Internet. Por defecto solo tiene un puerto
abierto: el de WireGuard, UDP 51820.

```bash
kiwi install kiwi-server            # o desde un clon: ./install.sh install
kiwi-server init && $EDITOR fleet.yaml
kiwi-server build fleet.yaml        # una ISO de instalación desatendida por máquina
kiwi-server apply fleet.yaml papaya # el rol, por SSH
```
