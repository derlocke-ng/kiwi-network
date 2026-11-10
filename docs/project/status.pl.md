# Repozytoria i stan

Każde repozytorium jest pod [github.com/derlocke-ng](https://github.com/derlocke-ng).
„Wydane” oznacza tag wersji, czyli to, co instaluje kiwi-updater. Wersje według
stanu na listopad 2026.

## Sieć { #the-network }

| Repozytorium | Co to jest | Wydanie | Katalog | Licencja |
|---|---|---|---|---|
| [kiwi-server](https://github.com/derlocke-ng/kiwi-server) | budowa i prowadzenie sieci: plik fleet → obrazy ISO instalacyjne → apply przez SSH | v2.42.0 | tak | GPL-3.0+ |
| [kiwi-modules](https://github.com/derlocke-ng/kiwi-modules) | 20 modułów i ich renderer: jeden plik maszyny → paczka stacka | v0.23.0 | nie | GPL-3.0+ |
| [kiwi-stack](https://github.com/derlocke-ng/kiwi-stack) | strona maszyny: umieszcza paczkę na maszynie i utrzymuje ją w działaniu | v0.5.0 | nie | GPL-3.0+ |
| [mullvad-socks5](https://github.com/derlocke-ng/mullvad-socks5) | proxy SOCKS5 Mullvad jako listy i rekordy DNS, odbudowywane co 6 godzin | gałąź `list` | nie | MIT (README) |

## Ludzie { #people }

| Repozytorium | Co to jest | Wydanie | Licencja |
|---|---|---|---|
| [kiwi-framework](https://github.com/derlocke-ng/kiwi-framework) | silnik sfederowanych hubów społeczności na nostr | v0.32.1 | GPL-3.0+ |
| [Armory](https://github.com/derlocke-ng/armory) | pierwszy hub: dziesięć narzędzi webowych peer-to-peer ([na żywo](https://derlocke-ng.github.io/armory/)) | śledzi `main` (0.1.0) | GPL-3.0+ |
| [kiwi-web-catalog](https://github.com/derlocke-ng/kiwi-web-catalog) | katalog hubów i ich aplikacji | (lista) | CC0 (README) |

## Pulpit { #the-desktop }

| Repozytorium | Co to jest | Wydanie | Katalog | Licencja |
|---|---|---|---|---|
| [kiwi-updater](https://github.com/derlocke-ng/kiwi-updater) | instaluje i aktualizuje aplikacje z katalogów git | v2.4.0 | tak | GPL-3.0+ |
| [kiwi-catalog](https://github.com/derlocke-ng/kiwi-catalog) | katalog aplikacji Kiwi | (lista) | n/d | nie podano |
| [ensconce](https://github.com/derlocke-ng/ensconce) | konfiguracja poinstalacyjna dla Bluefin-DX | v2.5.0 | tak | GPL-3.0+ |
| [kiwi-killswitch](https://github.com/derlocke-ng/kiwi-killswitch) | kill switch VPN dla GNOME w trybie fail-closed | v0.2.3 | tak | GPL-3.0+ |
| [kiwi-proxy](https://github.com/derlocke-ng/kiwi-proxy) | zapieczętowane wyjścia SOCKS5/VPN w Podmanie bez roota | v0.7.3 | tak | GPL-3.0+ |
| [kiwi-custodia](https://github.com/derlocke-ng/kiwi-custodia) | kontenery dystrybucji, których ruch wychodzi tylko przez wyjście | v0.2.3 | tak | GPL-3.0+ |
| [kiwi-fox](https://github.com/derlocke-ng/kiwi-fox) | odizolowane tożsamości przeglądarki na wyjściach kiwi-proxy | v0.7.1 | tak | GPL-3.0+ |
| [kiwi-plugin-tor](https://github.com/derlocke-ng/kiwi-plugin-tor) | dostawca kiwi-proxy: Tor | v0.3.0 | tak | GPL-3.0+ |
| [kiwi-plugin-vpn](https://github.com/derlocke-ng/kiwi-plugin-vpn) | dostawca kiwi-proxy: VPN przez gluetun | v0.2.2 | tak | GPL-3.0+ |
| [kiwi-plugin-9proxy](https://github.com/derlocke-ng/kiwi-plugin-9proxy) | dostawca kiwi-proxy: 9proxy | v0.2.0 | tak | GPL-3.0+ |
| [kiwi-plugin-myst](https://github.com/derlocke-ng/kiwi-plugin-myst) | dostawca kiwi-proxy: Mysterium | v0.5.2 | tak | GPL-3.0+ |
| [gnome-monitor](https://github.com/derlocke-ng/gnome-monitor) | układy ekranów dla GNOME | v0.3.2 | tak | GPL-3.0+ |
| [syncman](https://github.com/derlocke-ng/syncman) | dwukierunkowa synchronizacja folderów jako usługi użytkownika | v0.4.1 | tak | GPL-3.0+ |
| [kiwi-cli-tools-desktop](https://github.com/derlocke-ng/kiwi-cli-tools-desktop) | `pweb`, `select-server`, `tethering`, `torlink` | v1.2.1 | tak | GPL-3.0+ |
| [kiwi-gen](https://github.com/derlocke-ng/kiwi-gen) | klucze i certyfikaty SSH i TLS, offline w przeglądarce ([na żywo](https://derlocke-ng.github.io/kiwi-gen/)) | strona WWW | nie | MIT |
| [kiwi-icons](https://github.com/derlocke-ng/kiwi-icons) | ikony aplikacji ([podgląd](https://derlocke-ng.github.io/kiwi-icons/)) | brak tagów | nie | nie podano |
| [kiwi-network](https://github.com/derlocke-ng/kiwi-network) | ta strona i dokumentacja | n/d | n/d | AGPL-3.0 |

## Znane braki { #known-gaps }

Według samych repozytoriów:

- **kiwi-server**: sprawdzony na sprzęcie w październiku–listopadzie 2026, z
  kopiami zapasowymi node'ów odtworzonymi między node'ami i dostrojonym MTU
  tunelu, łącznie ze ścieżkami mobilnymi. Kilka serwerów kopii zapasowych,
  automatyczne odtwarzanie odbudowanej maszyny, timer przycinania i kontrola
  stanu dla zawieszonego komercyjnego wyjścia są na gałęziach
  `several-servers` kiwi-server i kiwi-modules, jeszcze niewydane. Federacja
  między sieciami nie jest jeszcze sprawdzona. Tylko IPv4, a obraz ISO Debiana
  jest tylko dla amd64. Płaszczyzna sterowania jest zaprojektowana, nie
  zbudowana.
- **kiwi-modules**: OpenCloud, Immich i Paperless-ngx są „do wypróbowania”.
  Serwer TURN dla rozmów czeka na scalenie.
- **kiwi-stack**: brak wycofywania zmian poza odtworzeniem danych i ponownym
  zastosowaniem starszej paczki.
- **kiwi-framework**: blog, zatwierdzenia moderacyjne, obserwowanie
  przestrzeni, których hub nie dostarcza, oraz podpisywanie NIP-07/NIP-46
  dopiero nadejdą.
- **kiwi-updater**: hostowany rejestr zaufanych katalogów jest zaplanowany.
  Tagi wydań pozostałych aplikacji nie są jeszcze podpisane, więc część root
  kiwi-killswitch pyta o hasło przy aktualizacji.
- **kiwi-proxy**: jego moduł kiwi-server nie działał na żadnej maszynie.
  Wyjścia to tylko TCP i IPv4. Moduł VPN trzyma jedną konfigurację na maszynę.
- **Moduły dostawców**: VPN i 9proxy nie są zweryfikowane od początku do końca
  z prawdziwym kontem; Mysterium jest (7 listopada 2026).
- **kiwi-custodia**: niektóre części trzeba jeszcze zmierzyć na prawdziwej
  maszynie (tun2socks w gatewayu bez roota, kompozytory inne niż GNOME).
- **Licencje**: kiwi-icons, kiwi-catalog i mullvad-socks5 nie mają pliku
  LICENSE, a kiwi-killswitch podaje swoją licencję tylko w README i
  manifeście.
