# Armory

Armory es el primer hub hecho con kiwi-framework, el software con el que
cualquier comunidad puede tener su propio hub. En los términos del framework,
Armory es una **distribución**: el framework junto con un nombre, unos relays
por defecto y una selección de apps. Armory incluye las diez apps del framework
y les pone nombres propios. Su mercado y su feed están pensados para
cultivadores de cáñamo. Ese tema lo ha elegido este hub, no el framework, y
otra comunidad usaría las mismas apps para el suyo. Puedes usar Armory tal como
está o copiarlo como plantilla para tu propio hub.

Todas las herramientas funcionan por completo en tu navegador. Se sincronizan a
través de relays, que son servidores que guardan tus datos y los reenvían, y
eres tú quien elige qué relays usar. No hace falta registrarse, el proyecto no
tiene ningún servidor propio para Armory y nada te rastrea. Todo se cifra antes
de salir de tu dispositivo. Desde su página de inicio puedes instalar Armory
como aplicación web.

- **Ábrelo:** [derlocke-ng.github.io/armory](https://derlocke-ng.github.io/armory/)
- El repositorio es [derlocke-ng/armory](https://github.com/derlocke-ng/armory)
  y la licencia es GPL-3.0-or-later.
- Armory es una distribución de [kiwi-framework](index.md) 0.32.1, que fija
  por commit. El propio Armory todavía no tiene etiquetas de versión.
- Está disponible en inglés, alemán, francés, español, italiano, neerlandés,
  polaco y portugués.

Armory se llamaba antes weaponized.js.

## Las herramientas { #the-tools }

| Herramienta | Qué hace |
|---|---|
| [**Loadout**](https://derlocke-ng.github.io/armory/loadout/) | Listas de la compra y de tareas, inventarios del hogar y notas en Markdown compartidas. Se mantienen iguales en todos tus dispositivos y en los de las personas con quienes las compartes. Todo está cifrado de extremo a extremo, y compartes una lista con un enlace que permite editar o solo ver. Loadout funciona sin conexión, y tus dispositivos devuelven a los relays lo que estos hayan perdido. |
| [**Uplink**](https://derlocke-ng.github.io/armory/uplink/) | Mensajes y archivos para tus amigos (NIP-17, cifrados en tu dispositivo). Los grupos existen hasta que su anfitrión los cierra. En las salas en directo entra cualquiera que tenga el enlace, y desaparecen cuando sale la última persona. Uplink tiene respuestas, reacciones, edición de mensajes, mensajes fijados, búsqueda en tu dispositivo y mensajes que desaparecen. Las llamadas de voz y de vídeo funcionan entre un máximo de seis personas. |
| [**Payload**](https://derlocke-ng.github.io/armory/payload/) | Compartir archivos, de tres maneras. Puedes crear un enlace a archivos que se quedan cifrados en tus servidores multimedia hasta que los borras. Puedes enviar archivos a amigos y grupos en Uplink. O puedes enviarlos directamente de tu navegador al de otra persona, y entonces no se guardan en ningún sitio. |
| [**Vault**](https://derlocke-ng.github.io/armory/vault/) | Un gestor de contraseñas para accesos, notas, tarjetas y códigos de doble factor, disponible en todos los dispositivos en los que inicies sesión. Tiene un generador de contraseñas y un informe de salud. El informe encuentra las contraseñas débiles, repetidas y antiguas y, si activas esa comprobación, las que han aparecido en filtraciones. Vault importa y exporta entradas. También gestiona claves SSH, una autoridad de certificación de SSH, una CA X.509 y certificados TLS. Está cifrado con una frase de contraseña propia. No rellena por ti las contraseñas en los sitios web. |
| [**Authenticator**](https://derlocke-ng.github.io/armory/authenticator/) | Códigos de doble factor (TOTP) para tus cuentas en otros servicios. Añades una cuenta con un código QR, con un enlace o un secreto, o con una exportación de Google Authenticator. Los códigos se guardan en la misma caja fuerte cifrada que usa Vault. |
| [**Calendar**](https://derlocke-ng.github.io/armory/calendar/) | Tus calendarios de tu propio Nextcloud o de cualquier otro servidor CalDAV. Muestra los próximos días o un mes, admite eventos que se repiten y te los recuerda mientras tengas una página abierta. No se envía nada a los relays, y los datos de acceso a tu servidor se guardan cifrados en tu cuenta. Tu servidor tiene que permitir las peticiones que llegan del origen de Armory (CORS). |
| [**Outpost**](https://derlocke-ng.github.io/armory/outpost/) | El feed de Armory, que se usa para informes y diarios de cultivo. Publicas entradas con fotos, semana a semana. Cada entrada puede ser para todos en Outpost, para tus amigos, para un círculo de amigos o solo para ti. Las entradas pueden llevar hashtags, «me gusta» y comentarios. Se cifran en tu dispositivo, igual que las fotos. |
| [**Trading Post**](https://derlocke-ng.github.io/armory/tradingpost/) | El mercado de Armory, que se usa para el cáñamo: semillas, esquejes y equipo. Los anuncios tienen fotos, y los compradores los encuentran por categoría y por los lugares a los que se envían. Al elegir «Message seller» (escribir al vendedor) se abre Uplink. Para usar Trading Post necesitas una cuenta, y no hay verificación de edad. Para poder vender, antes hay que haber publicado en Outpost (tres publicaciones, cada una con «me gusta» de tres personas) o haber sido aprobado por un moderador. |
| [**DevBoard**](https://derlocke-ng.github.io/armory/devboard/) | Un tablón de anuncios para freelancers. Publicas una nota en la que dices que contratas o que estás disponible. Cada nota va firmada con tu clave y exige una prueba de trabajo, un pequeño cálculo que encarece publicar en masa. Los demás pueden votar las notas. Una nota desaparece cuando caduca, entre 24 horas y 30 días después de publicarse. Todas las notas son públicas a propósito. |
| [**pongjs**](https://derlocke-ng.github.io/armory/pongjs/) | Pong retro para dos jugadores en dos navegadores. Para empezar una partida, comparte un enlace o un código QR, o elige una de las partidas abiertas. También puedes practicar contra el ordenador sin conexión. |

Está previsto un blog.

Cada herramienta es una de las apps del framework con el nombre que le ha
puesto Armory. Loadout es la app `boards` del framework, Uplink es `chat`,
Outpost es `feed`, Trading Post es `market`, DevBoard es `notices` y pongjs es
`pong`.

## Una cuenta para todas las herramientas { #one-account-every-tool }

En la página de inicio inicias sesión o creas una cuenta, con un nombre de
usuario y una contraseña o con una clave de nostr. A partir de ahí, todas las
herramientas usan esa cuenta. Las listas que hubieras creado en un dispositivo
antes de iniciar sesión pasan a la cuenta. Si no usas una cuenta, cada
dispositivo trabaja con su propia clave.

La página de ajustes vale para todo el hub. En ella están tu cuenta y tus
dispositivos, los amigos y los círculos, las personas bloqueadas, los relays,
los espacios y los servidores multimedia, las notificaciones y las copias de
seguridad cifradas.

## Relays y servidores multimedia { #relays-and-media-servers }

Los relays por defecto de Armory son `wss://nos.lol`, `wss://relay.damus.io`,
`wss://nostr.mom` y `wss://relay.primal.net`. Los servidores multimedia guardan
los archivos que subes y usan un protocolo llamado Blossom. Los que Armory trae
por defecto son `nostr.download`, `blossom.yakihonne.com`, `blossom.band` (que
solo acepta fotos) y `blossom.primal.net`. En los ajustes puedes elegir tus
propios relays y servidores multimedia.

Los relays guardan datos y los reenvían, pero no pueden leer nada que se haya
cifrado antes de enviarse. En el
[modelo de privacidad](index.md#privacy-model) se detalla qué pueden ver.

## Moderación { #moderation }

Los moderadores de Armory se ocupan de Outpost, Trading Post y DevBoard. Una
entrada de Outpost se puede marcar como +18 o como anuncio publicitario. La
marca la puede poner el autor o un moderador, y también se pone sola con dos
denuncias. Las entradas marcadas solo se muestran a quienes tienen una cuenta.

## Tu propio Armory { #your-own-armory }

Armory es también la plantilla para tu propio hub. Haz un fork del repositorio
o úsalo como plantilla, cambia `distribution.js` y las traducciones, y publica
el resultado. Los pasos están en [Tu propio hub](hubs.md).
