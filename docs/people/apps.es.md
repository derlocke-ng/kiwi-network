# Las apps del framework

kiwi-framework es el software con el que una comunidad puede tener su propio
hub, y esta página describe las diez apps que trae. Entre ellas hay un mercado
abierto, un feed para la comunidad, chat y una app para compartir archivos.

El framework da a sus apps nombres sencillos, como `market`. Una distribución,
es decir, un hub concreto hecho con el framework, **monta** las apps que
quiere. Montar una app significa usarla para un espacio, que es una comunidad
con sus propios moderadores y relays, y darle un nombre propio del hub. Una
misma app se puede montar muchas veces. Un banco de semillas y una tienda de
gemas, por ejemplo, son el mismo código de `market` en dos espacios. Cada uno
tiene sus moderadores y sus relays, y en el hub aparecen como dos tarjetas
distintas.

| App | Qué es | Nombre del montaje en Armory |
|---|---|---|
| `market` | **Un mercado abierto** para la comunidad a la que sirve el montaje. Un anuncio tiene fotos, un precio y, o bien desde dónde y adónde se envía, o bien la opción de recogerlo en persona. Los compradores encuentran los anuncios por categoría y según su propia ubicación. La búsqueda usa etiquetas que los relays pueden comparar, pero no leer. El comprador escribe al vendedor en el chat, donde ya le espera el borrador de un mensaje sobre el anuncio. Un anuncio se puede reservar, marcar como vendido, renovar y denunciar, y caduca al cabo de entre 30 y 90 días. Un montaje puede exigir que los vendedores hayan participado antes en un feed o que los haya aprobado un moderador. | Trading Post |
| `feed` | **Un feed para la comunidad.** La gente publica entradas con fotos y hashtags, y los demás pueden comentarlas y darles «me gusta». Una entrada puede ser para todo el espacio, para tus amigos, para un círculo (un grupo de amigos tuyos) o solo para ti. Un diario es una serie de entradas con una portada. Las entradas se pueden marcar como +18 o como anuncio publicitario. | Outpost |
| `chat` | **Mensajes.** Envías mensajes privados y archivos a tus amigos (NIP-17). Los grupos existen hasta que su anfitrión los cierra, y las salas en directo desaparecen cuando sale la última persona. El chat tiene respuestas, reacciones, edición de mensajes, mensajes fijados, búsqueda en el dispositivo y mensajes que desaparecen. Las llamadas de voz y de vídeo funcionan entre un máximo de seis personas. | Uplink |
| `notices` | **Un tablón de anuncios** para notas públicas. Cada nota va firmada por su autor y exige una prueba de trabajo, un pequeño cálculo que encarece publicar en masa. Las notas se pueden votar y denunciar, y caducan. | DevBoard |
| `boards` | **Listas y notas compartidas.** Son listas de tareas, inventarios con cantidades y notas en Markdown. Están cifradas de extremo a extremo y las compartes con enlaces que permiten editar o solo ver. | Loadout |
| `payload` | **Compartir archivos**, de tres maneras: con un enlace a archivos que se guardan cifrados en tus servidores multimedia, enviándolos a amigos y grupos, o directamente de un navegador a otro. | Payload |
| `vault` | **Un gestor de contraseñas** para accesos, notas, tarjetas y códigos de doble factor. Tiene un generador de contraseñas y un informe de salud. También gestiona claves SSH, una CA de SSH, una CA X.509 y certificados TLS. Está cifrado con una frase de contraseña propia. | Vault |
| `authenticator` | **Códigos de doble factor** (TOTP). Se guardan en la misma caja fuerte cifrada que las entradas del gestor de contraseñas. | Authenticator |
| `calendar` | **Tus calendarios** de Nextcloud o de cualquier otro servidor CalDAV. No se envía nada a los relays. | Calendar |
| `pong` | **Pong para dos jugadores**, entre dos navegadores. | pongjs |

Además, todo hub tiene una página de inicio, una de cuenta y una de ajustes.
En los ajustes están tu cuenta y tus dispositivos, los amigos y los círculos,
las personas bloqueadas, los relays, los espacios, los servidores multimedia y
las copias de seguridad. Las notificaciones no son una app aparte: forman parte
del propio hub.

## Espacios y montajes { #spaces-and-mounts }

- Un **espacio** es una comunidad con un nombre y un propietario. Tiene un id,
  la clave del propietario, un nombre, moderadores, sus propios relays y una
  marca que indica si es para adultos. Sigue el modelo de las comunidades
  moderadas de nostr (NIP-72), así que otros clientes de nostr pueden leerlo.
  Cada publicación y cada anuncio pertenecen a un único espacio.
- Un **montaje** es una app que se usa para un espacio, con su propio id, su
  nombre y su icono. Para añadir a tu hub la tienda de otra comunidad, basta
  una línea que defina el montaje.
- **Un enlace indica la app, el espacio y el elemento, pero nunca el
  sitio que lo aloja.** Un hub abre un enlace así con su propio montaje de esa app y ese
  espacio. Si no tiene ninguno, te dice de quién es el espacio y te ofrece una
  forma de volver.
- **Los espacios están federados**, es decir, un espacio no está atado a un
  solo hub. Dos hubs pueden ofrecer el mismo espacio. Por los relays de un
  espacio solo pasa el contenido de ese espacio.

Hay tres cosas previstas que aún no están implementadas. Los hubs se anunciarán
con un manifiesto firmado para que otros puedan encontrarlos. Las aprobaciones
se añadirán como una forma más de moderación. Y se podrá seguir un espacio que
tu hub no incluya.

## Escribir una app { #writing-an-app }

Este comando crea el esqueleto de una app nueva en tu distribución:

```bash
npm run new-app -- <id> "<Name>" <icon>
```

El resultado es una app de React que usa el kit de interfaz del framework.
Tiene un shell (el marco que rodea las páginas de la app), una página de inicio
y una de ajustes, sus textos en todos los idiomas, una entrada en el registro
de apps y un montaje. Las apps usan solo la API pública del framework y nunca
acceden directamente al almacenamiento ni a las claves. En
[Tu propio hub](hubs.md) se explica cómo compilar y publicar un hub.
