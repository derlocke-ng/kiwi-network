# kiwi-updater

kiwi-updater instaluje na twoim komputerze aplikacje open source i dba o to,
żeby były aktualne. Jego polecenie to `kiwi`. Aplikacje pobiera z **katalogów
aplikacji w gicie**. Katalog aplikacji to repozytorium git z listą aplikacji, a
aplikacja to repozytorium git z plikiem `kiwi.manifest` i skryptem
`install.sh`. kiwi klonuje aplikację, przełącza się na jej najnowszy tag
wydania i uruchamia jej instalator. Potem aktualizuje aplikację w tle i w ten
sam sposób aktualizuje też samego siebie.

Nie potrzebujesz konta, nie ma tu sklepu z aplikacjami ani producenta. Katalog
to repozytorium, które możesz przeczytać, sforkować i do którego możesz wysłać
pull request. W ten sposób instaluje się wszystkie desktopowe aplikacje Kiwi.

- Repozytorium: [derlocke-ng/kiwi-updater](https://github.com/derlocke-ng/kiwi-updater), GPL-3.0-or-later
- Najnowsze wydanie: **v2.5.1**
- **`kiwi`** to narzędzie wiersza poleceń. **Kiwi Apps** (`kiwi-gui`) to
  aplikacja desktopowa. Możesz w niej przeglądać i wyszukiwać aplikacje,
  instalować je i przeczytać instalator aplikacji, zanim zostanie uruchomiony.

## Na jakich systemach działa { #where-it-runs }

Narzędzie kiwi-updater powstało z myślą o Fedora Atomic Desktops, a dziś działa
też w innych dystrybucjach Linuksa. Każdą zmianę w kiwi-updater testuje się na
tych systemach pełnym zestawem testów i prawdziwą instalacją:

| System | Co działa |
|---|---|
| Fedora Silverblue, Bluefin, Fedora, Debian 13, Ubuntu 24.04, Arch, openSUSE Tumbleweed | wszystko |
| Alpine | wszystko, po zainstalowaniu narzędzi GNU |
| Debian 12, Ubuntu 22.04 (testowane, ale nie przy każdej zmianie) | `kiwi` i aplikacje wiersza poleceń. Biblioteka libadwaita w tych systemach jest za stara dla aplikacji desktopowych |

## Instalacja { #install }

To polecenie instaluje część użytkownika w twoim folderze domowym i część roota
dla aplikacji, które potrzebują roota. Hasło podajesz tylko raz:

```bash
curl -fsSL https://raw.githubusercontent.com/derlocke-ng/kiwi-updater/main/get-kiwi.sh | bash
```

Jeśli nie chcesz niczego poza folderem domowym i nie chcesz, żeby kiedykolwiek
pytano cię o hasło, zainstaluj tylko część użytkownika:

```bash
curl -fsSL https://raw.githubusercontent.com/derlocke-ng/kiwi-updater/main/get-kiwi.sh | bash -s -- --minimal
```

Instalator sprawdza, czy instalowane wydanie jest podpisane kluczem, którym
kiwi-updater podpisuje swoje wydania. Wydania bez takiego podpisu nie
zainstaluje. Podczas instalacji rejestrowany jest też katalog Kiwi. Potem
możesz zacząć:

```bash
kiwi list                    # wszystkie aplikacje, które możesz zainstalować
kiwi install <app>           # zainstaluj jedną z nich
kiwi info --installer <app>  # przeczytaj jej instalator, zanim zostanie uruchomiony
kiwi-gui                     # aplikacja desktopowa
```

## Części roota i podpisane wydania { #root-parts-and-signed-releases }

Niektóre aplikacje potrzebują roota, na przykład kiwi-killswitch, który ma
demona zapory sieciowej. Ich część roota instaluje osobna kopia kiwi należąca
do roota, i to tylko ze źródeł, które root sam ma na liście. Instalacja i
usunięcie takiej aplikacji zawsze wymagają podania hasła. W trybie domyślnym
aktualizacja odbywa się bez hasła tylko wtedy, gdy wydanie jest podpisane
kluczem, który root zapisał dla tej aplikacji.

## Pełna dokumentacja { #the-full-documentation }

Dokumentacja kiwi-updater jest w jego własnym repozytorium:

| Strona | Co opisuje |
|---|---|
| [Instalacja](https://github.com/derlocke-ng/kiwi-updater/blob/main/docs/install.md) | obsługiwane systemy, pakiety dla poszczególnych dystrybucji, tryby instalacji, odinstalowanie |
| [Korzystanie z kiwi](https://github.com/derlocke-ng/kiwi-updater/blob/main/docs/usage.md) | wszystkie polecenia, Kiwi Apps, aktualizacje w tle, ustawienia |
| [Katalogi aplikacji](https://github.com/derlocke-ng/kiwi-updater/blob/main/docs/catalogs.md) | dodawanie katalogów, `apps.list`, przypinanie wersji, zastępowanie wpisów z katalogu |
| [Bezpieczeństwo](https://github.com/derlocke-ng/kiwi-updater/blob/main/docs/security.md) | co działa jako root, kiedy wpisujesz hasło, co sprawdza kiwi |
| [Pisanie aplikacji](https://github.com/derlocke-ng/kiwi-updater/blob/main/docs/app-authors.md) | `kiwi.manifest`, `install.sh`, zależności, ikony, wydania |
| [Podpisane wydania](https://github.com/derlocke-ng/kiwi-updater/blob/main/docs/signing.md) | podpisywanie wydań twojej aplikacji narzędziem `kiwi-release` |
| [Rozwój](https://github.com/derlocke-ng/kiwi-updater/blob/main/docs/development.md) | testy, CI, publikowanie wydań kiwi-updater |

Od następnego wydania kiwi-updater te strony pojawią się też tutaj, w menu pod
kiwi-updater.

Jak opublikować własną aplikację, opisuje strona [Katalogi aplikacji i
publikowanie](catalogs.md).
