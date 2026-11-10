# Repositorios y estado

En esta página están todos los repositorios del proyecto Kiwi Network, con lo
que es cada uno, su última versión y su licencia. Al final se enumera lo que se
sabe que falta o que aún no se ha probado.

Todos los repositorios están en [github.com/derlocke-ng](https://github.com/derlocke-ng).
«Publicado» significa que un repositorio tiene un tag de versión, porque eso es
lo que instala kiwi-updater. Las versiones corresponden a noviembre de 2026.

## La red { #the-network }

| Repositorio | Qué es | Versión | Catálogo | Licencia |
|---|---|---|---|---|
| [kiwi-server](https://github.com/derlocke-ng/kiwi-server) | construye y administra la red: convierte el archivo fleet en ISO de instalación y aplica por SSH el rol de cada máquina | v2.42.0 | sí | GPL-3.0+ |
| [kiwi-modules](https://github.com/derlocke-ng/kiwi-modules) | los 20 módulos y su generador, que convierte un archivo de máquina en un paquete de stack | v0.23.0 | no | GPL-3.0+ |
| [kiwi-stack](https://github.com/derlocke-ng/kiwi-stack) | la parte que se ejecuta en la máquina: instala un paquete en ella y lo mantiene en marcha | v0.5.0 | no | GPL-3.0+ |
| [mullvad-socks5](https://github.com/derlocke-ng/mullvad-socks5) | listas y registros DNS de los proxies SOCKS5 de Mullvad, que se regeneran cada 6 horas | la rama `list` | no | MIT (README) |

## Personas { #people }

| Repositorio | Qué es | Versión | Licencia |
|---|---|---|---|
| [kiwi-framework](https://github.com/derlocke-ng/kiwi-framework) | el framework con el que se hacen hubs comunitarios federados sobre nostr | v0.32.1 | GPL-3.0+ |
| [Armory](https://github.com/derlocke-ng/armory) | el primer hub hecho con kiwi-framework, con diez herramientas web entre pares ([en vivo](https://derlocke-ng.github.io/armory/)) | sigue a `main` (0.1.0) | GPL-3.0+ |
| [kiwi-web-catalog](https://github.com/derlocke-ng/kiwi-web-catalog) | un catálogo de hubs y de sus apps | (una lista) | CC0 (README) |

## El escritorio { #the-desktop }

| Repositorio | Qué es | Versión | Catálogo | Licencia |
|---|---|---|---|---|
| [kiwi-updater](https://github.com/derlocke-ng/kiwi-updater) | instala y actualiza apps desde catálogos git | v2.4.0 | sí | GPL-3.0+ |
| [kiwi-catalog](https://github.com/derlocke-ng/kiwi-catalog) | el catálogo de apps de Kiwi | (una lista) | n/a | no indicada |
| [ensconce](https://github.com/derlocke-ng/ensconce) | configura Bluefin-DX después de instalarlo | v2.5.0 | sí | GPL-3.0+ |
| [kiwi-killswitch](https://github.com/derlocke-ng/kiwi-killswitch) | un kill switch de VPN fail-closed para GNOME: si se cae la conexión VPN, el tráfico queda bloqueado | v0.2.3 | sí | GPL-3.0+ |
| [kiwi-proxy](https://github.com/derlocke-ng/kiwi-proxy) | exits SOCKS5 y VPN en Podman rootless; cada exit es una conexión guardada con un nombre, encerrada en un contenedor cuya única ruta es esa conexión | v0.7.3 | sí | GPL-3.0+ |
| [kiwi-custodia](https://github.com/derlocke-ng/kiwi-custodia) | boxes (distribuciones de Linux en contenedores) cuyo tráfico solo puede salir a Internet por un exit de kiwi-proxy | v0.2.3 | sí | GPL-3.0+ |
| [kiwi-fox](https://github.com/derlocke-ng/kiwi-fox) | identidades de navegador aisladas que se conectan a través de exits de kiwi-proxy | v0.7.1 | sí | GPL-3.0+ |
| [kiwi-plugin-tor](https://github.com/derlocke-ng/kiwi-plugin-tor) | proveedor para kiwi-proxy: Tor | v0.3.0 | sí | GPL-3.0+ |
| [kiwi-plugin-vpn](https://github.com/derlocke-ng/kiwi-plugin-vpn) | proveedor para kiwi-proxy: una VPN mediante gluetun | v0.2.2 | sí | GPL-3.0+ |
| [kiwi-plugin-9proxy](https://github.com/derlocke-ng/kiwi-plugin-9proxy) | proveedor para kiwi-proxy: 9proxy | v0.2.0 | sí | GPL-3.0+ |
| [kiwi-plugin-myst](https://github.com/derlocke-ng/kiwi-plugin-myst) | proveedor para kiwi-proxy: Mysterium | v0.5.2 | sí | GPL-3.0+ |
| [gnome-monitor](https://github.com/derlocke-ng/gnome-monitor) | disposiciones de las pantallas para GNOME | v0.3.2 | sí | GPL-3.0+ |
| [syncman](https://github.com/derlocke-ng/syncman) | sincronización de carpetas en ambos sentidos, con servicios de usuario de systemd | v0.4.1 | sí | GPL-3.0+ |
| [kiwi-cli-tools-desktop](https://github.com/derlocke-ng/kiwi-cli-tools-desktop) | `pweb`, `select-server`, `tethering`, `torlink` | v1.2.1 | sí | GPL-3.0+ |
| [kiwi-gen](https://github.com/derlocke-ng/kiwi-gen) | crea claves y certificados SSH y TLS sin conexión, en el navegador ([en vivo](https://derlocke-ng.github.io/kiwi-gen/)) | página web | no | MIT |
| [kiwi-icons](https://github.com/derlocke-ng/kiwi-icons) | los iconos de las apps ([vista previa](https://derlocke-ng.github.io/kiwi-icons/)) | sin tags | no | no indicada |
| [kiwi-network](https://github.com/derlocke-ng/kiwi-network) | este sitio web y esta documentación | n/a | n/a | AGPL-3.0 |

## Carencias conocidas { #known-gaps }

Los propios repositorios señalan estas carencias:

- **kiwi-server**: Se ha probado en hardware real, en octubre y noviembre de
  2026. En esas pruebas se restauraron las copias de seguridad de un node en
  otro y se ajustó la MTU del túnel, también para conexiones móviles. Hay
  cuatro novedades en las ramas `several-servers` de kiwi-server y kiwi-modules
  que todavía no se han publicado: varios servidores de copias de seguridad, la
  restauración automática de una máquina reconstruida, un temporizador para
  eliminar los snapshots antiguos y una comprobación de estado (health check)
  que reinicia una conexión atascada con el proveedor de VPN comercial. Aún no
  se ha demostrado que la federación entre redes funcione. Todo funciona solo
  con IPv4, y la ISO de Debian solo existe para amd64. El plano de control está
  diseñado, aún sin implementar.
- **kiwi-modules**: Los módulos de OpenCloud, Immich y Paperless-ngx están
  marcados como «para probar». Hay un servidor TURN para llamadas pendiente de
  fusionarse.
- **kiwi-stack**: No hay forma de deshacer un `apply`. Solo puedes restaurar
  los datos y volver a aplicar un paquete anterior.
- **kiwi-framework**: Faltan todavía varias partes: el blog, las aprobaciones
  de moderación, poder seguir espacios que un hub no trae incluidos y los
  firmantes NIP-07/NIP-46.
- **kiwi-updater**: Está previsto un registro alojado de catálogos de
  confianza. Los tags de versión de las demás apps todavía no están firmados.
  Por eso, la parte de kiwi-killswitch que se ejecuta como root pide una
  contraseña cuando se actualiza.
- **kiwi-proxy**: Su módulo para kiwi-server todavía no ha funcionado en
  ninguna máquina. Los exits solo transportan TCP e IPv4. El módulo VPN admite
  una sola configuración por máquina.
- **Módulos de proveedor**: Los módulos de VPN y de 9proxy no se han validado
  de principio a fin con una cuenta real. El módulo de Mysterium sí se validó,
  el 7 de noviembre de 2026.
- **kiwi-custodia**: Aún hay cosas que medir en una máquina real: tun2socks en
  un contenedor gateway rootless y compositores distintos de GNOME.
- **Licencias**: kiwi-icons, kiwi-catalog y mullvad-socks5 no tienen archivo
  LICENSE, y kiwi-killswitch solo indica su licencia en el README y en el
  manifiesto.
