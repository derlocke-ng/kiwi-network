# De apps van het framework

kiwi-framework is de software waarmee een community haar eigen hub draait. Op
deze pagina staan de tien apps die erbij horen, waaronder een open markt, een
feed voor de community, chat en bestanden delen.

Het framework geeft zijn apps eenvoudige namen, zoals `market`. Een distributie,
dat is één bepaalde hub die met het framework is gebouwd, **koppelt** de apps
die ze wil hebben. Een app koppelen betekent: de app gebruiken voor één space,
een community met eigen moderatoren en relays, en haar een naam van de hub zelf
geven. Eén app kan vele keren worden gekoppeld. Een zadenbank en een
edelstenenwinkel zijn bijvoorbeeld dezelfde `market`-code op twee spaces. Elk
heeft eigen moderatoren en relays, en ze verschijnen als twee tegels op één hub.

| App | Wat het is | Naam in Armory |
|---|---|---|
| `market` | **Een open markt** voor de community die een mount bedient. Een advertentie heeft foto’s, een prijs, en ofwel de plaatsen van waaruit en waarnaartoe wordt verzonden, ofwel de mogelijkheid om het op te halen. Kopers vinden advertenties op categorie en op hun eigen locatie. De zoekfunctie gebruikt labels die relays wel kunnen vergelijken, maar niet kunnen lezen. Een koper schrijft de verkoper in de chat, waar al een bericht over de advertentie klaarstaat. Een advertentie kan worden gereserveerd, als verkocht gemarkeerd, verlengd en gemeld, en verloopt na 30 tot 90 dagen. Een mount kan eisen dat verkopers eerst actief zijn geweest in een feed of door een moderator zijn goedgekeurd. | Trading Post |
| `feed` | **Een feed voor de community.** Mensen plaatsen berichten met foto’s en hashtags, en anderen kunnen die liken en erop reageren. Een bericht kan bedoeld zijn voor de hele space, voor je vrienden, voor één kring (een groep van je vrienden) of alleen voor jou. Een dagboek is een reeks berichten met een omslag. Berichten kunnen als 18+ of als advertentie worden gemarkeerd. | Outpost |
| `chat` | **Berichten.** Je stuurt privéberichten en bestanden naar vrienden (NIP-17). Groepen bestaan tot degene die ze heeft aangemaakt ze sluit, en live-kamers verdwijnen zodra de laatste persoon weg is. De chat kent antwoorden, reacties, bewerken, vastgezette berichten, zoeken op het apparaat en verdwijnende berichten. Spraak- en videogesprekken werken met maximaal zes mensen. | Uplink |
| `notices` | **Een prikbord** voor openbare briefjes. Elk briefje is ondertekend door de schrijver en vraagt proof of work: een kleine berekening die het massaal plaatsen van briefjes duur maakt. Op briefjes kan worden gestemd, ze kunnen worden gemeld, en ze verlopen. | DevBoard |
| `boards` | **Gedeelde lijsten en notities.** Dat zijn checklists, voorraadlijsten met aantallen en notities in Markdown. Ze zijn end-to-end versleuteld, en je deelt ze met links waarmee de ander kan bewerken of alleen kan bekijken. | Loadout |
| `payload` | **Bestanden delen** op drie manieren: als link naar bestanden die versleuteld op je mediaservers staan, als bestanden die je naar vrienden en groepen stuurt, of rechtstreeks van de ene browser naar de andere. | Payload |
| `vault` | **Een wachtwoordbeheerder** voor logins, notities, kaarten en tweestapscodes. Hij heeft een wachtwoordgenerator en een gezondheidsrapport. Daarnaast beheert hij SSH-sleutels, een SSH-CA, een X.509-CA en TLS-certificaten. Hij is versleuteld met een eigen wachtzin. | Vault |
| `authenticator` | **Tweestapscodes** (TOTP). Ze staan in dezelfde versleutelde kluis als de items van de wachtwoordbeheerder. | Authenticator |
| `calendar` | **Je agenda’s** uit Nextcloud of een andere CalDAV-server. Er gaat niets naar relays. | Calendar |
| `pong` | **Pong voor twee spelers**, tussen twee browsers. | pongjs |

Elke hub heeft daarnaast een startpagina, een accountpagina en een pagina met
instellingen. In de instellingen beheer je je account en apparaten, vrienden en
kringen, geblokkeerde mensen, relays, spaces, mediaservers en back-ups.
Meldingen zijn geen aparte app, ze zitten in de hub zelf.

## Spaces en mounts { #spaces-and-mounts }

- Een **space** is een community met een naam en een eigenaar. Ze heeft een id,
  de sleutel van de eigenaar, een naam, moderatoren, eigen relays en een
  markering die aangeeft dat ze voor volwassenen is. Spaces zijn gebaseerd op
  de gemodereerde community’s van nostr (NIP-72), dus andere nostr-clients
  kunnen ze lezen. Elk bericht en elke advertentie hoort bij precies één space.
- Een **mount** is één app die voor één space wordt gebruikt, met een eigen id,
  naam en icoon. Wil je de winkel van een andere community aan je hub
  toevoegen, dan voeg je één regel toe die de mount beschrijft.
- **Een link noemt de app, de space en het item, maar nooit de host.** Een hub
  opent zo’n link met zijn eigen mount van die app en die space. Heeft de hub
  zo’n mount niet, dan laat hij zien van wie de space is en biedt hij een weg
  terug.
- **Spaces zijn gefedereerd**: een space is niet aan één hub gebonden. Twee hubs
  kunnen dezelfde space aanbieden. De relays van een space dragen alleen de
  inhoud van die space.

Drie dingen zijn gepland, maar nog niet gebouwd. Hubs gaan zichzelf aankondigen
met een ondertekend manifest, zodat anderen ze kunnen vinden. Goedkeuringen
komen erbij als vorm van moderatie. En je zult een space kunnen volgen die niet
bij je hub hoort.

## Een app schrijven { #writing-an-app }

Dit commando maakt het skelet van een nieuwe app in je distributie aan:

```bash
npm run new-app -- <id> "<Name>" <icon>
```

Het resultaat is een React-app die de UI-kit van het framework gebruikt. Ze
heeft een shell (het kader rond de pagina’s van de app), een startpagina en een
pagina met instellingen, haar teksten in elke taal, een vermelding in het
register van apps en een mount. Apps gebruiken alleen de openbare API van het
framework en komen nooit rechtstreeks aan de opslag of de sleutels. Hoe je een
hub bouwt en publiceert, lees je in [Je eigen hub draaien](hubs.md).
