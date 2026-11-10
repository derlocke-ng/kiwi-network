# Armory

**Herramientas web entre pares, armadas con nostr.** Cada herramienta funciona
por completo en tu navegador y se sincroniza a través de los relays que tú
eliges. Sin registro, sin servidor nuestro y sin rastreo, y todo se cifra antes
de salir de tu dispositivo. Instálala como app web desde la página de inicio.

- **Ábrela:** [derlocke-ng.github.io/armory](https://derlocke-ng.github.io/armory/)
- Repositorio: [derlocke-ng/armory](https://github.com/derlocke-ng/armory), GPL-3.0-or-later
- Una distribución de [kiwi-framework](index.md) 0.32.1 (fijado por commit).
  Todavía no hay tags de versión.
- En inglés, alemán, francés, español, italiano, neerlandés, polaco y portugués.

Armory antes se llamaba weaponized.js.

## Las herramientas { #the-tools }

| Herramienta | Qué hace |
|---|---|
| [**Loadout**](https://derlocke-ng.github.io/armory/loadout/) | Listas de la compra y de tareas compartidas, inventarios del hogar y notas en Markdown entre tus dispositivos y con quien quieras compartirlos. Cifrado de extremo a extremo, con enlaces de edición o de solo lectura. Funciona sin conexión, y tus dispositivos reponen lo que los relays olvidan. |
| [**Uplink**](https://derlocke-ng.github.io/armory/uplink/) | Mensajes y archivos a amigos (NIP-17, sellados en tu dispositivo), grupos que se mantienen hasta que su anfitrión los cierra, y salas en directo a las que entra quien tenga el enlace y que desaparecen al vaciarse. Respuestas, reacciones, ediciones, mensajes fijados, búsqueda en el dispositivo, mensajes efímeros y llamadas de voz y vídeo de hasta seis personas. |
| [**Payload**](https://derlocke-ng.github.io/armory/payload/) | Compartir archivos: un enlace que espera cifrado en tus servidores multimedia hasta que lo borres; archivos a amigos y grupos en Uplink; o directo de tu navegador al suyo, sin guardarse en ningún sitio. |
| [**Vault**](https://derlocke-ng.github.io/armory/vault/) | Un gestor de contraseñas: accesos, notas, tarjetas y códigos de doble factor en cada dispositivo donde inicias sesión. Un generador, un informe de salud (contraseñas débiles, reutilizadas, antiguas y, si lo activas, filtradas), importación y exportación, claves SSH, una autoridad de certificación SSH, una CA X.509 y certificados TLS. Sellado con su propia frase de contraseña. Sin autorrelleno. |
| [**Authenticator**](https://derlocke-ng.github.io/armory/authenticator/) | Códigos de doble factor (TOTP) para tus cuentas en otros sitios: añade uno desde un código QR, un enlace o un secreto, o una exportación de Google Authenticator. Guardados en el mismo almacén sellado. |
| [**Calendar**](https://derlocke-ng.github.io/armory/calendar/) | Tus calendarios de tu propio Nextcloud o de cualquier servidor CalDAV: los próximos días o un mes, eventos que se repiten, recordatorios mientras una página está abierta. Nada va a los relays; tu acceso queda sellado en tu cuenta. Tu servidor debe permitir el origen de Armory (CORS). |
| [**Outpost**](https://derlocke-ng.github.io/armory/outpost/) | Informes y diarios de cultivo: entradas con fotos, semana a semana, para todos en Outpost, tus amigos, un círculo o solo tú. Hashtags, me gusta y comentarios. Sellado en tu dispositivo, con las fotos cifradas. |
| [**Trading Post**](https://derlocke-ng.github.io/armory/tradingpost/) | Un mercado de cáñamo: semillas, esquejes y equipo con fotos, encontrados por categoría y por a dónde envían. «Escribir al vendedor» abre Uplink. Para personas con cuenta (sin verificación de edad). Los vendedores tienen que aparecer antes en Outpost (tres publicaciones, cada una con me gusta de tres personas) o que un moderador los apruebe. |
| [**DevBoard**](https://derlocke-ng.github.io/armory/devboard/) | Un tablón de anuncios para freelancers: publica que contratas o que estás disponible, firmado con tu clave, respaldado por prueba de trabajo, votado, desaparece al caducar (de 24 horas a 30 días). Público por diseño. |
| [**pongjs**](https://derlocke-ng.github.io/armory/pongjs/) | Pong retro para dos jugadores entre dos navegadores. Comparte un enlace o un código QR, o elige una partida abierta, o practica contra el ordenador sin conexión. |

Hay un blog previsto.

Cada herramienta es una de las apps del framework, montada con el nombre de
Armory: Loadout es `boards`, Uplink `chat`, Outpost `feed`, Trading Post
`market`, DevBoard `notices`, pongjs `pong`.

## Una cuenta, todas las herramientas { #one-account-every-tool }

Inicia sesión o crea una cuenta en la página de inicio (nombre de usuario y
contraseña, o una clave nostr) y todas las herramientas la usan. Las listas que
creaste en un dispositivo antes de iniciar sesión se conservan. Sin cuenta, cada
dispositivo usa su propia clave.

La página de ajustes abarca todo el hub: tu cuenta y tus dispositivos, amigos y
círculos, personas bloqueadas, relays, espacios y servidores multimedia,
notificaciones y copias de seguridad cifradas.

## Relays y servidores multimedia { #relays-and-media-servers }

Los relays por defecto de Armory son `wss://nos.lol`, `wss://relay.damus.io`,
`wss://nostr.mom` y `wss://relay.primal.net`. Sus servidores multimedia
(Blossom) por defecto son `nostr.download`, `blossom.yakihonne.com`,
`blossom.band` (solo fotos) y `blossom.primal.net`. Puedes elegir los tuyos en
los ajustes.

Los relays solo pasan datos, pero no pueden leer lo que se cifró antes. El
[modelo de privacidad](index.md#privacy-model) enumera lo que pueden ver.

## Moderación { #moderation }

Los moderadores de Armory moderan Outpost, Trading Post y DevBoard. Las entradas
de Outpost se pueden marcar como 18+ o como anuncio por quien las escribe, por
dos denuncias o por un moderador. Esas entradas solo se muestran a personas con
cuenta.

## Tu propio Armory { #your-own-armory }

Armory es la plantilla para tu propio hub. Haz un fork (o úsalo como plantilla),
cambia `distribution.js` y las traducciones, y publícalo. Consulta
[Tu propio hub](hubs.md).
