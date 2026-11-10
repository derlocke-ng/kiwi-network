# Repozytoria i stan

Ta strona wymienia wszystkie repozytoria projektu Kiwi Network: czym jest każde
z nich, jakie jest jego najnowsze wydanie i na jakiej licencji jest
udostępnione. Na końcu znajdziesz listę znanych braków i rzeczy, których jeszcze nie
przetestowano.

Wszystkie repozytoria są na [github.com/derlocke-ng](https://github.com/derlocke-ng).
„Wydane” oznacza, że repozytorium ma tag wersji, bo to właśnie tag wersji
instaluje kiwi-updater. Wersje są podane według stanu na listopad 2026.

## Sieć { #the-network }

| Repozytorium | Co to jest | Wydanie | Katalog | Licencja |
|---|---|---|---|---|
| [kiwi-server](https://github.com/derlocke-ng/kiwi-server) | buduje sieć i nią zarządza: zamienia plik fleet w instalacyjne obrazy ISO i przez SSH stosuje rolę każdej maszyny | v2.42.0 | tak | GPL-3.0+ |
| [kiwi-modules](https://github.com/derlocke-ng/kiwi-modules) | 20 modułów i program, który zamienia jeden plik maszyny w paczkę stacku | v0.23.0 | nie | GPL-3.0+ |
| [kiwi-stack](https://github.com/derlocke-ng/kiwi-stack) | część działająca na maszynie: umieszcza na niej paczkę i pilnuje, żeby działała | v0.5.0 | nie | GPL-3.0+ |
| [mullvad-socks5](https://github.com/derlocke-ng/mullvad-socks5) | listy i rekordy DNS proxy SOCKS5 Mullvada, odświeżane co 6 godzin | gałąź `list` | nie | MIT (README) |

## Ludzie { #people }

| Repozytorium | Co to jest | Wydanie | Licencja |
|---|---|---|---|
| [kiwi-framework](https://github.com/derlocke-ng/kiwi-framework) | framework do budowania federacyjnych hubów społeczności na nostr | v0.32.1 | GPL-3.0+ |
| [Armory](https://github.com/derlocke-ng/armory) | pierwszy hub zbudowany na kiwi-framework, z dziesięcioma narzędziami webowymi peer-to-peer ([na żywo](https://derlocke-ng.github.io/armory/)) | śledzi `main` (0.1.0) | GPL-3.0+ |
| [kiwi-web-catalog](https://github.com/derlocke-ng/kiwi-web-catalog) | katalog hubów i ich aplikacji | (lista) | CC0 (README) |

## Desktop { #the-desktop }

| Repozytorium | Co to jest | Wydanie | Katalog | Licencja |
|---|---|---|---|---|
| [kiwi-updater](https://github.com/derlocke-ng/kiwi-updater) | instaluje i aktualizuje aplikacje z katalogów aplikacji w gicie | v2.4.0 | tak | GPL-3.0+ |
| [kiwi-catalog](https://github.com/derlocke-ng/kiwi-catalog) | katalog aplikacji Kiwi | (lista) | nie dotyczy | nie podano |
| [ensconce](https://github.com/derlocke-ng/ensconce) | konfiguruje Bluefin-DX po instalacji | v2.5.0 | tak | GPL-3.0+ |
| [kiwi-killswitch](https://github.com/derlocke-ng/kiwi-killswitch) | kill switch VPN dla GNOME działający w trybie fail-closed: gdy połączenie VPN zostanie przerwane, ruch jest blokowany | v0.2.3 | tak | GPL-3.0+ |
| [kiwi-proxy](https://github.com/derlocke-ng/kiwi-proxy) | exity SOCKS5 i VPN w rootless Podman, każdy zamknięty w kontenerze, którego jedyną trasą jest to połączenie | v0.7.3 | tak | GPL-3.0+ |
| [kiwi-custodia](https://github.com/derlocke-ng/kiwi-custodia) | boxy z dystrybucjami Linuksa w kontenerach, których ruch może trafić do internetu tylko przez exit kiwi-proxy | v0.2.3 | tak | GPL-3.0+ |
| [kiwi-fox](https://github.com/derlocke-ng/kiwi-fox) | odizolowane tożsamości przeglądarki, które łączą się przez exity kiwi-proxy | v0.7.1 | tak | GPL-3.0+ |
| [kiwi-plugin-tor](https://github.com/derlocke-ng/kiwi-plugin-tor) | moduł dostawcy dla kiwi-proxy: Tor | v0.3.0 | tak | GPL-3.0+ |
| [kiwi-plugin-vpn](https://github.com/derlocke-ng/kiwi-plugin-vpn) | moduł dostawcy dla kiwi-proxy: VPN przez gluetun | v0.2.2 | tak | GPL-3.0+ |
| [kiwi-plugin-9proxy](https://github.com/derlocke-ng/kiwi-plugin-9proxy) | moduł dostawcy dla kiwi-proxy: 9proxy | v0.2.0 | tak | GPL-3.0+ |
| [kiwi-plugin-myst](https://github.com/derlocke-ng/kiwi-plugin-myst) | moduł dostawcy dla kiwi-proxy: Mysterium | v0.5.2 | tak | GPL-3.0+ |
| [gnome-monitor](https://github.com/derlocke-ng/gnome-monitor) | układy ekranów dla GNOME | v0.3.2 | tak | GPL-3.0+ |
| [syncman](https://github.com/derlocke-ng/syncman) | dwukierunkowa synchronizacja folderów, działająca jako usługi użytkownika systemd | v0.4.1 | tak | GPL-3.0+ |
| [kiwi-cli-tools-desktop](https://github.com/derlocke-ng/kiwi-cli-tools-desktop) | `pweb`, `select-server`, `tethering`, `torlink` | v1.2.1 | tak | GPL-3.0+ |
| [kiwi-gen](https://github.com/derlocke-ng/kiwi-gen) | tworzy klucze i certyfikaty SSH oraz TLS offline w przeglądarce ([na żywo](https://derlocke-ng.github.io/kiwi-gen/)) | strona WWW | nie | MIT |
| [kiwi-icons](https://github.com/derlocke-ng/kiwi-icons) | ikony aplikacji ([podgląd](https://derlocke-ng.github.io/kiwi-icons/)) | brak tagów | nie | nie podano |
| [kiwi-network](https://github.com/derlocke-ng/kiwi-network) | ta strona i dokumentacja | nie dotyczy | nie dotyczy | GPL-3.0-or-later, CC BY-SA 4.0 |

## Znane braki { #known-gaps }

Te braki wymieniają same repozytoria:

- **kiwi-server**: Działanie na prawdziwym sprzęcie zostało potwierdzone
  w październiku i listopadzie 2026. W tych testach kopie zapasowe node’a
  przywrócono z jednego node’a na drugi, a MTU tunelu dostrojono, także dla
  łączy komórkowych. Cztery nowości są na gałęziach `several-servers`
  repozytoriów kiwi-server i kiwi-modules i nie zostały jeszcze wydane: kilka
  serwerów kopii zapasowych, automatyczne przywracanie danych na odbudowanej
  maszynie, timer usuwający stare snapshoty oraz kontrola stanu, która
  restartuje zawieszone połączenie z komercyjnym dostawcą VPN. Działania
  federacji między sieciami jeszcze nie potwierdzono. Wszystko działa wyłącznie
  na IPv4, a obraz ISO Debiana istnieje tylko dla amd64. Warstwa sterowania
  jest zaprojektowana, ale jeszcze niezrealizowana.
- **kiwi-modules**: Moduły OpenCloud, Immich i Paperless-ngx są oznaczone jako
  „do wypróbowania”. Serwer TURN do połączeń czeka na scalenie.
- **kiwi-stack**: Nie ma wycofywania zmian. Można tylko przywrócić dane
  i ponownie zastosować starszą paczkę.
- **kiwi-framework**: Kilka części ma się dopiero pojawić: blog, zatwierdzanie
  w moderacji, obserwowanie przestrzeni, których hub nie dostarcza, oraz
  signery NIP-07/NIP-46.
- **kiwi-updater**: Planowany jest hostowany rejestr zaufanych katalogów
  aplikacji. Tagi wydań pozostałych aplikacji nie są jeszcze podpisane.
  Dlatego część kiwi-killswitch działająca jako root prosi przy aktualizacji
  o hasło.
- **kiwi-proxy**: Jego moduł dla kiwi-server nie działał jeszcze na żadnej
  maszynie. Exity przenoszą tylko TCP i IPv4. Moduł VPN przechowuje jedną
  konfigurację na maszynę.
- **Moduły dostawców**: Modułów VPN i 9proxy nie sprawdzono jeszcze w całości
  z prawdziwym kontem. Moduł Mysterium sprawdzono 7 listopada 2026.
- **kiwi-custodia**: Niektóre rzeczy trzeba jeszcze zmierzyć na prawdziwej
  maszynie: tun2socks w kontenerze gateway działającym bez roota (rootless)
  i kompozytory inne niż GNOME.
- **Licencje**: kiwi-icons, kiwi-catalog i mullvad-socks5 nie mają pliku
  LICENSE, a kiwi-killswitch podaje licencję tylko w README i manifeście.
