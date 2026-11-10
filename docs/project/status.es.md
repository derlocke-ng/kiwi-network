# Repositorios y estado

Todos los repositorios viven en [github.com/derlocke-ng](https://github.com/derlocke-ng).
«Publicado» significa un tag de versión, que es lo que instala kiwi-updater. Las
versiones corresponden a noviembre de 2026.

## La red { #the-network }

| Repositorio | Qué es | Versión | Catálogo | Licencia |
|---|---|---|---|---|
| [kiwi-server](https://github.com/derlocke-ng/kiwi-server) | construye y gestiona la red: archivo fleet → ISOs de instalación → apply por SSH | v2.42.0 | sí | GPL-3.0+ |
| [kiwi-modules](https://github.com/derlocke-ng/kiwi-modules) | los 20 módulos y su renderizador: un archivo de máquina → un paquete de stack | v0.23.0 | no | GPL-3.0+ |
| [kiwi-stack](https://github.com/derlocke-ng/kiwi-stack) | la parte de la máquina: pone un paquete en una máquina y lo mantiene en marcha | v0.5.0 | no | GPL-3.0+ |
| [mullvad-socks5](https://github.com/derlocke-ng/mullvad-socks5) | los proxies SOCKS5 de Mullvad como listas y registros DNS, regenerados cada 6 horas | la rama `list` | no | MIT (README) |

## Personas { #people }

| Repositorio | Qué es | Versión | Licencia |
|---|---|---|---|
| [kiwi-framework](https://github.com/derlocke-ng/kiwi-framework) | el motor de los hubs comunitarios federados sobre nostr | v0.32.1 | GPL-3.0+ |
| [Armory](https://github.com/derlocke-ng/armory) | el primer hub: diez herramientas web entre pares ([en línea](https://derlocke-ng.github.io/armory/)) | sigue `main` (0.1.0) | GPL-3.0+ |
| [kiwi-web-catalog](https://github.com/derlocke-ng/kiwi-web-catalog) | un catálogo de hubs y sus apps | (una lista) | CC0 (README) |

## El escritorio { #the-desktop }

| Repositorio | Qué es | Versión | Catálogo | Licencia |
|---|---|---|---|---|
| [kiwi-updater](https://github.com/derlocke-ng/kiwi-updater) | instala y actualiza apps desde catálogos git | v2.4.0 | sí | GPL-3.0+ |
| [kiwi-catalog](https://github.com/derlocke-ng/kiwi-catalog) | el catálogo de apps de Kiwi | (una lista) | n/a | no indicada |
| [ensconce](https://github.com/derlocke-ng/ensconce) | configuración posterior a la instalación para Bluefin-DX | v2.5.0 | sí | GPL-3.0+ |
| [kiwi-killswitch](https://github.com/derlocke-ng/kiwi-killswitch) | kill switch de VPN que falla cerrado para GNOME | v0.2.3 | sí | GPL-3.0+ |
| [kiwi-proxy](https://github.com/derlocke-ng/kiwi-proxy) | salidas SOCKS5/VPN selladas en Podman sin root | v0.7.3 | sí | GPL-3.0+ |
| [kiwi-custodia](https://github.com/derlocke-ng/kiwi-custodia) | distro boxes cuyo tráfico solo sale por una salida | v0.2.3 | sí | GPL-3.0+ |
| [kiwi-fox](https://github.com/derlocke-ng/kiwi-fox) | identidades de navegador aisladas en salidas de kiwi-proxy | v0.7.1 | sí | GPL-3.0+ |
| [kiwi-plugin-tor](https://github.com/derlocke-ng/kiwi-plugin-tor) | proveedor de kiwi-proxy: Tor | v0.3.0 | sí | GPL-3.0+ |
| [kiwi-plugin-vpn](https://github.com/derlocke-ng/kiwi-plugin-vpn) | proveedor de kiwi-proxy: una VPN a través de gluetun | v0.2.2 | sí | GPL-3.0+ |
| [kiwi-plugin-9proxy](https://github.com/derlocke-ng/kiwi-plugin-9proxy) | proveedor de kiwi-proxy: 9proxy | v0.2.0 | sí | GPL-3.0+ |
| [kiwi-plugin-myst](https://github.com/derlocke-ng/kiwi-plugin-myst) | proveedor de kiwi-proxy: Mysterium | v0.5.2 | sí | GPL-3.0+ |
| [gnome-monitor](https://github.com/derlocke-ng/gnome-monitor) | distribuciones de pantallas para GNOME | v0.3.2 | sí | GPL-3.0+ |
| [syncman](https://github.com/derlocke-ng/syncman) | sincronización de carpetas en ambos sentidos como servicios de usuario | v0.4.1 | sí | GPL-3.0+ |
| [kiwi-cli-tools-desktop](https://github.com/derlocke-ng/kiwi-cli-tools-desktop) | `pweb`, `select-server`, `tethering`, `torlink` | v1.2.1 | sí | GPL-3.0+ |
| [kiwi-gen](https://github.com/derlocke-ng/kiwi-gen) | claves y certificados SSH y TLS, sin conexión en el navegador ([en línea](https://derlocke-ng.github.io/kiwi-gen/)) | página web | no | MIT |
| [kiwi-icons](https://github.com/derlocke-ng/kiwi-icons) | los iconos de las apps ([vista previa](https://derlocke-ng.github.io/kiwi-icons/)) | sin tags | no | no indicada |
| [kiwi-network](https://github.com/derlocke-ng/kiwi-network) | este sitio web y esta documentación | n/a | n/a | AGPL-3.0 |

## Carencias conocidas { #known-gaps }

Según los propios repositorios:

- **kiwi-server**: probado en hardware en octubre–noviembre de 2026, con copias
  de seguridad de nodes restauradas entre nodes y la MTU del túnel ajustada,
  también en rutas móviles. Varios servidores de copias de seguridad, la
  restauración automática de una máquina reconstruida, un temporizador de
  limpieza y una comprobación de salud para una salida comercial atascada están
  en las ramas `several-servers` de kiwi-server y kiwi-modules, aún sin publicar.
  La federación entre redes todavía no está probada. Solo IPv4, y la ISO de
  Debian es solo amd64. El plano de control está diseñado, no construido.
- **kiwi-modules**: OpenCloud, Immich y Paperless-ngx están «para probar». Un
  servidor TURN para llamadas está esperando a fusionarse.
- **kiwi-stack**: no hay vuelta atrás más allá de restaurar datos y volver a
  aplicar un paquete anterior.
- **kiwi-framework**: el blog, las aprobaciones de moderación, seguir espacios
  que un hub no incluye y los firmantes NIP-07/NIP-46 están aún por llegar.
- **kiwi-updater**: está previsto un registro alojado de catálogos de confianza.
  Los tags de versión de las demás apps aún no están firmados, así que la mitad
  de root de kiwi-killswitch pide una contraseña para actualizarse.
- **kiwi-proxy**: su módulo de kiwi-server no se ha ejecutado en ninguna máquina.
  Las salidas son solo TCP e IPv4. El módulo VPN guarda una configuración por
  máquina.
- **Módulos de proveedores**: VPN y 9proxy no están validados de principio a fin
  contra una cuenta real; Mysterium sí (7 de noviembre de 2026).
- **kiwi-custodia**: algunas partes aún están por medir en una máquina real
  (tun2socks en un gateway sin root, compositores que no son GNOME).
- **Licencias**: kiwi-icons, kiwi-catalog y mullvad-socks5 no tienen archivo
  LICENSE, y kiwi-killswitch solo indica su licencia en su README y su
  manifiesto.
