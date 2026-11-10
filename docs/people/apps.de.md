# Die Apps des Frameworks

kiwi-framework liefert seine Apps unter schlichten Namen aus. Eine Distribution
**bindet** sie **ein**, auf einem Space und unter einem eigenen Namen. Eine App
kann viele Male eingebunden werden: Eine Saatgutbank und ein Edelsteinladen sind
derselbe `market`-Code auf zwei Spaces, jeder mit eigenen Moderatoren und Relays,
als zwei Kacheln auf einem Hub.

| App | Was sie ist | Armory bindet sie ein als |
|---|---|---|
| `market` | **Ein offener Marktplatz** für die Community, der eine Einbindung dient. Inserate haben Fotos, einen Preis, woher und wohin sie versendet werden, oder Abholung. Käufer finden sie nach Kategorie und nach ihrem Standort, über Suchlabels, die Relays abgleichen, aber nicht lesen können. Käufer schreiben dem Verkäufer im Chat, mit einer bereits vorformulierten Nachricht zum Inserat. Inserate können reserviert, verkauft, verlängert und gemeldet werden und laufen nach 30 bis 90 Tagen ab. Eine Einbindung kann verlangen, dass Verkäufer zuerst in einem Feed aufgetaucht sind oder von einem Moderator freigegeben wurden | Trading Post |
| `feed` | **Ein Community-Feed**: Einträge mit Fotos, Hashtags, Likes und Kommentaren für den Space, für Freunde, für einen Kreis oder nur für dich, dazu Tagebücher (eine Reihe von Einträgen mit einem Titelbild). Einträge können als 18+ oder als Werbung markiert werden | Outpost |
| `chat` | **Nachrichten**: private Nachrichten und Dateien an Freunde (NIP-17), Gruppen, die bleiben, bis ihr Gastgeber sie schließt, Live-Räume, die verschwinden, sobald sie leer sind, Antworten, Reaktionen, Bearbeitungen, Anheften, Suche auf dem Gerät, verschwindende Nachrichten sowie Sprach- und Videoanrufe zwischen bis zu sechs Personen | Uplink |
| `notices` | **Ein Schwarzes Brett** mit signierten, öffentlichen Notizen mit Proof of Work, Abstimmungen, Meldungen und einem Ablaufdatum | DevBoard |
| `boards` | **Geteilte Listen und Notizen**: Checklisten, Inventare mit Stückzahlen und Markdown-Notizen, Ende-zu-Ende verschlüsselt, mit Links zum Bearbeiten oder nur zum Ansehen | Loadout |
| `payload` | **Dateien teilen**: ein Link, der verschlüsselt auf deinen Medienservern wartet; Dateien an Freunde und Gruppen; oder direkt von Browser zu Browser | Payload |
| `vault` | **Ein Passwortmanager**: Anmeldungen, Notizen, Karten, Zwei-Faktor-Codes, ein Generator und ein Zustandsbericht, SSH-Schlüssel, eine SSH-CA, eine X.509-CA und TLS-Zertifikate. Versiegelt mit einer eigenen Passphrase | Vault |
| `authenticator` | **Zwei-Faktor-Codes** (TOTP), aufbewahrt im selben versiegelten Tresor | Authenticator |
| `calendar` | **Deine Kalender** aus Nextcloud oder einem anderen CalDAV-Server. Nichts geht an Relays | Calendar |
| `pong` | **Pong für zwei Spieler** zwischen Browsern | pongjs |

Jeder Hub hat außerdem eine Startseite, Einstellungen (dein Konto und deine Geräte,
Freunde und Kreise, blockierte Personen, Relays, Spaces, Medienserver, Backups) und
eine Kontoseite. Benachrichtigungen leben im Hub selbst.

## Spaces und Einbindungen { #spaces-and-mounts }

- Ein **Space** ist eine benannte Community mit einem Besitzer: eine ID, ein
  Besitzerschlüssel, ein Name, Moderatoren, eigene Relays und ein
  Erwachsenen-Kennzeichen. Er ist den moderierten Communities von nostr (NIP-72)
  nachgebildet, sodass andere nostr-Clients ihn lesen können. Jeder Beitrag und
  jedes Inserat gehört zu genau einem Space.
- Eine **Einbindung** (Mount) ist App-Code auf einem Space, mit eigener ID, eigenem
  Namen und eigenem Icon. Den Laden einer anderen Community zu importieren, ist eine
  einzige Mount-Zeile.
- **Links nennen die App, den Space und den Eintrag, nie den Host.** Ein Hub öffnet
  einen Link mit seiner eigenen Einbindung dieser App und dieses Space. Hat er
  keine, sagt er, wessen Space das ist, und bietet den Weg zurück an.
- **Spaces sind föderiert.** Zwei Hubs können denselben Space bedienen, und die
  Relays eines Space tragen nur seine Inhalte.

Geplant: Hubs, die sich mit einem signierten Manifest ankündigen, damit andere sie
finden, Freigaben durch Moderatoren und Leute, die einem Space folgen, den ihr Hub
nicht mitbringt.

## Eine App schreiben { #writing-an-app }

```bash
npm run new-app -- <id> "<Name>" <icon>
```

Das erzeugt das Gerüst einer React-App auf dem UI-Kit des Frameworks, mit einer
Shell, Start- und Einstellungsseiten, Texten in jeder Sprache, einem
Registry-Eintrag und einer Einbindung. Apps sprechen mit dem Framework nur über
seine öffentliche API und greifen nie direkt auf Speicher oder Schlüssel zu. Siehe
[Einen eigenen Hub betreiben](hubs.md).
