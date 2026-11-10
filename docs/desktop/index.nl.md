# De desktop

De Kiwi-desktoptools zijn gebouwd voor **Fedora Atomic-desktops**: Fedora
Silverblue en [Bluefin](https://projectbluefin.io/) (met name Bluefin-DX). Dit
zijn image-gebaseerde systemen met een onveranderlijke `/usr` en eenvoudig
terugdraaien. Er is geen speciale Kiwi-image: je installeert een standaardimage
en voegt er drie lagen aan toe.

1. **[kiwi-updater](kiwi-updater.md)** installeert en werkt apps bij vanuit
   git-catalogi: alles in je homemap, plus een deel dat eigendom is van root, alleen voor apps die
   dat nodig hebben. Hij werkt zichzelf ook bij.
2. **[ensconce](ensconce.md)** richt een verse Bluefin-DX in vanuit gewone
   lijstbestanden: pakketten, Flatpaks, GNOME-extensies, Nextcloud-synchronisatie,
   SSH, sysctl- en energie-instellingen, het inlogscherm en je Kiwi-apps.
   `--export` kloont een machine.
3. **De apps**, uit de [Kiwi-catalogus](catalogs.md):

| App | Wat het doet |
|---|---|
| [kiwi-killswitch](kiwi-killswitch.md) | Een fail-closed VPN-killswitch voor GNOME |
| [Klantnetwerken](../clients/index.md): kiwi-proxy, kiwi-custodia, kiwi-fox | Eén verzegelde exit per VPN- of SOCKS-eindpunt, en distroboxen en browsers die daarbinnen leven |
| [kiwi-server](../server/index.md) | Je eigen netwerk bouwen en draaien |
| [gnome-monitor](gnome-monitor.md) | Beeldschermindelingen opslaan en wisselen; losse monitoren uit en aan zetten |
| [syncman](syncman.md) | Tweerichtings-mappensynchronisatie (savegames en meer) als gebruikersservices |
| [kiwi-cli-tools-desktop](cli-tools.md) | `pweb`, `select-server`, `tethering`, `torlink` |

Ook hier: [kiwi-gen](kiwi-gen.md), een beheerder voor sleutels en certificaten
die offline in de browser draait.

## Vanaf een verse installatie { #from-a-fresh-install }

```bash
# 1. kiwi-updater: gebruikers- en systeemscope, één wachtwoordvraag; de Kiwi-catalogus komt mee
curl -fsSL https://raw.githubusercontent.com/derlocke-ng/kiwi-updater/main/get-kiwi.sh | bash
kiwi list

# 2. de machine inrichten
kiwi install ensconce
ensconce --init && $EDITOR "$(ensconce --config-dir)"/settings.sh
ensconce

# 3. de apps die je wilt (of zet ze in kiwi-apps.list van ensconce)
kiwi install kiwi-killswitch
kiwi install kiwi-custodia && kiwi-custodia setup
```

**Kiwi Apps** (`kiwi-gui`) in het app-overzicht doet hetzelfde met een klik.

## Je netwerk binnenkomen { #joining-your-network }

Een desktop komt in de mesh zoals elk ander apparaat: `kiwi-server enroll fleet.yaml
laptop --group devices` schrijft een WireGuard-configuratie, die je in de
GNOME-instellingen importeert. Importeer de CA van de fleet (`kiwiCA.pem`) zodat
de HTTPS-namen ervan vertrouwd worden. ensconce installeert elke `.pem` in zijn
map `certs/` systeembreed.

[kiwi-killswitch](kiwi-killswitch.md) houdt de machine daarna fail-closed rond
die verbinding. De instelling *trusted kiwi-nodes* laat een gateway-node op je
LAN thuis de plaats van de tunnel innemen.
