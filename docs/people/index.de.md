# Hubs statt Plattformen

Mit **kiwi-framework** kann jede Community ihren eigenen **Hub** betreiben. Ein
Hub ist eine Website mit Apps für die Mitglieder der Community: ein offener
Marktplatz, ein Feed, ein Chat, Dateiaustausch, geteilte Listen, ein
Passwortmanager und ein Kalender. Jeder kann für jede Community einen Hub
aufsetzen. Die Community ist dann nicht auf eine zentrale Plattform angewiesen,
bei der die Konten und Daten aller Mitglieder liegen.

Die Apps laufen vollständig im Browser. Ihre Daten synchronisieren sie über
[nostr](https://nostr.com)-Relays. Das sind Server, die signierte Nachrichten
speichern und weitergeben, und die Community entscheidet selbst, welche Relays
ihr Hub verwendet. Zwischen Browser und Relays gibt es weder einen Kontoserver
noch ein Backend, und alles Private wird schon auf dem Gerät verschlüsselt,
bevor es gesendet wird. Die anderen Teile von Kiwi Network verbinden deine
Maschinen, Hubs verbinden Menschen. Was die einzelnen Apps können, steht unter
[Die Apps des Frameworks](apps.md).

Armory ist der erste Hub, der mit dem Framework gebaut wurde. Armory ist ein
Beispiel und zugleich die Vorlage, die andere Communities für ihren eigenen Hub
kopieren.

Die Software verteilt sich auf drei Repositories:

| Repository | Was es ist |
|---|---|
| [**kiwi-framework**](https://github.com/derlocke-ng/kiwi-framework) | Die allgemeine Software, aus der jeder Hub gebaut wird. Sie enthält Identität und Konten, Relays und Synchronisation, Freunde und Teilen, Moderation, das Design-Kit, die Seiten des Hubs und zehn Apps. Das Framework allein lässt sich nicht als Website öffnen. Erst eine Distribution macht daraus einen Hub. Aktuell ist Version v0.32.1, die Lizenz ist GPL-3.0-or-later. |
| [**Armory**](armory.md) | Die erste **Distribution**, also ein Hub, der mit dem Framework gebaut wurde. Armory bringt einen Namen, voreingestellte Relays und alle zehn Apps mit, jede unter einem eigenen Namen. Wer einen eigenen Hub will, forkt Armory als Vorlage. Die Lizenz ist GPL-3.0-or-later. **Live:** [derlocke-ng.github.io/armory](https://derlocke-ng.github.io/armory/) |
| [**kiwi-web-catalog**](hubs.md#kiwi-web-catalog) | Ein Katalog, also ein git-Repository, das Hubs und ihre Apps auflistet. Er hat dasselbe Format wie der [kiwi-catalog](../desktop/catalogs.md) für den Desktop. |

## So hängt alles zusammen { #how-it-fits-together }

Das Schaubild zeigt, wie aus dem Framework ein Hub in deinem Browser wird und
mit welchen Servern der Browser danach spricht.

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

## Die Begriffe auf diesen Seiten { #the-words }

- **Hub**: die Website, die eine Community benutzt. Ein Hub entsteht, wenn du
  eine Distribution baust. Er besteht nur aus statischen Dateien. Einen Hub zu
  hosten heißt deshalb nichts anderes, als einen Ordner mit Dateien
  auszuliefern. Jeder Hub hat eine Startseite, eine Seite für die Einstellungen
  und eine für das Konto.
- **Distribution**: das Framework zusammen mit den Entscheidungen, die einen
  bestimmten Hub ausmachen. Dazu gehören Name und Aussehen, die voreingestellten
  Relays und die Auswahl der Apps mit den Spaces, für die sie eingebunden sind.
  Wenn du eine Distribution forkst, steht alles, was du änderst, in einer
  einzigen Datei, `distribution.js`, und in ihren Übersetzungen.
- **App**: ein Ordner mit einer Manifest-Datei. Eine App lässt sich in jede
  Distribution aufnehmen. Apps benutzen ausschließlich die öffentliche API des
  Frameworks und greifen nie direkt auf den Speicher oder auf Schlüssel zu.
- **Space**: eine Community mit einem Namen, einem Eigentümer, eigenen
  Moderatoren und, wenn sie das möchte, eigenen Relays. Vorbild sind die
  moderierten Communities von nostr (NIP-72). Auch ein anderer Hub kann
  denselben Space anbieten, indem er dessen Adresse angibt.
- **Mount**: eine App, die für einen Space eingebunden ist. Jeder Mount hat
  einen eigenen Namen, eine eigene Route (seine Adresse innerhalb des Hubs) und
  ein eigenes Icon. Eine App kann beliebig oft eingebunden werden. Der *Trading
  Post* von Armory zum Beispiel ist die App `market` des Frameworks, eingebunden
  für Armorys Space `tradingpost`.

Zwei Menschen, deren Hubs aus verschiedenen Distributionen stammen, können sich
befreunden, Dinge miteinander teilen und chatten, als wären sie auf demselben
Hub. Das funktioniert, weil die Identität und die Daten eines Menschen
nostr-Events sind, also signierte Nachrichten, die auf Relays liegen. Sie
gehören zu keinem Hub.

## Konten und Schlüssel { #accounts-and-keys }

- Wenn du einen Hub zum ersten Mal auf einem Gerät öffnest, erzeugt der Browser
  einen Schlüssel für dieses Gerät und speichert ihn.
- Ein **Konto** besteht aus einem Benutzernamen und einem Passwort. Es baut auf
  gewöhnlichen nostr-Events auf, ein Verzeichnis aller Konten gibt es nicht.
  Dein Passwort läuft durch scrypt, eine Funktion, deren Berechnung absichtlich
  lange dauert, und erst das Ergebnis entsperrt deinen Schlüssel. Ohne das
  Passwort kann niemand ein Konto übernehmen oder überschreiben. Passwörter
  lassen sich **nicht zurücksetzen**.
- Du kannst dich auch mit einem nostr-Schlüssel anmelden, den du schon hast, als
  `nsec`, in Hex-Schreibweise oder als `ncryptsec`. Die Anmeldung über eine
  Browser-Erweiterung (NIP-07) oder einen Remote-Signer (NIP-46) ist geplant,
  aber noch nicht umgesetzt.
- Ein Konto gilt für alle Apps des Hubs und auf jedem Gerät, auf dem du dich
  anmeldest.

## Was privat bleibt und was nicht { #privacy-model }

**Was verschlüsselt ist.** Der Browser verschlüsselt Inhalte, bevor er sie
irgendwohin sendet. Er verwendet AES-256-GCM, die Schlüssel werden mit HKDF
abgeleitet. Private Nachrichten sind NIP-17-Nachrichten in einem Gift Wrap nach
NIP-59. Ein Gift Wrap ist eine zweite Verschlüsselungsschicht. Ein Relay sieht
dadurch nur, dass irgendein Schlüssel eine verpackte Nachricht bekommen hat.
Jede Datei wird mit einem eigenen zufälligen AES-256-GCM-Schlüssel
verschlüsselt, bevor sie auf einen Medienserver hochgeladen wird. Fotos werden
vorher neu kodiert, dabei verschwinden die Metadaten, die Kameras hineinschreiben.
Vault, der Passwortmanager, ist mit einer eigenen Passphrase verschlüsselt (scrypt +
AES-256-GCM). Anrufe laufen direkt von Browser zu Browser und werden von WebRTC
verschlüsselt.

**Erst lokal, dann ins Netz.** Alles, was du schreibst, landet zuerst in der
Datenbank des Browsers und wird erst danach an die Relays geschickt. Die Apps
lesen aus dieser Datenbank auf dem Gerät und funktionieren deshalb auch
offline. Sobald ein Gerät wieder online ist, schickt es dem Relay alle Daten,
die dort inzwischen fehlen. Daten gehen also nur verloren, wenn jedes Gerät weg
ist, auf dem sie lagen, *und* es kein Backup gibt.

**Was andere sehen können.** Die Grenzen nennen die Repositories selbst:

- Relays sehen Metadaten: wer wann wie viel an welche Adressen schreibt und von
  welcher IP-Adresse aus. Wenn dir das wichtig ist, nutze ein VPN oder Tor.
- Der Schlüssel eines Space ist nicht geheim. Er sorgt nur dafür, dass die
  Beiträge einer Community nicht offen lesbar sind. Relays können Likes und
  Meldungen sehen und auch, wer was kommentiert hat.
- Notizen im DevBoard und Meldungen an die Moderation sind mit Absicht
  öffentlich.
- Dein Schlüssel liegt im Speicher des Browsers. Alle GitHub-Pages-Seiten eines
  GitHub-Kontos haben denselben Origin, und Browser trennen den Speicher von
  Websites nach Origin. Ein Hub auf einer eigenen Domain oder Subdomain ist
  deshalb besser geschützt.
- Bei einer direkten Dateiübertragung oder einem Anruf erfahren die beiden
  Browser die IP-Adresse des jeweils anderen. Auch die STUN-Server, die beim
  Verbindungsaufbau helfen, sehen beide Adressen. Voreingestellt sind die
  STUN-Server von Google und Cloudflare. Ein Hub kann eigene festlegen.
- „Kein Server von uns“ heißt: Die Apps sind auf keinen Server angewiesen, den
  das Projekt betreibt. Relays, Medienserver und, für den Kalender, einen
  CalDAV-Server brauchen sie trotzdem. Welche das sind, bestimmst du oder dein
  Hub.

## Moderation { #moderation }

Moderiert wird auf drei Ebenen. Die erste ist deine eigene Blockliste. Sie ist
verschlüsselt, sodass nur du sie lesen kannst. Die zweite sind Meldungen, die
öffentlich und signiert sind. Die dritte sind die Regeln der einzelnen Relays.

Jeder Space hat Moderatoren. Meldet ein Moderator einen Beitrag, wird der
Beitrag sofort eingeklappt. Sonst geschieht das erst nach drei Meldungen von
Leuten, die nicht blockiert sind. Ein Beitrag kann als 18+ oder als Werbung
markiert werden. Markierte Beiträge sehen nur Leute mit Konto.

## Weiterlesen { #read-on }

- [Armory und seine Apps](armory.md)
- [Einen eigenen Hub betreiben](hubs.md)
- Aus dem Framework selbst: die [Architektur](https://github.com/derlocke-ng/kiwi-framework/blob/main/docs/architecture.md)
  und das [Wire-Protokoll](https://github.com/derlocke-ng/kiwi-framework/blob/main/docs/protocol.md)
