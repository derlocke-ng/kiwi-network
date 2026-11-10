# Tu propio hub

Un hub son archivos estáticos, así que alojar uno es servir una carpeta por
HTTPS. Hay tres formas de tener uno:

- **Usar Armory tal cual:** [derlocke-ng.github.io/armory](https://derlocke-ng.github.io/armory/).
- **Crear tu propia distribución:** tu nombre, tus relays y tus apps, en
  cualquier alojamiento estático.
- **Ejecutar el contenedor del hub:** por ejemplo, dentro de tu propia Kiwi
  Network, con tu propio relay, como un hub privado al que solo llega la malla.

## Tipos de hub { #kinds-of-hub }

| Tipo | Cómo | Ejemplo |
|---|---|---|
| **Público** | Relays públicos; cualquiera puede abrirlo | Armory |
| **Privado** | Los relays del hub están bloqueados (`policy.relays: 'locked'`) y las páginas esperan hasta que uno de ellos responde (`requireHub`), con relays dentro de una VPN | el hub de una empresa en su kiwi-master |
| **Semipúblico** | Un hub privado con una zona pública para apps elegidas (el chat, por ejemplo) en relays públicos | |

Cada evento pertenece a una red (la propia del hub, la zona pública o la de un
espacio) y nunca pasa a otra.

## Tu propia distribución { #your-own-distribution }

Armory es la plantilla (en GitHub, *Use this template* te da una copia sin su
historial):

1. Edita **`distribution.js`**: id, nombre, marca, descripción, página de
   inicio, repositorio, relays, servidores multimedia, espacios, apps y
   montajes. Para servir también los espacios de Armory, copia su `owner` y su
   `id` del `hub.json` de Armory.
2. Edita **`locales/*.json`**: el título, la entradilla y el pie, y un texto de
   tarjeta por montaje. El inglés es el idioma de reserva.
3. Actualiza **`kiwi.manifest`** y, opcionalmente, añade tu hub a
   [kiwi-web-catalog](#kiwi-web-catalog).
4. En GitHub: *Settings → Pages → Source: GitHub Actions*, y luego haz push.

```bash
npm install
npm run dev                  # el hub con recarga en caliente, http://localhost:5173
npm test
npm run build && npm run serve
npm run relay:nostr          # un relay de pruebas local en ws://localhost:7777
npm run new-app -- <id> "<Name>" <icon>   # genera el esqueleto de una app nueva
```

Fija kiwi-framework por commit o por tag, nunca por rama. El build comprueba tu
`distribution.js` (por ejemplo, un montaje público necesita relays públicos, y
al revés).

El stack es TypeScript, React 19 y Vite para todo lo visible. La capa de datos
de `shared/` es JavaScript simple con tipos JSDoc. Las pruebas se ejecutan en el
test runner de node y, para el navegador, en Playwright.

## El contenedor del hub { #the-hub-container }

Armory también es una imagen de contenedor, `ghcr.io/derlocke-ng/armory`,
construida a partir del `container/Dockerfile` del framework (nginx). Al
arrancar, su entrypoint escribe `hub.local.json` a partir de las variables
`HUB_*`, y la página lo lee antes de conectarse. Así, un despliegue puede elegir
relays y política, pero no puede añadir código. Sin variables, el hub funciona
tal como se construyó.

```bash
docker run --rm -p 8080:80 \
  -e HUB_RELAYS=wss://relay.sh3.home \
  -e HUB_RELAYS_LOCKED=true -e HUB_REQUIRE_HUB=true \
  -e HUB_PUBLIC_RELAYS=wss://nos.lol -e HUB_PUBLIC_MOUNTS=uplink \
  ghcr.io/you/your-hub
```

| Variable | Significado |
|---|---|
| `HUB_RELAYS` | los relays propios del hub |
| `HUB_PUBLIC_RELAYS` | los relays de la zona pública (definida y vacía: sin zona pública) |
| `HUB_DIRECTORY_RELAYS` | dónde se publican y se consultan las listas de relays |
| `HUB_RELAYS_LOCKED` | `true`: nadie puede sustituir los relays del hub |
| `HUB_REQUIRE_HUB` | `true`: las páginas esperan mientras ninguno de los relays del hub responda |
| `HUB_PUBLIC_MOUNTS` | montajes en la zona pública, por id |
| `HUB_ACCOUNT_MOUNTS` | montajes que piden una cuenta |
| `HUB_REQUIRE_ACCOUNT` | `true`: todos los montajes piden una cuenta |
| `HUB_SPACE_RELAYS` | relays por espacio: `jobs=wss://…;gems=wss://a,wss://b` |
| `HUB_MODERATORS` | claves que moderan todos los espacios que define el hub |
| `HUB_REGISTER_POW` | bits de prueba de trabajo para una cuenta nueva (relays solo para miembros) |
| `HUB_CALDAV` | un Nextcloud; nginx le reenvía `/remote.php/dav/`, así el calendario no necesita CORS |
| `HUB_ICE`, `HUB_ICE_USERNAME`, `HUB_ICE_CREDENTIAL` | servidores STUN/TURN para llamadas y transferencias directas. El acceso al TURN es visible en la página, así que dale un acceso solo para este hub |

`HUB_USER_MOUNTS` se lee, pero todavía no hace nada: seguir un espacio que el hub
no incluye está aún por llegar.

El hub debe servirse por HTTPS (WebCrypto necesita un contexto seguro) y sus
relays por `wss://`. Por `http://` simple (salvo en localhost), la página lo
dice y se detiene.

### En una Kiwi Network { #on-a-kiwi-network }

Un kiwi-master puede llevar su propio relay y su propio hub: el módulo
`nostr-relay` (strfry en `relay.<host>`) y el módulo `hub` (esta imagen, Armory
por defecto, en `hub.<host>`). Son privados por defecto: accesibles solo desde la
malla, con el certificado de la fleet. Un hub semipúblico añade `public_relays` y
`public_mounts`. Uno público añade `reverse-proxy.public`, que obtiene
certificados de Let's Encrypt. Entonces el relay acepta publicaciones de la
malla y, desde Internet, solo de miembros que demuestran su clave (NIP-42): los
de la lista que firman los administradores (`write_pubkeys`) o, con
`members: registered`, cualquiera con una cuenta en el hub. Consulta la
[referencia de módulos](../server/modules.md#people).

## kiwi-web-catalog { #kiwi-web-catalog }

[derlocke-ng/kiwi-web-catalog](https://github.com/derlocke-ng/kiwi-web-catalog)
enumera hubs, sus apps y el framework, con la misma forma que el catálogo de
escritorio: un `apps.list` con una URL git por línea (`path=` para una app dentro
del repositorio de un hub, `ref=` para fijarla) y un `kiwi.manifest` en cada
entrada con una `CATEGORY` de `Framework`, `Hub` o `App`.

Hoy enumera kiwi-framework, Armory y las diez apps de Armory. **No** es para
`kiwi catalog add`: estas entradas no tienen instalador, y todavía nada lee el
catálogo automáticamente. Los archivos del catálogo son de dominio público (CC0,
según su README).

Para añadir tu hub: haz un fork, añade una línea, asegúrate de que el
repositorio lleva un `kiwi.manifest` y abre una pull request.

## Aún no construido { #not-built-yet }

Esto viene de la propia hoja de ruta del framework:

- El blog.
- Aprobaciones de moderación (NIP-72 kind 4550).
- Seguir espacios que un hub no incluye.
- Firmantes NIP-07 y NIP-46.
- Un servidor TURN en el stack de kiwi. Está esperando en kiwi-modules; sin TURN,
  dos teléfonos con datos móviles a menudo no encuentran una ruta directa.
