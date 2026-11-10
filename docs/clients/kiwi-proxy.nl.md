# kiwi-proxy

Verzegelde SOCKS5- en VPN-exits in rootless Podman, voor browsers, testtools,
applicaties op de host en kiwi-server-machines.

- Repository: [derlocke-ng/kiwi-proxy](https://github.com/derlocke-ng/kiwi-proxy), GPL-3.0-or-later
- Nieuwste release: **v0.7.3**. Het staat in de [Kiwi-catalogus](../desktop/catalogs.md), gebruikersscope.
- Een CLI (`kiwi-proxy`), een GTK4-app (**Kiwi Proxy**) en systemd-gebruikersunits.
  Het is de proxy-engine die vroeger in kiwi-fox zat, afgesplitst zodat hij meer
  dan één app bedient.

Een **exit** is één upstream, met een naam: een SOCKS5 die je hebt gekregen, of
een die een [providermodule](providers.md) maakt (Tor, een VPN-tunnel, 9proxy,
Mysterium). Een exit is alleen gegevens. Als je hem opstart, ontstaat er een
**gateway**:

```
gateway container   owns the network namespace
                    nftables: default drop, one permitted destination
                    forwarder 127.0.0.1:1080: adds the upstream's credentials
                    dnscrypt-proxy 127.0.0.2:53: DNS through the same exit, with blocklists
```

Wat zich ook bij de namespace van de gateway voegt (een kiwi-fox-browser, een
kiwi-custodia-box, een toolcontainer), heeft geen andere route dan die upstream.
Als de gateway uitvalt, verliezen zijn leden hun route.

## Installeren { #install }

```bash
kiwi install kiwi-proxy      # kiwi-fox en kiwi-custodia nemen het mee
kiwi-proxy setup             # de gateway-image, DNS-gegevens, images van providermodules
```

Het vereist rootless Podman, Python 3.12+ met pydantic, en GTK4 + libadwaita voor
de app. Wachtwoorden gaan naar de sleutelbos van de desktop (`secret-tool`), of
naar bestanden met 0600 op een machine zonder sleutelbos.

## Gebruik { #use }

```bash
kiwi-proxy add client-a socks5://user:pass@host:1080   # een exit; er draait nog niets
kiwi-proxy add tor-de --module tor --country de        # een exit van een providermodule
kiwi-proxy list
kiwi-proxy check client-a      # wat de wereld erdoorheen ziet
kiwi-proxy up client-a         # de gateway starten en laten draaien
kiwi-proxy down client-a       # hem afbreken, met iedereen die aansloot
kiwi-proxy ps                  # draaiende gateways, welke app ze ook startte
kiwi-proxy reap                # gateways afbreken die niemand gebruikt
kiwi-proxy-gui                 # "Kiwi Proxy" in het app-overzicht
```

Endpoints zijn `socks5://user:pass@host:port`, `http://…`, `https://…`, of het
leveranciersformaat `host:port:user:pass`. `kiwi-proxy test ENDPOINT` test er een
zonder iets aan te maken.

### Exits voor applicaties op de host { #exits-for-host-applications }

Elk programma op de host kan een exit gebruiken via een gepubliceerde
SOCKS5-poort, één poort per exit:

```bash
kiwi-proxy add se socks5://10.64.0.1:1080 --expose 1081
kiwi-proxy add nl socks5://10.65.0.1:1080 --expose 1082
kiwi-proxy up se && kiwi-proxy up nl
curl --proxy socks5h://127.0.0.1:1082 https://ifconfig.co/json
```

De poort luistert standaard op `127.0.0.1`. Een ander adres vereist een
gebruikersnaam (`--expose-user`) of een expliciete `--expose-open`.
`systemctl --user enable --now kiwi-proxy@NAME` houdt een exit vanaf het inloggen
in de lucht.

### DNS { #dns }

- **Resolvermodus** (de standaard): dnscrypt-proxy zoekt op via DoH door de exit
  (Google, Cloudflare, Quad9 of Mullvad als upstream), met blokkeerlijsten (OISD)
  die dagelijks worden ververst.
- **Remote-modus** (`--dns remote`): namen gaan naar de upstream zelf, voor Tor
  en `.onion`-namen. De blokkeerlijsten gelden nog steeds.

### Regels van de gateway { #rules-of-the-gateway }

- UDP kan nergens heen: geen QUIC, geen WebRTC-media, geen DNS in platte tekst.
- Voor de wereld is een exit IPv4. Een naam zonder IPv4-adres wordt geweigerd.
- Een gateway die een gebruiker opstartte, verdwijnt wanneer zijn laatste lid
  vertrekt. Een gateway die met `kiwi-proxy up` is gestart, blijft tot
  `kiwi-proxy down`.
- Eén exit, één gateway, een willekeurig aantal leden. Leden die gescheiden moeten
  blijven, gebruiken verschillende exits.

## De app { #the-app }

**Kiwi Proxy** voegt exits toe en bewerkt ze (een SOCKS5 die je hebt gekregen, of
een providermodule, met een doorzoekbare landenlijst of nodekiezer), start en
stopt ze, biedt er een aan als SOCKS5-poort op deze computer en kopieert het adres
ervan, controleert wat de wereld ziet, toont wie zich bij een gateway heeft
gevoegd en hun logs, en installeert en configureert providermodules.

## Op een kiwi-server-machine { #on-a-kiwi-server-machine }

kiwi-proxy bevat ook een kiwi-server-module die exits voor de hele mesh host (één
gateway per exit, gepubliceerd op het mesh-adres van de host). Die staat nog niet
in de boom van kiwi-server en heeft nog niet op een machine gedraaid, zoals de
documentatie ervan zegt. Providermodules zijn een desktopmechanisme en draaien
daar niet.

Verder lezen: [architectuur](https://github.com/derlocke-ng/kiwi-proxy/blob/main/docs/architecture.md),
[consumers](https://github.com/derlocke-ng/kiwi-proxy/blob/main/docs/consumers.md),
[pluginsysteem](https://github.com/derlocke-ng/kiwi-proxy/blob/main/docs/plugin-system.md).
