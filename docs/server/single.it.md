# Una macchina, senza fleet

kiwi-server gestisce un’intera fleet di macchine. Se vuoi far girare uno stack
su una macchina sola, non ti serve. Uno stack è l’insieme dei container e dei
servizi che una macchina esegue. kiwi-server è composto da due strumenti più
piccoli, che puoi usare anche da soli:

| Repository | Che cos’è |
|---|---|
| [**kiwi-modules**](https://github.com/derlocke-ng/kiwi-modules) | I moduli e il programma che li genera. Legge **un file macchina e scrive un bundle dello stack**, cioè una cartella con la configurazione generata dello stack della macchina. v0.23.0, GPL-3.0-or-later |
| [**kiwi-stack**](https://github.com/derlocke-ng/kiwi-stack) | La parte che gira sulla macchina. È composta dal comando `kiwi-stack` e da una libreria, che installano un bundle su una macchina CoreOS, uCore o Debian e lo tengono in funzione. v0.5.0, GPL-3.0-or-later |

Usa i due strumenti quando vuoi uno stack su una macchina sola, senza il resto
di kiwi-server: per esempio un node che configuri a mano, un modulo che stai
sviluppando o una macchina che genera da sé il proprio stack. kiwi-server
contiene una copia di entrambi, ciascuna fissata a un tag di release. Che tu
configuri una macchina con kiwi-server o con i due strumenti, il risultato è
identico, e in entrambi i casi dallo stesso seed si ottengono gli stessi
segreti.

```
machine.yaml ──kiwi-modules render──▶ bundle/ ──copy──▶ sudo kiwi-stack apply bundle/
                                      stack.sh            → podman quadlets (or compose)
                                      docker-compose.yml  → configs, host units, timers
                                      quadlets/  configs  → kiwi-stack.target, verify
```

## Generare la configurazione di una macchina { #render-a-machine }

I comandi qui sotto installano kiwi-modules, creano un seed e trasformano il
file macchina di esempio in un bundle. L’ultima riga copia il bundle sulla
macchina e lo applica lì.

```bash
git clone https://github.com/derlocke-ng/kiwi-modules && cd kiwi-modules
./install.sh install                       # ~/.local/bin/kiwi-modules
mkdir -p sh3/secrets && head -c 32 /dev/urandom > sh3/secrets/seed
cp examples/sh3.yaml sh3/                  # da modificare: file TLS, configurazione WireGuard
kiwi-modules render sh3/sh3.yaml -o sh3/sh3.bundle
scp -r sh3/sh3.bundle sh3:/tmp/ && ssh sh3 sudo kiwi-stack apply /tmp/sh3.bundle
```

kiwi-modules richiede Python 3 con PyYAML e Jinja2. `kiwi-modules modules -v`
elenca tutti i moduli e le loro impostazioni, e `kiwi-modules profiles` elenca
i ruoli con i loro preset.

Un file macchina descrive una sola macchina, come in questo esempio:

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
dns_records:                    # i nomi della rete
  - [10.8.0.1, gate.home]
  - [10.8.0.25, cloud.sh3.home]
master_ip: 10.8.0.1
ca_cert: ca.pem                 # considerato attendibile nei container e sull’host
seed: secrets/seed              # le password generate derivano da qui
```

kiwi-modules non ha un’autorità di certificazione propria. Se generi la
configurazione di una macchina senza kiwi-server, il certificato TLS e il file
della chiave devi quindi procurarteli tu. Se il file macchina non indica una
configurazione WireGuard, kiwi-modules la cerca in `secrets/<hostname>.conf`.

## Installarla sulla macchina { #put-it-on-the-machine }

Sulla macchina installa kiwi-stack e applica il bundle:

```bash
git clone https://github.com/derlocke-ng/kiwi-stack && cd kiwi-stack
sudo ./install.sh install          # /usr/local/bin/kiwi-stack e la sua libreria
sudo kiwi-stack apply /tmp/sh3.bundle
kiwi-stack status
```

kiwi-stack richiede bash e systemd. Richiede anche il runtime per container
indicato da `runtime` nel bundle: podman 4.4+ con catatonit, oppure docker con
il plugin compose. Su Debian, podman lo installa kiwi-stack.

`apply` fa con uno stack la stessa cosa che fa un ruolo di kiwi-server (vedi
[Macchine](machines.md#apply)), con una differenza: non imposta il nome host né
il fuso orario. Puoi ripeterlo quante volte vuoi, e applicare di nuovo lo
stesso bundle non cambia nulla. Non esiste un modo per tornare indietro
(rollback). Per recuperare i dati usa `kiwi-stack restore` del modulo di
backup. Per tornare a una configurazione precedente, applica un bundle più
vecchio.

Alcuni nomi sulla macchina contengono ancora `kiwi-server`, per esempio
`/etc/kiwi-server/stack.env` e `/var/lib/kiwi-server/`. È voluto: gli
strumenti Kiwi si basano su questi nomi, quindi non vengono rinominati.
