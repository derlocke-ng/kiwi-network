# Una máquina, sin fleet

kiwi-server está hecho de dos herramientas más pequeñas, y puedes usarlas por
separado:

| Repositorio | Qué es |
|---|---|
| [**kiwi-modules**](https://github.com/derlocke-ng/kiwi-modules) | Los módulos y su renderizador: **entra un archivo de máquina, sale un paquete de stack**. v0.23.0, GPL-3.0-or-later |
| [**kiwi-stack**](https://github.com/derlocke-ng/kiwi-stack) | La parte de la máquina: el comando `kiwi-stack` y la biblioteca que ponen un paquete en CoreOS, uCore o Debian y lo mantienen en marcha. v0.5.0, GPL-3.0-or-later |

Úsalas cuando quieras un stack en una máquina sin todo lo demás: un node que
configuras a mano, un módulo que estás desarrollando o una máquina que renderiza
su propio stack. kiwi-server incluye ambas en su repositorio, fijadas por tag.
Una máquina configurada de cualquiera de las dos formas acaba idéntica, y ambas
derivan los mismos secretos de la misma semilla.

```
machine.yaml ──kiwi-modules render──▶ bundle/ ──copy──▶ sudo kiwi-stack apply bundle/
                                      stack.sh            → podman quadlets (or compose)
                                      docker-compose.yml  → configs, host units, timers
                                      quadlets/  configs  → kiwi-stack.target, verify
```

## Renderizar una máquina { #render-a-machine }

```bash
git clone https://github.com/derlocke-ng/kiwi-modules && cd kiwi-modules
./install.sh install                       # ~/.local/bin/kiwi-modules
mkdir -p sh3/secrets && head -c 32 /dev/urandom > sh3/secrets/seed
cp examples/sh3.yaml sh3/                  # edita: archivos TLS, la configuración WireGuard
kiwi-modules render sh3/sh3.yaml -o sh3/sh3.bundle
scp -r sh3/sh3.bundle sh3:/tmp/ && ssh sh3 sudo kiwi-stack apply /tmp/sh3.bundle
```

Necesita Python 3 con PyYAML y Jinja2. `kiwi-modules modules -v` enumera cada
módulo y ajuste, y `kiwi-modules profiles` enumera los roles y sus presets.

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
dns_records:                    # the network's names
  - [10.8.0.1, gate.home]
  - [10.8.0.25, cloud.sh3.home]
master_ip: 10.8.0.1
ca_cert: ca.pem                 # de confianza dentro de los contenedores y en el host
seed: secrets/seed              # de ella derivan las contraseñas generadas
```

kiwi-modules no tiene autoridad de certificación propia, así que un render
independiente necesita los archivos del certificado TLS y de la clave. La
configuración WireGuard se busca en `secrets/<hostname>.conf` cuando el archivo
de máquina no nombra ninguna.

## Ponerlo en la máquina { #put-it-on-the-machine }

```bash
git clone https://github.com/derlocke-ng/kiwi-stack && cd kiwi-stack
sudo ./install.sh install          # /usr/local/bin/kiwi-stack y su biblioteca
sudo kiwi-stack apply /tmp/sh3.bundle
kiwi-stack status
```

Necesita bash y systemd, más podman 4.4+ con catatonit (o docker con el plugin
compose), según cuál sea el `runtime` del paquete. En Debian instala podman por
sí mismo.

`apply` hace lo que hace un rol de kiwi-server con un stack (consulta
[Máquinas](machines.md#apply)), salvo fijar el nombre de host y la zona horaria.
Es repetible: el mismo paquete otra vez no cambia nada. No hay vuelta atrás. Los
datos vuelven con `kiwi-stack restore` desde el módulo backup, y una
configuración anterior, aplicando un paquete anterior.

En la máquina, los nombres siguen diciendo `kiwi-server`
(`/etc/kiwi-server/stack.env`, `/var/lib/kiwi-server/`), por diseño: son el
contrato entre los dos.
