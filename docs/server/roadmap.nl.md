# Waar het heen gaat

!!! info "Ontworpen, niet gebouwd"
    Deze pagina vat het
    [control-plane-ontwerp](https://github.com/derlocke-ng/kiwi-server/blob/main/docs/design/control-plane.md)
    van kiwi-server samen, vastgesteld in oktober 2026. Tenzij er bij een regel
    *gebouwd* staat, bestaat er nog niets van. De
    [roadmap](https://github.com/derlocke-ng/kiwi-server/blob/main/docs/ROADMAP.md)
    houdt de volgorde bij.

Vandaag is kiwi-server een desktoptool: het fleet-bestand, de geheimen en de CA
staan op de machine van de beheerder. Het plan is er een **dienst** van te maken
die op een node kan draaien, zodat een netwerk kan worden aangemaakt en beheerd
zonder Linux-desktop, vanaf een telefoon, en door meer dan één persoon. Machines
blijven reproduceerbaar uit het fleet-bestand. Het control plane is alleen wat dat
bestand bewaart en de renderer draait.

## De lagen { #the-layers }

1. **kiwi-modules**: de modules en het rendercontract voor één machine. *Gebouwd.*
2. **kiwi-stack**: de kant van de machine, vanaf `kiwi-stack apply`. *Gebouwd.*
3. **kiwi-server core**: de fleet, hosts, targets, ISO's, de CA, aanmelden en
   toepassen, headless zoals vandaag. *Gebouwd.*
4. **De control-module**: de core als container, met een API en een webinterface,
   die als module op een node draait zoals elke andere.
5. **Clients**: eerst de webinterface. De GTK-app blijft en praat met de lokale
   CLI of met een controller via de mesh, en de CLI blijft ook. Geen enkele
   frontend krijgt eigen logica.

## De control node { #the-control-node }

De controller draait op een node thuis (de *control node*), vanuit de mesh alleen
bereikbaar voor beheerders, op een versleutelde schijf. Hij bewaart de seed, de
CA-sleutel, het fleet-bestand en elke configuratie.

De gehuurde **master wordt vervangbare relay-infrastructuur**. Hij bewaart alleen
wat hij nodig heeft om te draaien: zijn WireGuard-sleutels en peers, zijn eigen
wachtwoorden en zijn certificaat. Hem verliezen kost een nieuwe apply vanaf de
control node. De control node verliezen kost een restore van de fleet-back-up.

## Gebruikers { #users }

Een `users:`-blok met twee rollen: een **fleet-beheerder** die alles kan, en
**node-beheerders** die aan hun eigen hosts gebonden zijn. Een node-beheerder ziet
de status, logs, workloads en back-ups van die hosts, en meldt apparaten aan in de
groepen die de fleet-beheerder toestaat, maar ziet niets van de master, de CA of
de andere nodes. Inloggen gebeurt met een wachtwoord plus een clientcertificaat
van de fleet-CA of WebAuthn, en elke wijziging gaat naar een auditlog.

## Een machine toevoegen { #joining-a-machine }

Beide wegen blijven:

- **Een ISO per host** met zijn rol (het huidige `build --offline`), voor
  offline installaties.
- **Een generieke bootstrap-ISO** per target, één keer gebouwd door CI en zonder
  geheimen. Bij de eerste start haalt hij zijn rol op bij de controller met een
  eenmalig **join-token**. Een met de hand geïnstalleerde machine of een VPS komt
  erbij met één regel: `curl https://control.<host>.<tld>/join/<token> | sudo bash`.

Elke machine uit de CoreOS-lijn moet **één bootc-image** gaan draaien, waarbij de
rol bij de eerste start binnenkomt.

## Federatie en multi-hop { #federation-and-multi-hop }

Netwerken die elkaars CA vertrouwen en namen aan elkaar delegeren, worden clients
van elkaar. Met de derde exit-modus kan de master van het ene netwerk het
internet op via die van een ander: **multi-hop**, waarbij de tweede master alleen
de eerste ziet. Meerdere masters van één beheerder vormen dan een eigen
VPN-dienst: ingangsmasters in het ene land, exit-masters in andere, met Tor
erbinnen.

## De boomgaard { #the-orchard }

De boomgaard (orchard) is voor mensen die veel masters voor anderen draaien. Het
is een aparte app of een kiwi-server-plugin die VPS'en aanmaakt via API's van
providers, elke master zijn installatie en een registratietoken geeft, van elke
master een heartbeat verzamelt (versie, gezondheid, schijf, laatste update), en
updates uitrolt door image-tags per kanaal te verplaatsen.

Hij kan niet inloggen op een master, geen fleet lezen en geen node aanraken. De
control node van elke tenant thuis houdt diens netwerk. De host van de master kan
het niet lezen, en draait één VM per tenant. De netcup-ondersteuning van
kiwi-server (`kiwi-server
vps`, *gebouwd*) is het eerste stuk van zijn providerdriver.

## Ook op de lijst { #also-on-the-list }

Een stand-by-master, rootless podman, IPv6 van begin tot eind, ARM-borden,
poortbereiken en een games-module, en een restore van de gegevens van een node
bij de eerste start.
