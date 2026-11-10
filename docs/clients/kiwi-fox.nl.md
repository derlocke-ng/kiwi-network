# kiwi-fox

Geïsoleerde browseridentiteiten in rootless Podman.

Elk profiel is één blijvende identiteit: een eigen opslag en meestal een
[kiwi-proxy](kiwi-proxy.md)-exit met zijn verzegelde gateway en resolver met
advertentieblokkering, in een van drie browsers. Voor een klantnetwerk betekent
dat een browser die de webconsoles van de klant bereikt via de exit van de klant,
en verder niets.

- Repository: [derlocke-ng/kiwi-fox](https://github.com/derlocke-ng/kiwi-fox), GPL-3.0-or-later
- Nieuwste release: **v0.7.1**. Het staat in de [Kiwi-catalogus](../desktop/catalogs.md), gebruikersscope.
- De engines worden opgehaald, nooit herverspreid: Camoufox (MPL-2.0) bij de
  setup, Firefox en Tor Browser op verzoek (`kiwi-fox engine fetch`), met
  gecontroleerde handtekening.

| Engine | Wat een pagina ziet |
|---|---|
| **Camoufox** (standaard) | een samenhangende, gewone Windows 11-machine met een eigen regio: een bevroren, vervalste vingerafdruk |
| **Firefox** | standaard Mozilla Firefox, die niets vervalst: de eigen waarden van deze machine, via dezelfde verzegelde exit |
| **Tor Browser** | Tor Browser, ongewijzigd, via een exit op de tor-module, met een circuit per site en `.onion`-namen |

kiwi-fox is voor mensen die meerdere accounts beheren die van hen zijn of die ze
mogen beheren, en die niet willen dat die accounts via browservingerafdruk of IP
aan elkaar gekoppeld worden.

## Installeren { #install }

```bash
kiwi install kiwi-fox      # neemt kiwi-proxy mee; of ./install.sh install
kiwi-fox setup             # images, een browserengine van ~630 MB, DNS-gegevens; draait ook de setup van kiwi-proxy
kiwi-fox engine fetch --engine firefox     # of torbrowser: met gecontroleerde handtekening
```

Het vereist rootless Podman en kiwi-proxy, een Wayland-sessie (X11 werkt met een
zwakkere grens), Python 3.12+, GTK4 + libadwaita, `secret-tool`, en
`gpg`/`gpgv` om Firefox en Tor Browser te controleren. Met de propriëtaire
NVIDIA-driver is ook `nvidia-container-toolkit` met zijn CDI-spec nodig.

## Gebruik { #use }

```bash
kiwi-proxy add client-a socks5://user:pass@host:1080   # een exit, één keer gedefinieerd, in kiwi-proxy
kiwi-fox new work --exit client-a     # een profiel erop: test de exit, kiest een passende identiteit
kiwi-fox new plain --no-proxy         # de eigen verbinding van deze machine, niets verzegeld
kiwi-fox list                         # --tag shop, --by-tag
kiwi-fox run work                     # of de app
kiwi-fox stop work
kiwi-fox check                        # is elk profiel nog samenhangend?
kiwi-fox selfcheck work               # meten wat pagina's zien, en dat daarna controleren
kiwi-fox-gui                          # "Kiwi Fox" in het app-overzicht
```

`--desktop-entry` zet een profiel in het app-overzicht, en tags groeperen
profielen.

## Profielen en exits { #profiles-and-exits }

Een profiel verwijst naar een exit, en exits worden gedeeld: profielen op één
exit delen de gateway ervan (één namespace, één exit-IP, één set Tor-circuits).
Identiteiten die geen exit mogen delen, nemen verschillende exits. Met
`--no-proxy` is er geen gateway: de browsercontainer heeft een eigen netwerk op
de verbinding van deze machine, en er is niets verzegeld.

De browsercontainer sluit aan op de namespace van de gateway, waarbij elke
capability is weggenomen behalve `SYS_CHROOT` (de eigen sandbox van Firefox heeft
die nodig). Hij draait met `no-new-privileges`, en de engine is alleen-lezen
gemount.

## Een Camoufox-profiel { #a-camoufox-profile }

Het is de meest voorkomende machine die er is, want zeldzame waarden zijn wat
detectoren opmerken: een scherm van 1920×1080, de lettertypen die elke Windows 11
heeft en geen andere, en de eigen grafische kaart van deze machine zoals Firefox
op Windows die benoemt. Regio, taal, tijdzone en stemmen volgen de exit. Alles kan
achteraf worden gewijzigd (`kiwi-fox set`, `kiwi-fox webgl`, `kiwi-fox fonts`),
en wijzigingen worden alleen opgeslagen als het resultaat samenhangend blijft.

## Wat het niet doet { #what-it-does-not-do }

Het belooft geen "onopspoorbaarheid". Profielen zijn geïsoleerd wat betreft
opslag, IP en elk oppervlak dat de engine kan vervalsen, maar **niet** tegen
cross-browser-identificatoren op hardwareniveau: de frames die de GPU echt tekent
en de timing van de hardware komen van de echte machine en zijn voor elk profiel
erop hetzelfde. `docs/detection-notes.md` in de repository documenteert wat er
gemeten wordt.

Er is geen automatisering: geen bots en geen massale aanmaak van accounts. Het is
alleen voor interactief browsen.
