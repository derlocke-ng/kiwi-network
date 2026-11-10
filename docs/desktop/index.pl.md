# Desktop

Desktopowa część Kiwi Network to komputer, na którym pracujesz: linuksowa
stacja robocza, która konfiguruje się automatycznie i pobiera aplikacje
z katalogów aplikacji w gicie. Katalog aplikacji to repozytorium git z listą
aplikacji. Nie musisz konfigurować maszyny ręcznie, a następną możesz
skonfigurować dokładnie tak samo.

Narzędzia Kiwi dla desktopu są przeznaczone dla **Fedora Atomic Desktops**:
Fedory Silverblue i [Bluefina](https://projectbluefin.io/), a zwłaszcza
Bluefina-DX. Te systemy instaluje się i aktualizuje jako jeden kompletny obraz.
Ich folder `/usr` jest niezmienny, czyli nie da się go modyfikować,
a aktualizację można łatwo wycofać. Nie ma specjalnego obrazu Kiwi. Instalujesz
standardowy obraz Silverblue lub Bluefina i dokładasz do niego trzy rzeczy.

1. **[kiwi-updater](kiwi-updater.md)** instaluje aplikacje z katalogów
   w gicie i dba o ich aktualność. Wszystko instaluje w twoim folderze
   domowym. Tylko aplikacja, która potrzebuje roota, dostaje dodatkowo część
   należącą do roota. kiwi-updater aktualizuje też samego siebie.
2. **[ensconce](ensconce.md)** konfiguruje świeżo zainstalowanego Bluefina-DX.
   Opisujesz swoją konfigurację w prostych plikach z listami, a ensconce ją
   wprowadza: pakiety, Flatpaki, rozszerzenia GNOME, synchronizację
   z Nextcloudem, SSH, ustawienia sysctl i zasilania, ekran logowania oraz
   twoje aplikacje Kiwi. Z opcją `--export` zapisuje konfigurację istniejącej
   maszyny do takich plików, dzięki czemu możesz tę maszynę sklonować.
3. **Aplikacje**, które instalujesz z [katalogu Kiwi](catalogs.md):

| Aplikacja | Do czego służy |
|---|---|
| [kiwi-killswitch](kiwi-killswitch.md) | Kill switch dla VPN w GNOME. Działa w trybie fail-closed: dopóki VPN nie działa, cały ruch pozostaje zablokowany |
| [Sieci klientów](../clients/index.md): kiwi-proxy, kiwi-custodia, kiwi-fox | Osobny exit dla każdego punktu końcowego VPN lub SOCKS. Exit to odizolowany kontener, który może się łączyć tylko z tym jednym punktem końcowym. Do exitu można podłączyć boxy z dystrybucjami Linuksa i przeglądarki, a wtedy cały ich ruch przechodzi przez ten exit |
| [kiwi-server](../server/index.md) | Narzędzie, którym budujesz własną sieć i nią zarządzasz |
| [gnome-monitor](gnome-monitor.md) | Zapisuje układy ekranów i przełącza się między nimi. Potrafi też wyłączać i włączać pojedyncze monitory |
| [syncman](syncman.md) | Synchronizuje foldery w obu kierunkach, np. zapisy gier. Synchronizacja działa jako usługi użytkownika |
| [kiwi-cli-tools-desktop](cli-tools.md) | `pweb`, `select-server`, `tethering`, `torlink` |

W tej sekcji opisany jest też [kiwi-gen](kiwi-gen.md), menedżer kluczy
i certyfikatów, który działa w przeglądarce i nie potrzebuje połączenia
z internetem.

## Od świeżej instalacji { #from-a-fresh-install }

Te polecenia prowadzą od świeżo zainstalowanego systemu do desktopu
z aplikacjami Kiwi:

```bash
# 1. kiwi-updater: zakres użytkownika i systemowy, hasło podajesz raz; katalog Kiwi jest w zestawie
curl -fsSL https://raw.githubusercontent.com/derlocke-ng/kiwi-updater/main/get-kiwi.sh | bash
kiwi list

# 2. konfiguracja maszyny
kiwi install ensconce
ensconce --init && $EDITOR "$(ensconce --config-dir)"/settings.sh
ensconce

# 3. wybrane aplikacje (albo wpisz je do kiwi-apps.list w ensconce)
kiwi install kiwi-killswitch
kiwi install kiwi-custodia && kiwi-custodia setup
```

Aplikacje możesz instalować także bez terminala. **Kiwi Apps** (`kiwi-gui`)
z siatki aplikacji instaluje aplikację jednym kliknięciem.

## Dołączenie do twojej sieci { #joining-your-network }

Desktop dołącza do sieci mesh tak samo jak każde inne urządzenie. Sieć mesh to
prywatna sieć WireGuard, która łączy twoje serwery i urządzenia. Polecenie
`kiwi-server enroll fleet.yaml laptop --group devices` zapisuje plik
konfiguracyjny WireGuard, który importujesz w Ustawieniach GNOME. Zaimportuj
też urząd certyfikacji (CA) swojej sieci, `kiwiCA.pem`, żeby desktop ufał
certyfikatom HTTPS nazw w twojej sieci. ensconce instaluje dla całego systemu
każdy plik `.pem` ze swojego folderu `certs/`.

Potem [kiwi-killswitch](kiwi-killswitch.md) chroni to połączenie i utrzymuje
maszynę w trybie fail-closed. Oznacza to, że ruch, który nie przechodzi przez
to połączenie, jest blokowany, także wtedy, gdy połączenie nie działa. W domu
twój ruch może już kierować przez tunel node `gateway` w twojej sieci lokalnej.
Przy ustawieniu *trusted kiwi-nodes* kill switch akceptuje taki node zamiast
tunelu.
