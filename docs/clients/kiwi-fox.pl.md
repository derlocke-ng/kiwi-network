# kiwi-fox

Odizolowane tożsamości przeglądarki w Podmanie bez roota.

Każdy profil to jedna trwała tożsamość: własna pamięć i zwykle wyjście
[kiwi-proxy](kiwi-proxy.md) z zapieczętowanym gatewayem i resolverem
blokującym reklamy, w jednej z trzech przeglądarek. Dla sieci klienta oznacza
to przeglądarkę, która dociera do konsol webowych klienta przez wyjście
klienta i do niczego więcej.

- Repozytorium: [derlocke-ng/kiwi-fox](https://github.com/derlocke-ng/kiwi-fox), GPL-3.0-or-later
- Najnowsze wydanie: **v0.7.1**. Jest w [katalogu Kiwi](../desktop/catalogs.md), zakres użytkownika.
- Silniki są pobierane, nigdy redystrybuowane: Camoufox (MPL-2.0) przy
  konfiguracji, Firefox i Tor Browser na żądanie (`kiwi-fox engine fetch`), ze
  zweryfikowanym podpisem.

| Silnik | Co widzi strona |
|---|---|
| **Camoufox** (domyślny) | spójną, zwyczajną maszynę z Windows 11 z własnym regionem: zamrożony, sfałszowany fingerprint |
| **Firefox** | standardowy Mozilla Firefox, niczego nie fałszuje: własne wartości tej maszyny, przez to samo zapieczętowane wyjście |
| **Tor Browser** | niezmodyfikowany Tor Browser, przez wyjście na module tor, z obwodem na każdą witrynę i nazwami `.onion` |

kiwi-fox jest dla ludzi, którzy zarządzają kilkoma kontami, które posiadają
lub do których prowadzenia są upoważnieni, i nie chcą, żeby te konta były
powiązane przez fingerprint przeglądarki lub IP.

## Instalacja { #install }

```bash
kiwi install kiwi-fox      # przynosi ze sobą kiwi-proxy; albo ./install.sh install
kiwi-fox setup             # images, a ~630 MB browser engine, DNS data; runs kiwi-proxy's setup too
kiwi-fox engine fetch --engine firefox     # albo torbrowser: ze zweryfikowanym podpisem
```

Potrzebuje Podmana bez roota i kiwi-proxy, sesji Wayland (X11 działa ze
słabszą granicą), Pythona 3.12+, GTK4 + libadwaita, `secret-tool` oraz
`gpg`/`gpgv` do weryfikacji Firefoksa i Tor Browser. Na własnościowym
sterowniku NVIDIA potrzebuje też `nvidia-container-toolkit` z jego specyfikacją
CDI.

## Użycie { #use }

```bash
kiwi-proxy add client-a socks5://user:pass@host:1080   # wyjście, zdefiniowane raz, w kiwi-proxy
kiwi-fox new work --exit client-a     # profil na nim: sonduje je, losuje pasującą tożsamość
kiwi-fox new plain --no-proxy         # własne połączenie tej maszyny, nic nie jest zapieczętowane
kiwi-fox list                         # --tag shop, --by-tag
kiwi-fox run work                     # albo aplikacja
kiwi-fox stop work
kiwi-fox check                        # czy każdy profil jest nadal spójny?
kiwi-fox selfcheck work               # zmierz, co widzą strony, potem to sprawdź
kiwi-fox-gui                          # "Kiwi Fox" in the app grid
```

`--desktop-entry` umieszcza profil w siatce aplikacji, a tagi grupują
profile.

## Profile i wyjścia { #profiles-and-exits }

Profil odwołuje się do wyjścia, a wyjścia są współdzielone: profile na jednym
wyjściu dzielą jego gateway (jedna przestrzeń nazw, jeden IP wyjścia, jeden
zestaw obwodów Tor). Tożsamości, które nie mogą dzielić wyjścia, dostają różne
wyjścia. Z `--no-proxy` nie ma gatewaya: kontener przeglądarki ma własną sieć
na połączeniu tej maszyny i nic nie jest zapieczętowane.

Kontener przeglądarki dołącza do przestrzeni nazw gatewaya z odebranymi
wszystkimi uprawnieniami (capabilities) poza `SYS_CHROOT` (potrzebuje go
własna piaskownica Firefoksa). Działa z `no-new-privileges`, a silnik jest
zamontowany tylko do odczytu.

## Profil Camoufox { #a-camoufox-profile }

To najzwyklejsza maszyna, jaka istnieje, bo detektory oznaczają właśnie
rzadkie wartości: ekran 1920×1080, czcionki, które ma każdy Windows 11, i
żadne inne, oraz własna karta graficzna tej maszyny opisana tak, jak opisuje
ją Firefox na Windows. Region, język, strefa czasowa i głosy podążają za
wyjściem. Wszystko można później zmienić (`kiwi-fox set`, `kiwi-fox webgl`,
`kiwi-fox fonts`), a zmiany są zapisywane tylko wtedy, gdy wynik pozostaje
spójny.

## Czego nie robi { #what-it-does-not-do }

Nie obiecuje „niewykrywalności”. Profile są odizolowane pod względem pamięci,
IP i każdej powierzchni, którą silnik potrafi sfałszować, ale **nie** wobec
sprzętowych identyfikatorów między przeglądarkami: klatki, które faktycznie
rysuje GPU, i taktowanie sprzętu pochodzą z prawdziwej maszyny i są takie same
dla każdego profilu na niej. `docs/detection-notes.md` w repozytorium opisuje,
co jest mierzone.

Nie ma automatyzacji: żadnych botów ani masowego zakładania kont. Służy tylko
do interaktywnego przeglądania.
