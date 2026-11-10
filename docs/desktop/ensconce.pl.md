# ensconce

Modułowa konfiguracja poinstalacyjna dla [Bluefin-DX](https://projectbluefin.io/).
ensconce zamienia świeżą instalację Bluefin w twoją skonfigurowaną stację
roboczą na podstawie zwykłych plików z listami: nakładane pakiety, Flatpaki,
rozszerzenia GNOME, synchronizacja Nextcloud, synchronizowana konfiguracja
SSH, ustawienia pulpitu i ekranu logowania oraz twoje aplikacje Kiwi.

- Repozytorium: [derlocke-ng/ensconce](https://github.com/derlocke-ng/ensconce),
  GPL-3.0-or-later (według manifestu; README podaje GPL-3.0)
- Najnowsze wydanie: **v2.5.0**. Jest w [katalogu Kiwi](catalogs.md), zakres użytkownika.

```bash
kiwi install ensconce
ensconce --init          # utwórz ~/.config/ensconce z przykładów
ensconce                 # uruchom konfigurację
```

Albo z klona: `./ensconce.sh --init`, edytuj `config/`, potem `./ensconce.sh`.

## Kroki { #steps }

Każda faza to skrypt w `steps/`, uruchamiany po kolei:

| # | Krok | Robi |
|---|---|---|
| 01 | `rebase` | przełącza na Bluefin-DX |
| 02 | `ujust` | grupy deweloperskie i narzędzia CLI |
| 03 | `repos` | dodaje repozytoria RPM |
| 04 | `packages` | nakłada pakiety RPM |
| 05 | `flatpaks` | instaluje aplikacje Flatpak (`FLATPAK_LANGUAGES` wybiera ich tłumaczenia) |
| 06 | `overrides` | nadpisania uprawnień Flatpak |
| 07 | `extensions` | rozszerzenia GNOME Shell |
| 08 | `cacert` | własne certyfikaty CA |
| 09 | `nextcloud` | wstępnie konfiguruje synchronizację folderów Nextcloud |
| 10 | `dconf` | ustawienia pulpitu GNOME |
| 11 | `gdm` | ekran logowania |
| 12 | `ssh` | synchronizowana konfiguracja SSH, z Bitwarden lub GNOME jako agentem SSH |
| 13 | `kiwi` | instaluje kiwi-updater (`KIWI_INSTALL=recommended\|manual\|minimal`) i każdą aplikację z `kiwi-apps.list` |
| 14 | `sysctl` | pliki drop-in z `sysctl.d/` (przykład ogranicza dirty writeback dla wolnych dysków SSD) |
| 15 | `power` | `SYSTEM_SLEEP=off` maskuje targety uśpienia |

ensconce najpierw sprawdza środowisko (obraz Bluefin, `rpm-ostree`,
`flatpak`, `dconf`, `jq`, `curl`). Zapisuje swój postęp i wznawia pracę po
restartach, a przez cały przebieg nie pozwala maszynie zasnąć i potem
przywraca twoje ustawienia zasilania.

```bash
ensconce --dry-run                  # podgląd bez zmieniania czegokolwiek
ensconce --skip rebase,ujust        # pomiń kroki
ensconce --only extensions,dconf    # uruchom tylko te
ensconce --status | --list-steps | --reset
ensconce --log [file]               # zapisz wynik
ensconce --config-dir               # wypisz aktywny katalog konfiguracji
```

## Konfiguracja { #configuration }

Katalogiem konfiguracji jest pierwszy istniejący z: `$ENSCONCE_CONFIG`,
`~/.config/ensconce/` (instalacja przez kiwi), `config/` w klonie i
`config.example/` (z ostrzeżeniem).

| Plik / katalog | Przeznaczenie |
|---|---|
| `settings.sh` | adresy URL serwerów i przełączniki: SSH, kiwi-updater, języki Flatpak, uśpienie |
| `packages.list`, `flatpaks.list`, `extensions.list` | jedna pozycja na linię |
| `kiwi-apps.list` | aplikacje Kiwi do zainstalowania |
| `repos.d/`, `flatpak-overrides/` | pliki repozytoriów; nadpisania dla poszczególnych aplikacji we własnym formacie Flatpak |
| `nextcloud/folders.list` | foldery synchronizacji jako `localPath\|remotePath[\|tags]` |
| `nextcloud/exclude.lst`, `exclude.d/` | globalne i per-folder (oznaczone tagiem) wykluczenia z synchronizacji |
| `certs/` | certyfikaty CA (`.pem`), na przykład `kiwiCA.pem` twojej floty |
| `sysctl.d/` | ustawienia jądra |
| `dconf-settings.ini`, `gtk3-bookmarks` | ustawienia GNOME, zakładki Nautilusa |
| `gdm/dconf.d/`, `gdm/monitors.xml` | ustawienia i układ ekranów ekranu logowania |

Tag wykluczenia dla folderu, taki jak `browser`, umieszcza
`exclude.d/browser.lst` w tym folderze, co chroni bazy danych profilu
przeglądarki przed synchronizacją (i uszkodzeniem), podczas gdy `user.js` jest
nadal synchronizowany.

## Klonowanie maszyny { #cloning-a-machine }

`--export` odczytuje działający system i zapisuje drzewo konfiguracji
ensconce, odwrotność kroków:

```bash
ensconce --export ./my-setup        # na skonfigurowanej maszynie
ensconce --init                     # na nowej
cp -rT ./my-setup "$(ensconce --config-dir)"
ensconce --dry-run && ensconce
```

Zapisuje tylko to, co zostało dodane: jawnie żądane (requested) pakiety zamiast całego obrazu,
rozszerzenia faktycznie pochodzące z extensions.gnome.org, twoje własne pliki
repozytoriów i wybrane poddrzewa dconf zamiast pełnego zrzutu. Traktuj to jako
punkt wyjścia. `certs/` i `nextcloud/` mogą zawierać prywatne dane.

ensconce to aplikacja w **zakresie użytkownika**. Kroki, które potrzebują
roota, same o niego proszą. Własny krok dodasz jako `steps/NN-<name>.sh` z
funkcją `step_<name>()`.
