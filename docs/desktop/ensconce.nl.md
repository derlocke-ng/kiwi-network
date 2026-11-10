# ensconce

ensconce richt een vers geïnstalleerde [Bluefin-DX](https://projectbluefin.io/)
voor je in, zodat je niet elke nieuwe machine met de hand hoeft te configureren.
Je beschrijft je werkstation in eenvoudige lijstbestanden, en ensconce maakt van
de verse installatie dat werkstation. Het regelt gelaagde pakketten, Flatpaks,
GNOME-extensies, synchronisatie met Nextcloud, een SSH-configuratie die tussen
je machines gelijk wordt gehouden, de instellingen van de desktop en het
inlogscherm, en je Kiwi-apps. Gelaagde pakketten zijn RPM-pakketten die bovenop
het systeemimage worden toegevoegd. De inrichting is modulair: ze bestaat uit
losse stappen die je kunt uitvoeren of overslaan.

- Repository: [derlocke-ng/ensconce](https://github.com/derlocke-ng/ensconce).
  Volgens het manifest is de licentie GPL-3.0-or-later, in de README staat
  GPL-3.0.
- Nieuwste release: **v2.5.0**. Staat in de [Kiwi-catalogus](catalogs.md) en
  wordt geïnstalleerd in de user-scope, dus in je thuismap.

```bash
kiwi install ensconce
ensconce --init          # ~/.config/ensconce aanmaken op basis van de voorbeelden
ensconce                 # de inrichting uitvoeren
```

Je kunt het ook vanuit een kloon van de repository draaien. Voer
`./ensconce.sh --init` uit, pas de bestanden in `config/` aan en voer daarna
`./ensconce.sh` uit.

## Stappen { #steps }

De inrichting is verdeeld in stappen. Elke stap is een script in `steps/`, en
de stappen lopen in deze volgorde:

| # | Stap | Doet |
|---|---|---|
| 01 | `rebase` | zet het systeem om naar Bluefin-DX |
| 02 | `ujust` | richt groepen en opdrachtregeltools voor ontwikkelaars in |
| 03 | `repos` | voegt RPM-repository’s toe |
| 04 | `packages` | voegt RPM-pakketten als laag toe |
| 05 | `flatpaks` | installeert Flatpak-apps. `FLATPAK_LANGUAGES` bepaalt de talen van hun vertalingen |
| 06 | `overrides` | stelt afwijkende Flatpak-rechten in (overrides) |
| 07 | `extensions` | installeert extensies voor GNOME Shell |
| 08 | `cacert` | installeert eigen CA-certificaten |
| 09 | `nextcloud` | configureert vooraf welke mappen met Nextcloud worden gesynchroniseerd |
| 10 | `dconf` | past de instellingen van de GNOME-desktop toe |
| 11 | `gdm` | configureert het inlogscherm |
| 12 | `ssh` | richt de gesynchroniseerde SSH-configuratie in, met Bitwarden of GNOME als SSH-agent |
| 13 | `kiwi` | installeert kiwi-updater op de manier die `KIWI_INSTALL=recommended\|manual\|minimal` kiest, en daarna elke app uit `kiwi-apps.list` |
| 14 | `sysctl` | installeert de bestanden met kernelinstellingen uit `sysctl.d/`. Een voorbeeldbestand beperkt hoeveel nog niet weggeschreven gegevens de kernel in het geheugen houdt, wat helpt bij trage SSD’s |
| 15 | `power` | maskeert met `SYSTEM_SLEEP=off` de slaapdoelen van systemd, zodat de machine niet in slaapstand kan gaan |

Voordat ensconce begint, controleert het de omgeving. Het systeem moet een
Bluefin-image zijn, en `rpm-ostree`, `flatpak`, `dconf`, `jq` en `curl` moeten
beschikbaar zijn. ensconce houdt bij hoe ver het is, dus na een herstart gaat het
verder waar het was gebleven. Tijdens de hele uitvoering houdt het de machine
wakker, en daarna zet het je energie-instellingen terug.

Met deze opties stuur je een uitvoering:

```bash
ensconce --dry-run                  # vooraf bekijken zonder iets te veranderen
ensconce --skip rebase,ujust        # stappen overslaan
ensconce --only extensions,dconf    # alleen deze uitvoeren
ensconce --status | --list-steps | --reset
ensconce --log [file]               # de uitvoer opslaan
ensconce --config-dir               # de actieve configuratiemap tonen
```

## Configuratie { #configuration }

ensconce zoekt zijn configuratiemap op vier plekken en gebruikt de eerste die
bestaat. Eerst kijkt het naar `$ENSCONCE_CONFIG`, dan naar
`~/.config/ensconce/`, die wordt gebruikt als ensconce met kiwi is
geïnstalleerd, dan naar `config/` in een kloon, en ten slotte naar
`config.example/`. Gebruikt het `config.example/`, dan geeft het een
waarschuwing.

| Bestand / map | Doel |
|---|---|
| `settings.sh` | URL’s van servers, en de schakelaars voor SSH, kiwi-updater, Flatpak-talen en slaapstand |
| `packages.list`, `flatpaks.list`, `extensions.list` | de pakketten, Flatpaks en GNOME-extensies die worden geïnstalleerd, één per regel |
| `kiwi-apps.list` | de Kiwi-apps die worden geïnstalleerd |
| `repos.d/`, `flatpak-overrides/` | repositorybestanden, en overrides voor afzonderlijke apps in het eigen formaat van Flatpak |
| `nextcloud/folders.list` | de mappen die worden gesynchroniseerd, geschreven als `localPath\|remotePath[\|tags]` |
| `nextcloud/exclude.lst`, `exclude.d/` | wat buiten de synchronisatie blijft, voor alle mappen en voor afzonderlijke mappen met een tag |
| `certs/` | CA-certificaten (`.pem`), bijvoorbeeld `kiwiCA.pem` van je netwerk |
| `sysctl.d/` | kernelinstellingen |
| `dconf-settings.ini`, `gtk3-bookmarks` | GNOME-instellingen en bladwijzers van Nautilus |
| `gdm/dconf.d/`, `gdm/monitors.xml` | de instellingen en de schermindeling van het inlogscherm |

Met een tag in `nextcloud/folders.list` krijgt een map eigen uitzonderingen. De
tag `browser` zet bijvoorbeeld `exclude.d/browser.lst` in die map. De databases
van een browserprofiel worden dan niet gesynchroniseerd, omdat ze daar kapot
van kunnen gaan, terwijl `user.js` wel wordt gesynchroniseerd.

## Een machine klonen { #cloning-a-machine }

`--export` doet het omgekeerde van de stappen. Het leest het draaiende systeem
uit en schrijft daar een configuratiemap voor ensconce van. Met die map kun je
daarna een nieuwe machine inrichten:

```bash
ensconce --export ./my-setup        # op de ingerichte machine
ensconce --init                     # op de nieuwe
cp -rT ./my-setup "$(ensconce --config-dir)"
ensconce --dry-run && ensconce
```

De export bevat alleen wat je zelf aan het systeem hebt toegevoegd. Er staan de
pakketten in die je hebt aangevraagd, niet het hele image. Er staan alleen
extensies in die echt van extensions.gnome.org komen. Je eigen
repositorybestanden zitten erin, en in plaats van een volledige dump een
selectie van dconf-subtrees. Beschouw de export als vertrekpunt. `certs/` en
`nextcloud/` kunnen vertrouwelijke gegevens bevatten.

ensconce is een app voor de **user-scope**. De stappen die root nodig hebben,
vragen daar zelf om. Wil je een eigen stap toevoegen, maak dan een bestand
`steps/NN-<name>.sh` met een functie `step_<name>()`.
