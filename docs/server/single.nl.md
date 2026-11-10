# Eén machine zonder fleet

kiwi-server beheert een hele fleet van machines. Wil je alleen op één machine
een stack draaien, dan heb je het niet nodig. Een stack bestaat uit de
containers en diensten die een machine draait. kiwi-server is opgebouwd uit
twee kleinere programma’s, en die kun je ook los gebruiken:

| Repository | Wat het is |
|---|---|
| [**kiwi-modules**](https://github.com/derlocke-ng/kiwi-modules) | De modules en het programma dat er configuratie uit genereert. Het leest **één machinebestand en schrijft een stackbundel**: een map met de gegenereerde configuratie van de stack van de machine. v0.23.0, GPL-3.0-or-later |
| [**kiwi-stack**](https://github.com/derlocke-ng/kiwi-stack) | Het deel dat op de machine draait. Het bestaat uit het commando `kiwi-stack` en een bibliotheek, die een bundel op een machine met CoreOS, uCore of Debian zetten en hem in de lucht houden. v0.5.0, GPL-3.0-or-later |

Gebruik deze twee programma’s als je een stack op één machine wilt zonder de
rest van kiwi-server. Denk aan een node die je met de hand inricht, een module
waaraan je werkt, of een machine die haar eigen stack genereert. kiwi-server
bevat van beide een kopie, elk vastgezet op een releasetag. Een machine wordt
precies hetzelfde, of je haar nu met kiwi-server inricht of met de twee
programma’s, en in beide gevallen worden uit dezelfde seed dezelfde secrets
afgeleid.

```
machine.yaml ──kiwi-modules render──▶ bundle/ ──copy──▶ sudo kiwi-stack apply bundle/
                                      stack.sh            → podman quadlets (or compose)
                                      docker-compose.yml  → configs, host units, timers
                                      quadlets/  configs  → kiwi-stack.target, verify
```

## De configuratie van een machine genereren { #render-a-machine }

Met de commando’s hieronder installeer je kiwi-modules, maak je een seed aan en
genereer je uit het voorbeeldmachinebestand een bundel. De laatste regel
kopieert de bundel naar de machine en past hem daar toe.

```bash
git clone https://github.com/derlocke-ng/kiwi-modules && cd kiwi-modules
./install.sh install                       # ~/.local/bin/kiwi-modules
mkdir -p sh3/secrets && head -c 32 /dev/urandom > sh3/secrets/seed
cp examples/sh3.yaml sh3/                  # aanpassen: TLS-bestanden, de WireGuard-configuratie
kiwi-modules render sh3/sh3.yaml -o sh3/sh3.bundle
scp -r sh3/sh3.bundle sh3:/tmp/ && ssh sh3 sudo kiwi-stack apply /tmp/sh3.bundle
```

kiwi-modules heeft Python 3 met PyYAML en Jinja2 nodig.
`kiwi-modules modules -v` toont elke module en elke instelling, en
`kiwi-modules profiles` toont de rollen en hun presets.

Een machinebestand beschrijft één machine, zoals in dit voorbeeld:

```yaml
# een cloud-node
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
dns_records:                    # de namen van het netwerk
  - [10.8.0.1, gate.home]
  - [10.8.0.25, cloud.sh3.home]
master_ip: 10.8.0.1
ca_cert: ca.pem                 # vertrouwd in de containers en op de host
seed: secrets/seed              # gegenereerde wachtwoorden worden hieruit afgeleid
```

kiwi-modules heeft geen eigen certificaatautoriteit. Genereer je een machine
zonder kiwi-server, dan moet je de bestanden met het TLS-certificaat en de
sleutel dus zelf aanleveren. Noemt het machinebestand geen
WireGuard-configuratie, dan zoekt kiwi-modules die in
`secrets/<hostname>.conf`.

## Op de machine zetten { #put-it-on-the-machine }

Installeer kiwi-stack op de machine en pas de bundel toe:

```bash
git clone https://github.com/derlocke-ng/kiwi-stack && cd kiwi-stack
sudo ./install.sh install          # /usr/local/bin/kiwi-stack en de bibliotheek
sudo kiwi-stack apply /tmp/sh3.bundle
kiwi-stack status
```

kiwi-stack heeft bash en systemd nodig. Daarnaast is de container-runtime nodig
die bij `runtime` in de bundel staat: podman 4.4+ met catatonit, of docker met
de compose-plug-in. Op Debian installeert kiwi-stack podman zelf.

`apply` doet met een stack hetzelfde als een rol van kiwi-server (zie
[Machines](machines.md#apply)), alleen stelt het de hostnaam en de tijdzone
niet in. Je kunt het herhalen: pas je dezelfde bundel opnieuw toe, dan
verandert er niets. Er is geen rollback. Gegevens haal je terug met
`kiwi-stack restore` uit de module backup. Een oudere configuratie krijg je
terug door een oudere bundel toe te passen.

Sommige namen op de machine bevatten nog `kiwi-server`, bijvoorbeeld
`/etc/kiwi-server/stack.env` en `/var/lib/kiwi-server/`. Dat is met opzet: de
Kiwi-programma’s rekenen op deze namen, dus ze worden niet hernoemd.
