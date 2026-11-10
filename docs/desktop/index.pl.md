# Pulpit

Narzędzia desktopowe Kiwi są zbudowane dla **Fedora Atomic desktops**: Fedora
Silverblue i [Bluefin](https://projectbluefin.io/) (zwłaszcza Bluefin-DX). To
systemy oparte na obrazach, z niezmiennym `/usr` i łatwym wycofywaniem zmian.
Nie ma specjalnego obrazu Kiwi: instalujesz standardowy i dodajesz na nim trzy
warstwy.

1. **[kiwi-updater](kiwi-updater.md)** instaluje i aktualizuje aplikacje z
   katalogów git: wszystko w twoim katalogu domowym, plus część należącą do
   roota tylko dla aplikacji, które jej potrzebują. Aktualizuje też sam siebie.
2. **[ensconce](ensconce.md)** konfiguruje świeży Bluefin-DX ze zwykłych
   plików z listami: pakiety, Flatpaki, rozszerzenia GNOME, synchronizacja
   Nextcloud, SSH, sysctl i ustawienia zasilania, ekran logowania i twoje
   aplikacje Kiwi. `--export` klonuje maszynę.
3. **Aplikacje**, z [katalogu Kiwi](catalogs.md):

| Aplikacja | Co robi |
|---|---|
| [kiwi-killswitch](kiwi-killswitch.md) | Kill switch VPN dla GNOME, który w razie awarii blokuje ruch (fail-closed) |
| [Sieci klientów](../clients/index.md): kiwi-proxy, kiwi-custodia, kiwi-fox | Jedno zapieczętowane wyjście na każdy punkt końcowy VPN lub SOCKS oraz kontenery dystrybucji i przeglądarki, które żyją w ich wnętrzu |
| [kiwi-server](../server/index.md) | Zbuduj i prowadź własną sieć |
| [gnome-monitor](gnome-monitor.md) | Zapisuj i przełączaj układy ekranów; wyłączaj i włączaj pojedyncze monitory |
| [syncman](syncman.md) | Dwukierunkowa synchronizacja folderów (zapisy gier i nie tylko) jako usługi użytkownika |
| [kiwi-cli-tools-desktop](cli-tools.md) | `pweb`, `select-server`, `tethering`, `torlink` |

Również tutaj: [kiwi-gen](kiwi-gen.md), menedżer kluczy i certyfikatów, który
działa offline w przeglądarce.

## Od świeżej instalacji { #from-a-fresh-install }

```bash
# 1. kiwi-updater: zakres użytkownika i systemu, jedno pytanie o hasło; katalog Kiwi przychodzi razem z nim
curl -fsSL https://raw.githubusercontent.com/derlocke-ng/kiwi-updater/main/get-kiwi.sh | bash
kiwi list

# 2. skonfiguruj maszynę
kiwi install ensconce
ensconce --init && $EDITOR "$(ensconce --config-dir)"/settings.sh
ensconce

# 3. aplikacje, które chcesz (albo wypisz je w kiwi-apps.list ensconce)
kiwi install kiwi-killswitch
kiwi install kiwi-custodia && kiwi-custodia setup
```

**Kiwi Apps** (`kiwi-gui`) w siatce aplikacji robi to samo jednym kliknięciem.

## Dołączanie do twojej sieci { #joining-your-network }

Pulpit dołącza do sieci mesh jak każde inne urządzenie: `kiwi-server enroll fleet.yaml
laptop --group devices` zapisuje konfigurację WireGuard, którą importujesz w
Ustawieniach GNOME. Zaimportuj CA floty (`kiwiCA.pem`), żeby jej nazwy HTTPS
były zaufane. ensconce instaluje każdy `.pem` ze swojego katalogu `certs/` w
całym systemie.

[kiwi-killswitch](kiwi-killswitch.md) utrzymuje wtedy maszynę w trybie
fail-closed wokół tego połączenia. Jego ustawienie *trusted kiwi-nodes*
pozwala, by w domu node gateway w twoim LAN zastępował tunel.
