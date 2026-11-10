# Armory

**Peer-to-peer-webtools, gewapend met nostr.** Elke tool draait volledig in je
browser en synchroniseert via relays die jij kiest. Er is geen registratie, geen
server van ons en geen tracking, en alles wordt versleuteld voordat het je
apparaat verlaat. Installeer het als web-app vanaf de startpagina.

- **Openen:** [derlocke-ng.github.io/armory](https://derlocke-ng.github.io/armory/)
- Repository: [derlocke-ng/armory](https://github.com/derlocke-ng/armory), GPL-3.0-or-later
- Een distributie van [kiwi-framework](index.md) 0.32.1 (vastgepind op een
  commit). Er zijn nog geen release-tags.
- In het Engels, Duits, Frans, Spaans, Italiaans, Nederlands, Pools en
  Portugees.

Armory heette vroeger weaponized.js.

## De tools { #the-tools }

| Tool | Wat het doet |
|---|---|
| [**Loadout**](https://derlocke-ng.github.io/armory/loadout/) | Gedeelde boodschappen- en to-dolijsten, huishoudvoorraden en Markdown-notities tussen je apparaten en met iedereen met wie je ze deelt. End-to-end versleuteld, met links om te bewerken of alleen te bekijken. Werkt offline, en je apparaten zetten terug wat relays vergeten. |
| [**Uplink**](https://derlocke-ng.github.io/armory/uplink/) | Berichten en bestanden aan vrienden (NIP-17, verzegeld op je apparaat), groepen die blijven tot hun host ze sluit, en live-kamers waar iedereen met de link in kan, weg zodra ze leeg zijn. Antwoorden, reacties, bewerkingen, vastgezette berichten, zoeken op het apparaat, verdwijnende berichten, en spraak- en videogesprekken tussen maximaal zes mensen. |
| [**Payload**](https://derlocke-ng.github.io/armory/payload/) | Bestanden delen: een link die versleuteld op je mediaservers wacht tot je hem verwijdert; bestanden naar vrienden en groepen in Uplink; of rechtstreeks van jouw browser naar die van hen, nergens opgeslagen. |
| [**Vault**](https://derlocke-ng.github.io/armory/vault/) | Een wachtwoordbeheerder: logins, notities, kaarten en tweestapscodes op elk apparaat waarop je inlogt. Een generator, een gezondheidsrapport (zwakke, hergebruikte, oude en, als je het aanzet, gelekte wachtwoorden), import en export, SSH-sleutels, een SSH-certificaatautoriteit, een X.509-CA en TLS-certificaten. Verzegeld met een eigen wachtzin. Geen automatisch invullen. |
| [**Authenticator**](https://derlocke-ng.github.io/armory/authenticator/) | Tweestapscodes (TOTP) voor je accounts elders: voeg er een toe via een QR-code, een link of geheim, of een export uit Google Authenticator. Bewaard in dezelfde verzegelde kluis. |
| [**Calendar**](https://derlocke-ng.github.io/armory/calendar/) | Je agenda's uit je eigen Nextcloud of een andere CalDAV-server: de komende dagen of een maand, terugkerende afspraken, herinneringen zolang een pagina open is. Er gaat niets naar relays; de aanmelding zit verzegeld in je account. Je server moet de origin van Armory toestaan (CORS). |
| [**Outpost**](https://derlocke-ng.github.io/armory/outpost/) | Kweekverslagen en kweekdagboeken: berichten met foto's, week na week, voor iedereen in Outpost, je vrienden, een kring of alleen jou. Hashtags, likes en reacties. Verzegeld op je apparaat, foto's versleuteld. |
| [**Trading Post**](https://derlocke-ng.github.io/armory/tradingpost/) | Een hennepmarkt: zaden, stekken en spullen met foto's, gevonden op categorie en op waarheen ze verzonden worden. De knop om de verkoper een bericht te sturen opent Uplink. Voor mensen met een account (geen leeftijdscontrole). Verkopers moeten eerst in Outpost actief zijn geweest (drie berichten, elk geliket door drie mensen) of door een moderator zijn goedgekeurd. |
| [**DevBoard**](https://derlocke-ng.github.io/armory/devboard/) | Een prikbord voor freelancers: meld dat je mensen zoekt of beschikbaar bent, ondertekend met je sleutel, gedekt door proof of work, met stemmen, weg zodra het verloopt (24 uur tot 30 dagen). Bewust openbaar. |
| [**pongjs**](https://derlocke-ng.github.io/armory/pongjs/) | Retro-Pong voor twee spelers tussen twee browsers. Deel een link of QR-code of kies een open spel, of oefen offline tegen de computer. |

Er is een blog gepland.

Elke tool is een van de apps van het framework, gemount onder de naam van
Armory: Loadout is `boards`, Uplink `chat`, Outpost `feed`, Trading Post
`market`, DevBoard `notices`, pongjs `pong`.

## Eén account, elke tool { #one-account-every-tool }

Log in of maak een account aan op de startpagina (gebruikersnaam en wachtwoord,
of een nostr-sleutel) en elke tool gebruikt het. Lijsten die je op een apparaat
maakte voordat je inlogde, worden meegenomen. Zonder account gebruikt elk
apparaat een eigen sleutel.

De instellingenpagina beslaat de hele hub: je account en apparaten, vrienden en
kringen, geblokkeerde mensen, relays, spaces en mediaservers, meldingen, en
versleutelde back-ups.

## Relays en mediaservers { #relays-and-media-servers }

De standaardrelays van Armory zijn `wss://nos.lol`, `wss://relay.damus.io`,
`wss://nostr.mom` en `wss://relay.primal.net`. De standaard mediaservers
(Blossom) zijn `nostr.download`, `blossom.yakihonne.com`, `blossom.band` (alleen
foto's) en `blossom.primal.net`. Je kunt je eigen kiezen in de instellingen.

Relays geven gegevens door, maar wat eerst versleuteld is, kunnen ze niet lezen.
Het [privacymodel](index.md#privacy-model) somt op wat ze wel kunnen zien.

## Moderatie { #moderation }

De moderators van Armory modereren Outpost, Trading Post en DevBoard.
Outpost-berichten kunnen als 18+ of als advertentie worden gemarkeerd door hun
schrijver, door twee meldingen, of door een moderator. Die berichten zijn alleen
zichtbaar voor mensen met een account.

## Je eigen Armory { #your-own-armory }

Armory is het sjabloon voor je eigen hub. Fork het (of gebruik het als sjabloon),
wijzig `distribution.js` en de vertalingen, en publiceer het. Zie
[Je eigen hub draaien](hubs.md).
