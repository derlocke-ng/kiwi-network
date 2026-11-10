# Die Apps des Frameworks

Mit kiwi-framework betreibt eine Community ihren eigenen Hub. Diese Seite
beschreibt die zehn Apps, die das Framework mitbringt, darunter ein offener
Marktplatz, ein Feed für die Community, ein Chat und der Dateiaustausch.

Im Framework tragen die Apps schlichte Namen wie `market`. Eine Distribution,
also ein bestimmter Hub, der mit dem Framework gebaut wurde, **bindet** die
Apps **ein**, die sie haben will. Eine App einzubinden heißt, sie für einen
Space zu verwenden und ihr einen eigenen Namen des Hubs zu geben. Ein Space ist
eine Community mit eigenen Moderatoren und eigenen Relays. Dieselbe App kann
beliebig oft eingebunden werden. Eine Samenbank und ein Edelsteinladen zum
Beispiel sind derselbe `market`-Code für zwei Spaces. Jeder der beiden hat
eigene Moderatoren und eigene Relays, und auf dem Hub erscheinen sie als zwei
Kacheln.

| App | Was sie ist | Name in Armory |
|---|---|---|
| `market` | **Ein offener Marktplatz** für die Community, für die der Mount eingerichtet ist. Ein Inserat hat Fotos, einen Preis und entweder die Angabe, von wo und wohin versendet wird, oder das Angebot zur Abholung. Käufer finden Inserate über die Kategorie und über ihren eigenen Standort. Die Suche arbeitet mit Labels, die ein Relay vergleichen, aber nicht lesen kann. Dem Verkäufer schreibt ein Käufer im Chat, wo schon eine Nachricht zum Inserat vorformuliert ist. Ein Inserat lässt sich reservieren, als verkauft markieren, verlängern und melden, und nach 30 bis 90 Tagen läuft es ab. Ein Mount kann verlangen, dass Verkäufer vorher in einem Feed aktiv waren oder von einem Moderator freigeschaltet wurden. | Trading Post |
| `feed` | **Ein Feed für die Community.** Leute veröffentlichen Einträge mit Fotos und Hashtags, andere können sie liken und kommentieren. Ein Eintrag kann für den ganzen Space bestimmt sein, für deine Freunde, für einen Kreis (eine Gruppe deiner Freunde) oder nur für dich. Ein Tagebuch ist eine Reihe von Einträgen mit einem Titelbild. Einträge können als 18+ oder als Werbung markiert werden. | Outpost |
| `chat` | **Nachrichten.** Du schickst Freunden private Nachrichten und Dateien (NIP-17). Gruppen bestehen, bis ihr Gastgeber sie schließt, und Live-Räume verschwinden, sobald die letzte Person gegangen ist. Im Chat kannst du antworten, reagieren, Nachrichten bearbeiten und anheften, auf dem Gerät suchen und Nachrichten nach einer Weile verschwinden lassen. Sprach- und Videoanrufe sind mit bis zu sechs Personen möglich. | Uplink |
| `notices` | **Ein Schwarzes Brett** für öffentliche Notizen. Jede Notiz ist von ihrem Autor signiert und braucht einen Proof of Work, eine kleine Rechenaufgabe, die massenhaftes Posten teuer macht. Über Notizen kann abgestimmt werden, sie lassen sich melden, und sie laufen ab. | DevBoard |
| `boards` | **Geteilte Listen und Notizen.** Das sind Checklisten, Inventare mit Stückzahlen und Markdown-Notizen. Sie sind Ende-zu-Ende verschlüsselt. Geteilt werden sie über Links, die entweder das Bearbeiten oder nur das Ansehen erlauben. | Loadout |
| `payload` | **Dateien teilen**, auf drei Wegen: als Link zu Dateien, die verschlüsselt auf deinen Medienservern liegen, als Dateien an Freunde und Gruppen oder direkt von einem Browser zum anderen. | Payload |
| `vault` | **Ein Passwortmanager** für Anmeldungen, Notizen, Karten und Zwei-Faktor-Codes, mit Passwortgenerator und Zustandsbericht. Er verwaltet außerdem SSH-Schlüssel, eine SSH-CA, eine X.509-CA und TLS-Zertifikate. Verschlüsselt ist er mit einer eigenen Passphrase. | Vault |
| `authenticator` | **Zwei-Faktor-Codes** (TOTP). Sie liegen im selben verschlüsselten Tresor wie die Einträge des Passwortmanagers. | Authenticator |
| `calendar` | **Deine Kalender** aus Nextcloud oder von einem anderen CalDAV-Server. An Relays wird nichts gesendet. | Calendar |
| `pong` | **Pong für zwei Spieler** zwischen zwei Browsern. | pongjs |

Jeder Hub hat außerdem eine Startseite, eine Kontoseite und eine Seite für die
Einstellungen. Dort verwaltest du dein Konto und deine Geräte, Freunde und
Kreise, blockierte Personen, Relays, Spaces, Medienserver und Backups.
Benachrichtigungen sind keine eigene App, sie gehören zum Hub selbst.

## Spaces und Mounts { #spaces-and-mounts }

- Ein **Space** ist eine Community mit einem Namen und einem Eigentümer. Zu
  ihm gehören eine Id, der Schlüssel des Eigentümers, ein Name, Moderatoren,
  eigene Relays und ein Kennzeichen, das ihn als Space für Erwachsene ausweist.
  Vorbild sind die moderierten Communities von nostr (NIP-72), deshalb können
  auch andere nostr-Clients einen Space lesen. Jeder Beitrag und jedes Inserat
  gehört zu genau einem Space.
- Ein **Mount** ist eine App, die für einen Space eingebunden ist, mit eigener
  Id, eigenem Namen und eigenem Icon. Willst du den Laden einer anderen
  Community in deinen Hub aufnehmen, genügt eine Zeile, die den Mount
  definiert.
- **Ein Link nennt die App, den Space und den Inhalt, aber nie den Host.** Ein
  Hub öffnet einen solchen Link mit seinem eigenen Mount für diese App und
  diesen Space. Hat der Hub keinen passenden Mount, sagt er dir, wem der Space
  gehört, und bietet einen Weg zurück an.
- **Spaces sind föderiert.** Das heißt, ein Space ist nicht an einen Hub
  gebunden: Zwei Hubs können denselben Space anbieten. Über die Relays eines
  Space laufen nur die Inhalte dieses Space.

Drei Dinge sind geplant und noch nicht umgesetzt. Hubs sollen sich mit einem
signierten Manifest bekannt machen, damit andere sie finden. Freigaben sollen
als weitere Form der Moderation hinzukommen. Und du sollst einem Space folgen
können, den dein Hub nicht enthält.

## Eine App schreiben { #writing-an-app }

Dieser Befehl legt in deiner Distribution das Grundgerüst einer neuen App an:

```bash
npm run new-app -- <id> "<Name>" <icon>
```

Heraus kommt eine React-App, die das UI-Kit des Frameworks verwendet. Sie hat
eine Shell (den Rahmen um die Seiten der App), eine Startseite und eine Seite
für Einstellungen, ihre Texte in allen Sprachen, einen Eintrag im Verzeichnis
der Apps und einen Mount. Apps benutzen ausschließlich die öffentliche API des
Frameworks und greifen nie direkt auf den Speicher oder auf Schlüssel zu. Wie
du einen Hub baust und veröffentlichst, steht unter
[Einen eigenen Hub betreiben](hubs.md).
