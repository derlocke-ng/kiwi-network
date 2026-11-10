# Una sola máquina, sin fleet

kiwi-server administra toda una fleet de máquinas. Si solo quieres poner en
marcha un stack en una única máquina, no lo necesitas. Un stack es el conjunto
de contenedores y servicios que ejecuta una máquina. kiwi-server está hecho con
dos herramientas más pequeñas, y puedes usarlas por separado:

| Repositorio | Qué es |
|---|---|
| [**kiwi-modules**](https://github.com/derlocke-ng/kiwi-modules) | Los módulos y su generador. Lee **un archivo de máquina y escribe un paquete de stack**, un directorio con la configuración generada del stack de la máquina. v0.23.0, GPL-3.0-or-later |
| [**kiwi-stack**](https://github.com/derlocke-ng/kiwi-stack) | La parte que se ejecuta en la máquina. Consta del comando `kiwi-stack` y de una biblioteca, que instalan un paquete en una máquina con CoreOS, uCore o Debian y lo mantienen en marcha. v0.5.0, GPL-3.0-or-later |

Usa las dos herramientas cuando quieras un stack en una máquina sin el resto de
kiwi-server, por ejemplo para un node que preparas a mano, para un módulo que
estás desarrollando o para una máquina que genera su propio stack. kiwi-server
incluye una copia de las dos, cada una fijada a un tag de versión. La máquina
queda idéntica tanto si la preparas con kiwi-server como con las dos
herramientas, y por ambos caminos se derivan los mismos secretos a partir del
mismo seed.

```
machine.yaml ──kiwi-modules render──▶ bundle/ ──copy──▶ sudo kiwi-stack apply bundle/
                                      stack.sh            → podman quadlets (or compose)
                                      docker-compose.yml  → configs, host units, timers
                                      quadlets/  configs  → kiwi-stack.target, verify
```

## Generar una máquina { #render-a-machine }

Los comandos siguientes instalan kiwi-modules, crean un seed y generan un
paquete a partir del archivo de máquina de ejemplo. La última línea copia el
paquete a la máquina y lo aplica allí.

```bash
git clone https://github.com/derlocke-ng/kiwi-modules && cd kiwi-modules
./install.sh install                       # ~/.local/bin/kiwi-modules
mkdir -p sh3/secrets && head -c 32 /dev/urandom > sh3/secrets/seed
cp examples/sh3.yaml sh3/                  # edítalo: archivos TLS, configuración de WireGuard
kiwi-modules render sh3/sh3.yaml -o sh3/sh3.bundle
scp -r sh3/sh3.bundle sh3:/tmp/ && ssh sh3 sudo kiwi-stack apply /tmp/sh3.bundle
```

kiwi-modules necesita Python 3 con PyYAML y Jinja2. `kiwi-modules modules -v`
muestra todos los módulos y ajustes, y `kiwi-modules profiles` muestra los
roles y sus presets.

Un archivo de máquina describe una sola máquina, como en este ejemplo:

```yaml
# un node cloud
name: sh3
domain: home
target: ucore
timezone: Europe/Berlin
admin: { user: core }
role: node
node:
  preset: cloud
  cloud: { collabora: true, talk: true }
  reverse-proxy:
    tls_fullchain: secrets/sh3-fullchain.pem
    tls_privkey: secrets/sh3-privkey.pem
dns_records:                    # los nombres de la red
  - [10.8.0.1, gate.home]
  - [10.8.0.25, cloud.sh3.home]
master_ip: 10.8.0.1
ca_cert: ca.pem                 # de confianza dentro de los contenedores y en el host
seed: secrets/seed              # de él se derivan las contraseñas generadas
```

kiwi-modules no tiene autoridad de certificación propia. Por eso, cuando
generas una máquina sin kiwi-server, tienes que aportar tú los archivos del
certificado TLS y de su clave. Si el archivo de máquina no indica ninguna
configuración de WireGuard, kiwi-modules la busca en `secrets/<hostname>.conf`.

## Instalarlo en la máquina { #put-it-on-the-machine }

En la máquina, instala kiwi-stack y aplica el paquete:

```bash
git clone https://github.com/derlocke-ng/kiwi-stack && cd kiwi-stack
sudo ./install.sh install          # /usr/local/bin/kiwi-stack y su biblioteca
sudo kiwi-stack apply /tmp/sh3.bundle
kiwi-stack status
```

kiwi-stack necesita bash y systemd. También necesita el entorno de ejecución de
contenedores que indique el `runtime` del paquete: podman 4.4+ con catatonit, o
docker con el plugin de compose. En Debian, kiwi-stack instala podman por su
cuenta.

`apply` hace con un stack lo mismo que un rol de kiwi-server (consulta
[Máquinas](machines.md#apply)), salvo que no establece el nombre de host ni la
zona horaria. Puedes repetirlo cuantas veces quieras: aplicar otra vez el mismo
paquete no cambia nada. No hay forma de deshacer un `apply`. Para recuperar
datos, usa `kiwi-stack restore` del módulo backup. Para volver a una
configuración anterior, aplica un paquete anterior.

Algunos nombres de la máquina siguen diciendo `kiwi-server`, por ejemplo
`/etc/kiwi-server/stack.env` y `/var/lib/kiwi-server/`. Es a propósito: las
herramientas de Kiwi dependen de esos nombres, así que no se cambian.
