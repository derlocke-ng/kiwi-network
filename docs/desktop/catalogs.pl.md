# Katalogi i publikowanie aplikacji

## Katalog Kiwi { #the-kiwi-catalog }

[derlocke-ng/kiwi-catalog](https://github.com/derlocke-ng/kiwi-catalog) to
katalog aplikacji dla Kiwi Network. Instalacja kiwi-updater go rejestruje, a
`kiwi catalog add https://github.com/derlocke-ng/kiwi-catalog.git` rejestruje
go ręcznie.

| Aplikacja | Wydanie | Zakresy | Co to jest |
|---|---|---|---|
| [kiwi-updater](kiwi-updater.md) | v2.4.0 | user | sam updater |
| [kiwi-killswitch](kiwi-killswitch.md) | v0.2.3 | user + system | kill switch VPN dla GNOME w trybie fail-closed |
| [ensconce](ensconce.md) | v2.5.0 | user | konfiguracja poinstalacyjna dla Bluefin-DX |
| [kiwi-cli-tools-desktop](cli-tools.md) | v1.2.1 | user | `pweb`, `select-server`, `tethering`, `torlink` |
| [kiwi-proxy](../clients/kiwi-proxy.md) | v0.7.3 | user | zapieczętowane wyjścia SOCKS5/VPN w Podmanie bez roota |
| [kiwi-fox](../clients/kiwi-fox.md) | v0.7.1 | user | odizolowane tożsamości przeglądarki na wyjściach kiwi-proxy |
| [kiwi-custodia](../clients/kiwi-custodia.md) | v0.2.3 | user | kontenery dystrybucji, których ruch wychodzi tylko przez wyjście |
| [kiwi-server](../server/index.md) | v2.42.0 | user | zbuduj i prowadź własną sieć |
| [syncman](syncman.md) | v0.4.1 | user | dwukierunkowa synchronizacja folderów |
| [gnome-monitor](gnome-monitor.md) | v0.3.2 | user | układy ekranów dla GNOME |
| [kiwi-plugin-tor](../clients/providers.md) | v0.3.0 | user | dostawca kiwi-proxy: Tor |
| [kiwi-plugin-vpn](../clients/providers.md) | v0.2.2 | user | dostawca kiwi-proxy: VPN przez gluetun |
| [kiwi-plugin-9proxy](../clients/providers.md) | v0.2.0 | user | dostawca kiwi-proxy: 9proxy |
| [kiwi-plugin-myst](../clients/providers.md) | v0.5.2 | user | dostawca kiwi-proxy: Mysterium |

kiwi synchronizuje katalog przed każdym sprawdzeniem i aktualizacją, więc
zarządzanie flotą komputerów to po prostu git:

- **dodanie aplikacji**: dodaj jej URL do `apps.list` i zrób commit;
- **przypięcie lub wycofanie wersji**: dopisz `ref=<tag>` do jej linii (na
  jednej maszynie to samo robi `kiwi pin <app> <tag>`);
- **usunięcie**: skasuj linię (zainstalowane kopie zostają, dopóki ich nie
  odinstalujesz).

## Własny katalog { #your-own-catalog }

Katalog to repozytorium git z `apps.list` i opcjonalnie `catalog.manifest`,
który go opisuje:

```ini
# catalog.manifest
NAME=my-catalog
DESCRIPTION=What these apps are for
HOMEPAGE=https://…
MAINTAINER=you
```

```
# apps.list: jedna linia na aplikację, nawet gdy ma część root i część użytkownika
https://github.com/derlocke-ng/kiwi-updater.git
https://github.com/you/your-tool.git ref=v1.2.0
```

| Opcja | Znaczenie |
|---|---|
| `branch=<name>` | śledź gałąź zamiast tagów wydań |
| `ref=<tag>` | przypnij dokładną wersję |
| `scope=user\|system` | instaluj tylko tę połowę na maszynach używających tej listy. To *filtr*, a nie deklaracja |

Własna lista maszyny (`~/.config/kiwi-updater/apps.list` albo
`/etc/kiwi-updater/apps.list` dla roota) zawsze wygrywa z katalogiem.
`kiwi add <url>` dodaje do niej linię.

## Publikowanie aplikacji { #publishing-an-app }

Umieść `kiwi.manifest` i `install.sh` w katalogu głównym repozytorium.
Szablony są w [`templates/`](https://github.com/derlocke-ng/kiwi-updater/tree/main/templates)
kiwi-updater.

```ini
NAME=my-tool
DESCRIPTION=Short description
# COMPONENTS: cli gui daemon service gnome-extension config module
COMPONENTS=cli
# SCOPES: user, system albo oba
SCOPES=user
VERSION=0.1.0
HOMEPAGE=https://…
LICENSE=GPL-3.0-or-later
ICON=data/my-tool.svg
INSTALLER=install.sh
```

Inne klucze: `AUTHOR`, `CATEGORY`, `TAGS`, `SCREENSHOTS`, `ABOUT` (plik, który
pokazuje Kiwi Apps), `DEPENDS` i, dla wszystkiego z częścią systemową,
`ROOT_REASON`. `ICON=` to SVG lub PNG o rozmiarze najwyżej 1 MiB wewnątrz
repozytorium. Większość aplikacji Kiwi bierze swoje z
[kiwi-icons](../project/brand.md).

!!! warning "Komentarze w osobnej linii"
    Wartość biegnie do końca linii. `COMPONENTS=cli  # … gui …` czyni komentarz
    częścią wartości, a aplikacja jest wtedy traktowana tak, jakby miała GUI.

kiwi uruchamia twój instalator raz **dla każdego zadeklarowanego zakresu**, z:

| Zmienna | Wartość |
|---|---|
| `KIWI_SCOPE` | `user` lub `system` |
| `KIWI_PREFIX` | `~/.local` lub `/usr/local` |
| `KIWI_APP_DIR` | bezwzględna ścieżka klona |
| `KIWI_ACTION` | `install`, `update` lub `uninstall` |
| `KIWI_GUI` | `0` na maszynie bez interfejsu graficznego lub z `--cli-only` |
| `KIWI_PURGE` | `1`, gdy użytkownik poprosił o `--purge` |
| `PATH` | najpierw `$KIWI_PREFIX/bin`; stała ścieżka systemowa dla zakresu system |

Instalator z dwoma zakresami rozgałęzia się według `KIWI_SCOPE` i za każdym
razem robi tylko tę połowę. Bez `--purge` zostaw konfigurację użytkownika
tam, gdzie jest.

**Wydawaj z podpisanym tagiem**, żeby część systemowa aktualizowała się bez
hasła:

```bash
git config gpg.format ssh            # podpisuj swoim kluczem SSH
git tag -s v1.3.0 -m v1.3.0 && git push origin v1.3.0
```

`templates/release.yml` z kiwi-updater publikuje wydanie na GitHubie tylko
dla tagu podpisanego kluczem z `.github/allowed_signers` i nigdy sam nie
tworzy tagów. Potem otwórz pull request dodający twój URL do katalogu.
Wszystko, co jest open source i naprawdę używalne bez konta, subskrypcji czy
trackera, jest mile widziane.

## Zaufanie { #trust }

Katalog jest **kuratorowany, a nie audytowany**. Obecność na liście oznacza,
że ktoś uznał aplikację za wartą posiadania, a nie że jej kod został
przejrzany. Przeczytaj `kiwi info <app>`, zanim zainstalujesz coś, czego
jeszcze nie znasz, i `kiwi info --installer <app>`, żeby zobaczyć dokładnie,
co zostanie uruchomione.
