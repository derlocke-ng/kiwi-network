# Las apps del framework

kiwi-framework incluye sus apps con nombres simples. Una distribución las
**monta**, sobre un espacio y con un nombre propio. Una app se puede montar
muchas veces: un banco de semillas y una tienda de gemas son el mismo código
`market` en dos espacios, cada uno con sus propios moderadores y relays, como dos
mosaicos en un mismo hub.

| App | Qué es | Armory la monta como |
|---|---|---|
| `market` | **Un mercado abierto** para la comunidad a la que sirve un montaje. Los anuncios tienen fotos, un precio, desde dónde y hacia dónde se envían, o recogida en mano. Los compradores los encuentran por categoría y por dónde están, mediante etiquetas de búsqueda que los relays pueden comparar pero no leer. Los compradores escriben al vendedor en el chat, con un mensaje sobre el anuncio ya redactado. Los anuncios se pueden reservar, vender, renovar y denunciar, y caducan a los 30 a 90 días. Un montaje puede exigir que los vendedores hayan aparecido antes en un feed, o que un moderador los haya aprobado | Trading Post |
| `feed` | **Un feed de la comunidad**: entradas con fotos, hashtags, me gusta y comentarios para el espacio, para amigos, para un círculo o solo para ti, más diarios (una serie de entradas con portada). Las entradas se pueden marcar como 18+ o como anuncio | Outpost |
| `chat` | **Mensajes**: mensajes privados y archivos a amigos (NIP-17), grupos que se mantienen hasta que su anfitrión los cierra, salas en directo que desaparecen al vaciarse, respuestas, reacciones, ediciones, mensajes fijados, búsqueda en el dispositivo, mensajes efímeros y llamadas de voz y vídeo de hasta seis personas | Uplink |
| `notices` | **Un tablón de anuncios** de notas públicas firmadas con prueba de trabajo, votos, denuncias y caducidad | DevBoard |
| `boards` | **Listas y notas compartidas**: listas de comprobación, inventarios con cantidades y notas en Markdown, cifradas de extremo a extremo, con enlaces de edición o de solo lectura | Loadout |
| `payload` | **Compartir archivos**: un enlace que espera, cifrado, en tus servidores multimedia; archivos a amigos y grupos; o directo de navegador a navegador | Payload |
| `vault` | **Un gestor de contraseñas**: accesos, notas, tarjetas, códigos de doble factor, un generador y un informe de salud, claves SSH, una CA SSH, una CA X.509 y certificados TLS. Sellado con su propia frase de contraseña | Vault |
| `authenticator` | **Códigos de doble factor** (TOTP), guardados en el mismo almacén sellado | Authenticator |
| `calendar` | **Tus calendarios** de Nextcloud o de cualquier servidor CalDAV. Nada va a los relays | Calendar |
| `pong` | **Pong para dos jugadores** entre navegadores | pongjs |

Cada hub tiene además una página de inicio, ajustes (tu cuenta y tus
dispositivos, amigos y círculos, personas bloqueadas, relays, espacios,
servidores multimedia, copias de seguridad) y una página de cuenta. Las
notificaciones viven en el propio hub.

## Espacios y montajes { #spaces-and-mounts }

- Un **espacio** es una comunidad con nombre y con dueño: un id, una clave de
  propietario, un nombre, moderadores, sus propios relays y una marca de
  contenido adulto. Sigue el modelo de las comunidades moderadas de nostr
  (NIP-72), así que otros clientes nostr pueden leerlo. Cada publicación y cada
  anuncio pertenece exactamente a un espacio.
- Un **montaje** es código de una app sobre un espacio, con su propio id, nombre
  e icono. Importar la tienda de otra comunidad es una línea de montaje.
- **Los enlaces nombran la app, el espacio y el elemento, nunca el host.** Un hub
  abre un enlace con su propio montaje de esa app y ese espacio. Si no lo tiene,
  dice de quién es el espacio y ofrece el camino de vuelta.
- **Los espacios están federados.** Dos hubs pueden servir el mismo espacio, y
  los relays de un espacio solo transportan su contenido.

Previsto: hubs que se anuncian con un manifiesto firmado para que otros puedan
encontrarlos, aprobaciones de moderación y personas que siguen un espacio que su
hub no incluye.

## Escribir una app { #writing-an-app }

```bash
npm run new-app -- <id> "<Name>" <icon>
```

Esto genera el esqueleto de una app React sobre el kit de interfaz del framework,
con una estructura, páginas de inicio y de ajustes, textos en todos los idiomas,
una entrada en el registro y un montaje. Las apps solo hablan con el framework a
través de su API pública y nunca tocan directamente el almacenamiento ni las
claves. Consulta [Tu propio hub](hubs.md).
