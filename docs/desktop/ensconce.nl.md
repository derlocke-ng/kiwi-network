# ensconce

Modulaire inrichting na de installatie voor [Bluefin-DX](https://projectbluefin.io/).
ensconce maakt van een verse Bluefin-installatie je geconfigureerde werkplek, op
basis van gewone lijstbestanden: gelaagde pakketten, Flatpaks, GNOME-extensies,
Nextcloud-synchronisatie, een gesynchroniseerde SSH-configuratie, instellingen
voor de desktop en het inlogscherm, en je Kiwi-apps.

- Repository: [derlocke-ng/ensconce](https://github.com/derlocke-ng/ensconce),
  GPL-3.0-or-later (volgens het manifest; de README zegt GPL-3.0)
- Nieuwste release: **v2.5.0**. Het staat in de [Kiwi-catalogus](catalogs.md), gebruikersscope.

```bash
kiwi install ensconce
ensconce --init          # ~/.config/ensconce aanmaken uit de voorbeelden
ensconce                 # de inrichting uitvoeren
```

Of vanuit een clone: `./ensconce.sh --init`, `config/` bewerken, daarna `./ensconce.sh`.

## Stappen { #steps }

Elke fase is een script in `steps/`, op volgorde uitgevoerd:

| # | Stap | Doet |
|---|---|---|
| 01 | `rebase` | overstappen op Bluefin-DX |
| 02 | `ujust` | ontwikkelaarsgroepen en CLI-tools |
| 03 | `repos` | RPM-repository's toevoegen |
| 04 | `packages` | RPM-pakketten in lagen toevoegen |
| 05 | `flatpaks` | Flatpak-apps installeren (`FLATPAK_LANGUAGES` kiest hun vertalingen) |
| 06 | `overrides` | Flatpak-overrides voor rechten |
| 07 | `extensions` | GNOME Shell-extensies |
| 08 | `cacert` | eigen CA-certificaten |
| 09 | `nextcloud` | Nextcloud-mapsynchronisatie vooraf instellen |
| 10 | `dconf` | instellingen van de GNOME-desktop |
| 11 | `gdm` | het inlogscherm |
| 12 | `ssh` | een gesynchroniseerde SSH-configuratie, met Bitwarden of GNOME als SSH-agent |
| 13 | `kiwi` | kiwi-updater installeren (`KIWI_INSTALL=recommended\|manual\|minimal`) en elke app in `kiwi-apps.list` |
| 14 | `sysctl` | drop-ins uit `sysctl.d/` (een voorbeeld begrenst de dirty writeback voor trage SSD's) |
| 15 | `power` | `SYSTEM_SLEEP=off` maskeert de slaap-targets |

ensconce controleert eerst de omgeving (een Bluefin-image, `rpm-ostree`,
`flatpak`, `dconf`, `jq`, `curl`). Het slaat zijn voortgang op en gaat na
herstarts verder, en houdt de machine de hele run wakker, waarna je
energie-instellingen worden hersteld.

```bash
ensconce --dry-run                  # voorvertoning zonder iets te wijzigen
ensconce --skip rebase,ujust        # stappen overslaan
ensconce --only extensions,dconf    # alleen deze uitvoeren
ensconce --status | --list-steps | --reset
ensconce --log [file]               # de uitvoer opslaan
ensconce --config-dir               # de actieve configuratiemap tonen
```

## Configuratie { #configuration }

De configuratiemap is de eerste die bestaat van: `$ENSCONCE_CONFIG`,
`~/.config/ensconce/` (geïnstalleerd via kiwi), `config/` in een clone, en
`config.example/` (met een waarschuwing).

| Bestand / map | Doel |
|---|---|
| `settings.sh` | server-URL's en schakelaars: SSH, kiwi-updater, Flatpak-talen, slaapstand |
| `packages.list`, `flatpaks.list`, `extensions.list` | één item per regel |
| `kiwi-apps.list` | de Kiwi-apps die geïnstalleerd worden |
| `repos.d/`, `flatpak-overrides/` | repo-bestanden; overrides per app in het eigen formaat van Flatpak |
| `nextcloud/folders.list` | synchronisatiemappen als `localPath\|remotePath[\|tags]` |
| `nextcloud/exclude.lst`, `exclude.d/` | globale uitsluitingen en uitsluitingen per map (met tag) voor synchronisatie |
| `certs/` | CA-certificaten (`.pem`), bijvoorbeeld de `kiwiCA.pem` van je fleet |
| `sysctl.d/` | kernelinstellingen |
| `dconf-settings.ini`, `gtk3-bookmarks` | GNOME-instellingen, bladwijzers van Nautilus |
| `gdm/dconf.d/`, `gdm/monitors.xml` | de instellingen en schermindeling van het inlogscherm |

Een uitsluitingstag per map zoals `browser` zet `exclude.d/browser.lst` in die
map, waardoor de databases van een browserprofiel niet worden gesynchroniseerd
(en beschadigd) terwijl `user.js` wel wordt gesynchroniseerd.

## Een machine klonen { #cloning-a-machine }

`--export` leest het draaiende systeem uit en schrijft een configuratieboom voor
ensconce, het omgekeerde van de stappen:

```bash
ensconce --export ./my-setup        # op de geconfigureerde machine
ensconce --init                     # op de nieuwe
cp -rT ./my-setup "$(ensconce --config-dir)"
ensconce --dry-run && ensconce
```

Het legt alleen vast wat je hebt toegevoegd: gevraagde pakketten in plaats van de
hele image, extensies die echt van extensions.gnome.org komen, je eigen
repo-bestanden, en uitgekozen dconf-subbomen in plaats van een volledige dump.
Zie het als een beginpunt. `certs/` en `nextcloud/` kunnen privémateriaal
bevatten.

ensconce is een app met **gebruikersscope**. De stappen die root nodig hebben,
vragen daar zelf om. Voeg je eigen stap toe als `steps/NN-<name>.sh` met een
functie `step_<name>()`.
