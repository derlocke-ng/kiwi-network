# kiwi-gen: Kiwi Key Generator

kiwi-gen es una página web que crea y gestiona **claves SSH, certificados SSH
y certificados TLS** en tu navegador. Todo se genera en tu propio ordenador y
se guarda allí, en una caja fuerte cifrada, y no se envía nada a ningún
servidor.

- Repositorio: [derlocke-ng/kiwi-gen](https://github.com/derlocke-ng/kiwi-gen), MIT
- En línea: [derlocke-ng.github.io/kiwi-gen](https://derlocke-ng.github.io/kiwi-gen/)
- Es una página web estática, no una app de kiwi-updater. No tiene etiquetas de versión.

Puedes usarla para crear las claves SSH de tu archivo fleet (el archivo que
describe todas las máquinas de tu Kiwi Network), una autoridad de
certificación (CA) para tus propios servicios o certificados de cliente. Todo
se genera sin conexión, en el navegador.

## Funciones { #features }

**Caja fuerte.** Las claves y los certificados se guardan en una única caja
fuerte cifrada. Se cifra con AES-256-GCM, y la clave de cifrado se deriva de tu
contraseña maestra con PBKDF2-SHA256 y 600 000 iteraciones. La caja fuerte se
guarda cifrada en el localStorage del navegador. Solo se descifra en memoria, y
solo mientras está desbloqueada. Para hacer una copia de seguridad o llevarla a
otro sitio, expórtala a un archivo. Puedes importar claves y certificados que
ya tengas, y un certificado que viene con su clave y su cadena se guarda como
un solo elemento. También puedes fusionar otra caja fuerte con la tuya, añadir
notas, buscar y ver qué caduca pronto.

**Claves SSH.** kiwi-gen crea claves Ed25519, ECDSA (P-256/384/521) y RSA
(3072/4096). Las escribe en el formato OpenSSH real, que aceptan `ssh`,
`ssh-keygen` y `ssh-add`. La frase de contraseña es opcional. Si pones una, la
clave se cifra igual que lo hace `ssh-keygen` (bcrypt KDF, aes256-ctr). Se
muestra la huella SHA256 de la clave.

**Certificados SSH.** Puedes crear una CA de SSH o cargar una que ya tengas, y
firmar con ella certificados de usuario o de host. kiwi-gen te da las líneas
correspondientes para `sshd_config` y `known_hosts`, listas para usar.

**Certificados TLS.** Puedes crear una CA raíz o una CA intermedia (ECDSA o
RSA), o cargar una que ya tengas. Con la CA emites certificados de servidor
para nombres de host, comodines y direcciones IP, o certificados de cliente.
También puedes firmar una solicitud de firma de certificado (CSR) creada en
otro sitio, de modo que la clave privada nunca tenga que entrar en kiwi-gen.
kiwi-gen genera archivos con la cadena completa y paquetes `.p12`. Los
certificados superan `openssl verify -x509_strict` y cumplen los requisitos de
Apple para certificados de servidor TLS.

**Inspeccionar y convertir.** kiwi-gen lee certificados, CSR, claves y
certificados SSH en formato PEM o DER. Puede comprobar si una clave
corresponde a un certificado. Convierte claves privadas entre los formatos
PKCS#8, PKCS#1 y OpenSSH, y al hacerlo puede añadir o quitar una frase de
contraseña. También convierte claves públicas entre los formatos SSH y PEM.

## Cómo usarlo { #running-it }

Abre `index.html` en un navegador moderno. Funciona directamente desde el
disco, sin servidor web. También puedes servir la carpeta:

```bash
git clone https://github.com/derlocke-ng/kiwi-gen.git && cd kiwi-gen
python3 -m http.server 8000      # después http://localhost:8000
```

Las funciones WebCrypto del navegador solo funcionan en un contexto seguro, es
decir, en una página cargada por HTTPS, desde `localhost` o desde `file://`.
Si abres la página desde otra máquina por HTTP sin cifrar, no funcionará.

## Cómo funciona { #how-it-works }

Todas las operaciones criptográficas las hace la
[Web Crypto API](https://developer.mozilla.org/docs/Web/API/Web_Crypto_API) del
navegador. El código que codifica los formatos OpenSSH, X.509, PKCS#8, PKCS#10
y PKCS#12 está en un solo archivo, `kiwi-crypto.js`, que no tiene
dependencias. No hay paso de compilación, y la página no carga nada de ninguna
CDN. Una Content-Security-Policy bloquea todas las peticiones de red, así que
las claves no pueden salir de la página.

Una página web no puede hacer de agente SSH. Para usar las claves que creas,
cárgalas en tu `ssh-agent` habitual con `ssh-add`. La caja fuerte es tan
segura como tu contraseña maestra y tu perfil del navegador. Ed25519 necesita
un navegador actual (Chrome 137+, Firefox 129+, Safari 17+).
