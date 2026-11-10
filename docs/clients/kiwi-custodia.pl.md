# kiwi-custodia

Kontenery dystrybucji, z których każdy bajt wychodzi przez wyjście
[kiwi-proxy](kiwi-proxy.md). *Coś jak distrobox, z siecią pod nadzorem.*

- Repozytorium: [derlocke-ng/kiwi-custodia](https://github.com/derlocke-ng/kiwi-custodia), GPL-3.0-or-later
- Najnowsze wydanie: **v0.2.3**. Jest w [katalogu Kiwi](../desktop/catalogs.md), zakres użytkownika.
- CLI (`kiwi-custodia`) i aplikacja GTK4 (**Kiwi Custodia**)

**Kontener** (box) to jedna dystrybucja Linuksa w kontenerze Podmana bez
roota, z własnym katalogiem domowym, dołączona do zapieczętowanego gatewaya
wyjścia. Instaluj w nim cokolwiek jego menedżerem pakietów, uruchamiaj jego
aplikacje desktopowe na swoim pulpicie i umieszczaj je w siatce aplikacji.
Kontener nie ma żadnej trasy poza wyjściem: ani dla `dnf`, ani dla klienta
gry, ani dla statycznego pliku binarnego, który nigdy nie słyszał o
`$ALL_PROXY`. Jeśli wyjście zniknie, kontener nie ma żadnej trasy.

Dzięki temu osobny kontener dla każdej sieci klienta to czysty sposób pracy:
narzędzia, klucze i historia powłoki klienta A w jednym kontenerze, klienta B
w innym, każdy dociera tylko do własnego klienta.

## Instalacja { #install }

```bash
kiwi install kiwi-custodia   # przynosi ze sobą kiwi-proxy; albo ./install.sh install
kiwi-custodia setup          # the tunnel image, plus kiwi-proxy's gateway image and DNS data
```

Potrzebuje Podmana bez roota z `catatonit`, kiwi-proxy, sesji Wayland,
Pythona 3.12+ z pydantic, GTK4 + libadwaita dla aplikacji i `/dev/net/tun`
dostępnego dla kontenerów bez roota. Obrazy dystrybucji są pobierane przy
pierwszym starcie kontenera. Po aktualizacji uruchom ponownie
`kiwi-custodia setup`.

## Użycie { #use }

```bash
kiwi-proxy add client-a socks5://user:pass@host:1080       # wyjście, zdefiniowane raz, w kiwi-proxy
kiwi-custodia new work --exit client-a --distro fedora     # kontener na nim; pierwszy start instaluje bazowy zestaw
kiwi-custodia enter work                                   # powłoka w nim: sudo dnf install …
kiwi-custodia run work -- firefox                          # jedno polecenie w nim
kiwi-custodia check work                                   # co świat widzi od środka
kiwi-custodia apps work                                    # aplikacje desktopowe, które ma
kiwi-custodia export work firefox                          # "Firefox (work)" in the app grid
kiwi-custodia stop work
kiwi-custodia reset work                                   # powrót do obrazu bazowego; katalog domowy zostaje
kiwi-custodia-gui
```

Dystrybucje: `fedora` (domyślna), `fedora-toolbox`, `ubuntu`,
`ubuntu-toolbox`, `debian`, `debian-toolbox`, `kali`, `arch`, `arch-toolbox`,
`opensuse`, `rocky`, `alpine` lub `custom` z `--image`.

## Jak zbudowany jest kontener { #how-a-box-is-built }

Trzy kontenery dzielą jedną przestrzeń nazw sieciowych: **gateway**
kiwi-proxy, **sidecar tunelu** (tun2socks na urządzeniu TUN, które staje się
trasą domyślną) i sam **kontener**. Cały ruch wychodzi przez TUN do SOCKS5
wyjścia, więc objęte są też programy ignorujące ustawienia proxy.

- Kontener działa jako twój użytkownik, z tym samym uid i `sudo` bez hasła.
  Jego katalog domowy to `~/.local/share/kiwi-custodia/boxes/<id>/home`, osobny
  dla każdego kontenera zamiast twojego prawdziwego katalogu domowego: dwa
  kontenery to dwie tożsamości.
- Zmiany wewnątrz kontenera są zachowywane w snapshocie tego kontenera, gdy
  się zatrzymuje, a `reset` wraca do obrazu bazowego.
- Wayland, X11 (przez Xwayland), PipeWire, magistrala sesji i `/dev/dri` są
  przekazywane do środka, więc aplikacje desktopowe i gry działają.
- DNS idzie przez resolver gatewaya (z blokowaniem reklam) albo przez upstream
  na wyjściu ze zdalnym DNS.

## Czym nie jest { #what-it-is-not }

Kontener to **areszt sieciowy, a nie piaskownica oddzielająca od twojego
pulpitu**. Jak distrobox dostaje twój ekran i magistralę sesji, więc program w
kontenerze może pokazywać okna, czytać schowek i używać portali. Nie może
natomiast dotrzeć do sieci inaczej niż przez swoje wyjście. UDP nie ma drogi
na zewnątrz (bez QUIC, bez mediów WebRTC), a IPv6 nie ma trasy.

Kontenery, które nie mogą dzielić wyjścia, dostają różne wyjścia.
