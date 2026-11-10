# Beheer

Het dagelijkse werk aan een draaiende fleet, allemaal vanaf de machine van de
beheerder.

## Status { #status }

```bash
kiwi-server status fleet.yaml            # elke host
kiwi-server status fleet.yaml papaya        # één host
```

Elke machine rapporteert via SSH (alleen-lezen): haar rol, haar stack, problemen
(een mislukte rol, een gestopte container), haar schijven en of die versleuteld
of vergrendeld zijn, haar back-ups, en hoe lang haar certificaten nog geldig
zijn. Een back-upnode rapporteert ook zijn capaciteit. De app Kiwi Server toont
hetzelfde in het *Overview* van elke host.

## Geheimen { #secrets }

Alles wat geheim is, staat in `secrets/` naast het fleet-bestand: de seed waaruit
elk gegenereerd wachtwoord wordt afgeleid, de fleet-CA, WireGuard-configuraties,
LUKS-sleutels en SSH-hostsleutels.

```bash
kiwi-server secrets init fleet.yaml      # secrets/ wordt één met age versleuteld bestand
kiwi-server secrets unlock fleet.yaml    # openen in het geheugen (--for 8h; 0 houdt het open)
kiwi-server secrets lock fleet.yaml
kiwi-server secrets status fleet.yaml
kiwi-server secrets show fleet.yaml papaya [setting]   # de gegenereerde wachtwoorden van een host
```

`secrets init` bewaart één sleutel in de GNOME-sleutelbos en toont één keer een
**herstelsleutel**. Zolang de opslag open is, kan alles wat als jou draait hem
lezen.

## Een back-up van de fleet zelf { #backing-up-the-fleet-itself }

Na elke geslaagde render of build wordt de fleet-map versleuteld (AES-256 met
PBKDF2, 600.000 iteraties) en gekopieerd naar de nodes in `backup.hosts`, die de
nieuwste tien bewaren. Op een verse machine:

```bash
kiwi-server restore --from core@lychee.home  # de fleet-map terug
kiwi-server backup fleet.yaml --local /mnt/usb   # of een kopie naar een map, op elk moment
```

## Een back-up van de gegevens van de machines { #backing-up-the-machines-data }

Geef een node de module `backup-server` (een restic-REST-server), en elke machine
waarvan een back-up gemaakt moet worden de module `backup`, die ernaar wijst:

```yaml
lychee:
  node:
    modules: [vpn-client, reverse-proxy, backup-server]
    backup-server: { clients: [papaya.home, sorbet.home] }
papaya:
  node:
    modules: [vpn-client, reverse-proxy, cloud, vault, portainer, backup]
    backup: { server: https://backup.lychee.home }
```

Elke nacht om 03:00 (binnen 15 minuten daarna) verstuurt restic versleuteld wat
elke module wil bewaren. Elke machine kan alleen haar eigen repository bereiken,
en er alleen iets aan toevoegen. Oude snapshots verwijderen gebeurt daarom vanaf
de machine van de beheerder:

```bash
sudo kiwi-stack backup | snapshots | restore [--at TIME] MODULE...   # op de machine
kiwi-server prune fleet.yaml            # 7 dagelijkse, 4 wekelijkse, 6 maandelijkse bewaren
```

Een restore is van node naar node getest: de back-ups van papaya op lychee.

### In de volgende release { #coming-in-the-next-release }

!!! info "Op de branch `several-servers`"
    Dit werk is gepusht naar de branches `several-servers` van kiwi-modules en
    kiwi-server, maar is nog niet gemerged of uitgebracht. Meerdere servers en de
    automatische restore zijn op hardware getest. De gezondheidscontrole van de
    VPN niet.

- **Meerdere back-upservers.** `backup.servers` accepteert een lijst, en elke
  server krijgt een eigen volledige kopie. Als één server uitvalt, ontbreekt
  alleen diens kopie. Een restore neemt de nieuwste kopie van de server die haar
  heeft, en `kiwi-stack snapshots` toont ze per server. De enkele `server` werkt
  nog steeds.
- **Een opnieuw opgebouwde machine zet zichzelf terug.** Als een machine zichzelf
  in de back-ups aantreft maar er geen enkele van heeft gemaakt (een herbouw),
  zet ze elke module zelf terug vóór haar eerste back-up, en maakt daarna
  back-ups zoals voorheen (`backup.restore:
  auto`, de standaard). Met `hold` wacht ze op `kiwi-stack restore` of
  `kiwi-stack backup --new`.
- **Opschonen op een timer.** `kiwi-server prune fleet.yaml --every week` (of
  `day`) installeert een systemd-gebruikerstimer op je computer, de enige plek
  met de sleutels die mogen verwijderen. Een gemiste run volgt bij de volgende
  keer inloggen. `kiwi-server status` toont elke back-upkopie, en waarschuwt als
  een back-upnode drie weken niet is opgeschoond.
- **Een vastgelopen commerciële exit begint opnieuw.** gluetun krijgt een
  gezondheidscontrole. Na vijf ongezonde minuten wordt de container beëindigd, en
  bij de volgende start kiest hij een andere server.

## Versleutelde schijven en ontgrendelen { #encrypted-disks-and-unlocking }

- **Debian** (`debian.encrypt: true`) installeert met een eenmalige sleutel die
  je bij de eerste start intypt (`secrets/luks/<host>.once`). De eerste `apply`
  vervangt die door `secrets/luks/<host>.key`, en een master krijgt ook een
  nieuwe volumesleutel. Raak je dat sleutelbestand kwijt, dan blijft de schijf
  op slot, dus houd een back-up van de fleet.
- **CoreOS / uCore** versleutelen bij de installatie via Ignition (met ongeveer
  4 GiB RAM bij de eerste start).
- **Tang-ringen** laten versleutelde machines bij het opstarten ontgrendelen
  zonder dat er iemand bij is. Een node draait de module `tang` (elke ring is één
  Tang-server met eigen sleutels, standaard `infra` op poort 7500), en het
  `unlock:`-blok van een host bindt de schijf aan ringen met een drempel.
- **SSH in de initramfs** (`unlock.ssh: true`: dropbear op Debian, dracut-sshd
  op CoreOS) gebruikt een eigen beperkte sleutel, `secrets/unlock_ed25519`, die
  alleen het ontgrendelen kan uitvoeren.
- `kiwi-server unlock fleet.yaml <host>` stuurt een ring door naar een machine
  die bij het opstarten wacht, en `--manual` geeft de sleutel zelf door. Een
  `operator`-ring wordt vanaf je eigen machine geserveerd zolang hij nodig is.
  `vpn-server.unlock_relay` bereikt machines achter NAT.

## Tunnel-MTU { #tunnel-mtu }

WireGuard voegt eigen headers toe, dus een tunnel vervoert kleinere pakketten dan
de lijn eronder, en een mobiel pad nog kleinere. Een pakket dat te groot is voor
een verbinding onderweg, wordt weggegooid of opgesplitst, en verbindingen lopen
vast. Kiwi pakt dit aan in drie lagen:

- **Twee instellingen.** `wg_mtu` (standaard **1376**, een veelvoud van 16 omdat
  WireGuard tot 16 opvult) is de MTU van gluetun, de clientconfiguraties van
  wg-easy en `wg0`. `bridge_mtu` (standaard **1500**) is de MTU van het
  stacknetwerk. `validate` weigert een `wg_mtu` waarvan het opgevulde pakket plus
  80 bytes aan headers niet in de bridge past, en alles onder 1280, het minimum
  waarmee IPv6 werkt.
- **De MSS wordt in beide richtingen begrensd** op `wg_mtu - 40`, in wg-easy en
  in de VPN-client, zodat TCP nooit een segment probeert dat er niet door kan.
- **TCP tast zelf af.** De VPN-client draait met `net.ipv4.tcp_mtu_probing=1` en
  `tcp_base_mss=1024`, zodat een verbinding die op een pad stuit dat grote
  pakketten stilletjes weggooit, een werkende grootte vindt in plaats van te
  blijven hangen.

### Een pad meten: `kiwi-server mtu` { #measuring-a-path-kiwi-server-mtu }

```bash
kiwi-server mtu fleet.yaml papaya --ssh core@<address>   # een node
kiwi-server mtu fleet.yaml phone --ssh core@<master>     # een apparaat uit secrets/devices/
kiwi-server mtu fleet.yaml papaya --write                # en wg_mtu in het fleet-bestand schrijven
```

De meting stuurt pings met don't-fragment door de tunnel, van binnen de namespace
die de tunnel bevat. Een node wordt gemeten vanaf zijn eigen VPN-client (waarvan
de firewall binnenkomende pings weggooit), en een apparaat vanaf de
WireGuard-server. Hij begint met een gewone ping, probeert daarna elk veelvoud
van 16 vanaf 1280 en hoger, en meldt het grootste dat **heel** aankomt. Tijdens
het pingen leest hij de reassembly-tellers van de kernel, zodat een antwoord dat
onderweg is opgesplitst en weer samengevoegd niet telt als passend.

Hij zegt ook wat je moet instellen. Voor een **apparaat** is dat de eigen
`MTU =` van het apparaat in zijn WireGuard-configuratie, en niemand anders merkt
er iets van. Voor een **node** is het `wg_mtu` op die node en op zijn master, wat
`--write` in het fleet-bestand zet (waarbij alleen die regels veranderen). Een
pakket dat alleen op de heenweg wordt opgesplitst en door de andere kant weer
wordt samengevoegd, is vanaf deze kant niet te zien.

De standaardwaarden zijn op de test-fleet gemeten. Voor een telefoon op mobiele
data, waar paden vaak alleen IPv6 zijn achter 464XLAT met geneste encapsulatie,
meet je de telefoon zelf en verlaag je zijn eigen `MTU =` als de meting dat
aangeeft.

## netcup-VPS'en { #netcup-vpses }

```bash
kiwi-server vps login fleet.yaml         # inloggen via device flow; het token gaat naar secrets/
kiwi-server vps list fleet.yaml
kiwi-server vps install fleet.yaml sorbet  # de server wissen en de ISO van de host installeren
```

`vps install` vraagt eerst om bevestiging, tenzij je `--yes` meegeeft. Het
weigert een ISO met rolgeheimen, een verkeerde `disk:`, en CoreOS-schijfversleuteling
met minder dan 3500 MiB RAM.
