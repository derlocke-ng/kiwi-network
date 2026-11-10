# Waar het naartoe gaat

Op deze pagina lees je wat kiwi-server volgens de plannen moet worden, en
welke delen van dat plan er al zijn.

!!! info "Ontworpen, nog niet gebouwd"
    Deze pagina vat het
    [ontwerp voor de control plane](https://github.com/derlocke-ng/kiwi-server/blob/main/docs/design/control-plane.md)
    van kiwi-server samen, waarover in oktober 2026 overeenstemming is bereikt.
    Niets van wat hier staat, bestaat al, tenzij er *gebouwd* bij staat. In de
    [roadmap](https://github.com/derlocke-ng/kiwi-server/blob/main/docs/ROADMAP.md)
    staat in welke volgorde het werk wordt gedaan.

Op dit moment is kiwi-server een programma voor de desktop. Het fleetbestand,
de secrets en de CA (de certificaatautoriteit van de fleet) staan op de
beheercomputer. Het plan is er een **dienst** van te maken die op een node kan
draaien. Je kunt een netwerk dan zonder Linux-desktop opzetten en beheren,
vanaf een telefoon en met meer dan één persoon. Machines blijven uit het fleetbestand
te reproduceren. De control plane is het deel dat dat bestand bewaart
en er de configuratie van elke machine uit genereert.

## De lagen { #the-layers }

Het ontwerp deelt de software op in vijf lagen.

1. **kiwi-modules** bevat de modules en het contract dat vastlegt hoe
   de configuratie van één machine wordt gegenereerd. *Gebouwd.*
2. **kiwi-stack** is het deel dat op de machine draait. Het begint met
   `kiwi-stack apply`, dat een gegenereerde configuratie op de machine zet.
   *Gebouwd.*
3. **De kern van kiwi-server** regelt de fleet, de hosts, de doelsystemen, de
   ISO’s, de CA, het toevoegen van apparaten en het toepassen van rollen. Hij
   is headless, dus zonder eigen grafische interface, net als nu. *Gebouwd.*
4. **De control-module** is die kern als container, met een API en een
   webinterface. Hij draait op een node als een module zoals elke andere.
5. **Clients** zijn de programma’s waarmee je met de control-module werkt. De
   webinterface komt eerst. De GTK-app blijft, en praat ofwel met de lokale
   CLI, ofwel via de mesh, het besloten WireGuard-netwerk, met een controller
   (een draaiende control-module). Ook de CLI blijft. Alle logica blijft in de
   kern, dus geen enkele client krijgt eigen logica.

## De control-node { #the-control-node }

De controller draait op een node thuis, de *control-node*. Alleen beheerders
kunnen erbij, en dan nog alleen vanuit de mesh. De schijf is versleuteld. Op de
control-node staan de seed, de sleutel van de CA, het fleetbestand en elke
configuratie.

De gehuurde **master wordt een vervangbaar doorgeefluik**. Hij stuurt het
verkeer van het netwerk door en heeft alleen wat hij nodig heeft om te draaien:
zijn WireGuard-sleutels en peers, zijn eigen wachtwoorden en zijn certificaat.
Raak je de master kwijt, dan pas je hem vanaf de control-node opnieuw toe. Raak
je de control-node kwijt, dan zet je de back-up van de fleet terug.

## Gebruikers { #users }

Met een blok `users:` leg je gebruikers vast, elk met een van twee rollen. Een
**fleetbeheerder** mag alles. Een **nodebeheerder** is gebonden aan zijn eigen
hosts. Hij ziet de status, logs, workloads en back-ups van die hosts, en kan
apparaten toevoegen aan de groepen die de fleetbeheerder toestaat. Van de
master, de CA en de andere nodes ziet een nodebeheerder niets. Om in te loggen
heeft een gebruiker een wachtwoord nodig, plus een clientcertificaat van de CA
van de fleet of WebAuthn. Elke wijziging wordt in een auditlog vastgelegd.

## Een machine aansluiten { #joining-a-machine }

Een machine kan op twee manieren bij het netwerk komen, en beide blijven
bestaan:

- **Een ISO per host** waarop de rol van de machine staat, zoals nu met
  `build --offline`. Die is bedoeld voor installaties zonder netwerk.
- **Een algemene bootstrap-ISO** per doelsysteem, die één keer door CI wordt
  gebouwd en geen secrets bevat. Bij de eerste keer opstarten haalt de machine
  haar rol bij de controller op met een eenmalig **join-token**. Een machine die
  met de hand is geïnstalleerd, of een VPS, sluit aan met één regel:
  `curl https://control.<host>.<tld>/join/<token> | sudo bash`.

Alle machines uit de CoreOS-familie moeten **één bootc-image** gaan draaien,
een opstartbaar containerimage dat voor allemaal hetzelfde is. De machine
krijgt haar rol bij de eerste keer opstarten.

## Federatie en multi-hop { #federation-and-multi-hop }

Federatie verbindt afzonderlijke Kiwi Networks met elkaar. Netwerken die
elkaars CA vertrouwen en namen aan elkaar delegeren, worden clients van elkaar.
Een master heeft drie uitgangsmodi, die bepalen hoe zijn verkeer op internet
komt. Bij de derde stuurt de master van een netwerk zijn internetverkeer via de
master van een ander netwerk. Dat heet **multi-hop**, en de tweede master ziet
alleen de eerste. Wie op deze manier meerdere masters draait, heeft een eigen
VPN-dienst, met ingangsmasters in het ene land, uitgangsmasters in andere
landen, en Tor binnen het netwerk.

## De orchard { #the-orchard }

De orchard (Engels voor boomgaard) is de geplande dienst voor mensen die veel
masters voor anderen draaien. Het wordt een aparte app of een plug-in voor
kiwi-server. De orchard maakt VPS’en aan via de API’s van de hostingproviders
en geeft elke master zijn installatie en een registratietoken. Van elke master
ontvangt hij een heartbeat, een regelmatig statusbericht (versie, gezondheid,
schijf, laatste update). Updates rolt hij uit door de image-tag van elk
updatekanaal te verschuiven.

De orchard kan niet inloggen op een master, geen fleet lezen en geen node
wijzigen. Elke tenant, dat wil zeggen iedereen voor wie een master wordt
gedraaid, houdt zijn netwerk op zijn eigen control-node thuis. De fleet en de
sleutels blijven daar, zodat de hostingprovider die de VM van de master draait
de netwerkgegevens van de tenant niet kan lezen. De master van elke tenant
draait in een eigen VM. De orchard heeft een driver nodig voor de API’s van de
providers, en de ondersteuning voor netcup in kiwi-server (`kiwi-server vps`,
*gebouwd*) is daar het eerste stuk van.

## Meer hostingproviders, en opstarten via het netwerk { #more-hosters-and-network-boot }

*Gepland.* Het doel is dat een machine volledig automatisch kan worden
geïnstalleerd, waar ze ook staat.

- **Hostingproviders als plug-ins.** De ondersteuning voor netcup is nu
  ingebouwd. Het plan is een aparte repository voor de API’s van de providers,
  zodat iedereen AWS, Hetzner en andere providers kan toevoegen. Een plug-in
  zou werken zoals de ondersteuning voor netcup nu: hij maakt een server aan of
  wist hem, zet de installatie erop en start hem op.
- **Wake-on-LAN en opstarten via PXE** zijn gepland voor machines thuis. Met
  Wake-on-LAN zet je een machine via het netwerk aan, en met PXE start ze op
  vanaf het netwerk. Een node wordt dan wakker en installeert zichzelf via het
  netwerk, zonder USB-stick.

## Verder op de lijst { #also-on-the-list }

Op de roadmap staan ook een reservemaster (standby), rootless podman, IPv6 van
begin tot eind, ARM-borden, poortbereiken en een module voor games, en het
terugzetten van de gegevens van een node bij de eerste keer opstarten.
