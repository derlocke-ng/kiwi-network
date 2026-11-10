# Una macchina, senza fleet

kiwi-server è costruito da due strumenti più piccoli, e puoi usarli da soli:

| Repository | Cos'è |
|---|---|
| [**kiwi-modules**](https://github.com/derlocke-ng/kiwi-modules) | I moduli e il loro renderer: **entra un file macchina, esce un bundle di stack**. v0.23.0, GPL-3.0-or-later |
| [**kiwi-stack**](https://github.com/derlocke-ng/kiwi-stack) | Il lato macchina: il comando `kiwi-stack` e la libreria che mettono un bundle su CoreOS, uCore o Debian e lo tengono in funzione. v0.5.0, GPL-3.0-or-later |

Usali quando vuoi uno stack su una sola macchina senza tutto il resto: un node che configuri
a mano, un modulo che stai sviluppando o una macchina che esegue il render del proprio
stack. kiwi-server li include entrambi nel suo repository, fissati per tag. Una macchina configurata in un modo o nell'altro
risulta identica, ed entrambi derivano gli stessi segreti dallo stesso seed.

```
machine.yaml ──kiwi-modules render──▶ bundle/ ──copy──▶ sudo kiwi-stack apply bundle/
                                      stack.sh            → podman quadlets (or compose)
                                      docker-compose.yml  → configs, host units, timers
                                      quadlets/  configs  → kiwi-stack.target, verify
```

## Render di una macchina { #render-a-machine }

```bash
git clone https://github.com/derlocke-ng/kiwi-modules && cd kiwi-modules
./install.sh install                       # ~/.local/bin/kiwi-modules
mkdir -p sh3/secrets && head -c 32 /dev/urandom > sh3/secrets/seed
cp examples/sh3.yaml sh3/                  # da modificare: file TLS, la configurazione WireGuard
kiwi-modules render sh3/sh3.yaml -o sh3/sh3.bundle
scp -r sh3/sh3.bundle sh3:/tmp/ && ssh sh3 sudo kiwi-stack apply /tmp/sh3.bundle
```

Richiede Python 3 con PyYAML e Jinja2. `kiwi-modules modules -v` elenca ogni
modulo e ogni impostazione, e `kiwi-modules profiles` elenca i ruoli e i loro
preset.

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
ca_cert: ca.pem                 # attendibile nei container e sulla macchina host
seed: secrets/seed              # le password generate derivano da qui
```

kiwi-modules non ha un'autorità di certificazione propria, quindi un render autonomo
ha bisogno dei file del certificato TLS e della chiave. La configurazione WireGuard viene cercata in
`secrets/<hostname>.conf` quando il file macchina non ne indica una.

## Mettilo sulla macchina { #put-it-on-the-machine }

```bash
git clone https://github.com/derlocke-ng/kiwi-stack && cd kiwi-stack
sudo ./install.sh install          # /usr/local/bin/kiwi-stack e la sua libreria
sudo kiwi-stack apply /tmp/sh3.bundle
kiwi-stack status
```

Richiede bash e systemd, più podman 4.4+ con catatonit (oppure docker con
il plugin compose), a seconda del `runtime` del bundle. Su Debian installa
podman da solo.

`apply` fa con uno stack quello che fa un ruolo di kiwi-server (vedi
[Macchine](machines.md#apply)), tranne impostare hostname e fuso orario. È
ripetibile: applicare di nuovo lo stesso bundle non cambia nulla. Non c'è rollback. I dati
tornano con `kiwi-stack restore` dal modulo di backup, e una configurazione precedente
applicando un bundle precedente.

Sulla macchina i nomi dicono ancora `kiwi-server` (`/etc/kiwi-server/stack.env`,
`/var/lib/kiwi-server/`), per scelta: sono il contratto tra i due.
