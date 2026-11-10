# kiwi-cli-tools-desktop

Vier kleine hulpmiddelen voor de opdrachtregel op een Linux-desktop.

- Repository: [derlocke-ng/kiwi-cli-tools-desktop](https://github.com/derlocke-ng/kiwi-cli-tools-desktop), GPL-3.0-or-later
- Nieuwste release: **v1.2.1**. Het staat in de [Kiwi-catalogus](catalogs.md), gebruikersscope.

```bash
kiwi install kiwi-cli-tools-desktop   # of ./install.sh install, naar ~/.local/bin
```

## `torlink`: een machine bereiken via Tor { #torlink-reach-a-machine-over-tor }

Een VPN voor de arme man: bereik elke TCP-dienst (SSH, een webinterface, een
database) op een andere machine via Tor, zonder open poorten, zonder accounts en
zonder server. Tor en socat draaien in één rootless Podman-container, dus Podman
is alles wat je nodig hebt.

Een onion-adres is de identiteit. De aanbiedende kant maakt een
**uitnodigingscode** voor één peer, en de andere kant accepteert die. De code
bevat een sleutel voor Tor-clientautorisatie, zodat de dienst onzichtbaar is
voor iedereen die hem niet heeft: behandel de code als een wachtwoord.

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

Elke uitnodiging is een eigen onion-dienst met alleen de diensten die je hebt
opgegeven, dus `torlink revoke bob` haalt die toegang definitief weg.
`torlink ls` toont diensten, peers en doorverwijzingen. Tor is alleen TCP, en de
eerste verbinding duurt even. De SOCKS-poort van de container (19050) luistert
alleen op loopback. De status, inclusief je onion-sleutels, staat in
`~/.local/share/torlink`, en `torlink purge` verwijdert hem.

## `pweb`: een map delen via HTTPS { #pweb-share-a-folder-over-https }

Serveert de **huidige map** via HTTPS op een willekeurige vrije poort, om een
bestand aan een andere machine op hetzelfde netwerk te geven. Bij de eerste
start wordt een zelfondertekend certificaat gemaakt en daarna hergebruikt. Het
serveert aan het hele LAN, dus start het in de map die je wilt delen en stop het
met Ctrl+C.

```
$ cd ~/Downloads && pweb
serving /home/you/Downloads
on https://yourhost:40123  (also https://localhost:40123)
```

## `select-server`: een SSH-host kiezen { #select-server-pick-an-ssh-host }

Een genummerd menu met elke concrete `Host`-alias in je `~/.ssh/config`. Kies er
een en het maakt verbinding. Geef hosts tags met een commentaar `# tags: work prod`
binnen het `Host`-blok om te filteren:

```
$ select-server work            # alleen hosts met de tag "work"
$ select-server --tags          # de tags die je hebt
$ select-server -f other.conf   # een ander configuratiebestand
```

## `tethering`: de TTL-fix { #tethering-the-ttl-fix }

Zet TTL 64 op verkeer dat binnenkomt via één interface, zodat apparaten die via
deze machine tetheren eruitzien als het eigen verkeer van de machine voor een
provider die hops telt. Het vraagt om sudo, voegt één mangle-regel voor
`iptables` toe, en de regel overleeft een herstart **niet**.

```
tethering            # kies de interface, zet de regel
tethering --status
tethering --off
```
