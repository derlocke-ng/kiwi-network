# kiwi-updater

`kiwi` instaluje i aktualizuje aplikacje open source z **katalogów git** na
Fedora Silverblue, Bluefin i innych systemach ostree. Aplikacja to
repozytorium git z `kiwi.manifest` i `install.sh`. kiwi je klonuje, przełącza
się na jego najnowszy tag wydania, uruchamia jego instalator i aktualizuje go
w tle, łącznie z samym sobą.

Nie ma kont, sklepu ani dostawcy. Katalog to repozytorium, które możesz
przeczytać, sforkować i wysłać do niego pull request.

- Repozytorium: [derlocke-ng/kiwi-updater](https://github.com/derlocke-ng/kiwi-updater), GPL-3.0-or-later
- Najnowsze wydanie: **v2.4.0**, wydanie bezpieczeństwa
- **`kiwi`** to CLI. Potrzebuje `git`, coreutils, `util-linux` i `awk`,
  wszystkie w obrazie bazowym, plus `ssh-keygen` do sprawdzania podpisów.
- **Kiwi Apps** (`kiwi-gui`) to aplikacja GTK4: wyszukiwanie, filtry, widok
  szczegółów każdej aplikacji z ikoną, zrzutami ekranu i zależnościami.
  Pokazuje instalator i diff aktualizacji, zanim uruchomi którekolwiek z nich,
  i kolejkuje twoje kliknięcia. Dane pochodzą z CLI; ikony i zrzuty ekranu są
  odczytywane z klonów aplikacji, więc nic nie jest dla nich pobierane.

## Instalacja { #install }

```bash
# zalecane: zakres użytkownika plus należący do roota zakres systemowy, jedno pytanie o hasło
curl -fsSL https://raw.githubusercontent.com/derlocke-ng/kiwi-updater/main/get-kiwi.sh | bash

# minimalne: 100 % na poziomie użytkownika, tylko ~/.local, nigdy bez roota i bez hasła
curl -fsSL https://raw.githubusercontent.com/derlocke-ng/kiwi-updater/main/get-kiwi.sh | bash -s -- --minimal

# żadnych działań bez hasła: każda zmiana systemowa pyta o hasło
curl -fsSL https://raw.githubusercontent.com/derlocke-ng/kiwi-updater/main/get-kiwi.sh | bash -s -- --with-system=manual
```

[Katalog Kiwi](catalogs.md) jest rejestrowany przy instalacji. Przejdź od razu
do `kiwi list` albo otwórz **Kiwi Apps**.

Aplikacje, które są tylko plikami w twoim katalogu domowym (narzędzia CLI,
ensconce, syncman), są kompletne przy instalacji minimalnej. Aplikacja z
częścią root, taka jak kiwi-killswitch, potrzebuje zakresu systemowego. Przy
instalacji minimalnej `kiwi install kiwi-killswitch` konfiguruje go na
miejscu, z jednym hasłem.

## Polecenia { #commands }

```bash
kiwi list [--check]          # każda aplikacja, o której wie ta maszyna
kiwi search vpn              # znajdź aplikację w każdym zarejestrowanym katalogu
kiwi info kiwi-killswitch    # co to jest, co instaluje, czy potrzebuje roota
kiwi install <app>           # nazwa albo jawne --all
kiwi update [<app>]          # wszystko z nowym wydaniem
kiwi uninstall <app>         # --purge usuwa też jej konfigurację
kiwi check                   # kod wyjścia 10, jeśli cokolwiek ma aktualizację

kiwi add <https-url>         # śledź jedno repozytorium bezpośrednio, bez katalogu
kiwi catalog add|list|remove # zarządzaj katalogami
kiwi sync                    # odśwież katalogi teraz
kiwi self-update
kiwi trust --system <app>    # zapomnij klucz podpisu przypięty dla aplikacji systemowej
```

Zanim coś uruchomisz i gdy coś pójdzie nie tak:

```bash
kiwi info --installer <app>  # skrypt, który uruchomiłaby instalacja, zanim się uruchomi
kiwi diff <app>              # co zmieniłaby aktualizacja, łącznie z instalatorem
kiwi pin <app> v1.2.0        # zostań przy tej wersji; kiwi unpin <app>, żeby znów śledzić wydania
kiwi install <app> --dry-run # zakres, URL, ref, ścieżka instalatora i nic więcej
kiwi doctor                  # stare blokady, rozjazd wersji, złe pliki list, timery
```

## Wydania to tagi { #releases-are-tags }

Aplikacja śledzi swój najnowszy **tag wersji**, pasujący do
`^v?[0-9]+(\.[0-9]+){0,3}$` (`v1`, `v1.2`, `1.2.3`, `v1.2.3.4`). Wydania
wstępne i robocze tagi nigdy nie wyprzedzają wydania. Repozytorium bez tagu
wersji śledzi swoją domyślną gałąź. `ref=<tag>` w linii listy prosi o
konkretny tag.

## Zależności { #dependencies }

`DEPENDS=` w manifeście wymienia, czego aplikacja potrzebuje. Słowo, które
jest aplikacją w twoim własnym katalogu lub liście, jest instalowane
**najpierw**, w tym samym zakresie, w czasie instalacji. Na przykład
`kiwi install kiwi-plugin-tor` przynosi ze sobą kiwi-proxy. Każde inne słowo
to program, sprawdzany przez `command -v`.

## Jedna aplikacja, dwie połowy { #one-app-two-halves }

Niektóre aplikacje to tylko plik binarny w `~/.local/bin`. Inne, jak kill
switch VPN, to demon roota **i** aplikacja desktopowa **i** rozszerzenie
GNOME. Połowy instalują się z różnymi uprawnieniami, bo **root nigdy nie może
wykonać pliku, który użytkownik może zapisać**. Aplikacja to deklaruje:

```ini
COMPONENTS=daemon cli gui gnome-extension
SCOPES=user system
ROOT_REASON=installs a root firewall daemon, its D-Bus policy and two systemd units
```

Katalog wymienia taką aplikację raz, a kiwi poprawnie instaluje każdą połowę.
Zanim poprosi o twoje hasło, pokazuje `ROOT_REASON`.

| Element | Gdzie | Dlaczego |
|---|---|---|
| `kiwi`, Kiwi Apps, aplikacje użytkownika | `~/.local` | root niepotrzebny; przetrwa rebase ostree |
| własna kopia kiwi roota | `/usr/local/bin`, sklonowana do `/var/lib/kiwi-updater/repos/` | root nigdy nie uruchamia pliku, który możesz zapisać |
| aplikacje systemowe | `/var/lib`, `/etc` | zapisywalne na ostree, należące do roota |
| listy | `~/.config/kiwi-updater/apps.list`, `/etc/kiwi-updater/apps.list` | własne wpisy maszyny wygrywają z każdym katalogiem |
| przypięte klucze podpisu | `/etc/kiwi-updater/signers/<app>` | zobacz niżej |

Niezmienne `/usr` nigdy nie jest dotykane.

## Root, hasła i podpisy { #root-passwords-and-signatures }

| | Wymaga roota | Pyta o hasło |
|---|---|---|
| wszystko w zakresie użytkownika | nie | nie |
| **aktualizacja** aplikacji systemowej | tak | **nie** dla wydania podpisanego kluczem, który root przypiął dla tej aplikacji. **Tak** dla niepodpisanego wydania i zawsze w trybie `manual` |
| **instalacja** lub **odinstalowanie** aplikacji systemowej | tak | tak |

Od 2.4.0:

- **Podpisane wydania.** Root przypina jeden klucz podpisu SSH na aplikację
  systemową, pierwszy, jaki zobaczy (zaufanie przy pierwszym użyciu). Tag
  wydania podpisany tym kluczem aktualizuje się bez hasła. Niepodpisane
  wydanie pyta o hasło i mówi, że nie mogło go zweryfikować. Tag podpisany
  innym kluczem albo niepodpisany tag po podpisanych jest odrzucany, dopóki
  nie uruchomisz `kiwi trust --system <app>`. Dotyczy to zakresu systemowego.
- **Root instaluje tylko źródła, które sam ma na liście**:
  `/etc/kiwi-updater/apps.list` i katalogi zarejestrowane dla roota. Dla
  wszystkiego innego kiwi instaluje połowę użytkownika i podaje polecenie
  `kiwi add --system <https-url>` do uruchomienia. Kiwi Apps oferuje
  *Register and Install*.
- **Tylko https.** Źródła `http://` są wszędzie odrzucane.

Aktualizacje systemowe bez hasła przechodzą przez jeden pomocnik o stałym
przeznaczeniu, `/usr/local/libexec/kiwi-system-update`. Reguła polkit
zezwala na niego aktywnym sesjom `wheel`, a nazwy aplikacji przyjmuje tylko
jako wybór z własnych list roota.

## Aktualizacje w tle { #background-updates }

Jest jeden timer i jest twój: `kiwi-updater.timer` uruchamia
`kiwi update --all` sześć godzin po ostatnim uruchomieniu (dziesięć minut po
starcie, z pewnym losowym opóźnieniem). Aktualizuje połowy użytkownika
bezpośrednio, a połowy systemowe przez powyższy pomocnik. Nie ma timera roota.
W trybie `manual` połowy systemowe czekają na twoje następne interaktywne
`kiwi update`.

## Zaufanie { #trust }

Instalacja aplikacji **uruchamia `install.sh` z tego repozytorium**, a
aplikacja, która deklaruje zakres systemowy, uruchamia go **jako root**.
Katalogi są kuratorowane, a nie audytowane. Dodawaj te, którym ufasz, tak jak
dodaje się repozytorium pakietów, i używaj `kiwi info --installer`, `kiwi diff`
i `kiwi pin`, żeby decydować z otwartymi oczami. Podpis zawęża to, *kto może
publikować*. Nic nie mówi o tym, *co robi opublikowana rzecz*.

Nadal w planach: hostowany rejestr zaufanych katalogów (`kiwi catalog browse`)
z odciskami kluczy podpisujących dla każdego wpisu.
