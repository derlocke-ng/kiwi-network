# kiwi-killswitch

kiwi-killswitch to **kill switch dla VPN** w GNOME na Fedorze Silverblue
i Bluefinie. Kill switch pilnuje, żeby twój komputer nie wysłał żadnego ruchu
poza VPN-em, np. gdy połączenie VPN zostanie zerwane albo gdy przechodzisz do
innej sieci. Ten działa w trybie **fail-closed**: zapora sieciowa blokuje
wszystko, na co wyraźnie nie zezwolono, więc gdy coś zawiedzie, ruch zostaje
zablokowany, a nie przepuszczony.

Zaporą zarządza wyłącznie jeden demon z uprawnieniami roota. Sterujesz nim
przełącznikiem w szybkich ustawieniach GNOME, aplikacją GTK4 albo narzędziem
wiersza poleceń (CLI). Wszystkie trzy wysyłają polecenia do demona przez
systemową magistralę D-Bus i nigdy nie pytają o hasło.

Chroni **jedno** połączenie VPN naraz, WireGuard albo OpenVPN. Nie łączy się
z VPN-em za ciebie. Połączenia uruchamiasz w Ustawieniach GNOME, a kill switch
ustawia reguły zapory dla połączenia, które faktycznie działa, tak żeby żaden
ruch nie mógł wyjść z komputera poza nim.

- Repozytorium: [derlocke-ng/kiwi-killswitch](https://github.com/derlocke-ng/kiwi-killswitch), GPL-3.0-or-later
- Najnowsze wydanie: **v0.2.3**. Jest w [katalogu Kiwi](catalogs.md) i ma
  dwa zakresy, user + system. Jedna część instaluje się w twoim folderze
  domowym, druga należy do roota.
- Działa z GNOME Shell od wersji 45 do 50.

```
┌─ your session (unprivileged) ─────────────┐   ┌─ root ──────────────────────┐
│  GNOME Quick Settings toggle              │   │  kiwi-killswitchd           │
│  kiwi-killswitch-settings (GTK4)          │──▶│   nftables  (inet + netdev) │
│  kiwi-killswitch (CLI)                    │   │   systemd-resolved steering │
└───────────────────────────────────────────┘   │   NM + kernel event watcher │
             D-Bus system bus, group `wheel`    └─────────────────────────────┘
```

Rozszerzenie GNOME to proces bez uprawnień roota. Nie może zmieniać zapory
i nie powinno móc. Dlatego całe blokowanie wykonuje demon, a interfejs
użytkownika tylko wysyła do niego polecenia.

## Co robi { #what-it-does }

- **Działa w trybie fail-closed.** Zapora stosuje `policy drop` dla ruchu
  wychodzącego, przychodzącego i przekazywanego, zarówno w IPv4, jak i w IPv6.
  Oznacza to, że każdy pakiet jest odrzucany, chyba że zezwala na niego jakaś
  reguła. Nowy zestaw reguł zastępuje stary w jednym atomowym kroku. Ruch może
  wyjść tylko przez chroniony tunel. Jeśli VPN się rozłączy, jeśli uruchomisz
  komputer ponownie albo przełączysz się z Wi-Fi na tethering, wszystko
  pozostaje zablokowane, dopóki znów nie będzie dozwolonej drogi.
- **Nowe interfejsy sieciowe są blokowane.** Jeśli podłączysz tethering przez
  USB albo włączysz Wi-Fi, gdy kill switch jest uzbrojony, czyli włączony, nowy
  interfejs jest domyślnie zablokowany. Nie zostaje dopuszczony tylko dlatego,
  że żadna reguła o nim nie wspomina.
- **Są trzy poziomy filtrowania.** *Standard* filtruje ruch wychodzący
  i przychodzący. *Strict* jest ustawieniem domyślnym i filtruje dodatkowo ruch
  **przekazywany**. Jest to potrzebne, bo kontenery, maszyny wirtualne
  i Waydroid wysyłają swój ruch przez hosta, a pakiety przekazywane nigdy nie
  przechodzą przez hook output. *Paranoid* dodaje łańcuch **netdev egress** na
  każdej karcie sieciowej (NIC). Tylko ta warstwa widzi ruch z gniazd surowych
  (raw sockets).
- **Zapytania DNS nie mogą ominąć tunelu.** Wybierasz, który serwer DNS jest
  używany, gdy kill switch jest uzbrojony. Zapytania DNS możesz kierować przez
  VPN, korzystać z serwera DNS sieci, w której jesteś, albo z dowolnego
  serwera według własnego wyboru. Serwer DNS samej sieci jest używany tylko w sieci zaufanego
  kiwi-node’a. Kill switch wprowadza twój wybór przez ustawienia
  systemd-resolved dla poszczególnych interfejsów. Dodatkowym zabezpieczeniem
  jest reguła nftables, która odrzuca każde inne zapytanie DNS.
- **Jeśli serwer VPN ma nazwę hosta, demon nie ufa zwykłemu DNS.** Sam
  ustala adres serwera VPN. Używa do tego DNS-over-HTTPS, łączy się
  z przypiętym (stałym) adresem IP i weryfikuje certyfikat. Każdą odpowiedź
  zapamiętuje w pamięci podręcznej.
- **Najpierw wybierasz połączenie, potem zatwierdzasz zmiany.** Zmiany są
  przygotowywane, to znaczy zbierane i wchodzą w życie dopiero wtedy, gdy je
  zatwierdzisz. Dzięki temu możesz przejść z ustawienia „domowy LAN +
  kiwi-node” na „tethering + VPN”, *będąc już na tetheringu*. Zatwierdzenie
  wprowadza wtedy wszystkie zmiany w jednej atomowej transakcji, a kill switch
  ani na chwilę nie zostaje rozbrojony.
- **Zaufane kiwi-node’y.** W twojej sieci może być brama, która już kieruje
  twój ruch przez tunel. W sieci Kiwi jest to
  [node `gateway`](../server/roles.md#node). W swojej własnej sieci taka brama
  może zastąpić VPN. Kill switch rozpoznaje ją po adresie IP **i** adresie MAC.
  Musisz to włączyć samodzielnie. Kill switch nigdy nie uznaje bramy za zaufaną na
  własną rękę.
- **Połączyć się może tylko jeden VPN.** Dostępny jest wyłącznie serwer
  wybranego połączenia. Każdy inny tunel, który uruchomisz, nie nawiąże
  połączenia, a interfejs użytkownika poda jego nazwę.
- **Reguły zostają na miejscu.** Obowiązują nadal po ponownym uruchomieniu
  komputera, po wylogowaniu i zalogowaniu oraz po restarcie NetworkManagera.
  Osobna jednostka systemd wczytuje reguły blokujące, *zanim sieć zacznie
  działać*.

## Instalacja { #install }

kiwi-killswitch wymaga `nftables`, `NetworkManager` i `python3-gobject`,
a dla WireGuard także `wireguard-tools`. Wszystkie są dostępne w Silverblue
i Bluefinie. Nic nie jest zapisywane w niezmiennym `/usr`. Twój użytkownik
musi należeć do grupy `wheel`.

```bash
kiwi install kiwi-killswitch   # obie części; w razie potrzeby konfiguruje zakres systemowy kiwi
```

Możesz go też zainstalować z klona repozytorium. Najpierw uruchom
`sudo ./install.sh install`, które instaluje demona, CLI, politykę D-Bus
i jednostki systemd. Potem uruchom `./install.sh install`, które instaluje
rozszerzenie GNOME i aplikację ustawień. Wyloguj się i zaloguj ponownie, żeby
GNOME wczytało rozszerzenie. Przy odinstalowaniu kill switch jest najpierw
rozbrajany, więc odinstalowanie nie może zostawić cię z zablokowaną siecią.

## Używanie { #use }

W **Szybkich ustawieniach → Kill Switch** uzbrajasz i rozbrajasz kill switch
oraz wybierasz, który VPN jest chroniony. Do wszystkiego innego służy
aplikacja **Kiwi Kill Switch** w siatce aplikacji. CLI ma te polecenia:

```bash
kiwi-killswitch status                   # co jest w tej chwili egzekwowane
kiwi-killswitch list                     # połączenia VPN znane NetworkManagerowi
kiwi-killswitch vpn <name>               # przygotowuje wybór chronionego połączenia
kiwi-killswitch set dns_mode tunnel
kiwi-killswitch apply                    # jedna atomowa transakcja
kiwi-killswitch arm                      # albo: arm <vpn>
kiwi-killswitch disarm
kiwi-killswitch pending                  # co jest przygotowane; revert to odrzuca
```

!!! warning "Uzbrajanie przez SSH"
    Gdy uzbroisz kill switch, sesja SSH z podsieci, której nie ma
    w `mgmt_subnets`, zostanie przerwana. Tak właśnie powinien zachować się
    kill switch. Jeśli pracujesz przez SSH, najpierw ustaw te wartości:
    ```bash
    kiwi-killswitch set mgmt_subnets 192.168.0.0/16
    kiwi-killswitch set allow_in_ports 22
    kiwi-killswitch apply
    ```

**Gdy coś pójdzie nie tak.** CLI nie potrzebuje sieci, więc do uruchomienia
`kiwi-killswitch disarm` zawsze wystarczy konsola tekstowa (TTY). Jeśli nie ma
już samego demona, usuń jego tablice zapory poleceniami
`sudo nft delete table inet kiwi_ks` i
`sudo nft delete table netdev kiwi_ks_egress`.

**Maszyny wirtualne.** Maszyna wirtualna w trybie mostka (bridge) nigdy nie
wysyła ruchu przez hosta, więc kill switch jej nie dotyczy. Unikaj wtedy
poziomu `paranoid`, bo filtruje on na fizycznej karcie sieciowej. Maszyna
wirtualna za NAT-em wysyła ruch przez hosta. Przy poziomie `strict` ten ruch
wychodzi przez tunel i jest blokowany, gdy tunel nie działa. Dodaj podsieć
maszyny wirtualnej do `mgmt_subnets`, żeby jej zapytania DHCP i DNS docierały
do hosta. Tabela pokazuje, na co pozwala każde ustawienie:

| Ustawienie | Wychodzący | Przychodzący | Poza tunelem |
|---|---|---|---|
| `allow_lan` | tak (automatycznie) | nie | nie |
| `bypass_subnets` | tak | nie | nie |
| `mgmt_subnets` | tak | tak | tak |

**Sprawdzenie, czy działa.** Uzbrój kill switch, a potem wyłącz VPN poleceniem
`nmcli connection down …`. Teraz `curl --max-time 5 ifconfig.me` musi
**przekroczyć limit czasu**. Nie może pokazać twojego prawdziwego adresu IP.
Nie oceniaj wyniku na podstawie publicznych adresów IP, które widzisz. Żeby
udowodnić, że ruch idzie przez tunel, uruchom `wg show <iface> transfer` albo
`ip route get 1.1.1.1`.

## Inne zapory i znane ograniczenia { #coexistence-and-known-limits }

- **firewalld może pozostać włączony.** Jego łańcuchy działają z priorytetem
  10, a łańcuchy kill switcha z priorytetem −10.
- **Nie** uruchamiaj go razem z innym kill switchem, który ma własną tablicę
  odrzucającą ruch wychodzący.
- Nie ruszaj `nftables.service`, jeśli z niej nie korzystasz. Zatrzymanie tej
  usługi usuwa wszystkie tablice nftables. Demon wczytuje swoje reguły
  ponownie w ciągu kilku sekund, ale przez te kilka sekund reguł nie ma, a nie
  ma powodu do tego doprowadzać.
- VPN, którego serwer jest podany jako **nazwa hosta**, nie może połączyć się
  ponownie, gdy kill switch jest uzbrojony, chyba że DNS jest ustawiony na
  *a resolver I choose*, czyli na serwer DNS wybrany przez ciebie. Powód: NetworkManager i OpenVPN rozwiązują tę
  nazwę przez systemowy serwer DNS, a ten jest zablokowany, dopóki nie działa
  żaden tunel. Nie dotyczy to połączeń, których serwer jest podany jako adres IP.
- **Serwer DNS wybrany przez ciebie jest dostępny poza tunelem**, gdy tunel nie
  działa. Włącz dla niego DNS-over-TLS.
- **Zaufany node zapisany bez adresu MAC** jest rozpoznawany wyłącznie po
  adresie bramy.
- **Sterowanie bez hasła** działa dzięki polityce D-Bus dla grupy `wheel`.
  Oznacza to też, że każdy program działający jako twój użytkownik może
  wyłączyć kill switch bez pytania cię o zgodę.
- Zatrzymuje wycieki na poziomie sieci. To nie jest Tails ani Whonix. Nie
  chroni przed fingerprintingiem przeglądarki, przed WebRTC ani przed
  aplikacją, która wysyła dane swojemu producentowi przez tunel.
- To narzędzie osobiste, które nie przeszło niezależnego audytu.
  `tests/run.sh` testuje prawdziwego demona z prawdziwym nftables. Każda grupa
  testów działa we własnej przestrzeni nazw, a testy nie wymagają roota.
- Jego tagi wydań nie są jeszcze podpisane. Dlatego przy kiwi-updater 2.4 jego
  część systemowa pyta o hasło przy każdej aktualizacji.

kiwi-killswitch powstał na bazie trzech wcześniejszych narzędzi tego samego
autora. Kolejność uruchamiania przy starcie systemu pochodzi
z `gnome-vpn-killswitch`, wykrywanie bramy z `kiwi-vpn-monitor`, a architektura
demona z `nova-killswitch`.
