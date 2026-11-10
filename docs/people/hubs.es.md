# Tu propio hub

Esta página explica cómo poner en marcha un hub para tu propia comunidad. Un
hub es el sitio web que una comunidad obtiene de kiwi-framework: un mercado
abierto, un feed, chat y otras apps que funcionan en el navegador. Un hub se
compone únicamente de archivos estáticos, así que alojarlo consiste en servir
una carpeta de archivos por HTTPS. Hay tres maneras de tener uno:

- **Usar Armory tal como está.** Armory es el primer hub hecho con el
  framework y está abierto a todo el mundo en
  [derlocke-ng.github.io/armory](https://derlocke-ng.github.io/armory/).
- **Crear tu propia distribución.** Una distribución es el framework con tu
  propio nombre, tus relays y tu selección de apps. Puedes publicarla en
  cualquier servicio de alojamiento estático.
- **Ejecutar el contenedor del hub.** Puedes hacerlo, por ejemplo, dentro de
  tu propia Kiwi Network y junto a tu propio relay. El resultado es un hub
  privado al que solo se llega desde la mesh, es decir, la red WireGuard
  privada que comparten todas tus máquinas.

## Tipos de hub { #kinds-of-hub }

| Tipo | Cómo | Ejemplo |
|---|---|---|
| **Público** | El hub usa relays públicos y cualquiera puede abrirlo. | Armory |
| **Privado** | Los usuarios no pueden cambiar los relays del hub (`policy.relays: 'locked'`), y las páginas esperan hasta que responde alguno de esos relays (`requireHub`). Los relays están dentro de una VPN. | el hub de una empresa en su kiwi-master |
| **Semipúblico** | Un hub privado que además tiene una zona pública. En ella, las apps que se elijan, por ejemplo el chat, usan relays públicos. | |

Los relays de un hub forman redes separadas: la red propia del hub, la zona
pública y las redes de sus espacios. Cada evento, es decir, cada mensaje
firmado de nostr, pertenece a una de esas redes y nunca pasa a otra.

## Tu propia distribución { #your-own-distribution }

Parte de Armory, que es la plantilla. En GitHub, el botón *Use this template*
te da una copia del repositorio sin su historial. Después sigue estos pasos:

1. Edita **`distribution.js`**. Este archivo define el id, el nombre, el
   logotipo, la descripción, la página web, el repositorio, los relays, los
   servidores multimedia, los espacios, las apps y los montajes. Si quieres que
   tu hub ofrezca también los espacios de Armory, copia su `owner` y su `id`
   del `hub.json` de Armory.
2. Edita **`locales/*.json`**. Estos archivos contienen el título, la
   entradilla y el pie de página, además del texto de la tarjeta de cada
   montaje. El inglés es el idioma al que se recurre cuando falta una
   traducción.
3. Actualiza **`kiwi.manifest`**. Si quieres, añade también tu hub a
   [kiwi-web-catalog](#kiwi-web-catalog).
4. En GitHub, elige *Settings → Pages → Source: GitHub Actions* y después haz
   push.

Estos son los comandos que usarás mientras trabajas en una distribución:

```bash
npm install
npm run dev                  # el hub con recarga en caliente, http://localhost:5173
npm test
npm run build && npm run serve
npm run relay:nostr          # un relay local de pruebas en ws://localhost:7777
npm run new-app -- <id> "<Name>" <icon>   # crea el esqueleto de una app nueva
```

Fija kiwi-framework a un commit o a una etiqueta, nunca a una rama. Al
compilar se comprueba tu `distribution.js`. Por ejemplo, un hub con un montaje
público tiene que tener relays públicos, y un hub con relays públicos tiene que
tener un montaje público.

Todo lo que ves en el navegador está escrito en TypeScript con React 19 y se
compila con Vite. La capa de datos, en `shared/`, es JavaScript sin más, con
tipos JSDoc. Las pruebas se ejecutan con el test runner de node, y las que
necesitan un navegador, con Playwright.

## El contenedor del hub { #the-hub-container }

Armory también está disponible como imagen de contenedor,
`ghcr.io/derlocke-ng/armory`. La imagen se construye con el
`container/Dockerfile` del framework y sirve el hub con nginx. Cuando el
contenedor arranca, su script de entrada (el entrypoint) escribe el archivo
`hub.local.json` a partir de las variables `HUB_*`, y la página lee ese archivo
antes de conectarse. Así, quien instala el hub puede elegir los relays y la
política, pero no puede añadir código. Si no se define ninguna variable, el hub
funciona tal como se compiló.

Este ejemplo arranca un hub con su propio relay, que los usuarios no pueden
cambiar, y con un montaje en un relay público:

```bash
docker run --rm -p 8080:80 \
  -e HUB_RELAYS=wss://relay.sh3.home \
  -e HUB_RELAYS_LOCKED=true -e HUB_REQUIRE_HUB=true \
  -e HUB_PUBLIC_RELAYS=wss://nos.lol -e HUB_PUBLIC_MOUNTS=uplink \
  ghcr.io/you/your-hub
```

| Variable | Significado |
|---|---|
| `HUB_RELAYS` | Los relays propios del hub. |
| `HUB_PUBLIC_RELAYS` | Los relays de la zona pública. Si la variable está definida pero vacía, no hay zona pública. |
| `HUB_DIRECTORY_RELAYS` | Los relays en los que se publican y se consultan las listas de relays. |
| `HUB_RELAYS_LOCKED` | Con `true`, los usuarios no pueden cambiar los relays del hub. |
| `HUB_REQUIRE_HUB` | Con `true`, las páginas esperan mientras no responda ninguno de los relays del hub. |
| `HUB_PUBLIC_MOUNTS` | Los montajes que usan la zona pública, indicados por su id. |
| `HUB_ACCOUNT_MOUNTS` | Los montajes que piden una cuenta. |
| `HUB_REQUIRE_ACCOUNT` | Con `true`, todos los montajes piden una cuenta. |
| `HUB_SPACE_RELAYS` | Los relays de cada espacio, con el formato `jobs=wss://…;gems=wss://a,wss://b`. |
| `HUB_MODERATORS` | Las claves de las personas que moderan todos los espacios que define el hub. |
| `HUB_REGISTER_POW` | El número de bits de prueba de trabajo que necesita una cuenta nueva. Es para los relays que solo aceptan a miembros. |
| `HUB_CALDAV` | Un servidor Nextcloud. nginx le reenvía `/remote.php/dav/`, así que el calendario no necesita CORS. |
| `HUB_ICE`, `HUB_ICE_USERNAME`, `HUB_ICE_CREDENTIAL` | Los servidores STUN/TURN para las llamadas y las transferencias directas, que ayudan a dos navegadores a conectarse entre sí. El usuario y la contraseña de TURN se ven en la página, así que crea unos que solo use este hub. |

`HUB_USER_MOUNTS` se lee, pero todavía no tiene ningún efecto. Pertenece a una
función que aún está por llegar: seguir un espacio que el hub no incluye.

El hub tiene que servirse por HTTPS, porque WebCrypto necesita un contexto
seguro, y sus relays tienen que servirse por `wss://`. Si alguien abre el hub
por `http://`, sin cifrar, en cualquier sitio que no sea localhost, la página
lo avisa y se detiene.

### Un hub en tu Kiwi Network { #on-a-kiwi-network }

Un kiwi-master es el único servidor de una Kiwi Network accesible desde
Internet. Puede tener su propio relay y su propio hub, y de ello se encargan
dos módulos. El módulo `nostr-relay` ejecuta strfry, un software de relay, en
`relay.<host>`. El módulo `hub` ejecuta esta imagen de contenedor, con Armory
por defecto, en `hub.<host>`.

Los dos son privados por defecto: solo se llega a ellos desde la mesh, y usan
el certificado de la fleet. Para un hub semipúblico, añade `public_relays` y
`public_mounts`. Para un hub público, añade `reverse-proxy.public`, que obtiene
certificados de Let's Encrypt.

El relay de un hub público acepta las publicaciones que llegan desde la mesh.
Desde Internet solo acepta las de los miembros que demuestran que tienen su
clave (NIP-42). Son miembros las personas de la lista que firman los
administradores (`write_pubkeys`). Con `members: registered`, es miembro
cualquiera que tenga una cuenta en el hub. Consulta la
[referencia de los módulos](../server/modules.md#people).

## kiwi-web-catalog { #kiwi-web-catalog }

[derlocke-ng/kiwi-web-catalog](https://github.com/derlocke-ng/kiwi-web-catalog)
es un catálogo, es decir, un repositorio git con una lista de otros
repositorios. Recoge los hubs, sus apps y el framework, y tiene el mismo
formato que el catálogo del escritorio. El archivo `apps.list` contiene una URL
de git por línea. Una línea puede llevar `path=`, para una app que está dentro
del repositorio de un hub, y `ref=`, para fijar una versión. Cada entrada
contiene un `kiwi.manifest` cuya `CATEGORY` es `Framework`, `Hub` o `App`.

Hoy recoge kiwi-framework, Armory y las diez apps de Armory. **No** está
pensado para `kiwi catalog add`: sus entradas no tienen instalador, y todavía
no hay nada que lea el catálogo automáticamente. Según su README, los archivos
del catálogo son de dominio público (CC0).

Para añadir tu hub, haz un fork del catálogo, añade una línea, comprueba que tu
repositorio contiene un `kiwi.manifest` y abre una pull request.

## Aún sin implementar { #not-built-yet }

Estos puntos están en la hoja de ruta del propio framework y todavía no
existen:

- El blog.
- Las aprobaciones de moderación (NIP-72, kind 4550).
- Seguir un espacio que tu hub no incluye.
- Iniciar sesión con una extensión del navegador (NIP-07) o con un firmante
  remoto (NIP-46).
- Un servidor TURN en el stack de kiwi. El trabajo está pendiente en
  kiwi-modules. Sin TURN, es frecuente que dos móviles con datos móviles no
  consigan establecer una conexión directa.
