# Uma máquina, sem fleet

O kiwi-server é construído a partir de duas ferramentas mais pequenas, e podes
usá-las sozinhas:

| Repositório | O que é |
|---|---|
| [**kiwi-modules**](https://github.com/derlocke-ng/kiwi-modules) | Os módulos e o seu renderizador: **entra um ficheiro de máquina, sai um pacote de stack**. v0.23.0, GPL-3.0-or-later |
| [**kiwi-stack**](https://github.com/derlocke-ng/kiwi-stack) | O lado da máquina: o comando e a biblioteca `kiwi-stack`, que põem um pacote no CoreOS, no uCore ou no Debian e o mantêm a correr. v0.5.0, GPL-3.0-or-later |

Usa-as quando quiseres uma stack numa máquina sem o resto: um node que configuras
à mão, um módulo que estás a desenvolver, ou uma máquina que renderiza a sua
própria stack. O kiwi-server inclui ambas no seu repositório, fixadas por tag.
Uma máquina configurada de uma maneira ou de outra fica idêntica, e ambas derivam
os mesmos segredos da mesma seed.

```
machine.yaml ──kiwi-modules render──▶ bundle/ ──copy──▶ sudo kiwi-stack apply bundle/
                                      stack.sh            → podman quadlets (or compose)
                                      docker-compose.yml  → configs, host units, timers
                                      quadlets/  configs  → kiwi-stack.target, verify
```

## Renderizar uma máquina { #render-a-machine }

```bash
git clone https://github.com/derlocke-ng/kiwi-modules && cd kiwi-modules
./install.sh install                       # ~/.local/bin/kiwi-modules
mkdir -p sh3/secrets && head -c 32 /dev/urandom > sh3/secrets/seed
cp examples/sh3.yaml sh3/                  # edita: ficheiros TLS, a configuração WireGuard
kiwi-modules render sh3/sh3.yaml -o sh3/sh3.bundle
scp -r sh3/sh3.bundle sh3:/tmp/ && ssh sh3 sudo kiwi-stack apply /tmp/sh3.bundle
```

Precisa de Python 3 com PyYAML e Jinja2. `kiwi-modules modules -v` lista todos os
módulos e definições, e `kiwi-modules profiles` lista os papéis e as suas
predefinições.

```yaml
# um node cloud
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
dns_records:                    # os nomes da rede
  - [10.8.0.1, gate.home]
  - [10.8.0.25, cloud.sh3.home]
master_ip: 10.8.0.1
ca_cert: ca.pem                 # de confiança dentro dos contentores e no anfitrião
seed: secrets/seed              # as palavras-passe geradas derivam dela
```

O kiwi-modules não tem uma autoridade de certificação própria, por isso uma
renderização autónoma precisa dos ficheiros do certificado TLS e da chave. A
configuração WireGuard é encontrada em `secrets/<hostname>.conf` quando o ficheiro
de máquina não indica nenhuma.

## Pô-la na máquina { #put-it-on-the-machine }

```bash
git clone https://github.com/derlocke-ng/kiwi-stack && cd kiwi-stack
sudo ./install.sh install          # /usr/local/bin/kiwi-stack e a sua biblioteca
sudo kiwi-stack apply /tmp/sh3.bundle
kiwi-stack status
```

Precisa de bash e systemd, mais podman 4.4+ com catatonit (ou docker com o plugin
compose), conforme o `runtime` do pacote. No Debian instala o próprio podman.

O `apply` faz o que um papel do kiwi-server faz com uma stack (ver
[Máquinas](machines.md#apply)), exceto definir o nome de anfitrião e o fuso
horário. É repetível: o mesmo pacote outra vez não muda nada. Não há reversão. Os
dados regressam com `kiwi-stack restore` a partir do módulo backup, e uma
configuração mais antiga aplicando um pacote mais antigo.

Na máquina, os nomes continuam a dizer `kiwi-server` (`/etc/kiwi-server/stack.env`,
`/var/lib/kiwi-server/`), por desenho: são o contrato entre os dois.
