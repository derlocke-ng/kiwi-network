# Armory

Armory ist der erste Hub, der mit kiwi-framework gebaut wurde. Mit dieser
Software kann jede Community ihren eigenen Hub betreiben. Im Framework heißt so
etwas eine **Distribution**: das Framework zusammen mit einem Namen,
voreingestellten Relays und einer Auswahl von Apps. Armory enthält alle zehn
Apps des Frameworks und gibt ihnen eigene Namen. Marktplatz und Feed sind auf
Leute zugeschnitten, die Hanf anbauen. Dieses Thema hat sich dieser eine Hub
ausgesucht, nicht das Framework, und eine andere Community würde dieselben Apps
für ihr eigenes Thema verwenden. Du kannst Armory benutzen, wie es ist, oder es
als Vorlage für deinen eigenen Hub kopieren.

Jedes Tool läuft vollständig in deinem Browser. Die Tools synchronisieren über
Relays, also Server, die deine Daten speichern und weitergeben, und welche
Relays das sind, bestimmst du. Du musst dich nicht registrieren, das Projekt
betreibt für Armory keinen eigenen Server, und es gibt kein Tracking. Alles wird verschlüsselt, bevor es dein Gerät verlässt. Von der Startseite
aus kannst du Armory als Web-App installieren.

- **Öffnen:** [derlocke-ng.github.io/armory](https://derlocke-ng.github.io/armory/)
- Das Repository ist [derlocke-ng/armory](https://github.com/derlocke-ng/armory),
  die Lizenz ist GPL-3.0-or-later.
- Armory ist eine Distribution von [kiwi-framework](index.md) 0.32.1 und ist
  über einen Commit auf diese Version festgelegt. Armory selbst hat noch keine
  Release-Tags.
- Es gibt Armory auf Englisch, Deutsch, Französisch, Spanisch, Italienisch,
  Niederländisch, Polnisch und Portugiesisch.

Früher hieß Armory weaponized.js.

## Die Tools { #the-tools }

| Tool | Was es macht |
|---|---|
| [**Loadout**](https://derlocke-ng.github.io/armory/loadout/) | Gemeinsame Einkaufs- und To-do-Listen, Haushaltsinventare und Markdown-Notizen. Sie bleiben auf allen deinen Geräten und bei allen, mit denen du sie teilst, auf demselben Stand. Alles ist Ende-zu-Ende verschlüsselt. Eine Liste teilst du über einen Link, der entweder das Bearbeiten oder nur das Ansehen erlaubt. Loadout funktioniert offline, und was den Relays verloren gegangen ist, schicken deine Geräte wieder dorthin. |
| [**Uplink**](https://derlocke-ng.github.io/armory/uplink/) | Nachrichten und Dateien an Freunde (NIP-17, auf deinem Gerät verschlüsselt). Gruppen bestehen, bis ihr Gastgeber sie schließt. Einen Live-Raum kann jeder betreten, der den Link hat, und er verschwindet, sobald die letzte Person gegangen ist. Uplink kennt Antworten, Reaktionen, nachträgliches Bearbeiten, angeheftete Nachrichten, eine Suche auf deinem Gerät und verschwindende Nachrichten. Sprach- und Videoanrufe sind mit bis zu sechs Personen möglich. |
| [**Payload**](https://derlocke-ng.github.io/armory/payload/) | Dateien teilen, auf drei Wegen. Du erzeugst einen Link zu Dateien, die verschlüsselt auf deinen Medienservern liegen, bis du sie löschst. Du schickst Dateien in Uplink an Freunde und Gruppen. Oder du überträgst Dateien direkt von deinem Browser in den Browser einer anderen Person, dann werden sie nirgends gespeichert. |
| [**Vault**](https://derlocke-ng.github.io/armory/vault/) | Ein Passwortmanager für Anmeldungen, Notizen, Karten und Zwei-Faktor-Codes, verfügbar auf jedem Gerät, auf dem du dich anmeldest. Er hat einen Passwortgenerator und einen Zustandsbericht. Der Bericht findet schwache, mehrfach verwendete und alte Passwörter und, wenn du diese Prüfung einschaltest, auch Passwörter aus bekannten Datenlecks. Vault importiert und exportiert Einträge. Außerdem verwaltet Vault SSH-Schlüssel, eine SSH-Zertifizierungsstelle, eine X.509-CA und TLS-Zertifikate. Verschlüsselt ist Vault mit einer eigenen Passphrase. Passwörter auf Websites füllt Vault nicht für dich aus. |
| [**Authenticator**](https://derlocke-ng.github.io/armory/authenticator/) | Zwei-Faktor-Codes (TOTP) für deine Konten bei anderen Diensten. Ein Konto fügst du über einen QR-Code, über einen Link oder ein Secret oder aus einem Export von Google Authenticator hinzu. Die Codes liegen im selben verschlüsselten Tresor, den auch Vault benutzt. |
| [**Calendar**](https://derlocke-ng.github.io/armory/calendar/) | Deine Kalender aus deiner eigenen Nextcloud oder von einem anderen CalDAV-Server. Calendar zeigt die nächsten Tage oder einen Monat, kann mit wiederkehrenden Terminen umgehen und erinnert dich an Termine, solange eine Seite geöffnet ist. An Relays wird nichts gesendet, und die Anmeldedaten für deinen Server liegen verschlüsselt in deinem Konto. Dein Server muss Anfragen vom Origin von Armory zulassen (CORS). |
| [**Outpost**](https://derlocke-ng.github.io/armory/outpost/) | Der Feed von Armory, gedacht für Grow-Berichte und Grow-Tagebücher. Du veröffentlichst Woche für Woche Einträge mit Fotos. Jeder Eintrag kann für alle in Outpost bestimmt sein, für deine Freunde, für einen Kreis von Freunden oder nur für dich. Einträge können Hashtags, Likes und Kommentare haben. Sie werden auf deinem Gerät verschlüsselt, die Fotos ebenfalls. |
| [**Trading Post**](https://derlocke-ng.github.io/armory/tradingpost/) | Der Marktplatz von Armory, gedacht für Hanf: Samen, Stecklinge und Ausrüstung. Inserate haben Fotos, und Käufer finden sie über die Kategorie und darüber, wohin versendet wird. Die Schaltfläche „Nachricht senden“ öffnet Uplink. Für Trading Post brauchst du ein Konto, eine Altersprüfung gibt es nicht. Wer verkaufen will, muss vorher in Outpost gepostet haben (drei Beiträge mit je drei Likes) oder von einem Moderator freigeschaltet worden sein. |
| [**DevBoard**](https://derlocke-ng.github.io/armory/devboard/) | Ein Schwarzes Brett für Freelancer. In einer Notiz schreibst du, dass du Leute suchst oder dass du verfügbar bist. Jede Notiz ist mit deinem Schlüssel signiert und braucht einen Proof of Work, eine kleine Rechenaufgabe, die massenhaftes Posten teuer macht. Andere können über eine Notiz abstimmen. Eine Notiz läuft 24 Stunden bis 30 Tage nach dem Posten ab und verschwindet dann. Alle Notizen sind mit Absicht öffentlich. |
| [**pongjs**](https://derlocke-ng.github.io/armory/pongjs/) | Retro-Pong für zwei Spieler in zwei Browsern. Um ein Spiel zu starten, teilst du einen Link oder einen QR-Code oder suchst dir eines der offenen Spiele aus. Offline kannst du auch gegen den Computer üben. |

Ein Blog ist geplant.

Jedes Tool ist eine App des Frameworks unter dem Namen, den Armory ihr gegeben
hat. Loadout ist die App `boards` des Frameworks, Uplink ist `chat`, Outpost
ist `feed`, Trading Post ist `market`, DevBoard ist `notices` und pongjs ist
`pong`.

## Ein Konto für alle Tools { #one-account-every-tool }

Auf der Startseite meldest du dich an oder legst ein Konto an, entweder mit
Benutzername und Passwort oder mit einem nostr-Schlüssel. Danach benutzt jedes
Tool dieses Konto. Listen, die du vor der Anmeldung auf einem Gerät angelegt
hast, werden in das Konto übernommen. Ohne Konto arbeitet jedes Gerät mit
seinem eigenen Schlüssel.

Die Einstellungen gelten für den ganzen Hub. Dort verwaltest du dein Konto und
deine Geräte, Freunde und Kreise, blockierte Personen, Relays, Spaces und
Medienserver, Benachrichtigungen und verschlüsselte Backups.

## Relays und Medienserver { #relays-and-media-servers }

In Armory sind die Relays `wss://nos.lol`, `wss://relay.damus.io`,
`wss://nostr.mom` und `wss://relay.primal.net` voreingestellt. Medienserver
speichern die Dateien, die du hochlädst, und verwenden dafür ein Protokoll
namens Blossom. Als Medienserver sind `nostr.download`,
`blossom.yakihonne.com`, `blossom.band` (nimmt nur Fotos an) und
`blossom.primal.net` voreingestellt. In den Einstellungen kannst du eigene
Relays und Medienserver wählen.

Relays speichern Daten und geben sie weiter. Was vor dem Senden verschlüsselt
wurde, können sie aber nicht lesen. Was Relays sehen können, steht unter
[Was privat bleibt und was nicht](index.md#privacy-model).

## Moderation { #moderation }

Die Moderatoren von Armory sind für Outpost, Trading Post und DevBoard
zuständig. Ein Eintrag in Outpost kann als 18+ oder als Werbung markiert
werden. Das kann der Autor tun oder ein Moderator, und auch zwei Meldungen
führen dazu. Markierte Einträge sehen nur Leute mit Konto.

## Dein eigenes Armory { #your-own-armory }

Armory ist auch die Vorlage für deinen eigenen Hub. Forke das Repository oder
verwende es als Template, passe `distribution.js` und die Übersetzungen an und
veröffentliche das Ergebnis. Die einzelnen Schritte stehen unter
[Einen eigenen Hub betreiben](hubs.md).
