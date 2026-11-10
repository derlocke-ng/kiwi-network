# kiwi-fox

kiwi-fox daje ci osobną przeglądarkę dla każdej sieci klienta, w której
pracujesz, i dla każdego konta, którym zarządzasz. Profil przeglądarki
przeznaczony dla klienta łączy się z jego konsolami webowymi przez połączenie
tego klienta i nie ma żadnej innej drogi na zewnątrz. Nie potrzebujesz do tego
połączenia VPN na hoście.

Każdy profil to jedna trwała tożsamość. Ma własne dane, uruchamia jedną z trzech
przeglądarek w kontenerze rootless Podmana (kontenerze uruchamianym jako twój
własny użytkownik, bez uprawnień roota) i zwykle korzysta z exitu
[kiwi-proxy](kiwi-proxy.md). Exit to zapisane pod nazwą połączenie
z upstreamem, np. z proxy SOCKS5 klienta. Dla każdego exitu kiwi-proxy
uruchamia gateway. Gateway to kontener, którego jedyna trasa prowadzi do tego
upstreamu i w którym działa serwer DNS blokujący domeny reklamowe.

- Repozytorium: [derlocke-ng/kiwi-fox](https://github.com/derlocke-ng/kiwi-fox), GPL-3.0-or-later
- Najnowsze wydanie: **v0.7.1**. Jest w [katalogu Kiwi](../desktop/catalogs.md), zakres użytkownika.
- Przeglądarki, które kiwi-fox nazywa silnikami, są pobierane na twoją maszynę
  i nigdy nie są dalej rozpowszechniane. Camoufox (MPL-2.0) jest pobierany
  podczas konfiguracji. Firefox i Tor Browser są pobierane, gdy o nie
  poprosisz (`kiwi-fox engine fetch`), a ich podpisy są weryfikowane.

| Silnik | Co widzi strona |
|---|---|
| **Camoufox** (domyślny) | Zwykłą maszynę z Windows 11 z własnym regionem, której wszystkie wartości do siebie pasują. Ten fingerprint (zestaw wartości, które strona może odczytać z przeglądarki, żeby ją potem rozpoznać) jest podrobiony i się nie zmienia |
| **Firefox** | Niezmodyfikowanego Firefoksa od Mozilli, który niczego nie podrabia. Strona widzi wartości tej maszyny. Połączenie i tak przechodzi przez exit profilu |
| **Tor Browser** | Niezmodyfikowaną przeglądarkę Tor Browser, połączoną przez exit z modułu tor. Każda strona dostaje własny obwód (własną drogę przez sieć Tor), a nazwy `.onion` działają |

kiwi-fox jest dla osób, które zarządzają kilkoma kontami należącymi do nich
albo takimi, do których prowadzenia mają uprawnienia, i nie chcą, żeby te
konta dało się ze sobą powiązać po fingerprincie przeglądarki albo adresie IP.

## Instalacja { #install }

```bash
kiwi install kiwi-fox      # instaluje przy okazji kiwi-proxy; albo ./install.sh install
kiwi-fox setup             # obrazy, silnik przeglądarki (ok. 630 MB), dane DNS; uruchamia też konfigurację kiwi-proxy
kiwi-fox engine fetch --engine firefox     # albo torbrowser: z weryfikacją podpisu
```

kiwi-fox wymaga rootless Podmana, kiwi-proxy, Pythona 3.12+, GTK4
z libadwaita oraz `secret-tool`. Jest przeznaczony do sesji Wayland. X11 też
działa, ale izolacja jest tam słabsza. Do weryfikacji Firefoksa i Tor Browser
potrzebne są `gpg`/`gpgv`. Przy własnościowym sterowniku NVIDIA kiwi-fox
potrzebuje też `nvidia-container-toolkit` ze specyfikacją CDI.

## Używanie { #use }

```bash
kiwi-proxy add client-a socks5://user:pass@host:1080   # exit, definiowany raz, w kiwi-proxy
kiwi-fox new work --exit client-a     # profil na tym exicie: mierzy go i losuje pasującą tożsamość
kiwi-fox new plain --no-proxy         # własne połączenie tej maszyny, bez izolacji
kiwi-fox list                         # --tag shop, --by-tag
kiwi-fox run work                     # albo przez aplikację
kiwi-fox stop work
kiwi-fox check                        # czy każdy profil jest nadal spójny?
kiwi-fox selfcheck work               # mierzy, co widzą strony, i ocenia wynik
kiwi-fox-gui                          # „Kiwi Fox” w siatce aplikacji
```

Z opcją `--desktop-entry` profil dostaje własną pozycję w siatce aplikacji.
Tagi pozwalają grupować profile.

## Profile i exity { #profiles-and-exits }

Profil nie jest właścicielem exitu. Tylko się do niego odwołuje, a kilka
profili może odwoływać się do tego samego exitu. Profile na tym samym exicie
współdzielą jego gateway, a razem z nim jedną sieciową przestrzeń nazw
(network namespace), jeden adres IP exitu i jeden zestaw obwodów Tor.
Tożsamości, które nie mogą współdzielić exitu, potrzebują różnych exitów.
Profil utworzony z opcją `--no-proxy` nie ma gatewaya. Jego kontener
przeglądarki ma własną sieć i korzysta z własnego połączenia tej maszyny.
W tym przypadku nic nie jest izolowane: ruch profilu nie jest ograniczony do
jednej trasy.

Kontener przeglądarki dołącza do sieciowej przestrzeni nazw gatewaya. Odebrane
są mu wszystkie uprawnienia (capabilities) Linuksa oprócz `SYS_CHROOT`, którego
potrzebuje piaskownica samego Firefoksa. Kontener działa z
`no-new-privileges`, a silnik jest zamontowany tylko do odczytu.

## Profil Camoufox { #a-camoufox-profile }

Profil Camoufox udaje najpopularniejszą maszynę, jaka istnieje, bo systemy
wykrywania zwracają uwagę na rzadkie wartości. Zgłasza ekran 1920×1080,
czcionki, które ma każda instalacja Windows 11, i żadnych innych, oraz kartę
graficzną tej maszyny, nazwaną tak, jak nazywa ją Firefox w Windowsie. Region,
język, strefa czasowa i głosy są dopasowane do exitu. Wszystko to możesz
później zmienić poleceniami `kiwi-fox set`, `kiwi-fox webgl` i
`kiwi-fox fonts`. Zmiana zostaje zapisana tylko wtedy, gdy profil pozostaje
spójny, to znaczy gdy jego wartości nadal do siebie pasują.

## Czego nie robi { #what-it-does-not-do }

kiwi-fox nie obiecuje, że profil będzie „niewykrywalny”. Profile są od siebie
oddzielone pod względem danych, adresu IP i każdej wartości, którą silnik
potrafi podrobić. **Nie** są oddzielone pod względem identyfikatorów, które
pochodzą ze sprzętu i są takie same w każdej przeglądarce. Klatki, które
faktycznie rysuje GPU, i zależności czasowe sprzętu pochodzą z prawdziwej
maszyny, więc są takie same dla każdego profilu na niej. Plik
`docs/detection-notes.md` w repozytorium opisuje, co jest mierzone.

kiwi-fox nie ma automatyzacji. Nie uruchamia botów i nie zakłada kont
hurtowo. Jest przeznaczony wyłącznie do interaktywnego przeglądania.
