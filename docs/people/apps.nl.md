# De apps van het framework

kiwi-framework levert zijn apps onder gewone namen. Een distributie **mount** ze,
op een space en onder een eigen naam. Eén app kan vele keren gemount worden: een
zadenbank en een edelstenenwinkel zijn dezelfde `market`-code op twee spaces,
elk met eigen moderators en relays, als twee tegels op één hub.

| App | Wat het is | Armory mount het als |
|---|---|---|
| `market` | **Een open markt** voor de gemeenschap die een mount bedient. Advertenties hebben foto's, een prijs, waarvandaan en waarheen ze verzonden worden, of afhalen. Kopers vinden ze op categorie en op waar ze zijn, via zoeklabels die relays kunnen matchen maar niet lezen. Kopers schrijven de verkoper in de chat, met een bericht over de advertentie al klaargezet. Advertenties kunnen gereserveerd, verkocht, verlengd en gemeld worden, en verlopen na 30 tot 90 dagen. Een mount kan eisen dat verkopers eerst in een feed actief zijn geweest, of door een moderator zijn goedgekeurd | Trading Post |
| `feed` | **Een gemeenschapsfeed**: berichten met foto's, hashtags, likes en reacties voor de space, voor vrienden, voor een kring of alleen voor jou, plus dagboeken (een reeks berichten met een omslag). Berichten kunnen als 18+ of als advertentie gemarkeerd worden | Outpost |
| `chat` | **Berichten**: privéberichten en bestanden aan vrienden (NIP-17), groepen die blijven tot hun host ze sluit, live-kamers die verdwijnen zodra ze leeg zijn, antwoorden, reacties, bewerkingen, vastgezette berichten, zoeken op het apparaat, verdwijnende berichten, en spraak- en videogesprekken tussen maximaal zes mensen | Uplink |
| `notices` | **Een prikbord** met ondertekende, openbare notities met proof of work, stemmen, meldingen en een vervaldatum | DevBoard |
| `boards` | **Gedeelde lijsten en notities**: checklists, voorraadlijsten met aantallen en Markdown-notities, end-to-end versleuteld, met links om te bewerken of alleen te bekijken | Loadout |
| `payload` | **Bestanden delen**: een link die versleuteld op je mediaservers wacht; bestanden naar vrienden en groepen; of rechtstreeks van browser naar browser | Payload |
| `vault` | **Een wachtwoordbeheerder**: logins, notities, kaarten, tweestapscodes, een generator en een gezondheidsrapport, SSH-sleutels, een SSH-CA, een X.509-CA en TLS-certificaten. Verzegeld met een eigen wachtzin | Vault |
| `authenticator` | **Tweestapscodes** (TOTP), bewaard in dezelfde verzegelde kluis | Authenticator |
| `calendar` | **Je agenda's** uit Nextcloud of een andere CalDAV-server. Er gaat niets naar relays | Calendar |
| `pong` | **Pong voor twee spelers** tussen browsers | pongjs |

Elke hub heeft ook een startpagina, instellingen (je account en apparaten,
vrienden en kringen, geblokkeerde mensen, relays, spaces, mediaservers,
back-ups) en een accountpagina. Meldingen leven in de hub zelf.

## Spaces en mounts { #spaces-and-mounts }

- Een **space** is een benoemde gemeenschap met een eigenaar: een id, een
  eigenaarssleutel, een naam, moderators, eigen relays en een 18+-vlag. Hij is
  gemodelleerd naar de gemodereerde communities van nostr (NIP-72), zodat andere
  nostr-clients hem kunnen lezen. Elk bericht en elke advertentie hoort bij
  precies één space.
- Een **mount** is app-code op een space, met een eigen id, naam en icoon. De
  winkel van een andere gemeenschap importeren is één mount-regel.
- **Links noemen de app, de space en het item, nooit de host.** Een hub opent
  een link met zijn eigen mount van die app en space. Zonder zo'n mount zegt hij
  van wie deze space is en biedt hij de weg terug.
- **Spaces zijn gefedereerd.** Twee hubs kunnen dezelfde space bedienen, en de
  relays van een space vervoeren alleen de inhoud daarvan.

Gepland: hubs die zich aankondigen met een ondertekend manifest zodat anderen ze
kunnen vinden, goedkeuringen door moderators, en mensen die een space volgen die
hun hub niet meelevert.

## Een app schrijven { #writing-an-app }

```bash
npm run new-app -- <id> "<Name>" <icon>
```

Dit zet een React-app op met de UI-kit van het framework, met een shell, home-
en instellingenpagina's, teksten in elke taal, een registervermelding en een
mount. Apps praten met het framework alleen via de publieke API en raken opslag
of sleutels nooit rechtstreeks aan. Zie [Je eigen hub draaien](hubs.md).
