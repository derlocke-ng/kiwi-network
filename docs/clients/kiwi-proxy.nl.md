# kiwi-proxy

kiwi-proxy is bedoeld voor mensen die in de netwerken van veel klanten werken en
elk netwerk via een eigen VPN- of SOCKS-verbinding bereiken. Je slaat elke
verbinding op als **exit** met een naam, en start die alleen als je hem nodig
hebt. Elke exit is afgeschermd van de andere, en een programma dat een exit
gebruikt, kan het netwerk alleen via die exit bereiken. Tien klanten betekenen
dus niet tien VPN-verbindingen tegelijk op de host. Browsers, testtools,
programma’s op de host en kiwi-server-machines kunnen een exit gebruiken.
kiwi-proxy draait in rootless Podman, dus in containers die zonder rootrechten
als je eigen gebruiker draaien.

- Repository: [derlocke-ng/kiwi-proxy](https://github.com/derlocke-ng/kiwi-proxy), GPL-3.0-or-later
- Nieuwste release: **v0.7.3**. Staat in de [Kiwi-catalogus](../desktop/catalogs.md), scope user.
- Bestaat uit een opdrachtregeltool (`kiwi-proxy`), een GTK4-app
  (**Kiwi Proxy**) en systemd-units voor je eigen gebruiker. Het is de
  proxy-engine die vroeger in kiwi-fox zat. Hij is naar een eigen project
  verhuisd, zodat meer dan één app hem kan gebruiken.

Een **exit** is een opgeslagen verbinding naar een upstream, met een eigen naam.
De upstream is de proxy waar het verkeer naartoe wordt gestuurd. Dat is een
SOCKS5-proxy die je hebt gekregen, of een die een [providermodule](providers.md)
voor je aanmaakt via Tor, een VPN-tunnel, 9proxy of Mysterium. Een exit op
zichzelf is alleen een opgeslagen item, en er draait niets voor. Start je een
exit, dan start kiwi-proxy er een **gateway**-container voor:

```
gateway container   owns the network namespace
                    nftables: default drop, one permitted destination
                    forwarder 127.0.0.1:1080: adds the upstream's credentials
                    dnscrypt-proxy 127.0.0.2:53: DNS through the same exit, with blocklists
```

De gateway-container heeft een eigen netwerk-namespace: een eigen set
netwerkinterfaces, adressen en routes, met eigen firewallregels. Een browser
van kiwi-fox, een box van kiwi-custodia of een container met tools sluit zich
bij deze namespace aan en wordt zo lid van de gateway. Vanaf dat moment leidt
de enige route naar de upstream van de exit. Valt de gateway uit, dan hebben
zijn leden geen route meer. Dat heet fail-closed: bij een storing valt de
verbinding weg, en er gaat nooit een andere weg open.

## Installeren { #install }

```bash
kiwi install kiwi-proxy      # kiwi-fox en kiwi-custodia nemen het mee
kiwi-proxy setup             # het gateway-image, DNS-gegevens, images van providermodules
```

kiwi-proxy heeft rootless Podman nodig en Python 3.12+ met pydantic. De app
heeft daarnaast GTK4 en libadwaita nodig. Wachtwoorden worden via `secret-tool`
in de sleutelbos van de desktop bewaard. Op een machine zonder sleutelbos komen
ze in bestanden met modus 0600, die alleen je eigen gebruiker kan lezen.

## Gebruiken { #use }

```bash
kiwi-proxy add client-a socks5://user:pass@host:1080   # een exit; er draait nog niets
kiwi-proxy add tor-de --module tor --country de        # een exit uit een providermodule
kiwi-proxy list
kiwi-proxy check client-a      # wat de buitenwereld erdoorheen ziet
kiwi-proxy up client-a         # de gateway starten en laten draaien
kiwi-proxy down client-a       # afbreken, samen met alles wat erop zit
kiwi-proxy ps                  # draaiende gateways, door welke app ook gestart
kiwi-proxy reap                # gateways opruimen die niemand gebruikt
kiwi-proxy-gui                 # "Kiwi Proxy" in het overzicht van apps
```

Een eindpunt is het adres van een upstream. Je schrijft het als
`socks5://user:pass@host:port`, `http://…` of `https://…`, of in het formaat
van de aanbieder, `host:port:user:pass`. `kiwi-proxy test ENDPOINT` test een
eindpunt zonder een exit aan te maken.

### Exits voor programma’s op de host { #exits-for-host-applications }

Een programma op de host hoeft niet in een container te draaien om een exit te
gebruiken. kiwi-proxy kan een exit als SOCKS5-poort op de host aanbieden, met
één poort per exit:

```bash
kiwi-proxy add se socks5://10.64.0.1:1080 --expose 1081
kiwi-proxy add nl socks5://10.65.0.1:1080 --expose 1082
kiwi-proxy up se && kiwi-proxy up nl
curl --proxy socks5h://127.0.0.1:1082 https://ifconfig.co/json
```

Standaard luistert de poort alleen op `127.0.0.1`. Laat je hem op een ander
adres luisteren, dan moet je ofwel met `--expose-user` een gebruikersnaam
instellen, ofwel met `--expose-open` uitdrukkelijk open toegang toestaan. Wil je
een exit actief hebben vanaf het moment dat je inlogt, voer dan
`systemctl --user enable --now kiwi-proxy@NAME` uit.

### DNS { #dns }

- **Resolver-modus** is de standaard. dnscrypt-proxy zoekt namen op met DNS over
  HTTPS (DoH) en stuurt die verzoeken via de exit. De DoH-resolver kan Google,
  Cloudflare, Quad9 of Mullvad zijn. Er worden blokkeerlijsten (OISD) toegepast,
  die dagelijks worden ververst.
- **Remote-modus** (`--dns remote`) geeft de namen door aan de upstream, die ze
  zelf opzoekt. Deze modus is bedoeld voor Tor en `.onion`-namen. Ook in deze
  modus gelden de blokkeerlijsten.

### Regels van de gateway { #rules-of-the-gateway }

- UDP wordt niet doorgestuurd. Dus geen QUIC, geen media via WebRTC en geen DNS
  in platte tekst.
- Een exit bereikt de buitenwereld alleen via IPv4. Een naam zonder IPv4-adres
  wordt geweigerd.
- Een gateway die door een andere app is gestart, zoals kiwi-fox of
  kiwi-custodia, wordt opgeruimd zodra het laatste lid weggaat. Een gateway die
  je met `kiwi-proxy up` hebt gestart, blijft draaien tot je
  `kiwi-proxy down` uitvoert.
- Elke exit heeft precies één gateway, en daar kunnen willekeurig veel leden bij
  aansluiten. Leden die van elkaar gescheiden moeten blijven, gebruiken
  verschillende exits.

## De app { #the-app }

In de app **Kiwi Proxy** voeg je exits toe en bewerk je ze, op basis van een
SOCKS5-proxy die je hebt gekregen of van een providermodule. Voor een exit uit
een module kies je uit een doorzoekbare lijst met landen of uit een lijst met
nodes. Je kunt exits starten en stoppen, een exit als SOCKS5-poort op deze
computer aanbieden en het adres kopiëren, en controleren wat de buitenwereld
ziet als je er verbinding via maakt. De app laat ook zien welke leden bij een
gateway zijn aangesloten en wat hun logs zijn, en je installeert en configureert
er providermodules mee.

## Op een kiwi-server-machine { #on-a-kiwi-server-machine }

In de repository van kiwi-proxy zit ook een module voor kiwi-server. Daarmee
biedt een kiwi-server-machine exits aan voor de hele mesh, het besloten
WireGuard-netwerk waarin al je kiwi-server-machines zitten. De module draait
één gateway per exit en biedt die aan op het mesh-adres van de host. Volgens de
documentatie zit de module nog niet in de broncode van kiwi-server en is ze nog
op geen enkele machine gedraaid. Providermodules werken alleen op de desktop en
draaien niet op een kiwi-server-machine.

Verder lezen: [architectuur](https://github.com/derlocke-ng/kiwi-proxy/blob/main/docs/architecture.md),
[gebruikers van kiwi-proxy](https://github.com/derlocke-ng/kiwi-proxy/blob/main/docs/consumers.md),
[pluginsysteem](https://github.com/derlocke-ng/kiwi-proxy/blob/main/docs/plugin-system.md).
