# Uma máquina, sem ficheiro fleet

O kiwi-server gere um conjunto inteiro de máquinas. Se só quiseres correr uma
stack numa única máquina, não precisas dele. Uma stack é o conjunto de
contentores e serviços que uma máquina corre. O kiwi-server é feito de duas
ferramentas mais pequenas, e podes usá-las por si só:

| Repositório | O que é |
|---|---|
| [**kiwi-modules**](https://github.com/derlocke-ng/kiwi-modules) | Os módulos e o programa que gera a configuração a partir deles. Lê **o ficheiro de uma máquina e escreve um pacote com a stack**, ou seja, uma pasta com a configuração gerada da stack dessa máquina. v0.23.0, GPL-3.0-or-later |
| [**kiwi-stack**](https://github.com/derlocke-ng/kiwi-stack) | A parte que corre na máquina. É composta pelo comando `kiwi-stack` e por uma biblioteca, que instalam um pacote numa máquina CoreOS, uCore ou Debian e o mantêm a funcionar. v0.5.0, GPL-3.0-or-later |

Usa estas duas ferramentas quando quiseres uma stack numa máquina sem o resto
do kiwi-server: por exemplo, para um node que configuras à mão, para um módulo
que estás a desenvolver ou para uma máquina que gera a sua própria stack. O
kiwi-server traz uma cópia de cada uma, fixada numa tag de versão. Quer prepares
a máquina com o kiwi-server, quer com as duas ferramentas, o resultado é
idêntico, e as duas vias derivam os mesmos segredos da mesma seed.

```
machine.yaml ──kiwi-modules render──▶ bundle/ ──copy──▶ sudo kiwi-stack apply bundle/
                                      stack.sh            → podman quadlets (or compose)
                                      docker-compose.yml  → configs, host units, timers
                                      quadlets/  configs  → kiwi-stack.target, verify
```

## Gerar a configuração de uma máquina { #render-a-machine }

Os comandos abaixo instalam o kiwi-modules, criam uma seed e geram, a partir do
ficheiro de máquina de exemplo, um pacote. A última linha copia o pacote para a
máquina e aplica-o lá.

```bash
git clone https://github.com/derlocke-ng/kiwi-modules && cd kiwi-modules
./install.sh install                       # ~/.local/bin/kiwi-modules
mkdir -p sh3/secrets && head -c 32 /dev/urandom > sh3/secrets/seed
cp examples/sh3.yaml sh3/                  # a editar: os ficheiros TLS, a configuração WireGuard
kiwi-modules render sh3/sh3.yaml -o sh3/sh3.bundle
scp -r sh3/sh3.bundle sh3:/tmp/ && ssh sh3 sudo kiwi-stack apply /tmp/sh3.bundle
```

O kiwi-modules precisa do Python 3 com o PyYAML e o Jinja2.
`kiwi-modules modules -v` lista todos os módulos e definições, e
`kiwi-modules profiles` lista as funções e os respetivos presets.

Um ficheiro de máquina descreve uma única máquina, como neste exemplo:

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
ca_cert: ca.pem                 # de confiança dentro dos contentores e na máquina
seed: secrets/seed              # as palavras-passe geradas derivam dela
```

O kiwi-modules não tem uma autoridade de certificação própria. Por isso, quando
geras a configuração de uma máquina sem o kiwi-server, tens de fornecer tu os
ficheiros do certificado TLS e da chave. Se o ficheiro de máquina não indicar
nenhuma configuração WireGuard, o kiwi-modules procura-a em
`secrets/<hostname>.conf`.

## Instalar na máquina { #put-it-on-the-machine }

Na máquina, instala o kiwi-stack e aplica o pacote:

```bash
git clone https://github.com/derlocke-ng/kiwi-stack && cd kiwi-stack
sudo ./install.sh install          # /usr/local/bin/kiwi-stack e a sua biblioteca
sudo kiwi-stack apply /tmp/sh3.bundle
kiwi-stack status
```

O kiwi-stack precisa do bash e do systemd. Precisa também do runtime de
contentores indicado em `runtime` no pacote: ou o podman 4.4 ou mais recente,
com o catatonit, ou o docker com o plugin compose. No Debian, o kiwi-stack
instala o podman sozinho.

O `apply` faz com uma stack o mesmo que uma função do kiwi-server (vê
[Máquinas](machines.md#apply)), só que não define o nome da máquina nem o fuso
horário. Podes repeti-lo à vontade: aplicar outra vez o mesmo pacote não muda
nada. Não há forma de reverter para uma versão anterior. Para recuperares
dados, usa o `kiwi-stack restore` do módulo backup. Para voltares a uma
configuração mais antiga, aplica um pacote mais antigo.

Na máquina, os nomes continuam a dizer `kiwi-server` (`/etc/kiwi-server/stack.env`,
`/var/lib/kiwi-server/`), de propósito: as ferramentas
Kiwi dependem destes nomes, por isso não são alterados.
