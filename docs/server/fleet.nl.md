# Het fleet-bestand

`fleet.yaml` beschrijft elke machine die kiwi-server bouwt. Het heeft twee
sleutels: `defaults`, dat voor elke host geldt, en `hosts`, met één vermelding
per machine. Alles wat een host instelt, gaat boven de standaardwaarden.
`kiwi-server init` schrijft een becommentarieerd beginpunt, en de volledige
referentie is [examples/fleet.yaml](https://github.com/derlocke-ng/kiwi-server/blob/main/examples/fleet.yaml).

Een host heeft een **target** (wat er geïnstalleerd wordt) en een **rol** (wat
hij wordt):

- `target`: `coreos`, `ucore` (de standaard) of `debian`. Zie [Machines](machines.md).
- `role`: `bare` (de standaard), `master` of `node`. Zie [Rollen](roles.md).

## Voorbeeld { #example }

```yaml
defaults:
  target: ucore
  role: bare
  domain: home                       # papaya wordt papaya.home; diensten zijn cloud.papaya.home …
  timezone: Europe/Berlin
  disk: /dev/sda                     # door de ISO GEWIST zonder te vragen
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
        wg_host: vpn.example.org     # waarmee clients en nodes verbinden

  lychee:                                # een gateway-node
    role: node
    node:
      preset: gateway
      pub_iface: eth0                # de LAN-kant
      downloader: { download_dir: /mnt/data/downloads }

  papaya:                               # een cloud-node op uCore HCI
    role: node
    ucore: { image: ghcr.io/ublue-os/ucore-hci:stable }
    node:
      preset: cloud
      vpn_ip: 10.8.0.25
      cloud: { nextcloud_datadir: /mnt/nvme_2tb/docker/knnc-data, memory_limit: 8192M }
      vault: { signups_allowed: true }   # voor het eerste account; zet het daarna uit
```

Er staan geen wachtwoorden van diensten in. Elk wachtwoord dat je weglaat, wordt
gegenereerd uit `secrets/seed`, en `kiwi-server secrets show fleet.yaml papaya`
toont ze. De WireGuard-configuraties van de nodes worden ook niet genoemd:
`kiwi-server enroll` schrijft `secrets/<hostname>.conf`, die elke node zelf
vindt, en het mesh-adres van de node wordt daaruit gelezen.

## Standaardwaarden { #defaults }

| Sleutel | Standaard |
|---|---|
| `target` / `role` / `domain` | `ucore` / `bare` / `home` |
| `timezone` / `locale` / `keyboard` | `UTC` / `en_US.UTF-8` / `us` |
| `disk` | geen; vereist voor `build`, moet beginnen met `/dev/` |
| `admin` | `user: core`, `ssh_keys: []`, `ssh_password_auth: false`; geef een `password_hash` op voor de console |
| `network` | `dhcp: true`; statisch met `address` (CIDR), `gateway`, `dns`, of een `iprange` die adressen uitdeelt in de volgorde van het bestand |
| `updates` | `enabled: true`, `days: [Sun]`, `time: "03:30"`, `length_minutes: 90` |
| `install` | `on_done: poweroff` (of `reboot`) |
| `tls` | `auto: true`, `ca_dir: secrets/ca`, `name_constraints: []` |
| `debian` | `release: trixie`, `partitioning: lvm` (`regular`, `lvm`, `crypto`), `encrypt: false` |
| `ucore` | `image: ghcr.io/ublue-os/ucore:stable` |
| `unlock` | Tang-ringen om de schijf aan te binden (zie [Beheer](operations.md#encrypted-disks-and-unlocking)) |
| `backup` | waarheen de fleet-map wordt geback-upt (`hosts: []`, `keep: 10`) |
| `vps` | `server:` een id, naam of bijnaam van een netcup-server |

## Hoe instellingen samengaan { #how-settings-combine }

- Hosts gaan **sleutel voor sleutel** boven de standaardwaarden. De lijsten
  `admin.ssh_keys`, `debian.packages`, `debian.kernel_arguments` en de
  `coreos.*`-lijsten worden in plaats daarvan bij de standaardwaarden *opgeteld*.
- Een modulerol houdt zijn instellingen in een blok met de naam van de rol
  (`master:`, `node:`): eerst de **stack-instellingen**, daarna **één blok per
  module**.
- `modules:` in dat blok **vervangt** de modulelijst van de preset. Vereiste
  modules worden vanzelf toegevoegd.
- **Bestandsinstellingen** (certificaten, configuraties) zijn paden relatief aan
  het fleet-bestand. Hun inhoud wordt ingebed in het rolscript van de host.
- Een instelling zonder waarde betekent de standaard. Een verkeerd gespelde
  sleutel is een fout, met een suggestie.

## Stack-instellingen { #stack-settings }

| Instelling | Standaard | Opmerkingen |
|---|---|---|
| `preset` (node) | `gateway` | `gateway`, `cloud` of `minimal` |
| `runtime` | `podman` | podman-quadlets; `docker` draait docker compose |
| `auto_update` | `registry` | wekelijks `podman auto-update`; `off`: images veranderen met een apply |
| `docker_dir` | `/home/user/docker` | de stack en zijn gegevens |
| `service_user` | de beheerdersgebruiker | eigenaar van de gegevensmappen |
| `vpn_ip` | uit de WireGuard-configuratie | het mesh-adres van de machine |
| `master_ip` | uit de fleet | het mesh-adres van de master |
| `mesh_subnet` | `10.8.0.0/16` | |
| `wg_mtu` / `bridge_mtu` | `1376` / `1500` | meet met `kiwi-server mtu` |
| `docker_subnet` | `172.64.0.0/24` master, `172.128.0.0/24` node | |
| `pub_iface` | uit de standaardroute | de LAN-interface |
| `daily_vpn_restart` | `07:00` | leeg: nooit |
| `weekly_update` | `Sun *-*-* 00:00` | leeg: nooit |

`kiwi-server roles -v` en `kiwi-server modules -v` tonen elke instelling met
haar standaardwaarde.

## Controleren wat je schreef { #checking-what-you-wrote }

```bash
kiwi-server validate fleet.yaml          # fouten en waarschuwingen
kiwi-server show fleet.yaml papaya          # de effectieve configuratie van één host, geheimen gemaskeerd
```

kiwi-server controleert ook het domein: `.local` wordt geweigerd, `.lan` en
publieke topleveldomeinen krijgen een waarschuwing (zie
[DNS](../network/dns.md#names-servicehostnamehome)).

## Een v1-machine overnemen { #taking-over-a-v1-machine }

Een machine die een van de oude v1-stacks draaide, kan worden overgenomen zonder
gegevens te verliezen. De standaardruntime is nu podman, en het rolscript stopt
geen docker-containers. Stel dus `runtime: docker` in, of stop eerst de oude
stack. Stel daarna `docker_subnet` in op wat de oude stack gebruikte, en hernoem
de gegevensmappen naar de modulenamen (`kmvpn-server` → `km-vpn-server`,
`knvault` → `kn-vault`, …). De containers houden hun adressen en wg-easy houdt
zijn peers.
