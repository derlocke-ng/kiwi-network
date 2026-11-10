# Hubs, no plataformas

La red conecta tus máquinas. Los **hubs** conectan personas. Un hub es un
conjunto de apps web (un mercado abierto, un feed, chat, compartir archivos,
listas compartidas, un gestor de contraseñas, un calendario) que funcionan por
completo en el navegador y se sincronizan a través de relays
[nostr](https://nostr.com) que elige la comunidad. No hay servidor de cuentas ni
backend en medio, y todo lo privado se cifra en el dispositivo antes de salir de
él. Cualquiera puede gestionar un hub para cualquier comunidad. Consulta
[las apps del framework](apps.md).

Lo forman tres repositorios:

| Repositorio | Qué es |
|---|---|
| [**kiwi-framework**](https://github.com/derlocke-ng/kiwi-framework) | El motor: identidad y cuentas, relays y sincronización, personas y compartición, moderación, el kit de diseño, las páginas del hub y diez apps. No incluye nada que un usuario abra por sí mismo. v0.32.1, GPL-3.0-or-later |
| [**Armory**](armory.md) | La primera **distribución**: un hub construido con el framework, con un nombre, relays por defecto y las diez apps montadas con sus propios nombres. La plantilla para hacer un fork y crear la tuya. GPL-3.0-or-later. **En línea:** [derlocke-ng.github.io/armory](https://derlocke-ng.github.io/armory/) |
| [**kiwi-web-catalog**](hubs.md#kiwi-web-catalog) | Un catálogo git de hubs y sus apps, con la misma forma que el [kiwi-catalog](../desktop/catalogs.md) de escritorio |

## Cómo encaja todo { #how-it-fits-together }

```
kiwi-framework  (engine: shared data layer, React UI, hub pages, apps)
      │  pinned by commit or tag
      ▼
a distribution  (Armory: distribution.js + locales/ + app overlays)
      │  build → static files
      ▼
any static host (GitHub Pages)  or  the hub container (nginx + HUB_* settings)
      │  HTTPS
      ▼
┌──────────────── your browser: all the logic and all the crypto ────────────────┐
│  wss://   nostr relays: the hub's own, a public area, one network per space    │
│  https:// Blossom media servers: encrypted files, addressed by their SHA-256   │
│  WebRTC   browser to browser: direct file transfers, calls, pong               │
└─────────────────────────────────────────────────────────────────────────────────┘
```

## Vocabulario { #the-words }

- **Hub**: lo que produce una distribución. Archivos estáticos, así que alojar
  uno es servir una carpeta. Cada hub tiene una página de inicio, ajustes y una
  página de cuenta.
- **Distribución**: un hub construido sobre el framework, con un nombre y un
  aspecto, relays por defecto y un conjunto elegido de apps en espacios
  elegidos. Todo lo que cambia un fork vive en un solo archivo,
  `distribution.js`, más sus traducciones.
- **App**: una carpeta con un manifiesto que se conecta a cualquier
  distribución. Las apps solo hablan con la API pública del framework y nunca
  tocan directamente el almacenamiento ni las claves.
- **Espacio**: una comunidad con nombre y con dueño, con sus propios moderadores
  y, opcionalmente, sus propios relays (siguiendo el modelo de las comunidades
  moderadas de NIP-72). Otro hub puede servir el mismo espacio nombrando su
  dirección.
- **Montaje**: código de una app sobre un espacio, con su propio nombre, ruta e
  icono. Una app se puede montar muchas veces. El *Trading Post* de Armory es la
  app `market` del framework montada en el espacio `tradingpost` de Armory.

Dos personas en distribuciones distintas son amigas, comparten y chatean
exactamente igual que en una sola, porque la identidad y los datos son eventos
nostr, no del hub.

## Cuentas y claves { #accounts-and-keys }

- Cada dispositivo recibe una clave en su primera visita, guardada en el
  navegador.
- Una **cuenta** es un nombre de usuario y una contraseña, construida sobre
  eventos nostr simples sin ningún registro central: la contraseña se refuerza
  con scrypt y desbloquea tu clave. Nadie puede quitarte ni sobrescribir una
  cuenta sin la contraseña. **No hay restablecimiento de contraseña**.
- También puedes iniciar sesión con una clave nostr existente (`nsec`, hex o
  `ncryptsec`). Los firmantes de extensión de navegador y remotos (NIP-07,
  NIP-46) están previstos, no construidos.
- Una cuenta funciona en todas las apps del hub y en cada dispositivo donde
  inicias sesión.

## Modelo de privacidad { #privacy-model }

**Qué se cifra.** El contenido se sella en el navegador antes de ir a ninguna
parte: AES-256-GCM con claves derivadas por HKDF. Los mensajes privados son
mensajes NIP-17 en envoltorios de regalo NIP-59. Cada archivo recibe una clave
AES-256-GCM aleatoria antes de ir a un servidor multimedia, y las fotos se
recodifican, lo que elimina los metadatos de la cámara. El Vault se sella con su
propia frase de contraseña (scrypt + AES-256-GCM). Las llamadas van de navegador
a navegador, cifradas por WebRTC.

**Primero lo local.** Cada escritura va primero a la base de datos propia del
navegador y luego a los relays. Las lecturas salen del dispositivo, así que las
apps funcionan sin conexión. Cuando un dispositivo se vuelve a conectar, repone
lo que un relay olvidó: los datos solo se pierden si han desaparecido todos los
dispositivos que los tenían *y* no hay copia de seguridad.

**Qué pueden ver otros.** Los repositorios son explícitos sobre los límites:

- Los relays ven metadatos: quién escribe a qué direcciones, cuándo, cuánto y
  desde qué dirección IP. Usa una VPN o Tor si eso te importa.
- La clave de un espacio no es un secreto. Mantiene las publicaciones de una
  comunidad fuera de la vista directa. Los me gusta, las denuncias y quién
  comentó qué son visibles para los relays.
- Las notas de DevBoard y las denuncias de moderación son públicas por diseño.
- Tu clave vive en el almacenamiento del navegador. Todos los sitios de GitHub
  Pages de una misma cuenta comparten origen, así que un hub en su propio
  (sub)dominio es la configuración más sólida.
- Las transferencias directas y las llamadas revelan las direcciones IP de los
  dos navegadores entre sí y a los servidores STUN (los de Google y Cloudflare
  por defecto; un hub puede fijar los suyos).
- «Sin servidor nuestro» significa ninguno en el camino crítico. Las apps siguen
  usando los relays, los servidores multimedia y, para el calendario, el
  servidor CalDAV que elijáis tú o tu hub.

## Moderación { #moderation }

Tres capas: tu propia lista de bloqueo (cifrada, solo tú puedes leerla), las
denuncias (públicas, firmadas) y la política propia de los relays. Un espacio
tiene moderadores. La denuncia de un moderador pliega una publicación al
instante. Si no, hacen falta tres denuncias de personas que no estén bloqueadas.
Las publicaciones se pueden marcar como 18+ o como anuncio, y esas solo se
muestran a personas con cuenta.

## Sigue leyendo { #read-on }

- [Armory y sus apps](armory.md)
- [Tu propio hub](hubs.md)
- La propia [arquitectura](https://github.com/derlocke-ng/kiwi-framework/blob/main/docs/architecture.md)
  del framework y su [protocolo](https://github.com/derlocke-ng/kiwi-framework/blob/main/docs/protocol.md)
