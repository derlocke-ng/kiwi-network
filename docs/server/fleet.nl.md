# Het fleetbestand

In het fleetbestand, `fleet.yaml`, beschrijf je alle machines van je Kiwi
Network. Per machine staat erin welk besturingssysteem ze krijgt, waarvoor ze
wordt gebruikt en hoe haar diensten zijn ingericht. kiwi-server bouwt elke
machine op aan de hand van die beschrijving. Je legt dus één keer vast wat je
wilt en hoeft geen enkele machine met de hand te configureren.

Het bestand heeft twee sleutels. Onder `defaults` staan de instellingen die
voor alle hosts gelden, en onder `hosts` staat per machine een eigen blok. Een
instelling in het blok van een host gaat boven dezelfde instelling in de
standaardwaarden. `kiwi-server init` schrijft een bestand met uitleg in
commentaar waarmee je kunt beginnen. De volledige referentie is
[examples/fleet.yaml](https://github.com/derlocke-ng/kiwi-server/blob/main/examples/fleet.yaml).

Elke host heeft een **doelsysteem** (`target`), het besturingssysteem dat wordt
geïnstalleerd, en een **rol**, de taak die de machine daarna uitvoert.

- `target` is `coreos`, `ucore` (standaard) of `debian`. Zie [Machines](machines.md).
- `role` is `bare` (standaard), `master` of `node`. Zie [Rollen](roles.md).

## Voorbeeld { #example }

Dit fleetbestand beschrijft drie machines. De eerste is de master, de machine
waarmee alle andere verbinding maken, op een Debian-VPS (een gehuurde virtuele
server). De tweede is een gateway-node, die het verkeer van een lokaal netwerk
door de VPN stuurt. De derde is een cloud-node, waarop Nextcloud en Vaultwarden
draaien.

```yaml
defaults:
  target: ucore
  role: bare
  domain: home                       # papaya wordt papaya.home; diensten heten cloud.papaya.home …
  timezone: Europe/Berlin
  disk: /dev/sda                     # wordt door de ISO GEWIST zonder te vragen
  admin:
    user: core
    ssh_keys: [~/.ssh/id_ed25519.pub]
  updates: { enabled: true, days: [Sun], time: "03:30", length_minutes: 90 }
  install: { on_done: poweroff }
  tls: { auto: true, ca_dir: secrets/ca, name_constraints: [home] }
  debian: { release: trixie, partitioning: lvm }

hosts:
  sorbet:                              # de master, een Debian-VPS
    role: master
    target: debian
    disk: /dev/vda
    master:
      vpn-client:
        vpn_provider: mullvad
        wireguard_private_key: "<from your Mullvad WireGuard config>"
        wireguard_addresses: 10.66.1.2/32
        server_countries: Germany
      vpn-server:
        wg_host: vpn.example.org     # waarmee clients en nodes verbinding maken

  lychee:                                # een gateway-node
    role: node
    node:
      preset: gateway
      pub_iface: eth0                # de kant van het LAN
      downloader: { download_dir: /mnt/data/downloads }

  papaya:                               # een cloud-node op uCore HCI
    role: node
    ucore: { image: ghcr.io/ublue-os/ucore-hci:stable }
    node:
      preset: cloud
      vpn_ip: 10.8.0.25
      cloud: { nextcloud_datadir: /mnt/nvme_2tb/docker/knnc-data, memory_limit: 8192M }
      vault: { signups_allowed: true }   # voor het eerste account; zet dit daarna weer uit
```

In het voorbeeld staan geen wachtwoorden voor diensten. Elk wachtwoord dat je
weglaat, genereert kiwi-server uit de seed in `secrets/seed`, en
`kiwi-server secrets show fleet.yaml papaya` toont de wachtwoorden van die host.

Ook de WireGuard-configuratiebestanden van de nodes staan niet in het
voorbeeld. `kiwi-server enroll` schrijft de configuratie van een node naar
`secrets/<hostname>.conf`, en de VPN-client van de node vindt haar daar zonder
vermelding in het fleetbestand. Uit hetzelfde bestand wordt ook het mesh-adres
van de node gelezen. De mesh is het besloten WireGuard-netwerk waarin al je
machines zitten, en het mesh-adres is het adres van een machine in dat netwerk.

## Standaardwaarden { #defaults }

Staat een sleutel niet in je blok `defaults` en ook niet bij een host, dan
gebruikt kiwi-server de ingebouwde waarde uit deze tabel.

| Sleutel | Standaard |
|---|---|
| `target` / `role` / `domain` | `ucore` / `bare` / `home` |
| `timezone` / `locale` / `keyboard` | `UTC` / `en_US.UTF-8` / `us` |
| `disk` | Geen standaardwaarde. `build` heeft hem nodig, en de waarde moet met `/dev/` beginnen |
| `admin` | `user: core`, `ssh_keys: []`, `ssh_password_auth: false`. Stel een `password_hash` in als je op de console wilt inloggen |
| `network` | `dhcp: true`. Voor een vast adres stel je `address` (in CIDR-notatie), `gateway` en `dns` in. Of je stelt een `iprange` in, waaruit de hosts hun adressen krijgen in de volgorde waarin ze in het bestand staan |
| `updates` | `enabled: true`, `days: [Sun]`, `time: "03:30"`, `length_minutes: 90` |
| `install` | `on_done: poweroff` (of `reboot`) |
| `tls` | `auto: true`, `ca_dir: secrets/ca`, `name_constraints: []` |
| `debian` | `release: trixie`, `partitioning: lvm` (`regular`, `lvm`, `crypto`), `encrypt: false` |
| `ucore` | `image: ghcr.io/ublue-os/ucore:stable` |
| `unlock` | De Tang-ringen waaraan de schijf is gekoppeld. Een ring is een Tang-server, waarmee een versleutelde machine bij het opstarten haar schijf kan ontgrendelen (zie [Beheer](operations.md#encrypted-disks-and-unlocking)) |
| `backup` | De hosts waarop een back-up van de fleetmap wordt gemaakt, en hoeveel back-ups er worden bewaard (`hosts: []`, `keep: 10`) |
| `vps` | `server:` het id, de naam of de bijnaam van een server bij netcup |

## Hoe instellingen samengaan { #how-settings-combine }

- Een host overschrijft de standaardwaarden **per sleutel**. Bij een host hoef
  je dus alleen de sleutels te noemen die afwijken. Een uitzondering zijn de
  lijsten `admin.ssh_keys`, `debian.packages`, `debian.kernel_arguments` en de
  lijsten onder `coreos.*`. Wat een host in deze lijsten zet, komt *bij* de
  standaardwaarden en vervangt ze niet.
- De rollen die uit modules zijn opgebouwd, `master` en `node`, hebben hun
  instellingen in een blok met de naam van de rol (`master:` of `node:`). In dat
  blok staan eerst de **stack-instellingen** en daarna **een blok per module**.
  De stack bestaat uit alle containers die een machine voor haar modules
  draait, en de stack-instellingen gelden voor al die containers.
- Een lijst `modules:` in dat blok **vervangt** de lijst met modules van de
  preset. Een preset is een kant-en-klare lijst met modules. Modules die de
  opgesomde modules nodig hebben, worden automatisch toegevoegd.
- **Bestandsinstellingen**, zoals certificaten en configuratiebestanden, geef je
  op als pad ten opzichte van het fleetbestand. kiwi-server kopieert de inhoud
  van die bestanden in het rolscript van de host, het script dat de machine
  voor haar rol inricht.
- Een instelling die je zonder waarde opschrijft, krijgt de standaardwaarde.
  Maak je een tikfout in een sleutel, dan meldt kiwi-server een fout en stelt
  het de sleutel voor die je waarschijnlijk bedoelde.

## Stack-instellingen { #stack-settings }

De stack-instellingen gelden voor de hele stack van een machine. Je schrijft ze
direct in het blok van de rol.

| Instelling | Standaard | Opmerkingen |
|---|---|---|
| `preset` (node) | `gateway` | `gateway`, `cloud` of `minimal` |
| `runtime` | `podman` | `podman` draait de containers als podman-quadlets, systemd-units voor containers. `docker` gebruikt docker compose |
| `auto_update` | `registry` | `registry` voert eens per week `podman auto-update` uit. Met `off` veranderen de containerimages alleen als je de host opnieuw toepast |
| `docker_dir` | `/home/user/docker` | de map met de stack en de gegevens ervan |
| `service_user` | de beheerder | de gebruiker die eigenaar is van de gegevensmappen |
| `vpn_ip` | uit de WireGuard-configuratie | het mesh-adres van de machine |
| `master_ip` | uit de fleet | het mesh-adres van de master |
| `mesh_subnet` | `10.8.0.0/16` | |
| `wg_mtu` / `bridge_mtu` | `1376` / `1500` | je kunt ze meten met `kiwi-server mtu` |
| `docker_subnet` | `172.64.0.0/24` master, `172.128.0.0/24` node | |
| `pub_iface` | uit de standaardroute | de netwerkinterface aan de kant van het LAN |
| `daily_vpn_restart` | `07:00` | een lege waarde zet de dagelijkse herstart uit |
| `weekly_update` | `Sun *-*-* 00:00` | een lege waarde zet de wekelijkse update uit |

`kiwi-server roles -v` en `kiwi-server modules -v` tonen elke instelling met
haar standaardwaarde.

## Controleren wat je hebt geschreven { #checking-what-you-wrote }

kiwi-server kan het fleetbestand voor je controleren en laten zien wat het van
één host maakt.

```bash
kiwi-server validate fleet.yaml          # fouten en waarschuwingen
kiwi-server show fleet.yaml papaya          # de configuratie die echt geldt voor één host, secrets afgeschermd
```

kiwi-server controleert ook het domein. Het weigert `.local` en waarschuwt bij
`.lan` en bij openbare topleveldomeinen (zie
[DNS](../network/dns.md#names-servicehostnamehome)).

## Een v1-machine overnemen { #taking-over-a-v1-machine }

Een machine waarop een van de oude v1-stacks draaide, kun je in de fleet
opnemen zonder dat je gegevens kwijtraakt. De standaardruntime is nu podman, en
het rolscript stopt geen docker-containers die nog draaien. Stel dus
`runtime: docker` in, of stop eerst de oude stack. Stel daarna `docker_subnet`
in op het subnet dat de oude stack gebruikte, en hernoem de gegevensmappen naar
de nieuwe modulenamen (`kmvpn-server` → `km-vpn-server`, `knvault` → `kn-vault`,
…). De containers houden dan hun adressen, en wg-easy houdt zijn peers.
