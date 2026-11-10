# kiwi-cli-tools-desktop

kiwi-cli-tools-desktop is een pakket met vier kleine opdrachtregeltools voor een
Linux-desktop. Met `torlink` bereik je een dienst op een andere machine via Tor,
`pweb` deelt een map via HTTPS, met `select-server` kies je een SSH-host uit een
menu, en `tethering` past de TTL aan van verkeer van apparaten die via deze
machine internetten.

- Repository: [derlocke-ng/kiwi-cli-tools-desktop](https://github.com/derlocke-ng/kiwi-cli-tools-desktop), GPL-3.0-or-later
- Nieuwste release: **v1.2.1**. Staat in de [Kiwi-catalogus](catalogs.md), scope user.

```bash
kiwi install kiwi-cli-tools-desktop   # of ./install.sh install, naar ~/.local/bin
```

## `torlink`: een machine via Tor bereiken { #torlink-reach-a-machine-over-tor }

Met `torlink` bereik je elke TCP-dienst op een andere machine, zoals SSH, een
webinterface of een database, via het Tor-netwerk. Het is een eenvoudig
alternatief voor een VPN: geen van beide machines heeft een open poort nodig,
je hebt geen account nodig en er is geen server die je moet draaien. Tor en
socat draaien samen in één rootless Podman-container, dus je hebt alleen Podman
nodig.

Een machine die diensten aanbiedt, is te vinden via haar onion-adres, een adres
binnen het Tor-netwerk. Op die machine maak je een **uitnodigingscode** voor één
peer, de andere partij die toegang moet krijgen. De peer accepteert de code op
de andere machine. In de code zit een sleutel voor clientautorisatie van Tor.
Zonder die sleutel kan niemand zien dat de dienst bestaat, dus behandel de code
als een wachtwoord.

```bash
# machine A: SSH en een webinterface aanbieden aan "bob"
torlink add-service ssh 22
torlink add-service web 8080
torlink invite bob ssh web          # toont torlink1:…  (geheim!)

# machine B: ze gebruiken
torlink accept torlink1:… alice
torlink up
torlink ssh alice                   # SSH via Tor
torlink connect alice web           # 127.0.0.1:2200 → de webinterface van alice
torlink ssh-config >> ~/.ssh/config # daarna `ssh alice-tor`; `select-server tor` toont ze
```

Elke uitnodiging is een aparte onion-service met alleen de diensten die je erin
hebt opgenomen. Daarom trekt `torlink revoke bob` die toegang definitief in.
`torlink ls` toont je diensten, je peers en je doorverwijzingen: de lokale
poorten die naar de diensten van een peer leiden. Tor vervoert alleen TCP, en
de eerste verbinding duurt even. De SOCKS-poort van de container (19050)
luistert alleen op de loopback-interface. Alles wat `torlink` bewaart,
inclusief je onion-sleutels, staat in `~/.local/share/torlink`, en
`torlink purge` wist het.

## `pweb`: een map delen via HTTPS { #pweb-share-a-folder-over-https }

`pweb` biedt de **huidige map** via HTTPS aan op een willekeurige vrije poort.
Daarmee geef je snel een bestand door aan een andere machine in hetzelfde
netwerk. De eerste keer maakt `pweb` een zelfondertekend certificaat aan, en
daarna gebruikt het dat certificaat opnieuw. Zolang `pweb` draait, kan elke
machine in het lokale netwerk bij de map. Start het in de map die je echt wilt
delen, en stop het met Ctrl+C.

```
$ cd ~/Downloads && pweb
serving /home/you/Downloads
on https://yourhost:40123  (also https://localhost:40123)
```

## `select-server`: een SSH-host kiezen { #select-server-pick-an-ssh-host }

`select-server` toont een genummerd menu met elke concrete `Host`-alias uit je
`~/.ssh/config`, dus elke alias die geen jokertekenpatroon is. Kies er een, en
het programma maakt verbinding met die host. Wil je het menu filteren, geef je
hosts dan tags. Zet een commentaar zoals `# tags: work prod` in het
`Host`-blok, en geef een tag mee op de opdrachtregel:

```
$ select-server work            # alleen hosts met de tag "work"
$ select-server --tags          # de tags die je gebruikt
$ select-server -f other.conf   # een ander configuratiebestand
```

## `tethering`: de TTL instellen voor gedeelde verbindingen { #tethering-the-ttl-fix }

`tethering` is bedoeld voor als andere apparaten de internetverbinding van deze
machine gebruiken, wat tethering heet. Sommige providers tellen hoeveel
hops het verkeer heeft gemaakt, en zien daaraan welk verkeer van meeliftende
apparaten komt en welk van de machine zelf. `tethering` zet de TTL op 64 voor
al het verkeer dat via één interface binnenkomt. Voor de provider ziet het
verkeer van de meeliftende apparaten er dan uit als verkeer van de machine
zelf. Het programma vraagt om sudo en voegt één mangle-regel aan `iptables`
toe. Na een herstart is de regel **niet** meer aanwezig.

```
tethering            # interface kiezen, regel instellen
tethering --status
tethering --off
```
