# kiwi-updater

kiwi-updater installeert opensource-apps op je desktop en houdt ze up-to-date.
Het commando heet `kiwi`. De apps komen uit **git-catalogi**, en het werkt op
Fedora Silverblue, Bluefin en andere ostree-systemen. Een catalogus is een
git-repository met een lijst van apps. Een app is een git-repository met een
bestand `kiwi.manifest` en een script `install.sh`. kiwi kloont de repository
van de app, checkt de nieuwste release-tag uit en voert de installer uit. Daarna
werkt het de app op de achtergrond bij, en zichzelf op dezelfde manier.

Je hebt geen account nodig, en er is geen appwinkel en geen leverancier. Een
catalogus is een repository die je kunt lezen en forken, en waarvoor je een
pull request kunt sturen.

- Repository: [derlocke-ng/kiwi-updater](https://github.com/derlocke-ng/kiwi-updater), GPL-3.0-or-later
- Nieuwste release: **v2.4.0**, een beveiligingsrelease
- **`kiwi`** is de opdrachtregeltool (CLI). Die heeft `git`, coreutils,
  `util-linux` en `awk` nodig, die allemaal in het basisimage zitten. Om
  handtekeningen te controleren is ook `ssh-keygen` nodig.
- **Kiwi Apps** (`kiwi-gui`) is de desktop-app, gebouwd met GTK4. Je kunt de
  apps doorzoeken en filteren, en elke app heeft een detailweergave met icoon,
  schermafbeeldingen en afhankelijkheden. Kiwi Apps toont je de installer
  voordat het een app installeert, en wat een update verandert voordat het een
  app bijwerkt. Klik je meerdere acties na elkaar aan, dan zet Kiwi Apps ze in
  een wachtrij. De gegevens komen van de CLI. Iconen en schermafbeeldingen leest
  Kiwi Apps uit de lokale klonen van de apps, dus om ze te tonen wordt niets
  gedownload.

## Installeren { #install }

kiwi werkt met twee scopes. De user-scope is alles in je thuismap en heeft nooit
root nodig. De system-scope is een deel dat van root is, voor apps die root
nodig hebben. Bij de installatie kies je hoeveel van de system-scope je wilt:

```bash
# aanbevolen: user-scope plus de system-scope van root, één keer het wachtwoord invoeren
curl -fsSL https://raw.githubusercontent.com/derlocke-ng/kiwi-updater/main/get-kiwi.sh | bash

# minimaal: 100 % gebruikersniveau, alleen ~/.local, nooit root en nooit een wachtwoord
curl -fsSL https://raw.githubusercontent.com/derlocke-ng/kiwi-updater/main/get-kiwi.sh | bash -s -- --minimal

# niets zonder wachtwoord: elke wijziging aan het systeem vraagt om een wachtwoord
curl -fsSL https://raw.githubusercontent.com/derlocke-ng/kiwi-updater/main/get-kiwi.sh | bash -s -- --with-system=manual
```

De installatie registreert de [Kiwi-catalogus](catalogs.md), dus je kunt meteen
`kiwi list` uitvoeren of **Kiwi Apps** openen.

Sommige apps bestaan alleen uit bestanden in je thuismap, bijvoorbeeld de
CLI-tools, ensconce en syncman. Die apps zijn bij de minimale installatie
compleet. Een app met een deel dat als root draait, zoals kiwi-killswitch,
heeft de system-scope nodig. Bij een minimale installatie richt
`kiwi install kiwi-killswitch` de system-scope op dat moment in en vraagt het
één keer om je wachtwoord.

## Commando’s { #commands }

```bash
kiwi list [--check]          # elke app die deze machine kent
kiwi search vpn              # een app zoeken in alle geregistreerde catalogi
kiwi info kiwi-killswitch    # wat het is, wat het installeert, of het root nodig heeft
kiwi install <app>           # een naam, of uitdrukkelijk --all
kiwi update [<app>]          # alles met een nieuwe release
kiwi uninstall <app>         # --purge verwijdert ook de configuratie
kiwi check                   # exitcode 10 als er voor iets een update is

kiwi add <https-url>         # één repository rechtstreeks volgen, zonder catalogus
kiwi catalog add|list|remove # catalogi beheren
kiwi sync                    # catalogi nu verversen
kiwi self-update
kiwi trust --system <app>    # de vastgezette ondertekeningssleutel van een systeemapp vergeten
```

Met de volgende commando’s zie je wat een app gaat doen voordat je hem
uitvoert, en ze helpen als er iets misgaat:

```bash
kiwi info --installer <app>  # het script dat een installatie zou uitvoeren, vooraf
kiwi diff <app>              # wat een update zou veranderen, inclusief de installer
kiwi pin <app> v1.2.0        # daar blijven; met kiwi unpin <app> weer releases volgen
kiwi install <app> --dry-run # scope, URL, ref, pad van de installer, en verder niets
kiwi doctor                  # achtergebleven locks, versieverschillen, kapotte lijstbestanden, timers
```

## Releases zijn tags { #releases-are-tags }

kiwi gebruikt git-tags als releases. Een app volgt haar nieuwste
**versietag**. Een versietag is een tag die past op
`^v?[0-9]+(\.[0-9]+){0,3}$`, bijvoorbeeld `v1`, `v1.2`, `1.2.3` of `v1.2.3.4`.
Tags voor voorlopige versies en tijdelijke tags passen daar niet op, dus ze
worden nooit in plaats van een release gebruikt. Een repository zonder
versietag volgt haar standaardbranch. Wil je één bepaalde versie, zet dan
`ref=<tag>` achter de regel van de app in een lijst.

## Afhankelijkheden { #dependencies }

De regel `DEPENDS=` in een manifest noemt wat een app nodig heeft. Is een woord
op die regel de naam van een app in je eigen catalogus of lijst, dan installeert
kiwi die app **eerst**, in dezelfde scope, op het moment dat je de app
installeert die haar nodig heeft. `kiwi install kiwi-plugin-tor` installeert
bijvoorbeeld ook kiwi-proxy. Elk ander woord behandelt kiwi als de naam van een
programma, en met `command -v` controleert het of dat programma aanwezig is.

## Eén app, twee delen { #one-app-two-halves }

Sommige apps zijn maar één programma in `~/.local/bin`. Andere, zoals een
VPN-killswitch, bestaan uit een daemon die als root draait **en** een
desktop-app **en** een GNOME-extensie. Zo’n app heeft twee delen, een
gebruikersdeel en een systeemdeel, en die worden met verschillende rechten
geïnstalleerd. De reden: **root mag nooit een bestand uitvoeren waarin de
gebruiker kan schrijven**. De app geeft haar onderdelen en scopes op in haar
manifest:

```ini
COMPONENTS=daemon cli gui gnome-extension
SCOPES=user system
ROOT_REASON=installs a root firewall daemon, its D-Bus policy and two systemd units
```

Een catalogus noemt zo’n app maar één keer, en kiwi installeert elk deel in de
juiste scope. Voordat kiwi om je wachtwoord vraagt, toont het je de
`ROOT_REASON`.

| Onderdeel | Waar | Waarom |
|---|---|---|
| `kiwi`, Kiwi Apps, gebruikersapps | `~/.local` | heeft geen root nodig, en blijft staan als het systeem naar een ander ostree-image wordt omgezet (rebase) |
| de eigen kopie van kiwi voor root | `/usr/local/bin`, gekloond naar `/var/lib/kiwi-updater/repos/` | root voert nooit een bestand uit waarin jij kunt schrijven |
| systeemapps | `/var/lib`, `/etc` | deze mappen zijn op ostree-systemen beschrijfbaar en zijn van root |
| lijsten | `~/.config/kiwi-updater/apps.list`, `/etc/kiwi-updater/apps.list` | de regels in de eigen lijst van een machine gaan voor op elke catalogus |
| vastgezette ondertekeningssleutels | `/etc/kiwi-updater/signers/<app>` | zie het volgende deel |

kiwi verandert nooit iets in de onveranderlijke `/usr`.

## Root, wachtwoorden en handtekeningen { #root-passwords-and-signatures }

De tabel laat zien welke acties root nodig hebben en welke om een wachtwoord
vragen.

| | Root nodig | Vraagt om een wachtwoord |
|---|---|---|
| alles in de user-scope | nee | nee |
| een systeemapp **bijwerken** | ja | **nee**, als de release is ondertekend met de sleutel die root voor die app heeft vastgezet. **Ja**, als de release niet is ondertekend, en altijd in de modus `manual` |
| een systeemapp **installeren** of **verwijderen** | ja | ja |

Sinds versie 2.4.0 gelden deze regels:

- **Ondertekende releases.** Voor elke systeemapp zet root één
  SSH-ondertekeningssleutel vast. Een sleutel vastzetten betekent: hem onthouden
  en vanaf dan alleen die sleutel accepteren. Root zet de eerste sleutel vast die
  het voor de app ziet; dat heet trust on first use. Is een release-tag
  ondertekend met de vastgezette sleutel, dan wordt de update zonder wachtwoord
  geïnstalleerd. Is een release niet ondertekend, dan vraagt kiwi om je
  wachtwoord en meldt het dat het de release niet kon verifiëren. kiwi weigert
  een tag die met een andere sleutel is ondertekend, en het weigert een
  niet-ondertekende tag als eerdere tags wel ondertekend waren. Dat blijft zo
  tot je `kiwi trust --system <app>` uitvoert. Deze regels gelden voor de
  system-scope.
- **Root installeert alleen uit bronnen die het zelf in zijn lijsten heeft.**
  Die bronnen zijn `/etc/kiwi-updater/apps.list` en de catalogi die voor root
  zijn geregistreerd. Komt een app uit een andere bron, dan installeert kiwi
  alleen het gebruikersdeel en noemt het het commando
  `kiwi add --system <https-url>` dat je moet uitvoeren. Kiwi Apps biedt in dat
  geval de knop *Register and Install* aan, die de bron voor root registreert en
  de app installeert.
- **Alleen https.** kiwi weigert overal bronnen met `http://`.

Systeemupdates zonder wachtwoord worden uitgevoerd door één hulpprogramma,
`/usr/local/libexec/kiwi-system-update`, dat alleen voor dit ene doel bestaat.
Een polkit-regel staat gebruikers in de groep `wheel` toe het uit te voeren als
hun sessie actief is. Het hulpprogramma accepteert alleen namen van apps, en
een naam kan alleen een app uit de eigen lijsten van root kiezen.

## Updates op de achtergrond { #background-updates }

Er is één timer voor updates op de achtergrond, en dat is een systemd-timer
voor je eigen gebruiker. Hij draait dus als jouw gebruiker en niet als root.
`kiwi-updater.timer` voert `kiwi update --all` uit zes uur na de vorige keer en
tien minuten na het opstarten, met wat willekeurige vertraging. Daarbij worden
gebruikersdelen rechtstreeks bijgewerkt, en systeemdelen via het hulpprogramma
hierboven. Er is geen timer voor root. In de modus `manual` werkt de timer geen
systeemdelen bij. Die wachten tot je zelf `kiwi update` uitvoert.

## Vertrouwen { #trust }

Installeer je een app, dan **voert kiwi het `install.sh` uit de repository van
die app uit**. Geeft de app de system-scope op, dan voert kiwi dat script
**als root** uit. Catalogi zijn samengesteld, niet gecontroleerd: iemand heeft
de apps uitgekozen, maar dat betekent niet dat hun code is nagekeken. Voeg
alleen catalogi toe die je vertrouwt, zoals je dat ook bij een
pakketrepository zou doen. Met `kiwi info --installer`, `kiwi diff` en
`kiwi pin` zie je wat een app doet voordat je beslist. Een handtekening bepaalt
*wie een release mag publiceren*. Over *wat de gepubliceerde release doet*, zegt
ze niets.

Eén ding is nog gepland: een gehost register van vertrouwde catalogi, met het
commando `kiwi catalog browse` en met de vingerafdrukken van de ondertekenaars
bij elk item.
