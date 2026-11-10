# kiwi-updater

`kiwi` installeert en werkt opensource-apps bij vanuit **git-catalogi** op Fedora
Silverblue, Bluefin en andere ostree-systemen. Een app is een git-repo met een
`kiwi.manifest` en een `install.sh`. kiwi kloont hem, checkt de nieuwste
release-tag uit, voert de installer uit, en houdt hem op de achtergrond bij,
zichzelf inbegrepen.

Er zijn geen accounts, geen winkel en geen leverancier. Een catalogus is een repo
die je kunt lezen, forken en waar je een pull request naar kunt sturen.

- Repository: [derlocke-ng/kiwi-updater](https://github.com/derlocke-ng/kiwi-updater), GPL-3.0-or-later
- Nieuwste release: **v2.4.0**, een beveiligingsrelease
- **`kiwi`** is de CLI. Hij vereist `git`, coreutils, `util-linux` en `awk`,
  allemaal in de basisimage, plus `ssh-keygen` voor handtekeningcontroles.
- **Kiwi Apps** (`kiwi-gui`) is de GTK4-app: zoeken, filters, een detailweergave
  per app met icoon, schermafbeeldingen en afhankelijkheden. Hij toont de
  installer en de diff van een update voordat hij een van beide uitvoert, en zet
  je klikken in een wachtrij. Zijn gegevens komen van de CLI; iconen en
  schermafbeeldingen worden uit de clones van de apps gelezen, dus daarvoor wordt
  niets opgehaald.

## Installeren { #install }

```bash
# aanbevolen: gebruikersscope plus de systeemscope van root, één wachtwoordvraag
curl -fsSL https://raw.githubusercontent.com/derlocke-ng/kiwi-updater/main/get-kiwi.sh | bash

# minimaal: 100 % op gebruikersniveau, alleen ~/.local, nooit root en nooit een wachtwoord
curl -fsSL https://raw.githubusercontent.com/derlocke-ng/kiwi-updater/main/get-kiwi.sh | bash -s -- --minimal

# helemaal niets zonder wachtwoord: elke systeemwijziging vraagt om een wachtwoord
curl -fsSL https://raw.githubusercontent.com/derlocke-ng/kiwi-updater/main/get-kiwi.sh | bash -s -- --with-system=manual
```

De [Kiwi-catalogus](catalogs.md) wordt bij de installatie geregistreerd. Ga
meteen naar `kiwi list` of open **Kiwi Apps**.

Apps die alleen uit bestanden in je homemap bestaan (de CLI-tools, ensconce,
syncman), zijn compleet met de minimale installatie. Een app met een root-helft,
zoals kiwi-killswitch, heeft de systeemscope nodig. Op een minimale installatie
richt `kiwi install kiwi-killswitch` die ter plekke in met één wachtwoord.

## Commando's { #commands }

```bash
kiwi list [--check]          # elke app die deze machine kent
kiwi search vpn              # een app zoeken in elke geregistreerde catalogus
kiwi info kiwi-killswitch    # wat het is, wat het installeert, of het root nodig heeft
kiwi install <app>           # een naam, of expliciet --all
kiwi update [<app>]          # alles met een nieuwe release
kiwi uninstall <app>         # --purge verwijdert ook de configuratie
kiwi check                   # exitcode 10 als er voor iets een update is

kiwi add <https-url>         # één repo rechtstreeks volgen, zonder catalogus
kiwi catalog add|list|remove # catalogi beheren
kiwi sync                    # catalogi nu verversen
kiwi self-update
kiwi trust --system <app>    # de vastgepinde ondertekeningssleutel van een systeemapp vergeten
```

Voordat je iets uitvoert, en als er iets misgaat:

```bash
kiwi info --installer <app>  # het script dat een installatie zou uitvoeren, vóór het draait
kiwi diff <app>              # wat een update zou veranderen, inclusief de installer
kiwi pin <app> v1.2.0        # daar blijven; kiwi unpin <app> om weer releases te volgen
kiwi install <app> --dry-run # scope, URL, ref, pad van de installer, en verder niets
kiwi doctor                  # verouderde locks, versieverschillen, kapotte lijstbestanden, timers
```

## Releases zijn tags { #releases-are-tags }

Een app volgt zijn nieuwste **versietag**, een die overeenkomt met
`^v?[0-9]+(\.[0-9]+){0,3}$` (`v1`, `v1.2`, `1.2.3`, `v1.2.3.4`). Pre-releases en
tijdelijke tags halen een release nooit in. Een repo zonder versietag volgt zijn
standaardbranch. `ref=<tag>` op een lijstregel vraagt om een specifieke tag.

## Afhankelijkheden { #dependencies }

`DEPENDS=` in een manifest noemt wat een app nodig heeft. Een woord dat een app
is in je eigen catalogus of lijst, wordt bij de installatie **eerst**
geïnstalleerd, in dezelfde scope. `kiwi install kiwi-plugin-tor` neemt
bijvoorbeeld kiwi-proxy mee. Elk ander woord is een programma, gecontroleerd met
`command -v`.

## Eén app, twee helften { #one-app-two-halves }

Sommige apps zijn alleen een binary in `~/.local/bin`. Andere, zoals een
VPN-killswitch, zijn een root-daemon **en** een desktopapp **en** een
GNOME-extensie. De helften worden met verschillende rechten geïnstalleerd, want
**root mag nooit een bestand uitvoeren dat de gebruiker kan schrijven**. De app
declareert het:

```ini
COMPONENTS=daemon cli gui gnome-extension
SCOPES=user system
ROOT_REASON=installs a root firewall daemon, its D-Bus policy and two systemd units
```

Een catalogus vermeldt die app één keer, en kiwi installeert elke helft correct.
Voordat hij om je wachtwoord vraagt, toont hij de `ROOT_REASON`.

| Onderdeel | Waar | Waarom |
|---|---|---|
| `kiwi`, Kiwi Apps, gebruikersapps | `~/.local` | geen root nodig; overleeft een ostree-rebase |
| de eigen kopie van kiwi voor root | `/usr/local/bin`, gekloond naar `/var/lib/kiwi-updater/repos/` | root voert nooit een bestand uit dat jij kunt schrijven |
| systeemapps | `/var/lib`, `/etc` | schrijfbaar op ostree, eigendom van root |
| lijsten | `~/.config/kiwi-updater/apps.list`, `/etc/kiwi-updater/apps.list` | de eigen vermeldingen van een machine gaan voor elke catalogus |
| vastgepinde ondertekeningssleutels | `/etc/kiwi-updater/signers/<app>` | zie hieronder |

De onveranderlijke `/usr` wordt nooit aangeraakt.

## Root, wachtwoorden en handtekeningen { #root-passwords-and-signatures }

| | Heeft root nodig | Vraagt om een wachtwoord |
|---|---|---|
| alles in de gebruikersscope | nee | nee |
| een systeemapp **bijwerken** | ja | **nee**, voor een release die ondertekend is met de sleutel die root voor die app heeft vastgepind. **Ja** voor een niet-ondertekende release, en altijd in de modus `manual` |
| een systeemapp **installeren** of **deïnstalleren** | ja | ja |

Sinds 2.4.0:

- **Ondertekende releases.** Root pint per systeemapp één SSH-ondertekeningssleutel
  vast, de eerste die hij ziet (trust on first use). Een release-tag die met die
  sleutel is ondertekend, wordt zonder wachtwoord bijgewerkt. Een niet-ondertekende
  release vraagt om een wachtwoord en meldt dat hij niet geverifieerd kon worden.
  Een tag die met een andere sleutel is ondertekend, of een niet-ondertekende tag
  na ondertekende tags, wordt geweigerd tot je `kiwi trust --system <app>`
  uitvoert. Dit geldt voor de systeemscope.
- **Root installeert alleen bronnen die in zijn eigen lijsten staan**:
  `/etc/kiwi-updater/apps.list` en catalogi die voor root zijn geregistreerd. Voor
  al het andere installeert kiwi de gebruikershelft en noemt hij de opdracht
  `kiwi add --system <https-url>` die je moet uitvoeren. Kiwi Apps biedt
  *Register and Install* aan.
- **Alleen https.** `http://`-bronnen worden overal geweigerd.

Systeemupdates zonder wachtwoord lopen via één helper met een vast doel,
`/usr/local/libexec/kiwi-system-update`. Een polkit-regel staat hem toe voor
actieve `wheel`-sessies, en hij accepteert app-namen alleen als selectie uit de
eigen lijsten van root.

## Updates op de achtergrond { #background-updates }

Er is één timer, en die is van jou: `kiwi-updater.timer` draait
`kiwi update --all` zes uur na de vorige run (tien minuten na het opstarten, met
wat willekeurige vertraging). Hij werkt gebruikershelften rechtstreeks bij, en
systeemhelften via de helper hierboven. Er is geen root-timer. In de modus
`manual` wachten systeemhelften op je volgende interactieve `kiwi update`.

## Vertrouwen { #trust }

Een app installeren **voert de `install.sh` van die repo uit**, en een app die de
systeemscope declareert, voert hem uit **als root**. Catalogi zijn samengesteld,
niet geaudit. Voeg de catalogi toe die je vertrouwt, zoals je een
pakketrepository zou toevoegen, en gebruik `kiwi info --installer`, `kiwi diff`
en `kiwi pin` om met open ogen te beslissen. Een handtekening beperkt *wie mag
publiceren*. Ze zegt niets over *wat het gepubliceerde doet*.

Nog gepland: een gehost register van vertrouwde catalogi (`kiwi catalog browse`)
met vingerafdrukken van ondertekenaars per vermelding.
