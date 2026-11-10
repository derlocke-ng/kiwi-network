# Hubs, no plataformas

**kiwi-framework** es el software con el que cualquier comunidad puede tener su
propio **hub**. Un hub es un sitio web con un conjunto de apps para los
miembros de la comunidad: un mercado abierto, un feed, chat, archivos
compartidos, listas compartidas, un gestor de contraseñas y un calendario.
Cualquiera puede montar un hub para la comunidad que quiera, y esa comunidad
deja de depender de una plataforma central que guarde las cuentas y los datos
de todo el mundo.

Las apps funcionan por completo en el navegador. Se sincronizan a través de
relays de [nostr](https://nostr.com), que son servidores que guardan mensajes
firmados y los reenvían, y es la comunidad la que elige qué relays usa su hub.
Entre el navegador y los relays no hay ningún servidor de cuentas ni ningún
backend, y todo lo privado se cifra en el dispositivo antes de enviarse. Las
demás partes de Kiwi Network conectan tus máquinas; los hubs conectan a las
personas. Cada app está descrita en [Las apps del framework](apps.md).

Armory es el primer hub que se hizo con el framework. Es un ejemplo, y también
la plantilla que otras comunidades copian para crear el suyo.

El software está repartido en tres repositorios:

| Repositorio | Qué es |
|---|---|
| [**kiwi-framework**](https://github.com/derlocke-ng/kiwi-framework) | El software general del que sale cualquier hub. Incluye la identidad y las cuentas, los relays y la sincronización, los amigos y la forma de compartir con ellos, la moderación, el kit de diseño, las páginas del hub y diez apps. El framework no se puede abrir por sí solo como sitio web: es una distribución la que lo convierte en un hub. La versión actual es la v0.32.1 y la licencia es GPL-3.0-or-later. |
| [**Armory**](armory.md) | La primera **distribución**, es decir, un hub concreto hecho con el framework. Aporta un nombre, unos relays por defecto y las diez apps, cada una con un nombre propio de Armory. Es la plantilla de la que partes, con un fork, para hacer tu propio hub. La licencia es GPL-3.0-or-later. **En línea:** [derlocke-ng.github.io/armory](https://derlocke-ng.github.io/armory/) |
| [**kiwi-web-catalog**](hubs.md#kiwi-web-catalog) | Un catálogo, es decir, un repositorio git con una lista de hubs y de sus apps. Tiene el mismo formato que el [kiwi-catalog](../desktop/catalogs.md) del escritorio. |

## Cómo encaja todo { #how-it-fits-together }

El diagrama muestra cómo el framework se convierte en un hub en tu navegador y
con qué servidores habla después el navegador.

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

## Los términos que se usan aquí { #the-words }

- **Hub**: el sitio web que usa una comunidad. Es lo que obtienes al compilar
  una distribución. Se compone únicamente de archivos estáticos, así que
  alojar un hub consiste en servir una carpeta de archivos. Todo hub tiene una
  página de inicio, una de ajustes y una de cuenta.
- **Distribución**: el framework junto con las decisiones que definen un hub
  concreto, que son un nombre y un aspecto, unos relays por defecto y una
  selección de apps montadas en los espacios elegidos. Cuando haces un fork de
  una distribución, todo lo que cambias está en un solo archivo,
  `distribution.js`, y en sus traducciones.
- **App**: una carpeta con un archivo de manifiesto. Se puede añadir a
  cualquier distribución. Las apps usan solo la API pública del framework y
  nunca acceden directamente al almacenamiento ni a las claves.
- **Espacio**: una comunidad con un nombre, un propietario, sus propios
  moderadores y, si quiere, sus propios relays. Sigue el modelo de las
  comunidades moderadas de nostr (NIP-72). Otro hub puede ofrecer el mismo
  espacio con solo indicar su dirección.
- **Montaje**: una app que se usa para un espacio. Cada montaje tiene su
  propio nombre, su propia ruta (su dirección dentro del hub) y su propio
  icono. Una misma app se puede montar muchas veces. Por ejemplo, *Trading
  Post*, de Armory, es la app `market` del framework montada en el espacio
  `tradingpost` de Armory.

Dos personas que usan hubs de distribuciones distintas pueden ser amigas,
compartir cosas y chatear exactamente igual que si usaran el mismo hub. Es
posible porque la identidad y los datos de una persona son eventos de nostr, es
decir, mensajes firmados que se guardan en relays, y no pertenecen a ningún
hub.

## Cuentas y claves { #accounts-and-keys }

- La primera vez que abres un hub en un dispositivo, el navegador crea una
  clave para ese dispositivo y la guarda.
- Una **cuenta** es un nombre de usuario y una contraseña. Se basa en eventos
  normales de nostr, y no existe ningún registro de cuentas. La contraseña pasa
  por scrypt, una función que es lenta de calcular a propósito, y el resultado
  desbloquea tu clave. Sin la contraseña, nadie puede apoderarse de una cuenta
  ni sobrescribirla. **La contraseña no se puede restablecer.**
- También puedes iniciar sesión con una clave de nostr que ya tengas, en
  formato `nsec`, hexadecimal o `ncryptsec`. Iniciar sesión con una extensión
  del navegador (NIP-07) o con un firmante remoto (NIP-46) está previsto, pero
  aún sin implementar.
- Una misma cuenta sirve para todas las apps del hub y en todos los
  dispositivos en los que inicies sesión.

## Modelo de privacidad { #privacy-model }

**Qué se cifra.** El navegador cifra el contenido antes de enviarlo a ningún
sitio. Usa AES-256-GCM con claves derivadas mediante HKDF. Los mensajes
privados son mensajes NIP-17 dentro de un «gift wrap» de NIP-59. El gift wrap
es una segunda capa de cifrado, con la que un relay solo ve que alguna clave ha
recibido un mensaje envuelto. Cada archivo se cifra con su propia clave
AES-256-GCM aleatoria antes de subirse a un servidor multimedia. Las fotos se
vuelven a codificar antes, y con ello desaparecen los metadatos que añaden las
cámaras. El Vault se cifra con una frase de contraseña propia (scrypt +
AES-256-GCM). Las llamadas van directamente de navegador a navegador y las
cifra WebRTC.

**Primero en local.** Todo lo que escribes se guarda primero en la base de
datos del propio navegador y después se envía a los relays. Las apps leen de
esa base de datos del dispositivo, así que también funcionan sin conexión.
Cuando un dispositivo vuelve a conectarse, envía al relay los datos que este ya
no tenga. Por eso solo se pierden datos si desaparecen todos los dispositivos
que los tenían *y* además no hay copia de seguridad.

**Qué pueden ver los demás.** Los propios repositorios explican los límites:

- Los relays ven metadatos: quién escribe a qué direcciones, cuándo, cuánto y
  desde qué dirección IP. Si eso te importa, usa una VPN o Tor.
- La clave de un espacio no es un secreto. Solo impide que las publicaciones de
  una comunidad se puedan leer abiertamente. Los relays pueden ver los «me
  gusta», las denuncias y quién ha comentado qué.
- Las notas de DevBoard y las denuncias de moderación son públicas a propósito.
- Tu clave se guarda en el almacenamiento del navegador. Todos los sitios de
  GitHub Pages de una misma cuenta comparten un único origen, y los navegadores
  separan por origen lo que guarda cada sitio web. Por eso un hub en su propio
  dominio o subdominio es la opción más segura.
- En una transferencia directa de archivos o en una llamada, cada navegador
  conoce la dirección IP del otro, y los servidores STUN que los ayudan a
  conectarse también ven las dos. Por defecto son los servidores STUN de Google
  y de Cloudflare. Un hub puede configurar los suyos.
- «Sin servidor nuestro» significa que las apps no dependen de ningún servidor
  gestionado por el proyecto. Aun así, usan relays, servidores multimedia y,
  para el calendario, un servidor CalDAV. Cuáles, lo decides tú o lo decide tu
  hub.

## Moderación { #moderation }

La moderación tiene tres niveles. El primero es tu propia lista de bloqueados,
que está cifrada para que solo tú puedas leerla. El segundo son las denuncias,
que son públicas y van firmadas. El tercero es la política de cada relay.

Cada espacio tiene moderadores. Cuando un moderador denuncia una publicación,
esta queda plegada de inmediato. En los demás casos, una publicación se pliega
después de tres denuncias de personas que no estén bloqueadas. Una publicación
se puede marcar como +18 o como anuncio publicitario, y las publicaciones
marcadas solo se muestran a quienes tienen una cuenta.

## Sigue leyendo { #read-on }

- [Armory y sus apps](armory.md)
- [Tu propio hub](hubs.md)
- La [arquitectura](https://github.com/derlocke-ng/kiwi-framework/blob/main/docs/architecture.md)
  y el [protocolo de comunicación](https://github.com/derlocke-ng/kiwi-framework/blob/main/docs/protocol.md)
  del framework, en su propia documentación
