# Katalogi aplikacji i publikowanie

Katalog aplikacji to lista aplikacji, które może zainstalować kiwi-updater.
Jest repozytorium git, więc możesz go przeczytać, skopiować i zaproponować
w nim zmiany. Ta strona opisuje katalog Kiwi, pokazuje, jak zrobić własny
katalog, np. dla wszystkich desktopów, którymi się opiekujesz, i wyjaśnia, jak
opublikować aplikację, żeby inni mogli ją zainstalować przez kiwi.

## Katalog Kiwi { #the-kiwi-catalog }

[derlocke-ng/kiwi-catalog](https://github.com/derlocke-ng/kiwi-catalog) to
katalog aplikacji Kiwi Network. Rejestruje się automatycznie, gdy instalujesz
kiwi-updater. Żeby zarejestrować go ręcznie, uruchom
`kiwi catalog add https://github.com/derlocke-ng/kiwi-catalog.git`.

Tabela wymienia aplikacje z katalogu. Kolumna *Zakresy* pokazuje, gdzie
aplikacja jest instalowana. Zakres użytkownika to twój folder domowy. Zakres
systemowy to część należąca do roota.

| Aplikacja | Wydanie | Zakresy | Czym jest |
|---|---|---|---|
| [kiwi-updater](kiwi-updater.md) | v2.4.0 | user | sam program aktualizujący |
| [kiwi-killswitch](kiwi-killswitch.md) | v0.2.3 | user + system | kill switch dla VPN w GNOME. Działa w trybie fail-closed: dopóki VPN nie działa, cały ruch pozostaje zablokowany |
| [ensconce](ensconce.md) | v2.5.0 | user | konfiguruje świeżo zainstalowanego Bluefina-DX |
| [kiwi-cli-tools-desktop](cli-tools.md) | v1.2.1 | user | `pweb`, `select-server`, `tethering`, `torlink` |
| [kiwi-proxy](../clients/kiwi-proxy.md) | v0.7.3 | user | exity dla połączeń SOCKS5 i VPN. Exit to odizolowany kontener w rootless Podmanie |
| [kiwi-fox](../clients/kiwi-fox.md) | v0.7.1 | user | odizolowane tożsamości przeglądarki, które korzystają z exitów kiwi-proxy |
| [kiwi-custodia](../clients/kiwi-custodia.md) | v0.2.3 | user | boxy z dystrybucjami Linuksa (kontenery z dystrybucją Linuksa), których ruch przechodzi wyłącznie przez exit |
| [kiwi-server](../server/index.md) | v2.42.0 | user | narzędzie, którym budujesz własną sieć i nią zarządzasz |
| [syncman](syncman.md) | v0.4.1 | user | synchronizuje foldery w obu kierunkach |
| [gnome-monitor](gnome-monitor.md) | v0.3.2 | user | zapisuje i przełącza układy ekranów w GNOME |
| [kiwi-plugin-tor](../clients/providers.md) | v0.3.0 | user | moduł dostawcy dla kiwi-proxy: Tor |
| [kiwi-plugin-vpn](../clients/providers.md) | v0.2.2 | user | moduł dostawcy dla kiwi-proxy: VPN przez gluetun |
| [kiwi-plugin-9proxy](../clients/providers.md) | v0.2.0 | user | moduł dostawcy dla kiwi-proxy: 9proxy |
| [kiwi-plugin-myst](../clients/providers.md) | v0.5.2 | user | moduł dostawcy dla kiwi-proxy: Mysterium |

Przed każdym sprawdzeniem i każdą aktualizacją kiwi pobiera aktualną wersję
katalogu. Dlatego aplikacjami na wielu desktopach możesz zarządzać samym gitem:

- **Żeby dodać aplikację**, dopisz jej URL do `apps.list` i zrób commit.
- **Żeby przypiąć aplikację do wersji albo cofnąć ją do starszej**, dopisz
  `ref=<tag>` na końcu jej wiersza. Na pojedynczej maszynie to samo robi
  `kiwi pin <app> <tag>`.
- **Żeby usunąć aplikację**, usuń jej wiersz. Już zainstalowane kopie zostają,
  dopóki ich nie odinstalujesz.

## Własny katalog { #your-own-catalog }

Katalog aplikacji to repozytorium git z plikiem `apps.list`. Może też zawierać
plik `catalog.manifest`, w którym katalog opisuje sam siebie:

```ini
# catalog.manifest
NAME=my-catalog
DESCRIPTION=What these apps are for
HOMEPAGE=https://…
MAINTAINER=you
```

```
# apps.list: one line per app, even when it has a root half and a user half
https://github.com/derlocke-ng/kiwi-updater.git
https://github.com/you/your-tool.git ref=v1.2.0
```

Wiersz w `apps.list` może mieć po adresie URL następujące opcje:

| Opcja | Znaczenie |
|---|---|
| `branch=<name>` | śledź gałąź zamiast tagów wydań |
| `ref=<tag>` | zostań dokładnie na tej wersji |
| `scope=user\|system` | na maszynach korzystających z tej listy instaluj tylko tę część aplikacji. Ta opcja jest *filtrem*. Nie określa, jakie zakresy ma aplikacja |

Każda maszyna ma też własną listę: `~/.config/kiwi-updater/apps.list` dla
twojego użytkownika i `/etc/kiwi-updater/apps.list` dla roota. Wpis na
własnej liście maszyny zawsze ma pierwszeństwo przed katalogiem.
`kiwi add <url>` dopisuje wiersz do tej listy.

## Publikowanie aplikacji { #publishing-an-app }

Żeby opublikować aplikację, umieść plik `kiwi.manifest` i skrypt `install.sh`
w głównym folderze swojego repozytorium. Szablony znajdziesz w folderze
[`templates/`](https://github.com/derlocke-ng/kiwi-updater/tree/main/templates)
repozytorium kiwi-updater.

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

Manifest może mieć więcej kluczy: `AUTHOR`, `CATEGORY`, `TAGS`, `SCREENSHOTS`,
`ABOUT` (plik, który pokazuje Kiwi Apps), `DEPENDS` i `ROOT_REASON`. Każda
aplikacja z częścią systemową musi mieć `ROOT_REASON`. `ICON=` wskazuje plik
SVG lub PNG o rozmiarze najwyżej 1 MiB wewnątrz repozytorium. Większość
aplikacji Kiwi bierze ikonę z [kiwi-icons](../project/brand.md).

!!! warning "Komentarze pisz w osobnym wierszu"
    Wartość ciągnie się do końca wiersza. Jeśli napiszesz
    `COMPONENTS=cli  # … gui …`, komentarz stanie się częścią wartości, a kiwi
    potraktuje aplikację tak, jakby miała interfejs graficzny.

kiwi uruchamia twój instalator raz **dla każdego zakresu zadeklarowanego przez
aplikację**. Ustawia dla instalatora te zmienne:

| Zmienna | Wartość |
|---|---|
| `KIWI_SCOPE` | `user` albo `system` |
| `KIWI_PREFIX` | `~/.local` albo `/usr/local` |
| `KIWI_APP_DIR` | ścieżka bezwzględna klonu |
| `KIWI_ACTION` | `install`, `update` albo `uninstall` |
| `KIWI_GUI` | `0` na maszynie bez środowiska graficznego albo przy `--cli-only` |
| `KIWI_PURGE` | `1`, gdy użytkownik zażądał `--purge` |
| `PATH` | `$KIWI_PREFIX/bin` jest na początku. Zakres systemowy dostaje stałą ścieżkę systemową |

Instalator aplikacji z oboma zakresami musi sprawdzać `KIWI_SCOPE` i w każdym
przebiegu wykonywać tylko pracę dla danej części. Jeśli użytkownik nie zażądał
`--purge`, zostaw jego konfigurację tam, gdzie jest.

**Publikuj każde wydanie jako podpisany tag.** Tylko wtedy część systemowa może
się aktualizować bez hasła:

```bash
git config gpg.format ssh            # podpisywanie kluczem SSH
git tag -s v1.3.0 -m v1.3.0 && git push origin v1.3.0
```

kiwi-updater udostępnia workflow wydań, `templates/release.yml`. Publikuje on
wydanie na GitHubie tylko dla tagu podpisanego kluczem wymienionym
w `.github/allowed_signers` i nigdy sam nie tworzy tagów. Na koniec otwórz pull
request, który dopisuje twój URL do katalogu. Mile widziana jest każda
aplikacja, która jest open source i naprawdę daje się używać bez konta,
subskrypcji i śledzenia.

## Zaufanie { #trust }

Katalog jest **wybierany ręcznie, ale nie audytowany**. Aplikacja trafia na
listę, bo ktoś uznał, że warto ją mieć. Nie oznacza to, że ktoś przejrzał jej
kod. Zanim zainstalujesz aplikację, której nie znasz, przeczytaj wynik
`kiwi info <app>`. Uruchom `kiwi info --installer <app>`, żeby zobaczyć
dokładnie, co zostanie uruchomione.
