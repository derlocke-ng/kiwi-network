# Catalogi en apps publiceren

Een catalogus is een lijst van apps die kiwi-updater kan installeren. Het is een
git-repository, dus je kunt hem lezen, kopiëren en er wijzigingen voor
voorstellen. Op deze pagina lees je wat er in de Kiwi-catalogus staat, hoe je
een eigen catalogus maakt, bijvoorbeeld voor alle desktops die je beheert, en
hoe je een app publiceert zodat anderen hem met kiwi kunnen installeren.

## De Kiwi-catalogus { #the-kiwi-catalog }

[derlocke-ng/kiwi-catalog](https://github.com/derlocke-ng/kiwi-catalog) is de
catalogus met apps van Kiwi Network. Hij wordt automatisch geregistreerd als je
kiwi-updater installeert. Met de hand registreren doe je met
`kiwi catalog add https://github.com/derlocke-ng/kiwi-catalog.git`.

De tabel toont de apps in de catalogus. In de kolom *Scopes* zie je waar een app
wordt geïnstalleerd. De scope user is je thuismap, de scope system is een deel
dat van root is.

| App | Release | Scopes | Wat het is |
|---|---|---|---|
| [kiwi-updater](kiwi-updater.md) | v2.4.0 | user | de updater zelf |
| [kiwi-killswitch](kiwi-killswitch.md) | v0.2.3 | user + system | VPN-killswitch voor GNOME. Hij is fail-closed: zolang de VPN niet actief is, blijft al het verkeer geblokkeerd |
| [ensconce](ensconce.md) | v2.5.0 | user | richt een vers geïnstalleerde Bluefin-DX in |
| [kiwi-cli-tools-desktop](cli-tools.md) | v1.2.1 | user | `pweb`, `select-server`, `tethering`, `torlink` |
| [kiwi-proxy](../clients/kiwi-proxy.md) | v0.7.3 | user | exits voor SOCKS5- en VPN-verbindingen. Een exit is een afgeschermde container in rootless Podman |
| [kiwi-fox](../clients/kiwi-fox.md) | v0.7.1 | user | afgeschermde browseridentiteiten die exits van kiwi-proxy gebruiken |
| [kiwi-custodia](../clients/kiwi-custodia.md) | v0.2.3 | user | boxen (containers met een Linux-distributie) waarvan het verkeer alleen via een exit gaat |
| [kiwi-server](../server/index.md) | v2.42.0 | user | het programma waarmee je je eigen netwerk opbouwt en beheert |
| [syncman](syncman.md) | v0.4.1 | user | synchroniseert mappen in beide richtingen |
| [gnome-monitor](gnome-monitor.md) | v0.3.2 | user | slaat schermindelingen in GNOME op en wisselt ertussen |
| [kiwi-plugin-tor](../clients/providers.md) | v0.3.0 | user | providermodule voor kiwi-proxy: Tor |
| [kiwi-plugin-vpn](../clients/providers.md) | v0.2.2 | user | providermodule voor kiwi-proxy: een VPN via gluetun |
| [kiwi-plugin-9proxy](../clients/providers.md) | v0.2.0 | user | providermodule voor kiwi-proxy: 9proxy |
| [kiwi-plugin-myst](../clients/providers.md) | v0.5.2 | user | providermodule voor kiwi-proxy: Mysterium |

Voor elke controle en elke update haalt kiwi de actuele catalogus op. Daardoor
kun je de apps op al je desktops alleen met git beheren:

- **Een app toevoegen:** zet de URL in `apps.list` en commit.
- **Een app op een versie vastzetten of terugzetten naar een oudere:** zet
  `ref=<tag>` achter de regel. Op één machine doet `kiwi pin <app> <tag>`
  hetzelfde.
- **Een app verwijderen:** haal de regel weg. Wat al geïnstalleerd is, blijft
  staan tot je het verwijdert.

## Je eigen catalogus { #your-own-catalog }

Een catalogus is een git-repository met een bestand `apps.list`. Er kan ook een
bestand `catalog.manifest` in staan, waarin de catalogus zichzelf beschrijft:

```ini
# catalog.manifest
NAME=my-catalog
DESCRIPTION=What these apps are for
HOMEPAGE=https://…
MAINTAINER=you
```

```
# apps.list: één regel per app, ook als die een root-deel en een gebruikersdeel heeft
https://github.com/derlocke-ng/kiwi-updater.git
https://github.com/you/your-tool.git ref=v1.2.0
```

Een regel in `apps.list` kan na de URL deze opties hebben:

| Optie | Betekenis |
|---|---|
| `branch=<name>` | een branch volgen in plaats van release-tags |
| `ref=<tag>` | precies op deze versie blijven |
| `scope=user\|system` | alleen dat deel van de app installeren op machines die deze lijst gebruiken. Deze optie is een *filter*. Ze legt niet vast welke scopes de app heeft |

Elke machine heeft daarnaast een eigen lijst:
`~/.config/kiwi-updater/apps.list` voor je gebruiker en
`/etc/kiwi-updater/apps.list` voor root. Een regel in de eigen lijst van de
machine gaat altijd voor op een catalogus. `kiwi add <url>` voegt een regel aan
deze lijst toe.

## Een app publiceren { #publishing-an-app }

Om een app te publiceren, zet je een bestand `kiwi.manifest` en een script
`install.sh` in de hoofdmap van je repository. Sjablonen vind je in de map
[`templates/`](https://github.com/derlocke-ng/kiwi-updater/tree/main/templates)
van kiwi-updater.

```ini
NAME=my-tool
DESCRIPTION=Short description
# COMPONENTS: cli gui daemon service gnome-extension config module
COMPONENTS=cli
# SCOPES: user, system of beide
SCOPES=user
VERSION=0.1.0
HOMEPAGE=https://…
LICENSE=GPL-3.0-or-later
ICON=data/my-tool.svg
INSTALLER=install.sh
```

Een manifest kan nog meer sleutels hebben: `AUTHOR`, `CATEGORY`, `TAGS`,
`SCREENSHOTS`, `ABOUT` (een bestand dat Kiwi Apps toont), `DEPENDS` en
`ROOT_REASON`. Elke app met een systeemdeel heeft `ROOT_REASON` nodig. `ICON=`
verwijst naar een SVG- of PNG-bestand van maximaal 1 MiB in de repository. De
meeste Kiwi-apps halen hun icoon uit [kiwi-icons](../project/brand.md).

!!! warning "Zet commentaar op een eigen regel"
    Een waarde loopt door tot het einde van de regel. Schrijf je
    `COMPONENTS=cli  # … gui …`, dan hoort het commentaar bij de waarde, en
    behandelt kiwi de app alsof hij een GUI heeft.

kiwi voert je installer één keer uit **voor elke scope die de app opgeeft**.
Daarbij zet kiwi deze variabelen voor de installer:

| Variabele | Waarde |
|---|---|
| `KIWI_SCOPE` | `user` of `system` |
| `KIWI_PREFIX` | `~/.local` of `/usr/local` |
| `KIWI_APP_DIR` | absoluut pad van de kloon |
| `KIWI_ACTION` | `install`, `update` of `uninstall` |
| `KIWI_GUI` | `0` op een machine zonder grafische desktop (headless), of met `--cli-only` |
| `KIWI_PURGE` | `1` als de gebruiker om `--purge` heeft gevraagd |
| `PATH` | `$KIWI_PREFIX/bin` staat vooraan. De system-scope krijgt een vast systeempad |

Een installer voor een app met beide scopes moet `KIWI_SCOPE` controleren en
bij elke uitvoering alleen het werk voor dat deel doen. Heeft de gebruiker niet
om `--purge` gevraagd, laat de configuratie van de gebruiker dan staan.

**Publiceer elke release als ondertekende tag.** Alleen dan kan een systeemdeel
zonder wachtwoord worden bijgewerkt:

```bash
git config gpg.format ssh            # ondertekenen met je SSH-sleutel
git tag -s v1.3.0 -m v1.3.0 && git push origin v1.3.0
```

kiwi-updater levert een release-workflow mee, `templates/release.yml`. Die
publiceert alleen een GitHub-release voor een tag die is ondertekend met een
sleutel uit `.github/allowed_signers`, en maakt zelf nooit tags aan. Open tot
slot een pull request dat je URL aan de catalogus toevoegt. Elke app die
opensource is en echt zonder account, abonnement of tracker te gebruiken is,
is welkom.

## Vertrouwen { #trust }

De catalogus is **samengesteld, niet gecontroleerd**. Een app staat erin omdat
iemand hem de moeite waard vond. Dat betekent niet dat de code is nagekeken.
Lees de uitvoer van `kiwi info <app>` voordat je een app installeert die
je niet kent. Met `kiwi info --installer <app>` zie je precies wat er wordt
uitgevoerd.
