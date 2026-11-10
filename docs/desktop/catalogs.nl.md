# Catalogi en apps publiceren

## De Kiwi-catalogus { #the-kiwi-catalog }

[derlocke-ng/kiwi-catalog](https://github.com/derlocke-ng/kiwi-catalog) is de
appcatalogus voor het Kiwi Network. De installatie van kiwi-updater registreert
hem, en `kiwi catalog add https://github.com/derlocke-ng/kiwi-catalog.git`
registreert hem met de hand.

| App | Release | Scopes | Wat het is |
|---|---|---|---|
| [kiwi-updater](kiwi-updater.md) | v2.4.0 | user | de updater zelf |
| [kiwi-killswitch](kiwi-killswitch.md) | v0.2.3 | user + system | fail-closed VPN-killswitch voor GNOME |
| [ensconce](ensconce.md) | v2.5.0 | user | inrichting na de installatie voor Bluefin-DX |
| [kiwi-cli-tools-desktop](cli-tools.md) | v1.2.1 | user | `pweb`, `select-server`, `tethering`, `torlink` |
| [kiwi-proxy](../clients/kiwi-proxy.md) | v0.7.3 | user | verzegelde SOCKS5/VPN-exits in rootless Podman |
| [kiwi-fox](../clients/kiwi-fox.md) | v0.7.1 | user | geïsoleerde browseridentiteiten op kiwi-proxy-exits |
| [kiwi-custodia](../clients/kiwi-custodia.md) | v0.2.3 | user | distroboxen waarvan het verkeer alleen via een exit vertrekt |
| [kiwi-server](../server/index.md) | v2.42.0 | user | je eigen netwerk bouwen en draaien |
| [syncman](syncman.md) | v0.4.1 | user | tweerichtings-mappensynchronisatie |
| [gnome-monitor](gnome-monitor.md) | v0.3.2 | user | schermindelingen voor GNOME |
| [kiwi-plugin-tor](../clients/providers.md) | v0.3.0 | user | kiwi-proxy-provider: Tor |
| [kiwi-plugin-vpn](../clients/providers.md) | v0.2.2 | user | kiwi-proxy-provider: een VPN via gluetun |
| [kiwi-plugin-9proxy](../clients/providers.md) | v0.2.0 | user | kiwi-proxy-provider: 9proxy |
| [kiwi-plugin-myst](../clients/providers.md) | v0.5.2 | user | kiwi-proxy-provider: Mysterium |

kiwi synchroniseert de catalogus vóór elke controle en update, dus een vloot
desktops beheren is gewoon git:

- **een app toevoegen**: voeg de URL toe aan `apps.list` en commit;
- **vastpinnen of terugdraaien**: zet `ref=<tag>` achter de regel (op één machine
  doet `kiwi pin <app> <tag>` hetzelfde);
- **verwijderen**: wis de regel (geïnstalleerde kopieën blijven tot je ze
  deïnstalleert).

## Je eigen catalogus { #your-own-catalog }

Een catalogus is een git-repo met een `apps.list` en, optioneel, een
`catalog.manifest` die de catalogus zelf beschrijft:

```ini
# catalog.manifest
NAME=my-catalog
DESCRIPTION=What these apps are for
HOMEPAGE=https://…
MAINTAINER=you
```

```
# apps.list: één regel per app, ook als die een root-helft en een gebruikershelft heeft
https://github.com/derlocke-ng/kiwi-updater.git
https://github.com/you/your-tool.git ref=v1.2.0
```

| Optie | Betekenis |
|---|---|
| `branch=<name>` | een branch volgen in plaats van release-tags |
| `ref=<tag>` | een exacte versie vastpinnen |
| `scope=user\|system` | alleen die helft installeren op machines die deze lijst gebruiken. Dit is een *filter*, geen declaratie |

De eigen lijst van een machine (`~/.config/kiwi-updater/apps.list`, of
`/etc/kiwi-updater/apps.list` voor root) gaat altijd vóór een catalogus.
`kiwi add <url>` voegt er een regel aan toe.

## Een app publiceren { #publishing-an-app }

Zet een `kiwi.manifest` en een `install.sh` in de hoofdmap van je repo. Sjablonen
staan in [`templates/`](https://github.com/derlocke-ng/kiwi-updater/tree/main/templates)
van kiwi-updater.

```ini
NAME=my-tool
DESCRIPTION=Short description
# COMPONENTS: cli gui daemon service gnome-extension config module
COMPONENTS=cli
# SCOPES: user, system, or both
SCOPES=user
VERSION=0.1.0
HOMEPAGE=https://…
LICENSE=GPL-3.0-or-later
ICON=data/my-tool.svg
INSTALLER=install.sh
```

Andere sleutels: `AUTHOR`, `CATEGORY`, `TAGS`, `SCREENSHOTS`, `ABOUT` (een bestand
dat Kiwi Apps toont), `DEPENDS` en, voor alles met een systeemhelft,
`ROOT_REASON`. `ICON=` is een SVG of PNG van hoogstens 1 MiB binnen de repo. De
meeste Kiwi-apps halen het hunne uit [kiwi-icons](../project/brand.md).

!!! warning "Commentaar op een eigen regel"
    Een waarde loopt door tot het einde van de regel. `COMPONENTS=cli  # … gui …`
    maakt het commentaar deel van de waarde, en de app wordt dan behandeld alsof
    hij een GUI heeft.

kiwi voert je installer één keer **per gedeclareerde scope** uit, met:

| Variabele | Waarde |
|---|---|
| `KIWI_SCOPE` | `user` of `system` |
| `KIWI_PREFIX` | `~/.local` of `/usr/local` |
| `KIWI_APP_DIR` | absoluut pad van de clone |
| `KIWI_ACTION` | `install`, `update` of `uninstall` |
| `KIWI_GUI` | `0` op een machine zonder beeldscherm, of met `--cli-only` |
| `KIWI_PURGE` | `1` als de gebruiker om `--purge` vroeg |
| `PATH` | eerst `$KIWI_PREFIX/bin`; een vast systeempad voor de systeemscope |

Een installer voor beide scopes vertakt op `KIWI_SCOPE` en doet elke keer alleen
die helft. Laat zonder `--purge` de configuratie van de gebruiker staan waar ze
staat.

**Publiceer een release met een ondertekende tag**, zodat een systeemhelft
zonder wachtwoord kan bijwerken:

```bash
git config gpg.format ssh            # ondertekenen met je SSH-sleutel
git tag -s v1.3.0 -m v1.3.0 && git push origin v1.3.0
```

`templates/release.yml` van kiwi-updater publiceert alleen een GitHub-release
voor een tag die is ondertekend met een sleutel uit `.github/allowed_signers`, en
maakt nooit zelf tags aan. Open daarna een pull request die je URL aan de
catalogus toevoegt. Alles wat open source is en echt bruikbaar zonder account,
abonnement of tracker is welkom.

## Vertrouwen { #trust }

De catalogus is **samengesteld, niet geaudit**. Vermeld staan betekent dat
iemand de app de moeite waard vond, niet dat de code is nagekeken. Lees
`kiwi info <app>` voordat je iets installeert wat je nog niet kent, en
`kiwi info --installer <app>` om precies te zien wat er gaat draaien.
