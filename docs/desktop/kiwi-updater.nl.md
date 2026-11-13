# kiwi-updater

kiwi-updater installeert opensource-apps op je computer en houdt ze up-to-date.
Het commando heet `kiwi`. Het haalt de apps uit **git-catalogi**. Een catalogus
is een git-repository met een lijst van apps, en een app is een git-repository
met een bestand `kiwi.manifest` en een script `install.sh`. kiwi kloont de app,
checkt de nieuwste release-tag uit en voert de installer uit. Daarna werkt het
de app op de achtergrond bij, en zichzelf op dezelfde manier.

Je hebt geen account nodig, en er is geen appwinkel en geen leverancier. Een
catalogus is een repository die je kunt lezen en forken, en waarvoor je een
pull request kunt sturen. Alle desktop-apps van Kiwi worden zo geïnstalleerd.

- Repository: [derlocke-ng/kiwi-updater](https://github.com/derlocke-ng/kiwi-updater), GPL-3.0-or-later
- Nieuwste release: **v2.5.1**
- **`kiwi`** is de opdrachtregeltool. **Kiwi Apps** (`kiwi-gui`) is de
  desktop-app. Daarin kun je door de apps bladeren en ernaar zoeken, ze
  installeren en de installer van een app lezen voordat die wordt uitgevoerd.

## Waar het draait { #where-it-runs }

kiwi-updater is gemaakt voor de Fedora Atomic-desktops en draait inmiddels ook
op andere Linux-distributies. Elke wijziging aan kiwi-updater wordt op deze
systemen getest, met de volledige testsuite en een echte installatie:

| Systeem | Wat werkt |
|---|---|
| Fedora Silverblue, Bluefin, Fedora, Debian 13, Ubuntu 24.04, Arch, openSUSE Tumbleweed | alles |
| Alpine | alles, zodra de GNU-tools zijn geïnstalleerd |
| Debian 12, Ubuntu 22.04 (getest, maar niet bij elke wijziging) | `kiwi` en opdrachtregelapps. De libadwaita van deze systemen is te oud voor de desktop-apps |

## Installeren { #install }

Dit installeert het gebruikersdeel in je thuismap en het rootdeel voor apps die
root nodig hebben. Je hoeft daarvoor maar één keer je wachtwoord in te voeren:

```bash
curl -fsSL https://raw.githubusercontent.com/derlocke-ng/kiwi-updater/main/get-kiwi.sh | bash
```

Wil je dat er niets buiten je thuismap terechtkomt en dat je nooit om een
wachtwoord wordt gevraagd, installeer dan alleen het gebruikersdeel:

```bash
curl -fsSL https://raw.githubusercontent.com/derlocke-ng/kiwi-updater/main/get-kiwi.sh | bash -s -- --minimal
```

De installer controleert of de release die hij installeert, is ondertekend met
de sleutel waarmee kiwi-updater zijn releases ondertekent. Is dat niet zo, dan
weigert hij de release. Tijdens de installatie wordt ook de Kiwi-catalogus
geregistreerd. Daarna kun je aan de slag:

```bash
kiwi list                    # alle apps die je kunt installeren
kiwi install <app>           # er één installeren
kiwi info --installer <app>  # de installer lezen voordat die wordt uitgevoerd
kiwi-gui                     # de desktop-app
```

## Rootdelen en ondertekende releases { #root-parts-and-signed-releases }

Sommige apps hebben root nodig, bijvoorbeeld kiwi-killswitch, dat een
firewall-daemon heeft. Het rootdeel van zo’n app wordt geïnstalleerd door een
kopie van kiwi die van root is, en alleen uit bronnen die in de eigen lijsten
van root staan. Als je zo’n app installeert of verwijdert, wordt altijd om je
wachtwoord gevraagd. In de standaardmodus gaat een update alleen zonder
wachtwoord als de release is ondertekend met de sleutel die root voor die app
heeft opgeslagen.

## De volledige documentatie { #the-full-documentation }

kiwi-updater heeft zijn eigen documentatie, in zijn eigen repository:

| Pagina | Waar het over gaat |
|---|---|
| [Installeren](https://github.com/derlocke-ng/kiwi-updater/blob/main/docs/install.md) | ondersteunde systemen, pakketten per distributie, installatiemodi, verwijderen |
| [kiwi gebruiken](https://github.com/derlocke-ng/kiwi-updater/blob/main/docs/usage.md) | alle commando’s, Kiwi Apps, updates op de achtergrond, instellingen |
| [Catalogi](https://github.com/derlocke-ng/kiwi-updater/blob/main/docs/catalogs.md) | catalogi toevoegen, `apps.list`, een app op een versie vastzetten, een catalogusvermelding vervangen |
| [Beveiliging](https://github.com/derlocke-ng/kiwi-updater/blob/main/docs/security.md) | wat als root draait, wanneer je een wachtwoord invoert, wat kiwi controleert |
| [Een app schrijven](https://github.com/derlocke-ng/kiwi-updater/blob/main/docs/app-authors.md) | `kiwi.manifest`, `install.sh`, afhankelijkheden, iconen, releases |
| [Ondertekende releases](https://github.com/derlocke-ng/kiwi-updater/blob/main/docs/signing.md) | de releases van je app ondertekenen met `kiwi-release` |
| [Ontwikkeling](https://github.com/derlocke-ng/kiwi-updater/blob/main/docs/development.md) | tests, CI, een release van kiwi-updater uitbrengen |

Vanaf de volgende release van kiwi-updater staan deze pagina’s ook hier, in het
menu onder kiwi-updater.

Wil je zelf een app publiceren, kijk dan bij [Catalogi en
publiceren](catalogs.md).
