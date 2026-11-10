# Hubs statt Plattformen

Das Netzwerk verbindet deine Maschinen. **Hubs** verbinden Menschen. Ein Hub ist
eine Sammlung von Web-Apps (ein offener Marktplatz, ein Feed, Chat, Dateien teilen,
geteilte Listen, ein Passwortmanager, ein Kalender), die komplett im Browser laufen
und über [nostr](https://nostr.com)-Relays synchronisieren, die die Community
auswählt. Es gibt keinen Kontoserver und kein Backend in der Mitte, und alles
Private wird auf dem Gerät verschlüsselt, bevor es dieses verlässt. Jeder kann einen
Hub für jede Community betreiben. Siehe [die Apps des Frameworks](apps.md).

Drei Repositories bilden das Ganze:

| Repository | Was es ist |
|---|---|
| [**kiwi-framework**](https://github.com/derlocke-ng/kiwi-framework) | Der Motor: Identität und Konten, Relays und Synchronisation, Menschen und Teilen, Moderation, das Design-Kit, die Hub-Seiten und zehn Apps. Für sich allein liefert es nichts aus, was ein Nutzer öffnet. v0.32.1, GPL-3.0-or-later |
| [**Armory**](armory.md) | Die erste **Distribution**: ein mit dem Framework gebauter Hub, mit Namen, Standard-Relays und allen zehn Apps, eingebunden unter eigenen Namen. Die Vorlage, die du für deinen eigenen forkst. GPL-3.0-or-later. **Live:** [derlocke-ng.github.io/armory](https://derlocke-ng.github.io/armory/) |
| [**kiwi-web-catalog**](hubs.md#kiwi-web-catalog) | Ein Git-Katalog von Hubs und ihren Apps, in derselben Form wie der Desktop-[kiwi-catalog](../desktop/catalogs.md) |

## Wie es zusammenpasst { #how-it-fits-together }

```
kiwi-framework  (engine: shared data layer, React UI, hub pages, apps)
      │  pinned by commit or tag
      ▼
a distribution  (Armory: distribution.js + locales/ + app overlays)
      │  build → static files
      ▼
any static host (GitHub Pages)  or  the hub container (nginx + HUB_* settings)
      │  HTTPS
      ▼
┌──────────────── your browser: all the logic and all the crypto ────────────────┐
│  wss://   nostr relays: the hub's own, a public area, one network per space    │
│  https:// Blossom media servers: encrypted files, addressed by their SHA-256   │
│  WebRTC   browser to browser: direct file transfers, calls, pong               │
└─────────────────────────────────────────────────────────────────────────────────┘
```

## Die Begriffe { #the-words }

- **Hub**: das, was eine Distribution erzeugt. Statische Dateien, einen zu hosten
  heißt also, einen Ordner auszuliefern. Jeder Hub hat eine Startseite,
  Einstellungen und eine Kontoseite.
- **Distribution**: ein auf dem Framework gebauter Hub, mit Namen und Aussehen,
  Standard-Relays und einer gewählten Auswahl von Apps auf gewählten Spaces. Alles,
  was ein Fork ändert, steht in einer Datei, `distribution.js`, plus ihren
  Übersetzungen.
- **App**: ein Ordner mit einem Manifest, der sich in jede Distribution einstecken
  lässt. Apps sprechen nur mit der öffentlichen API des Frameworks und greifen nie
  direkt auf Speicher oder Schlüssel zu.
- **Space**: eine benannte Community mit einem Besitzer, mit eigenen Moderatoren und
  optional eigenen Relays (den moderierten Communities nach NIP-72 nachgebildet).
  Ein anderer Hub kann denselben Space bedienen, indem er dessen Adresse nennt.
- **Mount** (Einbindung): App-Code auf einem Space, mit eigenem Namen, eigener Route
  und eigenem Icon. Eine App kann viele Male eingebunden werden. *Trading Post* von
  Armory ist die App `market` des Frameworks, eingebunden auf dem Space
  `tradingpost` von Armory.

Zwei Menschen auf verschiedenen Distributionen sind Freunde, teilen und chatten
genau so wie auf einer, denn Identität und Daten sind nostr-Events, nicht Eigentum
des Hubs.

## Konten und Schlüssel { #accounts-and-keys }

- Jedes Gerät bekommt bei seinem ersten Besuch einen Schlüssel, der im Browser
  aufbewahrt wird.
- Ein **Konto** ist ein Benutzername und ein Passwort, aufgebaut auf einfachen
  nostr-Events ohne irgendein Register: Das Passwort wird mit scrypt gestreckt und
  entsperrt deinen Schlüssel. Niemand kann ein Konto ohne das Passwort übernehmen
  oder überschreiben. Es gibt **kein Zurücksetzen des Passworts**.
- Du kannst dich auch mit einem vorhandenen nostr-Schlüssel anmelden (`nsec`, hex
  oder `ncryptsec`). Signer per Browser-Erweiterung und entfernte Signer (NIP-07,
  NIP-46) sind geplant, nicht gebaut.
- Ein Konto funktioniert in allen Apps des Hubs und auf jedem Gerät, auf dem du
  angemeldet bist.

## Datenschutzmodell { #privacy-model }

**Was verschlüsselt ist.** Inhalte werden im Browser versiegelt, bevor sie
irgendwohin gehen: AES-256-GCM mit per HKDF abgeleiteten Schlüsseln. Private
Nachrichten sind NIP-17-Nachrichten in NIP-59-Gift-Wraps. Dateien bekommen jeweils
einen zufälligen AES-256-GCM-Schlüssel, bevor sie auf einen Medienserver gehen, und
Fotos werden neu kodiert, wodurch Kamera-Metadaten wegfallen. Der Vault ist mit
einer eigenen Passphrase versiegelt (scrypt + AES-256-GCM). Anrufe gehen von Browser
zu Browser, verschlüsselt durch WebRTC.

**Lokal zuerst.** Jeder Schreibvorgang geht zuerst in die eigene Datenbank des
Browsers, dann an die Relays. Gelesen wird vom Gerät, sodass die Apps offline
funktionieren. Verbindet sich ein Gerät wieder, stellt es wieder her, was ein Relay
vergessen hat: Daten gehen nur verloren, wenn jedes Gerät, das sie hatte, weg ist
*und* es kein Backup gibt.

**Was andere sehen können.** Die Repositories sind bei den Grenzen deutlich:

- Relays sehen Metadaten: wer an welche Adressen schreibt, wann, wie viel und von
  welcher IP-Adresse. Nutze ein VPN oder Tor, wenn das wichtig ist.
- Der Schlüssel eines Space ist kein Geheimnis. Er hält die Beiträge einer
  Community von offener Sicht fern. Likes, Meldungen und wer was kommentiert hat,
  sind für Relays sichtbar.
- DevBoard-Notizen und Moderationsmeldungen sind mit Absicht öffentlich.
- Dein Schlüssel liegt im Speicher des Browsers. Alle GitHub-Pages-Sites eines
  Kontos teilen sich einen Origin, daher ist ein Hub auf eigener (Sub-)Domain die
  stärkere Einrichtung.
- Direktübertragungen und Anrufe verraten die IP-Adressen der beiden Browser
  einander und den STUN-Servern (standardmäßig die von Google und Cloudflare; ein Hub
  kann eigene festlegen).
- „Kein Server von uns“ heißt: keiner im kritischen Pfad. Die Apps nutzen weiterhin
  die Relays, die Medienserver und, für den Kalender, den CalDAV-Server, die du oder
  dein Hub auswählen.

## Moderation { #moderation }

Drei Ebenen: deine eigene Blockliste (verschlüsselt, nur du kannst sie lesen),
Meldungen (öffentlich, signiert) und die eigene Richtlinie der Relays. Ein Space hat
Moderatoren. Die Meldung eines Moderators klappt einen Beitrag sofort ein. Sonst
braucht es drei Meldungen von Leuten, die nicht blockiert sind. Beiträge können als
18+ oder als Werbung markiert werden, und solche sehen nur Leute mit Konto.

## Weiterlesen { #read-on }

- [Armory und seine Apps](armory.md)
- [Einen eigenen Hub betreiben](hubs.md)
- Die eigene [Architektur](https://github.com/derlocke-ng/kiwi-framework/blob/main/docs/architecture.md)
  und das [Wire-Protokoll](https://github.com/derlocke-ng/kiwi-framework/blob/main/docs/protocol.md) des Frameworks
