# kiwi-killswitch

**Kill switch VPN w trybie fail-closed** dla GNOME na Fedora Silverblue i
Bluefin. Jeden demon roota zarządza zaporą. Przełącznik w Szybkich
ustawieniach GNOME, aplikacja GTK4 i CLI sterują nim przez systemową magistralę
D-Bus, nigdy nie pytając o hasło.

Chroni **jedno** połączenie VPN naraz, WireGuard lub OpenVPN. Nie łączy za
ciebie z VPN-em: połączenia uruchamiasz w Ustawieniach GNOME, a kill switch
buduje szczelną zaporę wokół tego, co faktycznie działa.

- Repozytorium: [derlocke-ng/kiwi-killswitch](https://github.com/derlocke-ng/kiwi-killswitch), GPL-3.0-or-later
- Najnowsze wydanie: **v0.2.3**. Jest w [katalogu Kiwi](catalogs.md), zakresy user + system.
- GNOME Shell od 45 do 50.

```
┌─ your session (unprivileged) ─────────────┐   ┌─ root ──────────────────────┐
│  GNOME Quick Settings toggle              │   │  kiwi-killswitchd           │
│  kiwi-killswitch-settings (GTK4)          │──▶│   nftables  (inet + netdev) │
│  kiwi-killswitch (CLI)                    │   │   systemd-resolved steering │
└───────────────────────────────────────────┘   │   NM + kernel event watcher │
             D-Bus system bus, group `wheel`    └─────────────────────────────┘
```

Rozszerzenie GNOME to proces bez uprawnień. Nie może i nie powinno dotykać
zapory, więc egzekwowanie reguł leży w demonie, a interfejs tylko prosi.

## Co robi { #what-it-does }

- **Fail-closed.** `policy drop` na output, input i forward, IPv4 i IPv6,
  podmieniane atomowo. Ruch wychodzi tylko przez chroniony tunel. Jeśli VPN
  padnie, zrestartujesz komputer albo przełączysz się z Wi-Fi na tethering,
  wszystko pozostaje zablokowane, dopóki nie wróci dozwolona ścieżka.
- **Nowe interfejsy nie mogą przeciekać.** Podłącz tethering USB lub włącz
  Wi-Fi, gdy kill switch jest uzbrojony, a nowy interfejs jest domyślnie
  zablokowany, a nie dopuszczony przez przeoczenie.
- **Trzy poziomy egzekwowania.** *Standard* filtruje output i input. *Strict*
  (domyślny) filtruje też ruch **przekazywany** (forward), bo kontenery,
  maszyny wirtualne i Waydroid trasują przez hosta, a przekazywane pakiety
  nigdy nie przechodzą przez hook output. *Paranoid* dodaje łańcuch **netdev
  egress** na każdej karcie sieciowej, jedyną warstwę, która widzi ruch z
  surowych gniazd.
- **DNS nie może zabłądzić.** Wybierz: przez VPN, własny DNS sieci (tylko
  zaufane kiwi-nodes) albo resolver, który wskażesz. Jest stosowany przez
  ustawienia systemd-resolved dla poszczególnych łączy, z zabezpieczeniem
  nftables, które odrzuca każde inne zapytanie.
- **Punkty końcowe z nazwą hosta są przypięte, a nie powierzone DNS.** Demon
  sam rozwiązuje nazwę hosta serwera VPN, przez DNS-over-HTTPS do przypiętego
  IP ze zweryfikowanym certyfikatem, i zapamiętuje każdą odpowiedź.
- **Wybierz połączenie, potem Apply.** Zmiany są przygotowywane, więc możesz
  przełączyć się z „domowy LAN + kiwi-node” na „tethering + VPN” *będąc już na
  tetheringu*, a potem zastosować to jako jedną atomową transakcję, bez okna
  rozbrojenia pomiędzy.
- **Zaufane kiwi-nodes.** Brama, która już tuneluje dla ciebie
  ([node gateway](../server/roles.md#node)), dopasowana po IP **i** MAC, może
  zastąpić VPN w swojej własnej sieci. To opcja do włączenia, nigdy nie jest
  wywnioskowana.
- **Jeden VPN, egzekwowany.** Osiągalny jest tylko serwer wybranego
  połączenia. Każdy inny tunel, który uruchomisz, nie może się połączyć, a
  interfejs go nazywa.
- **Przetrwa wszystko.** Restarty, wylogowanie i logowanie, restarty
  NetworkManagera: reguły zostają. Osobna jednostka instaluje twardą blokadę
  *zanim sieć się podniesie*.

## Instalacja { #install }

Wymaga `nftables`, `NetworkManager`, `python3-gobject` i, dla WireGuard,
`wireguard-tools`, wszystkie obecne na Silverblue i Bluefin. Nic nie jest
zapisywane w niezmiennym `/usr`. Twój użytkownik musi być w `wheel`.

```bash
kiwi install kiwi-killswitch   # both halves; sets up kiwi's system scope if needed
```

Albo z klona: `sudo ./install.sh install` (demon, CLI, polityka magistrali i
jednostki systemd), potem `./install.sh install` (rozszerzenie GNOME i
aplikacja ustawień). Wyloguj się i zaloguj ponownie, żeby GNOME wczytał
rozszerzenie. Odinstalowanie najpierw rozbraja, więc nie może cię zostawić
odciętego.

## Użycie { #use }

Otwórz **Szybkie ustawienia → Kill Switch**, żeby uzbroić, rozbroić i wybrać,
który VPN jest chroniony, albo **Kiwi Kill Switch** w siatce aplikacji do
wszystkiego innego.

```bash
kiwi-killswitch status                   # co jest egzekwowane w tej chwili
kiwi-killswitch list                     # połączenia VPN znane NetworkManagerowi
kiwi-killswitch vpn <name>               # przygotuj, które jest chronione
kiwi-killswitch set dns_mode tunnel
kiwi-killswitch apply                    # jedna atomowa transakcja
kiwi-killswitch arm                      # albo: arm <vpn>
kiwi-killswitch disarm
kiwi-killswitch pending                  # co jest przygotowane; revert to odrzuca
```

!!! warning "Uzbrajanie przez SSH"
    Uzbrojenie przerywa sesję z podsieci, której nie ma w `mgmt_subnets`. To
    prawidłowe zachowanie kill switcha. Ustaw to najpierw:
    ```bash
    kiwi-killswitch set mgmt_subnets 192.168.0.0/16
    kiwi-killswitch set allow_in_ports 22
    kiwi-killswitch apply
    ```

**Odzyskiwanie.** CLI nie potrzebuje sieci, więc TTY zawsze wystarczy:
`kiwi-killswitch disarm`. Jeśli nie ma samego demona:
`sudo nft delete table inet kiwi_ks` i `sudo nft delete table netdev kiwi_ks_egress`.

**Maszyny wirtualne.** Maszyna wirtualna w trybie mostka nigdy nie trasuje
przez hosta, więc kill switch zostawia ją w spokoju (unikaj `paranoid`, który
filtruje na fizycznej karcie). Maszyna wirtualna za NAT-em trasuje przez
hosta. `strict` wysyła ją przez tunel i blokuje, gdy tunel nie działa. Dodaj
jej podsieć do `mgmt_subnets`, żeby jej DHCP i DNS docierały do hosta:

| Ustawienie | Wychodzący | Przychodzący | Przypięty poza tunelem |
|---|---|---|---|
| `allow_lan` | tak (auto) | nie | nie |
| `bypass_subnets` | tak | nie | nie |
| `mgmt_subnets` | tak | tak | tak |

**Weryfikacja.** Uzbrój, potem wyłącz VPN (`nmcli connection down …`).
`curl --max-time 5 ifconfig.me` musi **przekroczyć limit czasu**, a nie
pokazać twój prawdziwy IP. Nie oceniaj tego, porównując adresy IP wyjścia:
udowodnij użycie tunelu przez `wg show <iface> transfer` lub
`ip route get 1.1.1.1`.

## Współistnienie i znane ograniczenia { #coexistence-and-known-limits }

- **firewalld może zostać włączony.** Jego łańcuchy działają z priorytetem
  10, a nasze z −10.
- **Nie** uruchamiaj go obok innego kill switcha, który ma własną tabelę
  output-drop.
- Zostaw `nftables.service` w spokoju, jeśli go nie używasz. Zatrzymanie go
  czyści każdą tabelę. Demon przywraca swoje reguły w ciągu kilku sekund, ale
  nie ma powodu otwierać tego okna.
- VPN z punktem końcowym w postaci **nazwy hosta** nie może ponownie połączyć
  się, gdy kill switch jest uzbrojony, chyba że DNS jest ustawiony na
  *resolver, który wybieram*. NetworkManager i OpenVPN rozwiązują nazwę przez
  systemowy resolver, który jest zablokowany, gdy żaden tunel nie działa.
  Połączeń z dosłownym adresem IP to nie dotyczy.
- **Resolver, który wybierasz, jest osiągalny poza tunelem**, gdy tunel nie
  działa. Włącz dla niego DNS-over-TLS.
- **Zaufany node zapisany bez MAC** jest dopasowywany tylko po adresie bramy.
- **Sterowanie bez hasła** to polityka magistrali D-Bus dla grupy `wheel`.
  Oznacza to też, że każdy program działający jako ty może wyłączyć
  przełącznik bez pytania.
- Zatrzymuje wycieki na poziomie sieci. To nie Tails ani Whonix i nie robi nic
  z fingerprintingiem przeglądarki, WebRTC ani aplikacją, która dzwoni do domu
  przez tunel.
- To osobiste narzędzie i nie przeszło niezależnego audytu. `tests/run.sh`
  sprawdza prawdziwego demona z prawdziwym nftables, każdą grupę testów we
  własnej przestrzeni nazw, bez roota.
- Jego tagi wydań nie są jeszcze podpisane, więc z kiwi-updater 2.4 jego
  część root pyta o twoje hasło przy aktualizacji.

Wywodzi się z narzędzi autora `gnome-vpn-killswitch` (kolejność przy starcie),
`kiwi-vpn-monitor` (wykrywanie bramy) i `nova-killswitch` (architektura
demona).
