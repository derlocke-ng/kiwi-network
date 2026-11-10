# kiwi-gen: Kiwi Key Generator

Un gestor en el navegador para **claves SSH, certificados SSH y certificados
TLS**. Todo se crea y se guarda localmente en un almacén cifrado, y no se envía
nada a ningún servidor.

- Repositorio: [derlocke-ng/kiwi-gen](https://github.com/derlocke-ng/kiwi-gen), MIT
- En línea: [derlocke-ng.github.io/kiwi-gen](https://derlocke-ng.github.io/kiwi-gen/)
- Es una página web estática, no una app de kiwi-updater. No hay tags de versión.

Úsalo para las claves SSH de tu archivo fleet, para una CA de tus propios
servicios o para certificados de cliente, todo generado sin conexión en el
navegador.

## Funciones { #features }

**Almacén.** Las claves y los certificados se guardan en un solo almacén cifrado:
AES-256-GCM, con la clave derivada de tu contraseña maestra mediante
PBKDF2-SHA256 con 600.000 iteraciones. El almacén se guarda cifrado en el
localStorage del navegador y solo se descifra en memoria mientras está
desbloqueado. Expórtalo como archivo para hacer una copia de seguridad o
moverlo. Puedes importar claves y certificados existentes (un certificado con su
clave y su cadena se convierte en un solo elemento), fusionar otro almacén,
añadir notas, buscar y ver lo que caduca pronto.

**Claves SSH.** Ed25519, ECDSA (P-256/384/521) y RSA (3072/4096), en formato
OpenSSH real que aceptan `ssh`, `ssh-keygen` y `ssh-add`. Las frases de
contraseña opcionales se cifran como lo hace `ssh-keygen` (KDF bcrypt,
aes256-ctr), y se muestra la huella SHA256.

**Certificados SSH.** Crea una CA SSH o carga una, y luego firma certificados de
usuario o de host. Te da líneas listas para `sshd_config` y `known_hosts`.

**Certificados TLS.** Crea una CA raíz o intermedia (ECDSA o RSA), o carga una
existente. Emite certificados de servidor (nombres de host, comodines, IPs) o de
cliente, y firma CSR de otros sitios para que la clave privada nunca tenga que
llegar aquí. Produce archivos de cadena completa y paquetes `.p12`. Los
certificados pasan `openssl verify -x509_strict` y cumplen los requisitos de
Apple para certificados de servidor TLS.

**Inspeccionar y convertir.** Lee certificados, CSR, claves y certificados SSH
(PEM o DER), comprueba que una clave corresponde a un certificado, convierte
claves privadas entre PKCS#8, PKCS#1 y OpenSSH (añadiendo o quitando una frase de
contraseña) y convierte claves públicas entre SSH y PEM.

## Ejecutarlo { #running-it }

Abre `index.html` en un navegador moderno (funciona directamente desde el disco),
o sirve la carpeta:

```bash
git clone https://github.com/derlocke-ng/kiwi-gen.git && cd kiwi-gen
python3 -m http.server 8000      # luego http://localhost:8000
```

WebCrypto solo funciona en contextos seguros: HTTPS, `localhost` o `file://`. El
HTTP simple desde otra máquina no funcionará.

## Cómo funciona { #how-it-works }

Toda la criptografía usa la
[Web Crypto API](https://developer.mozilla.org/docs/Web/API/Web_Crypto_API) del
navegador. La codificación OpenSSH, X.509, PKCS#8, PKCS#10 y PKCS#12 está en un
solo archivo sin dependencias, `kiwi-crypto.js`. No hay paso de build y nada se
carga desde una CDN. Una Content-Security-Policy bloquea todas las peticiones de
red, así que las claves no pueden salir de la página.

Una página web no puede hacer de agente SSH. Carga las claves que crees en tu
`ssh-agent` habitual con `ssh-add`. El almacén es tan seguro como tu contraseña
maestra y tu perfil del navegador. Ed25519 necesita un navegador actual
(Chrome 137+, Firefox 129+, Safari 17+).
