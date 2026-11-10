# kiwi-updater

kiwi-updater instaluje na twoim desktopie aplikacje open source i dba o to,
żeby były aktualne. Jego polecenie to `kiwi`. Aplikacje pobiera z **katalogów
aplikacji w gicie** i działa na Fedorze Silverblue, Bluefinie i innych
systemach ostree. Katalog aplikacji to repozytorium git z listą aplikacji.
Aplikacja to repozytorium git z plikiem `kiwi.manifest` i skryptem
`install.sh`. kiwi klonuje repozytorium aplikacji, przełącza się na jej
najnowszy tag wydania i uruchamia jej instalator. Potem aktualizuje aplikację
w tle i w ten sam sposób aktualizuje też samego siebie.

Nie potrzebujesz konta, nie ma tu sklepu z aplikacjami ani żadnego dostawcy.
Katalog to repozytorium, które możesz przeczytać, sforkować i do którego
możesz wysłać pull request.

- Repozytorium: [derlocke-ng/kiwi-updater](https://github.com/derlocke-ng/kiwi-updater), GPL-3.0-or-later
- Najnowsze wydanie: **v2.4.0**, wydanie z poprawkami bezpieczeństwa
- **`kiwi`** to narzędzie wiersza poleceń (CLI). Potrzebuje `git`, coreutils,
  `util-linux` i `awk`, a wszystko to jest w obrazie bazowym. Do sprawdzania
  podpisów potrzebuje też `ssh-keygen`.
- **Kiwi Apps** (`kiwi-gui`) to aplikacja desktopowa napisana w GTK4. Możesz
  w niej wyszukiwać i filtrować aplikacje, a każda ma widok szczegółów z ikoną,
  zrzutami ekranu i zależnościami. Przed instalacją Kiwi Apps pokazuje ci
  instalator, a przed aktualizacją to, co aktualizacja zmieni. Gdy klikniesz
  kilka działań po kolei, ustawia je w kolejce. Dane pobiera z CLI. Ikony
  i zrzuty ekranu czyta z lokalnych klonów aplikacji, więc żeby je pokazać,
  niczego nie pobiera.

## Instalacja { #install }

kiwi działa w dwóch zakresach. Zakres użytkownika obejmuje wszystko w twoim
folderze domowym i nigdy nie wymaga roota. Zakres systemowy to część należąca
do roota, przeznaczona dla aplikacji, które potrzebują uprawnień roota. Przy
instalacji wybierasz, ile zakresu systemowego chcesz mieć:

```bash
# zalecane: zakres użytkownika plus systemowy, należący do roota; hasło podajesz raz
curl -fsSL https://raw.githubusercontent.com/derlocke-ng/kiwi-updater/main/get-kiwi.sh | bash

# minimalnie: w 100% na poziomie użytkownika, tylko ~/.local, nigdy roota ani hasła
curl -fsSL https://raw.githubusercontent.com/derlocke-ng/kiwi-updater/main/get-kiwi.sh | bash -s -- --minimal

# żadnych działań bez hasła: każda zmiana w systemie pyta o hasło
curl -fsSL https://raw.githubusercontent.com/derlocke-ng/kiwi-updater/main/get-kiwi.sh | bash -s -- --with-system=manual
```

Instalacja rejestruje [katalog Kiwi](catalogs.md), więc od razu możesz
uruchomić `kiwi list` albo otworzyć **Kiwi Apps**.

Niektóre aplikacje składają się wyłącznie z plików w twoim folderze domowym,
np. narzędzia CLI, ensconce i syncman. Po minimalnej instalacji są one
kompletne. Aplikacja z częścią działającą jako root, taka jak kiwi-killswitch,
potrzebuje zakresu systemowego. Po minimalnej instalacji polecenie
`kiwi install kiwi-killswitch` konfiguruje zakres systemowy właśnie w tym
momencie i raz pyta o hasło.

## Polecenia { #commands }

```bash
kiwi list [--check]          # wszystkie aplikacje znane tej maszynie
kiwi search vpn              # szuka aplikacji we wszystkich zarejestrowanych katalogach
kiwi info kiwi-killswitch    # co to jest, co instaluje, czy potrzebuje roota
kiwi install <app>           # nazwa albo jawnie --all
kiwi update [<app>]          # wszystko, co ma nowe wydanie
kiwi uninstall <app>         # --purge usuwa też jej konfigurację
kiwi check                   # kod wyjścia 10, jeśli cokolwiek ma aktualizację

kiwi add <https-url>         # śledzi jedno repozytorium bezpośrednio, bez katalogu
kiwi catalog add|list|remove # zarządzanie katalogami
kiwi sync                    # odświeża katalogi od razu
kiwi self-update
kiwi trust --system <app>    # zapomina klucz podpisujący przypięty do aplikacji systemowej
```

Te polecenia pokazują, co aplikacja zrobi, zanim ją uruchomisz, i pomagają,
gdy coś pójdzie nie tak:

```bash
kiwi info --installer <app>  # skrypt, który uruchomiłaby instalacja, zanim zostanie uruchomiony
kiwi diff <app>              # co zmieniłaby aktualizacja, łącznie z instalatorem
kiwi pin <app> v1.2.0        # zostaje na tej wersji; kiwi unpin <app> znów śledzi wydania
kiwi install <app> --dry-run # zakres, URL, ref, ścieżka instalatora i nic poza tym
kiwi doctor                  # stare blokady, rozbieżne wersje, błędne pliki list, timery
```

## Wydania to tagi { #releases-are-tags }

kiwi traktuje tagi git jako wydania. Aplikacja śledzi swój najnowszy **tag
wersji**, czyli tag pasujący do wzorca `^v?[0-9]+(\.[0-9]+){0,3}$`, np. `v1`,
`v1.2`, `1.2.3` albo `v1.2.3.4`. Tagi wersji przedpremierowych i tagi
tymczasowe do niego nie pasują, więc nigdy nie zostaną użyte zamiast wydania.
Repozytorium bez tagu wersji śledzi swoją domyślną gałąź. Żeby wybrać jedną
konkretną wersję, dopisz `ref=<tag>` do wiersza aplikacji na liście.

## Zależności { #dependencies }

Wiersz `DEPENDS=` w manifeście wymienia, czego aplikacja potrzebuje. Jeśli
słowo w tym wierszu jest nazwą aplikacji z twojego katalogu lub twojej listy,
kiwi instaluje tę aplikację **najpierw**, w tym samym zakresie, w chwili, gdy
instalujesz aplikację, która jej potrzebuje. Na przykład
`kiwi install kiwi-plugin-tor` instaluje także kiwi-proxy. Każde inne słowo kiwi
traktuje jako nazwę programu i sprawdza poleceniem `command -v`, czy ten program
jest w systemie.

## Jedna aplikacja, dwie części { #one-app-two-halves }

Niektóre aplikacje to tylko jeden program w `~/.local/bin`. Inne, np. kill
switch dla VPN, składają się z demona działającego jako root **oraz** aplikacji
desktopowej **oraz** rozszerzenia GNOME. Taka aplikacja ma dwie części: część
użytkownika i część systemową, a każda z nich jest instalowana z innymi
uprawnieniami. Powód jest prosty: **root nie może nigdy uruchomić pliku, który
użytkownik może zmienić**. Aplikacja deklaruje swoje składniki i zakresy
w manifeście:

```ini
COMPONENTS=daemon cli gui gnome-extension
SCOPES=user system
ROOT_REASON=installs a root firewall daemon, its D-Bus policy and two systemd units
```

Katalog wymienia taką aplikację tylko raz, a kiwi instaluje każdą część
w odpowiednim zakresie. Zanim kiwi poprosi o hasło, pokazuje ci `ROOT_REASON`.

| Element | Gdzie | Dlaczego |
|---|---|---|
| `kiwi`, Kiwi Apps, aplikacje użytkownika | `~/.local` | nie wymaga roota i zostaje na miejscu, gdy system przechodzi (rebase) na inny obraz ostree |
| własna kopia kiwi należąca do roota | `/usr/local/bin`, sklonowana do `/var/lib/kiwi-updater/repos/` | root nigdy nie uruchamia pliku, który ty możesz zmienić |
| aplikacje systemowe | `/var/lib`, `/etc` | w systemach ostree te foldery są zapisywalne i należą do roota |
| listy | `~/.config/kiwi-updater/apps.list`, `/etc/kiwi-updater/apps.list` | wpisy na własnej liście maszyny mają pierwszeństwo przed każdym katalogiem |
| przypięte klucze podpisujące | `/etc/kiwi-updater/signers/<app>` | patrz następna sekcja |

kiwi nigdy niczego nie zmienia w niezmiennym `/usr`.

## Root, hasła i podpisy { #root-passwords-and-signatures }

Tabela pokazuje, które działania wymagają roota i które pytają o hasło.

| | Wymaga roota | Pyta o hasło |
|---|---|---|
| wszystko w zakresie użytkownika | nie | nie |
| **aktualizacja** aplikacji systemowej | tak | **nie**, jeśli wydanie jest podpisane kluczem, który root przypiął do tej aplikacji. **Tak**, jeśli wydanie nie jest podpisane, i zawsze w trybie `manual` |
| **instalacja** lub **odinstalowanie** aplikacji systemowej | tak | tak |

Od wersji 2.4.0 obowiązują te zasady:

- **Podpisane wydania.** Dla każdej aplikacji systemowej root przypina jeden
  klucz podpisujący SSH. Przypiąć klucz to zapamiętać go i od tej pory
  akceptować tylko ten klucz. Root przypina pierwszy klucz, który zobaczy dla
  danej aplikacji (zasada trust on first use, czyli zaufanie przy pierwszym
  użyciu). Jeśli tag wydania jest podpisany przypiętym kluczem, aktualizacja
  instaluje się bez hasła. Jeśli wydanie nie jest podpisane, kiwi pyta o hasło
  i informuje, że nie mogło zweryfikować wydania. kiwi odrzuca tag podpisany
  innym kluczem, a także tag niepodpisany, jeśli wcześniejsze tagi były
  podpisane. Odrzuca je, dopóki nie uruchomisz `kiwi trust --system <app>`.
  Te zasady dotyczą zakresu systemowego.
- **Root instaluje tylko ze źródeł, które sam ma na liście.** Te źródła to
  `/etc/kiwi-updater/apps.list` i katalogi zarejestrowane dla roota. Jeśli
  aplikacja pochodzi z innego źródła, kiwi instaluje tylko część użytkownika
  i podaje polecenie `kiwi add --system <https-url>`, które musisz uruchomić.
  Kiwi Apps oferuje w takiej sytuacji przycisk *Register and Install*, który
  rejestruje źródło dla roota i instaluje aplikację.
- **Tylko https.** kiwi wszędzie odrzuca źródła `http://`.

Aktualizacje systemowe bez hasła wykonuje jeden program pomocniczy,
`/usr/local/libexec/kiwi-system-update`, który służy tylko do tego. Reguła
polkit pozwala go uruchamiać użytkownikom z grupy `wheel`, gdy ich sesja jest
aktywna. Program pomocniczy przyjmuje wyłącznie nazwy aplikacji, a nazwa może
wskazać tylko aplikację z list samego roota.

## Aktualizacje w tle { #background-updates }

Aktualizacje w tle uruchamia jeden timer i jest to timer użytkownika, więc
działa z uprawnieniami twojego użytkownika, a nie roota. `kiwi-updater.timer`
uruchamia `kiwi update --all` sześć godzin po poprzednim przebiegu oraz
dziesięć minut po starcie systemu, z niewielkim losowym opóźnieniem. Ten
przebieg aktualizuje części użytkownika bezpośrednio, a części systemowe przez
opisany wyżej program pomocniczy. Timera roota nie ma. W trybie `manual` timer
nie aktualizuje części systemowych. Czekają one, aż sam uruchomisz
`kiwi update`.

## Zaufanie { #trust }

Gdy instalujesz aplikację, kiwi **uruchamia skrypt `install.sh`
z repozytorium tej aplikacji**. Jeśli aplikacja deklaruje zakres systemowy,
kiwi uruchamia ten skrypt **jako root**. Katalogi są wybierane ręcznie, ale nie
audytowane. Oznacza to, że ktoś wybrał te aplikacje, a nie że ktoś przejrzał
ich kod. Dodawaj tylko katalogi, którym ufasz, tak samo jak dodajesz
repozytorium pakietów. Zanim zdecydujesz, sprawdź, co robi aplikacja, za
pomocą `kiwi info --installer`, `kiwi diff` i `kiwi pin`. Podpis ogranicza to,
*kto może opublikować* wydanie. Nie mówi nic o tym, *co opublikowane wydanie
robi*.

Jedna rzecz jest jeszcze planowana: hostowany rejestr zaufanych katalogów,
z poleceniem `kiwi catalog browse` i z odciskami kluczy osób podpisujących dla
każdej pozycji.
