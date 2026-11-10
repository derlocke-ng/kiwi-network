# kiwi-cli-tools-desktop

kiwi-cli-tools-desktop to pakiet czterech małych narzędzi wiersza poleceń dla
linuksowego desktopu. `torlink` łączy cię przez Tor z usługą na innej maszynie,
`pweb` udostępnia folder przez HTTPS, `select-server` pozwala wybrać host SSH
z menu, a `tethering` zmienia TTL ruchu z urządzeń korzystających z tetheringu.

- Repozytorium: [derlocke-ng/kiwi-cli-tools-desktop](https://github.com/derlocke-ng/kiwi-cli-tools-desktop), GPL-3.0-or-later
- Najnowsze wydanie: **v1.2.1**. Jest w [katalogu Kiwi](catalogs.md), zakres użytkownika.

```bash
kiwi install kiwi-cli-tools-desktop   # albo ./install.sh install, do ~/.local/bin
```

## `torlink`: połączenie z maszyną przez Tor { #torlink-reach-a-machine-over-tor }

`torlink` pozwala połączyć się przez sieć Tor z dowolną usługą TCP na innej
maszynie, np. z SSH, interfejsem WWW albo bazą danych. To prosty zamiennik
VPN-u: żadna z maszyn nie potrzebuje otwartego portu, nie potrzebujesz konta
i nie musisz utrzymywać żadnego serwera. Tor i socat działają razem w jednym
kontenerze rootless Podmana, więc wystarczy ci sam Podman.

Maszynę, która udostępnia usługi, identyfikuje jej adres onion, czyli adres
wewnątrz sieci Tor. Na tej maszynie tworzysz **kod zaproszenia** dla jednego
partnera, czyli drugiej strony, która ma dostać dostęp. Partner przyjmuje kod
na swojej maszynie. Kod zawiera klucz autoryzacji klienta Tor. Bez tego klucza
nikt nie zobaczy nawet, że usługa istnieje, więc traktuj kod jak hasło.

```bash
# maszyna A: udostępnia SSH i interfejs WWW dla „bob”
torlink add-service ssh 22
torlink add-service web 8080
torlink invite bob ssh web          # wypisuje torlink1:…  (tajne!)

# maszyna B: korzysta z nich
torlink accept torlink1:… alice
torlink up
torlink ssh alice                   # SSH przez Tor
torlink connect alice web           # 127.0.0.1:2200 → interfejs WWW alice
torlink ssh-config >> ~/.ssh/config # potem `ssh alice-tor`; `select-server tor` je wymienia
```

Każde zaproszenie to osobna usługa onion, która zawiera tylko usługi wymienione
w tym zaproszeniu. Dlatego `torlink revoke bob` trwale odbiera ten dostęp.
`torlink ls` pokazuje twoje usługi, twoich partnerów i twoje przekierowania,
czyli lokalne porty prowadzące do usług partnera. Tor przenosi tylko TCP,
a pierwsze połączenie trwa chwilę. Port SOCKS kontenera (19050) nasłuchuje
wyłącznie na interfejsie loopback. Stan `torlink`, łącznie z twoimi kluczami
onion, jest przechowywany w `~/.local/share/torlink`, a `torlink purge` go
usuwa.

## `pweb`: udostępnianie folderu przez HTTPS { #pweb-share-a-folder-over-https }

`pweb` serwuje **bieżący folder** przez HTTPS na losowym wolnym porcie. Używaj
go, żeby przekazać plik na inną maszynę w tej samej sieci. Przy pierwszym
uruchomieniu tworzy certyfikat z podpisem własnym i potem używa go ponownie.
Dopóki `pweb` działa, folder jest dostępny dla każdej maszyny w sieci lokalnej.
Uruchamiaj go w folderze, który naprawdę chcesz udostępnić, i zatrzymuj
kombinacją Ctrl+C.

```
$ cd ~/Downloads && pweb
serving /home/you/Downloads
on https://yourhost:40123  (also https://localhost:40123)
```

## `select-server`: wybór hosta SSH { #select-server-pick-an-ssh-host }

`select-server` pokazuje ponumerowane menu wszystkich konkretnych aliasów
`Host` z twojego `~/.ssh/config`, czyli wszystkich aliasów, które nie są
wzorcami z symbolami wieloznacznymi. Wybierz jeden, a narzędzie połączy się
z tym hostem. Żeby filtrować menu, oznacz swoje hosty tagami. Dodaj w bloku
`Host` komentarz w rodzaju `# tags: work prod` i podaj tag w wierszu poleceń:

```
$ select-server work            # tylko hosty z tagiem „work”
$ select-server --tags          # tagi, których używasz
$ select-server -f other.conf   # inny plik konfiguracyjny
```

## `tethering`: TTL dla urządzeń na tetheringu { #tethering-the-ttl-fix }

`tethering` przydaje się wtedy, gdy inne urządzenia korzystają z połączenia
internetowego tej maszyny, czyli z tetheringu. Niektórzy operatorzy komórkowi
liczą przeskoki ruchu w sieci i w ten sposób odróżniają urządzenia podłączone
przez tethering od samej maszyny. `tethering` ustawia TTL na 64 dla całego
ruchu przychodzącego z jednego interfejsu. Dla operatora ruch podłączonych
urządzeń wygląda wtedy jak ruch samej maszyny. Narzędzie prosi o sudo i dodaje
jedną regułę `iptables` w tablicy mangle. Reguła **nie** przetrwa ponownego
uruchomienia komputera.

```
tethering            # wybór interfejsu, ustawienie reguły
tethering --status
tethering --off
```
