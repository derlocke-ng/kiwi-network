# kiwi-cli-tools-desktop

Cztery małe narzędzia wiersza poleceń dla pulpitu z Linuksem.

- Repozytorium: [derlocke-ng/kiwi-cli-tools-desktop](https://github.com/derlocke-ng/kiwi-cli-tools-desktop), GPL-3.0-or-later
- Najnowsze wydanie: **v1.2.1**. Jest w [katalogu Kiwi](catalogs.md), zakres użytkownika.

```bash
kiwi install kiwi-cli-tools-desktop   # albo ./install.sh install, do ~/.local/bin
```

## `torlink`: dostęp do maszyny przez Tor { #torlink-reach-a-machine-over-tor }

VPN dla ubogich: dostęp do dowolnej usługi TCP (SSH, interfejsu WWW, bazy
danych) na innej maszynie przez Tor, bez otwartych portów, bez kont i bez
serwera. Tor i socat działają w jednym kontenerze Podmana bez roota, więc
potrzebujesz tylko Podmana.

Adres onion jest tożsamością. Strona udostępniająca tworzy **kod zaproszenia**
dla jednego peera, a druga strona go przyjmuje. Kod zawiera klucz autoryzacji
klienta Tor, więc usługa jest niewidoczna dla każdego, kto go nie ma: traktuj
kod jak hasło.

```bash
# maszyna A: udostępnij SSH i interfejs WWW dla „bob”
torlink add-service ssh 22
torlink add-service web 8080
torlink invite bob ssh web          # wypisuje torlink1:…  (sekret!)

# maszyna B: użyj ich
torlink accept torlink1:… alice
torlink up
torlink ssh alice                   # SSH przez Tor
torlink connect alice web           # 127.0.0.1:2200 → alice's web UI
torlink ssh-config >> ~/.ssh/config # then `ssh alice-tor`; `select-server tor` lists them
```

Każde zaproszenie to osobna usługa onion tylko z usługami w nim wymienionymi,
więc `torlink revoke bob` usuwa ten dostęp na dobre. `torlink ls` pokazuje
usługi, peerów i przekierowania. Tor obsługuje tylko TCP, a pierwsze
połączenie chwilę trwa. Port SOCKS kontenera (19050) nasłuchuje tylko na
loopbacku. Stan, łącznie z twoimi kluczami onion, leży w
`~/.local/share/torlink`, a `torlink purge` go usuwa.

## `pweb`: udostępnij folder przez HTTPS { #pweb-share-a-folder-over-https }

Serwuje **bieżący katalog** przez HTTPS na losowym wolnym porcie, żeby
przekazać plik innej maszynie w tej samej sieci. Certyfikat z własnym podpisem
powstaje przy pierwszym uruchomieniu i jest potem używany ponownie. Serwuje do
całego LAN, więc uruchamiaj go w folderze, który chcesz udostępnić, i
zatrzymuj przez Ctrl+C.

```
$ cd ~/Downloads && pweb
serving /home/you/Downloads
on https://yourhost:40123  (also https://localhost:40123)
```

## `select-server`: wybierz host SSH { #select-server-pick-an-ssh-host }

Numerowane menu wszystkich konkretnych aliasów `Host` z twojego
`~/.ssh/config`. Wybierz jeden, a narzędzie się połączy. Żeby filtrować,
oznacz hosty komentarzem `# tags: work prod` wewnątrz bloku `Host`:

```
$ select-server work            # only hosts tagged "work"
$ select-server --tags          # twoje tagi
$ select-server -f other.conf   # inny plik konfiguracyjny
```

## `tethering`: poprawka TTL { #tethering-the-ttl-fix }

Ustawia TTL 64 na ruchu przychodzącym z jednego interfejsu, więc urządzenia
podłączone przez tethering do tej maszyny wyglądają dla operatora, który
liczy przeskoki, jak własny ruch tej maszyny. Prosi o sudo, dodaje jedną
regułę mangle `iptables`, a reguła **nie** przetrwa restartu.

```
tethering            # wybierz interfejs, ustaw regułę
tethering --status
tethering --off
```
