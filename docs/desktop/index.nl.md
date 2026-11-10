# De desktop

Het desktopdeel van Kiwi Network is de computer waaraan je werkt: een
Linux-werkstation dat automatisch wordt ingericht en zijn apps uit
git-catalogi haalt. Een catalogus is een git-repository met een lijst van apps.
Je hoeft de machine niet met de hand in te richten, en de volgende richt je op
precies dezelfde manier in.

De desktoptools van Kiwi zijn gemaakt voor **Fedora Atomic-desktops**: Fedora
Silverblue en [Bluefin](https://projectbluefin.io/), en dan vooral Bluefin-DX.
Deze systemen worden als één compleet image geïnstalleerd en bijgewerkt. Hun
map `/usr` is onveranderlijk, er kan dus niets in worden gewijzigd, en een
update is eenvoudig terug te draaien. Er is geen speciaal Kiwi-image. Je
installeert een standaardimage van Silverblue of Bluefin en zet daar drie
dingen bovenop.

1. **[kiwi-updater](kiwi-updater.md)** installeert apps uit git-catalogi en
   houdt ze up-to-date. Alles komt in je thuismap terecht. Alleen een app die
   root nodig heeft, krijgt daarnaast een deel dat van root is. kiwi-updater
   werkt ook zichzelf bij.
2. **[ensconce](ensconce.md)** richt een vers geïnstalleerde Bluefin-DX in. Je
   beschrijft je inrichting in eenvoudige lijstbestanden, en ensconce voert die
   uit: pakketten, Flatpaks, GNOME-extensies, synchronisatie met Nextcloud,
   SSH, sysctl- en energie-instellingen, het inlogscherm en je Kiwi-apps. Met
   `--export` schrijft ensconce de inrichting van een bestaande machine naar
   zulke bestanden, zodat je die machine kunt klonen.
3. **De apps**, die je installeert uit de [Kiwi-catalogus](catalogs.md):

| App | Wat het doet |
|---|---|
| [kiwi-killswitch](kiwi-killswitch.md) | Een VPN-killswitch voor GNOME. Hij is fail-closed: zolang de VPN niet actief is, blijft al het verkeer geblokkeerd |
| [Klantnetwerken](../clients/index.md): kiwi-proxy, kiwi-custodia, kiwi-fox | Een exit voor elk VPN- of SOCKS-eindpunt. Een exit is een afgeschermde container die alleen dat ene eindpunt kan bereiken. Je kunt boxen met een Linux-distributie en browsers aan een exit koppelen, zodat al hun verkeer erdoorheen gaat |
| [kiwi-server](../server/index.md) | Het programma waarmee je je eigen netwerk opbouwt en beheert |
| [gnome-monitor](gnome-monitor.md) | Slaat schermindelingen op en wisselt ertussen. Het zet ook losse monitoren uit en aan |
| [syncman](syncman.md) | Synchroniseert mappen in beide richtingen, bijvoorbeeld opgeslagen spellen. De synchronisatie draait als gebruikersservices |
| [kiwi-cli-tools-desktop](cli-tools.md) | `pweb`, `select-server`, `tethering`, `torlink` |

In dit deel staat ook [kiwi-gen](kiwi-gen.md), een beheerprogramma voor
sleutels en certificaten dat in de browser draait en offline werkt.

## Vanaf een verse installatie { #from-a-fresh-install }

Met deze commando’s kom je van een vers geïnstalleerd systeem tot een desktop
met de Kiwi-apps:

```bash
# 1. kiwi-updater: user- en system-scope, één keer het wachtwoord invoeren; de Kiwi-catalogus komt mee
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

Apps installeren kan ook zonder terminal. Met **Kiwi Apps** (`kiwi-gui`) in het
overzicht van apps installeer je een app met één klik.

## Je netwerk binnenhalen { #joining-your-network }

Een desktop komt op dezelfde manier in de mesh als elk ander apparaat. De mesh
is het besloten WireGuard-netwerk waarin al je servers en apparaten zitten.
Het commando `kiwi-server enroll fleet.yaml laptop --group devices` schrijft een
WireGuard-configuratiebestand, en dat bestand importeer je in Instellingen van
GNOME. Importeer ook de certificaatautoriteit (CA) van je netwerk, `kiwiCA.pem`,
zodat de desktop de HTTPS-certificaten van de namen in je netwerk vertrouwt.
ensconce installeert elk `.pem`-bestand uit zijn map `certs/` voor het hele
systeem.

Daarna beschermt [kiwi-killswitch](kiwi-killswitch.md) die verbinding en houdt
de machine fail-closed. Verkeer dat niet via de verbinding gaat, wordt dus
geblokkeerd, ook als de verbinding wegvalt. Thuis kan een gateway-node in je LAN
je verkeer al door een tunnel sturen. Met de instelling *trusted kiwi-nodes*
accepteert de killswitch zo’n gateway-node in plaats van de tunnel.
