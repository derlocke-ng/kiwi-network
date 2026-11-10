# kiwi-fox

kiwi-fox geeft je een aparte browser voor elk klantnetwerk waarin je werkt, en
voor elk account dat je beheert. Het browserprofiel voor een klant bereikt de
webconsoles van die klant via diens eigen verbinding, en kan nergens anders
heen. Een VPN-verbinding op de host heb je daarvoor niet nodig.

Elk profiel is één blijvende identiteit. Het heeft een eigen opslag, draait een
van drie browsers in een rootless Podman-container (een container die zonder
rootrechten als je eigen gebruiker draait), en gebruikt meestal een exit van
[kiwi-proxy](kiwi-proxy.md). Een exit is een opgeslagen verbinding naar een
upstream, met een eigen naam, zoals de SOCKS5-proxy van een klant. Voor elke
exit draait kiwi-proxy een gateway-container. De enige route uit de gateway
leidt naar die upstream, en er zit een DNS-resolver in die reclamedomeinen
blokkeert.

- Repository: [derlocke-ng/kiwi-fox](https://github.com/derlocke-ng/kiwi-fox), GPL-3.0-or-later
- Nieuwste release: **v0.7.1**. Staat in de [Kiwi-catalogus](../desktop/catalogs.md), scope user.
- De browsers, die kiwi-fox engines noemt, worden naar je machine gedownload en
  nooit verder verspreid. Camoufox (MPL-2.0) wordt tijdens de setup gedownload.
  Firefox en Tor Browser worden gedownload als je erom vraagt
  (`kiwi-fox engine fetch`), en hun handtekeningen worden gecontroleerd.

| Engine | Wat een pagina ziet |
|---|---|
| **Camoufox** (standaard) | Een gewone Windows 11-machine met een eigen regio, waarvan alle waarden bij elkaar passen. Deze fingerprint (de waarden die een pagina uit een browser kan lezen om hem te herkennen) is vervalst en verandert niet |
| **Firefox** | Ongewijzigde Mozilla Firefox, die niets vervalst. Een pagina ziet de eigen waarden van deze machine. De verbinding gaat wel via de exit van het profiel |
| **Tor Browser** | Ongewijzigde Tor Browser, verbonden via een exit op de module tor. Elke site krijgt een eigen circuit (een eigen pad door het Tor-netwerk), en `.onion`-namen werken |

kiwi-fox is bedoeld voor mensen die meerdere accounts beheren die van henzelf
zijn of waarvoor ze toestemming hebben, en die niet willen dat die accounts via de fingerprint
van de browser of het IP-adres aan elkaar te koppelen zijn.

## Installeren { #install }

```bash
kiwi install kiwi-fox      # neemt kiwi-proxy mee; of ./install.sh install
kiwi-fox setup             # images, een browser-engine van ~630 MB, DNS-gegevens; voert ook de setup van kiwi-proxy uit
kiwi-fox engine fetch --engine firefox     # of torbrowser: met gecontroleerde handtekening
```

kiwi-fox heeft rootless Podman nodig, kiwi-proxy, Python 3.12+, GTK4 met
libadwaita, en `secret-tool`. Het is gemaakt voor een Wayland-sessie. X11 werkt
ook, maar daar is de afscherming zwakker. Om Firefox en Tor Browser te
verifiëren, zijn `gpg`/`gpgv` nodig. Met de propriëtaire NVIDIA-driver heeft
kiwi-fox ook `nvidia-container-toolkit` met de bijbehorende CDI-spec nodig.

## Gebruiken { #use }

```bash
kiwi-proxy add client-a socks5://user:pass@host:1080   # een exit, één keer vastgelegd, in kiwi-proxy
kiwi-fox new work --exit client-a     # een profiel erop: meet de exit, kiest een passende identiteit
kiwi-fox new plain --no-proxy         # de eigen verbinding van deze machine, niets afgeschermd
kiwi-fox list                         # --tag shop, --by-tag
kiwi-fox run work                     # of via de app
kiwi-fox stop work
kiwi-fox check                        # klopt elk profiel nog?
kiwi-fox selfcheck work               # meten wat pagina’s zien, en dat daarna nalopen
kiwi-fox-gui                          # "Kiwi Fox" in het overzicht van apps
```

Met `--desktop-entry` krijgt een profiel een eigen item in het overzicht van
apps. Met tags kun je profielen groeperen.

## Profielen en exits { #profiles-and-exits }

Een profiel heeft geen eigen exit. Het verwijst naar een exit, en meerdere
profielen kunnen naar dezelfde exit verwijzen. Profielen op dezelfde exit delen
de gateway ervan, en daarmee één netwerk-namespace, één IP-adres naar buiten en
één set Tor-circuits. Identiteiten die geen exit mogen delen, hebben
verschillende exits nodig. Een profiel dat met `--no-proxy` is aangemaakt, heeft
geen gateway. De browsercontainer heeft dan een eigen netwerk en gebruikt de
eigen verbinding van deze machine. In dat geval is er niets afgeschermd: het
verkeer is niet tot één route beperkt.

De browsercontainer sluit zich aan bij de netwerk-namespace van de gateway. Op
`SYS_CHROOT` na, die de eigen sandbox van Firefox nodig heeft, krijgt de
container geen enkele Linux-capability. De container draait met `no-new-privileges`, en
de engine is alleen-lezen gekoppeld.

## Een Camoufox-profiel { #a-camoufox-profile }

Een Camoufox-profiel doet zich voor als de meest voorkomende machine die er is,
want detectiesystemen slaan aan op waarden die zeldzaam zijn. Het meldt een
scherm van 1920×1080, precies de lettertypen die elke installatie van Windows 11
heeft, en de eigen grafische kaart van deze machine, genoemd zoals Firefox op
Windows haar noemt. Regio, taal, tijdzone en stemmen worden passend bij de exit
ingesteld. Dat alles kun je achteraf aanpassen met `kiwi-fox set`,
`kiwi-fox webgl` en `kiwi-fox fonts`. Een wijziging wordt alleen opgeslagen als
het profiel consistent blijft, dus als de waarden nog bij elkaar passen.

## Wat het niet doet { #what-it-does-not-do }

kiwi-fox belooft niet dat een profiel “niet te detecteren” is. Profielen zijn van
elkaar gescheiden in hun opslag, hun IP-adres en elke waarde die de engine kan
vervalsen. Ze zijn **niet** gescheiden in kenmerken die van de hardware komen
en in elke browser hetzelfde zijn. De beelden die de GPU echt tekent en de
timing van de hardware komen van de echte machine, dus die zijn voor elk
profiel op die machine gelijk. Wat er wordt gemeten, staat in het bestand
`docs/detection-notes.md` in de repository.

kiwi-fox heeft geen automatisering. Het draait geen bots en maakt niet in bulk
accounts aan. Het is alleen gemaakt om zelf te browsen.
