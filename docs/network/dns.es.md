# DNS, nombres y certificados

## Una sola cadena de resolución { #one-resolver-chain }

El DNS es una sola cadena para toda la red:

```
LAN device ──▶ gateway node's Pi-hole ──▶ master's Pi-hole ──▶ gluetun DNS-over-TLS (Quad9)
VPN client ───────────────────────────────▶ master's Pi-hole       └─ leaves through the VPN exit
```

- **Los clientes VPN** (portátiles, teléfonos) preguntan al Pi-hole del master en
  `10.8.0.1`.
- **El Pi-hole de un node** pregunta primero al Pi-hole del master, así la red
  comparte una sola lista de bloqueo y cada consulta sale por la salida del
  master. Quad9 (`9.9.9.9`, `149.112.112.112`, `fallback_dns`) va después en
  orden estricto y solo responde mientras el master no es accesible.
- **El Pi-hole del master** reenvía al resolvedor DNS-over-TLS de su cliente VPN
  (Quad9 por defecto, `dot_providers`).
- **Los nombres bajo el dominio de la fleet** se reenvían al master y nunca
  salen de él. El master marca el dominio como local.

Cada host del stack lleva además los nombres de la fleet en `/etc/hosts` (sus
propios nombres apuntando a sí mismo), de modo que las copias de seguridad y las
renovaciones de certificados se resuelven sin un Pi-hole. En Fedora CoreOS y
uCore, el propio host resuelve a través del Pi-hole de su propio stack.

**Vecinos en la misma LAN.** El Pi-hole y el archivo hosts de un node responden
con la **dirección LAN** de los nodes de la fleet que tienen una dirección
estática en su propia subred, así el tráfico entre dos máquinas de la misma
habitación se queda en la habitación. El master sigue respondiendo con
direcciones de malla.

## Nombres: `service.hostname.home` { #names-servicehostnamehome }

Cada host es `<host>.<domain>` (`papaya.home`), y cada servicio que ejecuta es un
nombre debajo de él: `cloud.papaya.home`, `vault.papaya.home`,
`portainer.papaya.home`, `dl.lychee.home` y, en el master, `wg.sorbet.home`,
`pihole.sorbet.home`, `hub.sorbet.home`, `relay.sorbet.home`. Cada nombre que
anuncia un módulo entra en los registros DNS de la fleet con la **dirección de
malla** del host. Cada Pi-hole de la fleet resuelve todos los nombres de host y
de servicio (horizonte dividido, `fleet_records`). Añade los tuyos con
`extra_records`.

El dominio por defecto es **`.home`**, porque la ICANN no lo delegará como
dominio de nivel superior público. Un nombre de la fleet nunca puede filtrarse a
un registro público, y nadie más puede registrarlo ni obtener para él un
certificado en el que confíen los navegadores. `.kiwi` es un TLD real, y por eso
la fleet dejó de usarlo. kiwi-server comprueba tu elección: `home`, `corp`,
`mail`, `internal`, `arpa` y `test` pasan sin aviso, `.local` se rechaza
(pertenece a mDNS), `.lan` recibe una advertencia (los routers lo responden ellos
mismos) y los TLD públicos reciben una advertencia.

Los nombres *fuera* del dominio de la fleet, para un hub o un relay públicos,
reciben certificados de Let's Encrypt cuando el proxy inverso del master es
público.

## Proxies SOCKS5 de Mullvad por nombre { #mullvad-socks5-proxies-by-name }

Desde kiwi-server 2.2.0, el Pi-hole del master responde por cada **proxy SOCKS5
de Mullvad**, tanto como `de-fra-wg-socks5-001.relays.mullvad.net` como con el
nombre corto `de-fra-001.mullvad.home`. gluetun rechaza estas respuestas de rango
privado (protección contra DNS rebinding), así que sin los registros los nombres
solo se resolverían a través de los resolvedores de reserva. Un temporizador del
host (`km-mullvad-socks.timer`, cada 6 horas) actualiza la lista desde
[derlocke-ng/mullvad-socks5](https://github.com/derlocke-ng/mullvad-socks5).
De ella solo se aceptan nombres `*.relays.mullvad.net` con direcciones `10.x`,
así que la lista nunca puede redirigir ningún otro nombre.

Está activado en el preset del master, cuya salida es Mullvad. Desactívalo con
`mullvad_socks: false` en el bloque `dns:` del master.

## Una CA para la fleet { #one-ca-for-the-fleet }

Con `tls.auto: true` (el valor por defecto), kiwi-server mantiene **una autoridad
de certificación** para la fleet en `secrets/ca/` (`kiwiCA.key`, `kiwiCA.pem`,
RSA-4096, válida 3650 días), creada la primera vez que un host necesita un
certificado. Cada host que ejecuta el proxy inverso recibe un certificado para
`<hostname>` y `*.<hostname>` (825 días, la vida más larga que los navegadores
aún aceptan, renovado cuando quedan menos de 30 días), y cada máquina que
construye kiwi-server instala la CA en su almacén de confianza.

Fija **restricciones de nombre** y la CA solo podrá firmar nombres bajo el
dominio de la fleet: `tls: { name_constraints: [home] }`. La fleet de ejemplo lo
hace; el valor por defecto integrado es sin restricción. Así, una `kiwiCA.key`
robada no vale para nada más, lo que importa porque todas las máquinas confían
en ella.

```bash
kiwi-server ca fleet.yaml        # muestra la CA de la fleet
```

Importa `kiwiCA.pem` en tus propios dispositivos (navegadores, teléfonos) para
que `https://cloud.papaya.home` sea de confianza. Para usar tus propios
certificados en su lugar, fija `tls_fullchain` y `tls_privkey` en el módulo
reverse-proxy.

!!! warning "Mantén `secrets/` en privado"
    `kiwiCA.key` firma certificados en los que confían todas tus máquinas.
    Mantén `secrets/` y `output/` fuera de git (`output/` ya está en el
    `.gitignore` de kiwi-server).
