# Armory

**Peer-to-Peer-Webtools, bewaffnet mit nostr.** Jedes Tool läuft komplett in deinem
Browser und synchronisiert über Relays, die du auswählst. Es gibt keine
Registrierung, keinen Server von uns und kein Tracking, und alles wird
verschlüsselt, bevor es dein Gerät verlässt. Installiere es von der Startseite aus
als Web-App.

- **Öffnen:** [derlocke-ng.github.io/armory](https://derlocke-ng.github.io/armory/)
- Repository: [derlocke-ng/armory](https://github.com/derlocke-ng/armory), GPL-3.0-or-later
- Eine Distribution von [kiwi-framework](index.md) 0.32.1 (per Commit festgelegt).
  Release-Tags gibt es noch keine.
- Auf Englisch, Deutsch, Französisch, Spanisch, Italienisch, Niederländisch,
  Polnisch und Portugiesisch.

Armory hieß früher weaponized.js.

## Die Tools { #the-tools }

| Tool | Was es tut |
|---|---|
| [**Loadout**](https://derlocke-ng.github.io/armory/loadout/) | Geteilte Einkaufs- und To-do-Listen, Haushaltsinventare und Markdown-Notizen über deine Geräte hinweg und mit allen, mit denen du sie teilst. Ende-zu-Ende verschlüsselt, mit Links zum Bearbeiten oder nur zum Ansehen. Funktioniert offline, und deine Geräte stellen wieder her, was die Relays vergessen. |
| [**Uplink**](https://derlocke-ng.github.io/armory/uplink/) | Nachrichten und Dateien an Freunde (NIP-17, auf deinem Gerät versiegelt), Gruppen, die bleiben, bis ihr Gastgeber sie schließt, und Live-Räume, die jeder mit dem Link betreten kann und die verschwinden, sobald sie leer sind. Antworten, Reaktionen, Bearbeitungen, Anheften, Suche auf dem Gerät, verschwindende Nachrichten sowie Sprach- und Videoanrufe zwischen bis zu sechs Personen. |
| [**Payload**](https://derlocke-ng.github.io/armory/payload/) | Dateien teilen: ein Link, der verschlüsselt auf deinen Medienservern wartet, bis du ihn löschst; Dateien an Freunde und Gruppen in Uplink; oder direkt von deinem Browser in ihren, nirgends gespeichert. |
| [**Vault**](https://derlocke-ng.github.io/armory/vault/) | Ein Passwortmanager: Anmeldungen, Notizen, Karten und Zwei-Faktor-Codes auf jedem Gerät, auf dem du angemeldet bist. Ein Generator, ein Zustandsbericht (schwache, wiederverwendete, alte und, wenn du es einschaltest, geleakte Passwörter), Import und Export, SSH-Schlüssel, eine SSH-Zertifizierungsstelle, eine X.509-CA und TLS-Zertifikate. Versiegelt mit einer eigenen Passphrase. Kein Autofill. |
| [**Authenticator**](https://derlocke-ng.github.io/armory/authenticator/) | Zwei-Faktor-Codes (TOTP) für deine Konten anderswo: Füge einen aus einem QR-Code, einem Link oder Geheimnis oder einem Export aus Google Authenticator hinzu. Aufbewahrt im selben versiegelten Tresor. |
| [**Calendar**](https://derlocke-ng.github.io/armory/calendar/) | Deine Kalender aus deiner eigenen Nextcloud oder einem anderen CalDAV-Server: die nächsten Tage oder ein Monat, wiederkehrende Termine, Erinnerungen, solange eine Seite offen ist. Nichts geht an Relays; die Anmeldung liegt versiegelt in deinem Konto. Dein Server muss den Origin von Armory erlauben (CORS). |
| [**Outpost**](https://derlocke-ng.github.io/armory/outpost/) | Grow-Berichte und Grow-Tagebücher: Einträge mit Fotos, Woche für Woche, für alle in Outpost, deine Freunde, einen Kreis oder nur dich. Hashtags, Likes und Kommentare. Auf deinem Gerät versiegelt, Fotos verschlüsselt. |
| [**Trading Post**](https://derlocke-ng.github.io/armory/tradingpost/) | Ein Hanf-Marktplatz: Samen, Stecklinge und Ausrüstung mit Fotos, gefunden nach Kategorie und danach, wohin sie gehen. Den Verkäufer anzuschreiben öffnet Uplink. Für Leute mit Konto (keine Altersprüfung). Verkäufer müssen zuerst in Outpost aufgetaucht sein (drei Beiträge, jeder von drei Personen geliked) oder von einem Moderator freigegeben werden. |
| [**DevBoard**](https://derlocke-ng.github.io/armory/devboard/) | Ein Schwarzes Brett für Freelancer: Schreib, dass du Leute suchst oder verfügbar bist, mit deinem Schlüssel signiert, mit Proof of Work abgesichert, bewertet, weg, wenn es abläuft (24 Stunden bis 30 Tage). Mit Absicht öffentlich. |
| [**pongjs**](https://derlocke-ng.github.io/armory/pongjs/) | Retro-Pong für zwei Spieler zwischen zwei Browsern. Teile einen Link oder QR-Code oder such dir ein offenes Spiel aus, oder übe offline gegen den Computer. |

Ein Blog ist geplant.

Jedes Tool ist eine der Apps des Frameworks, eingebunden unter dem Namen von Armory:
Loadout ist `boards`, Uplink `chat`, Outpost `feed`, Trading Post `market`,
DevBoard `notices`, pongjs `pong`.

## Ein Konto, jedes Tool { #one-account-every-tool }

Melde dich auf der Startseite an oder leg ein Konto an (Benutzername und Passwort
oder ein nostr-Schlüssel), und jedes Tool benutzt es. Listen, die du auf einem
Gerät vor dem Anmelden angelegt hast, werden übernommen. Ohne Konto benutzt jedes
Gerät seinen eigenen Schlüssel.

Die Einstellungsseite deckt den ganzen Hub ab: dein Konto und deine Geräte, Freunde
und Kreise, blockierte Personen, Relays, Spaces und Medienserver,
Benachrichtigungen und verschlüsselte Backups.

## Relays und Medienserver { #relays-and-media-servers }

Die Standard-Relays von Armory sind `wss://nos.lol`, `wss://relay.damus.io`,
`wss://nostr.mom` und `wss://relay.primal.net`. Seine Standard-Medienserver
(Blossom) sind `nostr.download`, `blossom.yakihonne.com`, `blossom.band` (nur
Fotos) und `blossom.primal.net`. Eigene wählst du in den Einstellungen.

Relays reichen Daten nur weiter; was vorher verschlüsselt wurde, können sie nicht
lesen. Das [Datenschutzmodell](index.md#privacy-model) listet auf, was sie sehen
können.

## Moderation { #moderation }

Die Moderatoren von Armory moderieren Outpost, Trading Post und DevBoard.
Outpost-Einträge können von ihrem Verfasser, durch zwei Meldungen oder durch einen
Moderator als 18+ oder als Werbung markiert werden. Solche Einträge sehen nur Leute
mit Konto.

## Dein eigenes Armory { #your-own-armory }

Armory ist die Vorlage für deinen eigenen Hub. Forke es (oder nutze es als
Template), ändere `distribution.js` und die Übersetzungen und veröffentliche es.
Siehe [Einen eigenen Hub betreiben](hubs.md).
