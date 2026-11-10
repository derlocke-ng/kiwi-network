# kiwi-server

kiwi-server maakt en beheert een Kiwi Network. Je beschrijft elke machine in één
`fleet.yaml`. kiwi-server maakt voor elke host een **installatie-ISO die zonder
tussenkomst installeert**: hij installeert Fedora CoreOS, uCore of Debian en
schakelt de machine uit. Daarna **past** hij de rol toe via SSH, waardoor de
machine een `kiwi-master` of een `kiwi-node` wordt. Vervolgens blijft hij met de
fleet werken: hij meldt WireGuard-clients aan, leest de gezondheid van elke
machine uit, bewaart de geheimen, maakt back-ups van de fleet, en ontgrendelt
versleutelde schijven.

Er is een CLI, `kiwi-server`, en een GTK4-app, **Kiwi Server**. Beide installeren
in `~/.local` en hebben geen root nodig.

- Repository: [derlocke-ng/kiwi-server](https://github.com/derlocke-ng/kiwi-server), GPL-3.0-or-later
- Nieuwste release: **v2.42.0**. Het staat in de [Kiwi-catalogus](../desktop/catalogs.md).
- Gebouwd op [kiwi-modules](single.md) v0.23.0 (de modules en hun renderer) en
  [kiwi-stack](single.md) v0.5.0 (de kant van de machine), opgenomen en
  vastgepind op een tag.

```
fleet.yaml + secrets/
   │  kiwi-server: merge defaults, work out DNS records, the master's mesh address,
   │  LAN neighbours, and a certificate from the fleet CA per host
   ▼
kiwi-modules renders each host's stack  →  compose file, podman quadlets, configs, units
   │
   ├─ build ─▶ <host>.iso      base system only: hostname, network, admin user, updates;
   │                            installs to the named disk WITHOUT ASKING, then powers off
   └─ apply ─▶ over SSH        role script + stack → kiwi-stack starts and verifies it
```

## Installeren { #install }

```bash
kiwi install kiwi-server        # met kiwi-updater
```

Of vanuit een checkout: `./install.sh install`, daarna `kiwi-server doctor`.

Het vereist Python 3.9+ met PyYAML en Jinja2, `openssl` en `ssh`. De
geheimenopslag vereist `age`. ISO's bouwen vereist `butane`, `coreos-installer`
en `xorriso` (plus `cpio`, `gzip` en `curl` voor Debian). Bouw ze op Silverblue of
Bluefin als één container-image in plaats van pakketten in lagen toe te voegen:

```bash
kiwi-server toolchain build     # wordt automatisch gebruikt als de tools ontbreken
```

`qrencode` (voor `enroll --qr`), `shellcheck` en `docker compose` zijn optioneel.

## Van niets tot een draaiend netwerk { #from-nothing-to-a-running-network }

```bash
kiwi-server init                          # een becommentarieerde fleet.yaml
$EDITOR fleet.yaml                        # hosts, rollen, je SSH-sleutel, de installatieschijf
kiwi-server secrets init fleet.yaml       # optioneel: secrets/ als één met age versleutelde opslag
kiwi-server validate fleet.yaml

# de master
kiwi-server build fleet.yaml sorbet         # → output/sorbet/sorbet.iso
#   opstarten; hij installeert en schakelt uit; start hem opnieuw
kiwi-server apply fleet.yaml sorbet --ssh core@203.0.113.5

# elke node: eerst zijn WireGuard-client, dan het medium, dan de rol
kiwi-server enroll fleet.yaml papaya         # → secrets/papaya.home.conf
kiwi-server build fleet.yaml papaya
kiwi-server apply fleet.yaml papaya --ssh core@192.168.1.25

# je eigen apparaten
kiwi-server enroll fleet.yaml laptop --group devices
kiwi-server status fleet.yaml             # wat elke machine rapporteert
```

Media bevatten standaard **geen enkel geheim van de stack**: alleen het
basissysteem. De rol en haar stack komen met `apply`. Als een machine niet via
SSH bereikbaar is, zet `build --offline` in plaats daarvan de hele rol en haar
geheimen op de ISO. Houd zo'n ISO uit de ISO-opslag van een provider en verwijder
hem na de installatie.

**Helemaal geen ISO?** `kiwi-server script fleet.yaml papaya` toont het script
voor een machine die je zelf hebt geïnstalleerd (`--offline` voor de hele rol).

Op een netcup-VPS wist `kiwi-server vps install fleet.yaml sorbet` de server en
installeert hij de ISO via de API van netcup, zonder dat er iemand achter een
console zit. netcup is tot nu toe de enige provider; andere zijn
[gepland](roadmap.md#more-hosters-and-network-boot).

## Commando's { #commands }

| Commando | Wat het doet |
|---|---|
| `init [fleet.yaml]` | het voorbeeld-fleet-bestand schrijven (`--domain`, standaard `home`) |
| `validate fleet.yaml [host…]` | het controleren, waarbij elke stack wordt gerenderd om modulefouten te vinden |
| `list` / `show fleet.yaml <host>` | de hosts en wat er gegenereerd is / de effectieve configuratie van één host, geheimen gemaskeerd |
| `render fleet.yaml [host…]` | rolscripts, stacks en installatieconfiguraties naar `output/<host>/` |
| `build fleet.yaml [host…]` | renderen, daarna de ISO: standaard het basissysteem, `--offline` voor de hele rol |
| `script fleet.yaml <host>` | het script voor elke machine (`--offline` voor de hele rol) |
| `apply fleet.yaml <host…>` | opnieuw renderen, de rol via SSH versturen en uitvoeren (`--ssh USER@ADDR`, `--no-run`) |
| `status fleet.yaml [host…]` | wat de machines rapporteren: rol, stack, problemen, schijven, back-ups, certificaten |
| `enroll fleet.yaml <host\|name>` | een WireGuard-client op de master aanmaken of ophalen (`--group`, `--split`, `--qr`, `--address`, `--existing`) |
| `secrets init\|unlock\|lock\|status` | `secrets/` als één met age versleuteld bestand, geopend in het geheugen (`--for 8h`) |
| `secrets show fleet.yaml <host> [setting]` | de gegenereerde wachtwoorden van een host |
| `ca fleet.yaml` | de fleet-CA |
| `mtu fleet.yaml <node\|device\|address>` | de echte MTU van een tunnel meten en zeggen wat je moet instellen (`--write`) |
| `openwrt fleet.yaml` | een script dat een OpenWrt-router aan de mesh koppelt ([Routers](../network/routers.md)) |
| `backup` / `restore` / `prune` | de fleet-map naar nodes en terug; oude back-ups van machines verwijderd ([Beheer](operations.md)) |
| `unlock fleet.yaml <host>` | een Tang-ring doorsturen naar een machine die bij het opstarten wacht ([Beheer](operations.md)) |
| `vps login\|list\|probe\|install` | de Server Control Panel-API van netcup |
| `roles [-v]`, `modules [-v]`, `targets` | wat er beschikbaar is, met elke instelling en haar standaardwaarde |
| `toolchain [status\|build]`, `doctor` | de ISO-tools; deze machine controleren |

Elk commando accepteert `--porcelain` (JSON), `-o/--output-dir`, `--quiet` en
`-v`. `kiwi-server <command> -h` legt één commando uit.

## De app { #the-app }

**Kiwi Server** opent je laatste fleet. De zijbalk heeft een overzicht, één rij
per host, en de standaardwaarden. Het *Overview* van een host toont live gegevens
uit `kiwi-server status` (eens per minuut opgevraagd zolang het venster focus
heeft, alleen-lezen via SSH). Zijn *Settings* is een formulier dat is opgebouwd
uit de rollen en modules. *Apply*, *Build* en *Render* voeren de CLI uit en tonen
de uitvoer live, en *Build* toont de schijven die gewist worden voordat het
begint. *Unlock* en *Lock* openen en sluiten de geheimenopslag. De app schrijft
gewone YAML, dus commentaar in een met de hand geschreven fleet-bestand gaat
verloren als hij opslaat.

## Let op { #mind }

!!! danger "De ISO's wissen de schijf die hun is opgegeven"
    Bij het opstarten, zonder te vragen. Label ze. `disk:` is precies daarom
    verplicht voor `build`.

- **De uitvoer bevat geheimen**: wachtwoordhashes, WireGuard-sleutels,
  TLS-sleutels, LUKS-sleutels. Bestanden worden met 0600 geschreven en `output/`
  wordt door git genegeerd. Behandel ISO's die met `--offline` zijn gemaakt op
  dezelfde manier.
- **Wachtwoorden van diensten worden gegenereerd** uit `secrets/seed` als je ze
  in het fleet-bestand weglaat. `validate` waarschuwt voor wachtwoorden die erin
  staan. `kiwi-server secrets show` toont ze. Een machine weigert een apply die
  met een andere seed is gemaakt.
- **SSH-hostsleutels** worden bij het eerste contact vastgelegd in
  `secrets/known_hosts`, en een gewijzigde sleutel wordt geweigerd (verwijder na
  een herinstallatie de regel).
- **Een rolscript draait als root.** Lees `kiwi-server script fleet.yaml <host>
  --offline` voordat je een rol vertrouwt die je niet zelf hebt geschreven.
- **Een mislukte rol meldt dat.** De machine bewaart
  `/var/lib/kiwi-server/role.failed` (de stap en het commando), en `status` toont
  het.

## Status { #status }

De pijplijn is in oktober en november 2026 op hardware bewezen. Debian, uCore en
Fedora CoreOS zijn van begin tot eind opgestart op twee VPS'en, een mini-pc en
een VM, en een oefening met een dode node herbouwde een versleutelde
Debian-machine in ongeveer 14 minuten. Back-ups van nodes zijn van de ene node op
de andere teruggezet (papaya naar lychee), en de tunnel-MTU is op echte paden
gemeten en afgestemd, mobiele paden inbegrepen. CI rendert elke rol, shellcheckt
elk script, valideert elke Butane-configuratie, en legt vier gouden stacks byte
voor byte vast.

Nog niet bewezen: federatie tussen netwerken. Alles is IPv4. De Debian-ISO is
alleen amd64. Een gepland control plane (`kiwi-server serve`) is ontworpen maar
niet gebouwd.

Verder lezen: [Het fleet-bestand](fleet.md) · [Rollen](roles.md) · [Modules](modules.md) ·
[Machines](machines.md) · [Beheer](operations.md) ·
[Eén machine zonder fleet](single.md)
