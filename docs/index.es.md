---
hide:
  - toc
---

<div class="kiwi-hero" markdown>

![](assets/logo.svg)

<p class="kiwi-motto">Ex fructu arbor agnoscitur</p>

# Kiwi Network

<p class="kiwi-lede">Tu propia red privada: un master en la puerta, nodes detrás, cada máquina tuya. Construida a partir de un solo archivo, con una sola puerta a Internet.</p>

[Cómo funciona](network/index.md){ .md-button .md-button--primary }
[Construye una](server/index.md){ .md-button }

</div>

<div class="kiwi-cards" markdown>

<a href="network/">
<strong>La red</strong>
<span>Un master, muchos nodes, una malla WireGuard. Grupos de clientes, una salida de doble salto, DNS y certificados propios.</span>
<em>Cómo funciona →</em>
</a>

<a href="server/">
<strong>kiwi-server</strong>
<span>El archivo fleet, ISOs de instalación, aplicar por SSH, altas, copias de seguridad, desbloqueo. CLI y app GTK.</span>
<em>Construye una red →</em>
</a>

<a href="server/modules/">
<strong>Módulos</strong>
<span>Los 20: WireGuard, Pi-hole, Tor, Nextcloud, Vaultwarden, copias de seguridad, Tang, Immich, Paperless-ngx y más.</span>
<em>Qué puede ser un node →</em>
</a>

<a href="people/">
<strong>Hubs</strong>
<span>kiwi-framework: mercados abiertos, feeds, chat y compartir sobre nostr, sellado en el navegador. Armory es el primero.</span>
<em>Hubs, no plataformas →</em>
</a>

<a href="desktop/">
<strong>El escritorio</strong>
<span>kiwi-updater y las apps para Fedora Atomic: kill switch, salidas selladas para redes de clientes, instalación, sincronización.</span>
<em>Apps desde git →</em>
</a>

<a href="project/status/">
<strong>Estado</strong>
<span>Cada repositorio, su versión y sus carencias conocidas, descritos tal como son.</span>
<em>Dónde están las cosas →</em>
</a>

</div>

## La idea { #the-idea }

Kiwi Network es un entorno Linux totalmente automatizado para vivir y trabajar:
seguro, sólido y a salvo para una vida en línea dura. Tus máquinas se cuidan
solas.

- **Se instalan solas.** Una ISO desatendida por máquina, o directamente en un
  servidor alquilado a través de la API del proveedor (hoy netcup, más
  [previstos](server/roadmap.md#more-hosters-and-network-boot)).
- **Se mantienen al día solas.** Las actualizaciones se instalan de forma
  continua, y los reinicios esperan a la ventana que fijes.
- **Hacen sus propias copias de seguridad.** Cada noche, cifradas y solo de
  anexado, en nodes de copia de seguridad propios. El archivo fleet y sus
  secretos también tienen copia de seguridad.
- **Vuelven a levantarse.** Los discos cifrados se desbloquean a través de Tang,
  o en remoto cuando algo va mal, y una máquina reconstruida vuelve a partir del
  archivo fleet y de su copia de seguridad.

## Las máquinas { #the-machines }

| Rol | En qué se convierte la máquina |
|---|---|
| `master` | la puerta: WireGuard, una salida de doble salto o directa, Pi-hole, Tor, las páginas de administración y, opcionalmente, un relay nostr y un hub |
| `node` · `gateway` | una LAN a través de la VPN, con Pi-hole como DNS y DHCP, una estación de descargas y SFTP |
| `node` · `cloud` | Nextcloud con Collabora, y Vaultwarden |
| `node` · `minimal` | el túnel y nginx, para los módulos que elijas: copias de seguridad, Tang, Immich, Paperless-ngx, OpenCloud |
| `bare` | solo el sistema base |

Los masters llevan nombres de postres de fruta (sorbet, crumble, compote), y los
nodes, nombres de frutas (papaya, lychee, quince). El master es la única máquina
que tiene que ser accesible desde Internet y, por defecto, publica un puerto:
WireGuard, UDP 51820.

```bash
kiwi install kiwi-server            # o desde un clon: ./install.sh install
kiwi-server init && $EDITOR fleet.yaml
kiwi-server build fleet.yaml        # una ISO desatendida por máquina
kiwi-server apply fleet.yaml papaya # el rol, por SSH
```
