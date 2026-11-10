# Eén machine, zonder fleet

kiwi-server is gebouwd uit twee kleinere tools, en die kun je ook los gebruiken:

| Repository | Wat het is |
|---|---|
| [**kiwi-modules**](https://github.com/derlocke-ng/kiwi-modules) | De modules en hun renderer: **één machinebestand erin, een stackbundel eruit**. v0.23.0, GPL-3.0-or-later |
| [**kiwi-stack**](https://github.com/derlocke-ng/kiwi-stack) | De kant van de machine: het commando `kiwi-stack` en de bibliotheek die een bundel op CoreOS, uCore of Debian zetten en draaiende houden. v0.5.0, GPL-3.0-or-later |

Gebruik ze als je een stack op één machine wilt zonder de rest: een node die je
met de hand inricht, een module die je ontwikkelt, of een machine die haar eigen
stack rendert. kiwi-server neemt beide in zich op, vastgepind op een tag. Een
machine die op de ene of de andere manier is ingericht, ziet er uiteindelijk
hetzelfde uit, en beide leiden dezelfde geheimen af uit dezelfde seed.

```
machine.yaml ──kiwi-modules render──▶ bundle/ ──copy──▶ sudo kiwi-stack apply bundle/
                                      stack.sh            → podman quadlets (or compose)
                                      docker-compose.yml  → configs, host units, timers
                                      quadlets/  configs  → kiwi-stack.target, verify
```

## Een machine renderen { #render-a-machine }

```bash
git clone https://github.com/derlocke-ng/kiwi-modules && cd kiwi-modules
./install.sh install                       # ~/.local/bin/kiwi-modules
mkdir -p sh3/secrets && head -c 32 /dev/urandom > sh3/secrets/seed
cp examples/sh3.yaml sh3/                  # bewerken: TLS-bestanden, de WireGuard-configuratie
kiwi-modules render sh3/sh3.yaml -o sh3/sh3.bundle
scp -r sh3/sh3.bundle sh3:/tmp/ && ssh sh3 sudo kiwi-stack apply /tmp/sh3.bundle
```

Het vereist Python 3 met PyYAML en Jinja2. `kiwi-modules modules -v` toont elke
module en instelling, en `kiwi-modules profiles` toont de rollen en hun presets.

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
ca_cert: ca.pem                 # vertrouwd binnen de containers en op de host
seed: secrets/seed              # gegenereerde wachtwoorden worden hiervan afgeleid
```

kiwi-modules heeft geen eigen certificaatautoriteit, dus een losse render heeft
de bestanden met het TLS-certificaat en de sleutel nodig. De WireGuard-configuratie
wordt gezocht in `secrets/<hostname>.conf` als het machinebestand er geen noemt.

## Op de machine zetten { #put-it-on-the-machine }

```bash
git clone https://github.com/derlocke-ng/kiwi-stack && cd kiwi-stack
sudo ./install.sh install          # /usr/local/bin/kiwi-stack en de bibliotheek
sudo kiwi-stack apply /tmp/sh3.bundle
kiwi-stack status
```

Het vereist bash en systemd, plus podman 4.4+ met catatonit (of docker met de
compose-plugin), afhankelijk van de `runtime` van de bundel. Op Debian
installeert het podman zelf.

`apply` doet wat een kiwi-server-rol met een stack doet (zie
[Machines](machines.md#apply)), behalve de hostnaam en tijdzone instellen. Het is
herhaalbaar: dezelfde bundel nog eens verandert niets. Er is geen rollback.
Gegevens komen terug met `kiwi-stack restore` uit de backup-module, en een
oudere configuratie door een oudere bundel toe te passen.

Op de machine zeggen de namen nog steeds `kiwi-server`
(`/etc/kiwi-server/stack.env`, `/var/lib/kiwi-server/`), en dat is zo bedoeld:
ze zijn het contract tussen de twee.
