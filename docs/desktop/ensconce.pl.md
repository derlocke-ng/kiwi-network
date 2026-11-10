# ensconce

ensconce konfiguruje za ciebie świeżo zainstalowanego
[Bluefina-DX](https://projectbluefin.io/), więc nie musisz ustawiać każdej nowej
maszyny ręcznie. Opisujesz swoją stację roboczą w prostych plikach z listami,
a ensconce zamienia świeżą instalację w tę stację roboczą. Zajmuje się
nakładanymi pakietami, Flatpakami, rozszerzeniami GNOME, synchronizacją
z Nextcloudem, konfiguracją SSH synchronizowaną między twoimi maszynami,
ustawieniami pulpitu i ekranu logowania oraz twoimi aplikacjami Kiwi. Pakiety
nakładane (layered) to pakiety RPM dodawane na wierzch obrazu systemu.
Konfiguracja jest modułowa: składa się z osobnych kroków, które możesz
uruchomić albo pominąć.

- Repozytorium: [derlocke-ng/ensconce](https://github.com/derlocke-ng/ensconce).
  Według manifestu licencja to GPL-3.0-or-later, a według README GPL-3.0.
- Najnowsze wydanie: **v2.5.0**. Jest w [katalogu Kiwi](catalogs.md)
  i instaluje się w zakresie użytkownika, czyli w twoim folderze domowym.

```bash
kiwi install ensconce
ensconce --init          # tworzy ~/.config/ensconce z przykładów
ensconce                 # uruchamia konfigurację
```

Możesz go też uruchomić z klona repozytorium. Uruchom `./ensconce.sh --init`,
zmień pliki w `config/`, a potem uruchom `./ensconce.sh`.

## Kroki { #steps }

Konfiguracja jest podzielona na kroki. Każdy krok to skrypt w `steps/`, a kroki
wykonują się w tej kolejności:

| # | Krok | Co robi |
|---|---|---|
| 01 | `rebase` | przełącza system na Bluefina-DX |
| 02 | `ujust` | konfiguruje grupy dla programistów i narzędzia CLI |
| 03 | `repos` | dodaje repozytoria RPM |
| 04 | `packages` | nakłada pakiety RPM |
| 05 | `flatpaks` | instaluje aplikacje Flatpak. `FLATPAK_LANGUAGES` wybiera języki ich tłumaczeń |
| 06 | `overrides` | ustawia nadpisania uprawnień Flatpaków |
| 07 | `extensions` | instaluje rozszerzenia GNOME Shell |
| 08 | `cacert` | instaluje własne certyfikaty CA |
| 09 | `nextcloud` | z góry konfiguruje synchronizację folderów z Nextcloudem |
| 10 | `dconf` | wprowadza ustawienia pulpitu GNOME |
| 11 | `gdm` | konfiguruje ekran logowania |
| 12 | `ssh` | konfiguruje synchronizowaną konfigurację SSH, z Bitwardenem albo GNOME jako agentem SSH |
| 13 | `kiwi` | instaluje kiwi-updater w sposób wybrany przez `KIWI_INSTALL=recommended\|manual\|minimal`, a potem każdą aplikację z `kiwi-apps.list` |
| 14 | `sysctl` | instaluje pliki z ustawieniami jądra z `sysctl.d/`. Przykładowy plik ogranicza ilość niezapisanych danych, które jądro trzyma w pamięci, co pomaga na wolnych dyskach SSD |
| 15 | `power` | przy `SYSTEM_SLEEP=off` maskuje cele uśpienia, więc maszyna nie może przejść w stan uśpienia |

Przed startem ensconce sprawdza środowisko. System musi być obrazem Bluefin,
a `rpm-ostree`, `flatpak`, `dconf`, `jq` i `curl` muszą być dostępne. ensconce
zapisuje postęp, więc po ponownym uruchomieniu komputera wznawia pracę od miejsca,
w którym ją przerwał. Przez cały przebieg nie pozwala maszynie zasnąć, a na koniec
przywraca twoje ustawienia zasilania.

Przebiegiem sterują te opcje:

```bash
ensconce --dry-run                  # podgląd bez żadnych zmian
ensconce --skip rebase,ujust        # pomija kroki
ensconce --only extensions,dconf    # uruchamia tylko te
ensconce --status | --list-steps | --reset
ensconce --log [file]               # zapisuje wynik
ensconce --config-dir               # wypisuje używany folder konfiguracji
```

## Konfiguracja { #configuration }

ensconce szuka swojego folderu konfiguracji w czterech miejscach i używa
pierwszego, które istnieje. Najpierw sprawdza `$ENSCONCE_CONFIG`, potem
`~/.config/ensconce/`, używany wtedy, gdy ensconce zainstalowano przez kiwi,
potem `config/` w klonie, a na końcu `config.example/`. Gdy używa
`config.example/`, wypisuje ostrzeżenie.

| Plik / folder | Do czego służy |
|---|---|
| `settings.sh` | adresy URL serwerów oraz przełączniki dla SSH, kiwi-updater, języków Flatpaków i usypiania |
| `packages.list`, `flatpaks.list`, `extensions.list` | pakiety, Flatpaki i rozszerzenia GNOME do zainstalowania, po jednym w wierszu |
| `kiwi-apps.list` | aplikacje Kiwi do zainstalowania |
| `repos.d/`, `flatpak-overrides/` | pliki repozytoriów i nadpisania dla poszczególnych aplikacji we własnym formacie Flatpaka |
| `nextcloud/folders.list` | foldery do synchronizacji, w zapisie `localPath\|remotePath[\|tags]` |
| `nextcloud/exclude.lst`, `exclude.d/` | co jest wyłączone z synchronizacji, dla wszystkich folderów i dla poszczególnych folderów z tagiem |
| `certs/` | certyfikaty CA (`.pem`), np. `kiwiCA.pem` twojej sieci |
| `sysctl.d/` | ustawienia jądra |
| `dconf-settings.ini`, `gtk3-bookmarks` | ustawienia GNOME i zakładki Nautilusa |
| `gdm/dconf.d/`, `gdm/monitors.xml` | ustawienia i układ ekranów ekranu logowania |

Tag w `nextcloud/folders.list` nadaje folderowi własne wyłączenia. Na przykład
tag `browser` umieszcza w tym folderze `exclude.d/browser.lst`. Bazy danych
profilu przeglądarki nie są wtedy synchronizowane, bo synchronizacja mogłaby
je uszkodzić, a `user.js` nadal jest synchronizowany.

## Klonowanie maszyny { #cloning-a-machine }

`--export` działa odwrotnie niż kroki. Odczytuje działający system i zapisuje
na jego podstawie folder konfiguracji ensconce. Tym folderem możesz potem
skonfigurować nową maszynę:

```bash
ensconce --export ./my-setup        # na skonfigurowanej maszynie
ensconce --init                     # na nowej
cp -rT ./my-setup "$(ensconce --config-dir)"
ensconce --dry-run && ensconce
```

Eksport zawiera tylko twoje własne dodatki do systemu. Wymienia pakiety
zainstalowane na twoje życzenie, a nie cały obraz. Wymienia tylko rozszerzenia, które
naprawdę pochodzą z extensions.gnome.org. Zawiera twoje własne pliki
repozytoriów oraz wybrane poddrzewa dconf zamiast pełnego zrzutu. Traktuj
eksport jako punkt wyjścia. `certs/` i `nextcloud/` mogą zawierać prywatne
dane.

ensconce to aplikacja działająca w **zakresie użytkownika**. Kroki, które
potrzebują roota, same o niego proszą. Żeby dodać własny krok, utwórz plik
`steps/NN-<name>.sh` z funkcją `step_<name>()`.
