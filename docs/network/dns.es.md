# DNS, nombres y certificados

Cada máquina y cada servicio de una Kiwi Network tiene un nombre, como
`cloud.papaya.home`, y se abre por HTTPS con un certificado en el que tus
dispositivos confían. En esta página se explica cómo se resuelven los nombres
dentro de la red, cómo se forman y de dónde salen los certificados. Los
servidores DNS son Pi-holes, que además bloquean los dominios no deseados con
una lista de bloqueo común.

## Una sola cadena de servidores DNS { #one-resolver-chain }

Todas las consultas DNS de la red recorren la misma cadena de servidores:

```
LAN device ──▶ gateway node's Pi-hole ──▶ master's Pi-hole ──▶ gluetun DNS-over-TLS (Quad9)
VPN client ───────────────────────────────▶ master's Pi-hole       └─ leaves through the VPN exit
```

- **Los clientes de la VPN** (portátiles, teléfonos) envían sus consultas al
  Pi-hole del master, en `10.8.0.1`.
- **El Pi-hole de un node** pregunta primero al Pi-hole del master. De este
  modo, toda la red comparte una única lista de bloqueo y todas las consultas
  llegan a Internet por la salida del master, que es su conexión con Internet.
  Quad9 (`9.9.9.9`, `149.112.112.112`, definido con `fallback_dns`) va después,
  en orden estricto, así que solo responde mientras no se pueda llegar al
  master.
- **El Pi-hole del master** reenvía las consultas al servidor DNS-over-TLS de
  su cliente de VPN. Por defecto, ese servidor es Quad9 (`dot_providers`).
- **Los nombres del dominio de la fleet** se reenvían al master, y de ahí no
  pasan a ningún otro servidor: el master marca el dominio como local.

Además, toda máquina que tiene un stack lleva los nombres de la fleet en su
archivo `/etc/hosts`, donde sus propios nombres apuntan a ella misma. Así, las
copias de seguridad y la renovación de certificados pueden resolver nombres
aunque no haya ningún Pi-hole. En Fedora CoreOS y uCore, la propia máquina usa
como servidor DNS el Pi-hole de su stack.

**Vecinos en la misma LAN.** Si otros nodes de la fleet tienen una dirección
estática en la subred de un node, el Pi-hole y el archivo hosts de ese node
responden con la **dirección de LAN** de esos vecinos. De esta forma, el tráfico
entre dos máquinas de la misma LAN no sale de ella. El master sigue respondiendo
con las direcciones de la mesh, la red WireGuard privada que comparten todas las
máquinas.

## Nombres: `service.hostname.home` { #names-servicehostnamehome }

Cada host se llama `<host>.<domain>`, por ejemplo `papaya.home`. Cada servicio
que funciona en él recibe un nombre que cuelga del nombre del host:
`cloud.papaya.home`, `vault.papaya.home`, `portainer.papaya.home`,
`dl.lychee.home` y, en el master, `wg.sorbet.home`, `pihole.sorbet.home`,
`hub.sorbet.home`, `relay.sorbet.home`. Todos los nombres que anuncia un módulo
se añaden a los registros DNS de la fleet con la **dirección del host en la
mesh**, y cualquier Pi-hole de la fleet puede resolver todos los nombres de
host y de servicio. El ajuste correspondiente es `fleet_records`. La técnica se
llama DNS de horizonte dividido (split-horizon DNS), porque esos nombres solo se
responden dentro de tu red. Con `extra_records` puedes añadir tus propios
registros.

El dominio por defecto es **`.home`**. Se eligió porque la ICANN no lo va a
delegar como dominio de nivel superior (TLD) público. Por tanto, un nombre de tu
fleet nunca podrá acabar en un registro público, y nadie más podrá registrarlo
ni conseguir para él un certificado en el que confíen los navegadores. `.kiwi`,
en cambio, es un TLD real, y por eso Kiwi Network ya no lo usa. kiwi-server
comprueba el dominio que eliges. `home`, `corp`, `mail`, `internal`, `arpa` y
`test` se aceptan sin más. `.local` se rechaza, porque pertenece a mDNS. Con
`.lan` aparece un aviso, porque los routers lo responden ellos mismos, y con los
TLD públicos también.

Los nombres de *fuera* del dominio de la fleet, que hacen falta para un hub o
un relay públicos, reciben certificados de Let's Encrypt si el proxy inverso del
master es público.

## Los proxies SOCKS5 de Mullvad, por su nombre { #mullvad-socks5-proxies-by-name }

Los proxies SOCKS5 de Mullvad tienen direcciones de un rango privado, y esta
función te permite usarlos por su nombre. Desde kiwi-server 2.2.0, el Pi-hole
del master resuelve los nombres de todos los **proxies SOCKS5 de Mullvad**, tanto
el nombre completo (por ejemplo, `de-fra-wg-socks5-001.relays.mullvad.net`) como
un nombre corto (por ejemplo, `de-fra-001.mullvad.home`). gluetun rechaza
las respuestas DNS que apuntan a direcciones privadas: es su protección contra
el DNS rebinding. Sin estos registros, esos nombres solo se resolverían a través
de los servidores DNS de reserva. Un temporizador del host
(`km-mullvad-socks.timer`, cada 6 horas) actualiza la lista desde
[derlocke-ng/mullvad-socks5](https://github.com/derlocke-ng/mullvad-socks5).
De esa lista solo se aceptan los nombres `*.relays.mullvad.net` con direcciones
`10.x`, de modo que la lista nunca puede redirigir ningún otro nombre.

La función viene activada en el preset del master, porque la salida de ese
preset es Mullvad. Para desactivarla, pon `mullvad_socks: false` en el bloque
`dns:` del master.

## Una sola CA para toda la fleet { #one-ca-for-the-fleet }

Una autoridad de certificación (CA) firma los certificados que tus servicios
usan para HTTPS. Con `tls.auto: true`, que es el valor por defecto, kiwi-server
mantiene **una única autoridad de certificación** para toda la fleet en
`secrets/ca/`. La CA consta de los archivos `kiwiCA.key` y `kiwiCA.pem`, usa
RSA-4096 y es válida durante 3650 días. kiwi-server la crea la primera vez que
un host necesita un certificado. Cada host que ejecuta el proxy inverso recibe
un certificado para `<hostname>` y `*.<hostname>`. Ese certificado es válido
durante 825 días, la duración máxima que los navegadores todavía aceptan, y se
renueva cuando le quedan menos de 30 días. Todas las máquinas que construye
kiwi-server instalan la CA en su almacén de confianza.

Si defines **restricciones de nombres** (name constraints), la CA solo puede
firmar nombres del dominio de la fleet: `tls: { name_constraints: [home] }`. El
archivo fleet de ejemplo las define, aunque el valor por defecto de kiwi-server
es no poner ninguna restricción. Con la restricción, un `kiwiCA.key` robado no
sirve de nada para ningún otro nombre. Esto es importante, porque todas las
máquinas confían en la CA.

```bash
kiwi-server ca fleet.yaml        # muestra la CA de la fleet
```

Importa `kiwiCA.pem` en tus propios dispositivos (navegadores, teléfonos) para
que confíen en `https://cloud.papaya.home`. Si prefieres usar tus propios
certificados, define `tls_fullchain` y `tls_privkey` en el módulo reverse-proxy.

!!! warning "Mantén `secrets/` en privado"
    `kiwiCA.key` firma certificados en los que confían todas tus máquinas.
    Deja `secrets/` y `output/` fuera de git (`output/` ya está en el
    `.gitignore` de kiwi-server).
