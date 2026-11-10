# Einen eigenen Hub betreiben

Auf dieser Seite geht es darum, wie du einen Hub für deine eigene Community
betreibst. Ein Hub ist die Website, die eine Community mit kiwi-framework
bekommt: ein offener Marktplatz, ein Feed, ein Chat und weitere Apps, die im
Browser laufen. Ein Hub besteht nur aus statischen Dateien. Ihn zu hosten
heißt also, einen Ordner mit Dateien über HTTPS auszuliefern. Dafür gibt es
drei Wege:

- **Armory so verwenden, wie es ist.** Armory ist der erste Hub, der mit dem
  Framework gebaut wurde, und steht unter
  [derlocke-ng.github.io/armory](https://derlocke-ng.github.io/armory/) allen
  offen.
- **Eine eigene Distribution bauen.** Eine Distribution ist das Framework mit
  deinem eigenen Namen, deinen Relays und deiner Auswahl an Apps. Du kannst sie
  auf jedem Hoster für statische Seiten veröffentlichen.
- **Den Hub-Container betreiben.** Zum Beispiel in deinem eigenen Kiwi Network,
  zusammen mit einem eigenen Relay. So entsteht ein privater Hub, der nur aus
  dem Mesh erreichbar ist, also aus dem privaten Netzwerk, in dem deine
  Maschinen hängen.

## Arten von Hubs { #kinds-of-hub }

| Art | Wie | Beispiel |
|---|---|---|
| **Öffentlich** | Der Hub nutzt öffentliche Relays, und jeder kann ihn öffnen. | Armory |
| **Privat** | Niemand kann die Relays des Hubs durch andere ersetzen (`policy.relays: 'locked'`), und die Seiten warten, bis eines dieser Relays antwortet (`requireHub`). Die Relays stehen in einem VPN. | der Hub einer Firma auf ihrem kiwi-master |
| **Halböffentlich** | Ein privater Hub, der zusätzlich einen öffentlichen Bereich hat. Ausgewählte Apps, zum Beispiel der Chat, nutzen dort öffentliche Relays. | |

Die Relays eines Hubs bilden getrennte Netze: das eigene Netz des Hubs, den
öffentlichen Bereich und die Netze seiner Spaces. Jedes Event, also jede
signierte nostr-Nachricht, gehört zu genau einem dieser Netze und wird nie in
ein anderes weitergegeben.

## Deine eigene Distribution { #your-own-distribution }

Du fängst mit Armory an, das als Vorlage dient. Mit *Use this template* legt
GitHub dir eine Kopie des Repositorys ohne dessen Versionsgeschichte an. Danach
gehst du so vor:

1. Bearbeite **`distribution.js`**. Diese Datei legt Id, Name, Logo,
   Beschreibung, Homepage, Repository, Relays, Medienserver, Spaces, Apps und
   Mounts fest. Soll dein Hub auch die Spaces von Armory anbieten, übernimm
   deren `owner` und `id` aus der `hub.json` von Armory.
2. Bearbeite **`locales/*.json`**. In diesen Dateien stehen Titel, Einleitung
   und Fußzeile sowie für jeden Mount ein Text für seine Karte. Fehlt eine
   Übersetzung, wird Englisch angezeigt.
3. Passe **`kiwi.manifest`** an. Wenn du möchtest, trag deinen Hub auch in
   [kiwi-web-catalog](#kiwi-web-catalog) ein.
4. Wähle auf GitHub *Settings → Pages → Source: GitHub Actions* und pushe
   anschließend.

Mit diesen Befehlen arbeitest du an einer Distribution:

```bash
npm install
npm run dev                  # der Hub mit Hot Reload, http://localhost:5173
npm test
npm run build && npm run serve
npm run relay:nostr          # ein lokales Test-Relay auf ws://localhost:7777
npm run new-app -- <id> "<Name>" <icon>   # Grundgerüst für eine neue App
```

Lege kiwi-framework auf einen Commit oder ein Tag fest, nie auf einen Branch.
Beim Bauen wird deine `distribution.js` geprüft. Ein Hub mit einem öffentlichen
Mount muss zum Beispiel öffentliche Relays haben, und ein Hub mit öffentlichen
Relays braucht einen öffentlichen Mount.

Alles, was du im Browser siehst, ist in TypeScript mit React 19 geschrieben und
wird mit Vite gebaut. Die Datenschicht in `shared/` ist reines JavaScript mit
Typangaben in JSDoc. Die Tests laufen im Test-Runner von node, und die Tests, die
einen Browser brauchen, in Playwright.

## Der Hub-Container { #the-hub-container }

Armory gibt es auch als Container-Image, `ghcr.io/derlocke-ng/armory`. Das
Image wird aus `container/Dockerfile` des Frameworks gebaut und liefert den Hub
mit nginx aus. Beim Start des Containers schreibt sein Entrypoint-Skript aus
den `HUB_*`-Variablen die Datei `hub.local.json`, und die Seite liest diese
Datei, bevor sie sich verbindet. Auf diese Weise kann eine Installation Relays
und Regeln festlegen, aber keinen Code hinzufügen. Ist keine Variable gesetzt,
läuft der Hub so, wie er gebaut wurde.

Dieses Beispiel startet einen Hub mit einem eigenen Relay, das niemand durch ein
anderes ersetzen kann, und einem Mount auf einem öffentlichen Relay:

```bash
docker run --rm -p 8080:80 \
  -e HUB_RELAYS=wss://relay.sh3.home \
  -e HUB_RELAYS_LOCKED=true -e HUB_REQUIRE_HUB=true \
  -e HUB_PUBLIC_RELAYS=wss://nos.lol -e HUB_PUBLIC_MOUNTS=uplink \
  ghcr.io/you/your-hub
```

| Variable | Bedeutung |
|---|---|
| `HUB_RELAYS` | Die eigenen Relays des Hubs. |
| `HUB_PUBLIC_RELAYS` | Die Relays des öffentlichen Bereichs. Ist die Variable gesetzt, aber leer, gibt es keinen öffentlichen Bereich. |
| `HUB_DIRECTORY_RELAYS` | Die Relays, auf denen Relay-Listen veröffentlicht und nachgeschlagen werden. |
| `HUB_RELAYS_LOCKED` | Mit `true` kann niemand die Relays des Hubs durch andere ersetzen. |
| `HUB_REQUIRE_HUB` | Mit `true` warten die Seiten, solange keines der Relays des Hubs antwortet. |
| `HUB_PUBLIC_MOUNTS` | Die Mounts, die den öffentlichen Bereich nutzen, angegeben über ihre Id. |
| `HUB_ACCOUNT_MOUNTS` | Die Mounts, die ein Konto verlangen. |
| `HUB_REQUIRE_ACCOUNT` | Mit `true` verlangt jeder Mount ein Konto. |
| `HUB_SPACE_RELAYS` | Die Relays der einzelnen Spaces, in der Form `jobs=wss://…;gems=wss://a,wss://b`. |
| `HUB_MODERATORS` | Die Schlüssel der Leute, die jeden Space moderieren, den der Hub definiert. |
| `HUB_REGISTER_POW` | Wie viele Bits Proof of Work ein neues Konto braucht. Das ist für Relays gedacht, die nur Mitglieder annehmen. |
| `HUB_CALDAV` | Ein Nextcloud-Server. nginx leitet `/remote.php/dav/` an ihn weiter, deshalb braucht der Kalender kein CORS. |
| `HUB_ICE`, `HUB_ICE_USERNAME`, `HUB_ICE_CREDENTIAL` | Die STUN- und TURN-Server für Anrufe und direkte Übertragungen. Sie helfen zwei Browsern, sich miteinander zu verbinden. Die Zugangsdaten für TURN sind in der Seite sichtbar. Lege deshalb einen TURN-Zugang an, den nur dieser Hub verwendet. |

`HUB_USER_MOUNTS` wird zwar gelesen, hat aber noch keine Wirkung. Die Variable
gehört zu einer Funktion, die erst noch kommt: einem Space folgen, den der Hub
nicht enthält.

Der Hub muss über HTTPS ausgeliefert werden, weil WebCrypto einen sicheren
Kontext braucht. Seine Relays müssen über `wss://` erreichbar sein. Wird der
Hub über einfaches `http://` geöffnet und nicht auf localhost, weist die Seite
darauf hin und bricht ab.

### Ein Hub in deinem Kiwi Network { #on-a-kiwi-network }

Ein kiwi-master ist der eine Server eines Kiwi Network, der aus dem Internet
erreichbar ist. Er kann ein eigenes Relay und einen eigenen Hub betreiben.
Dafür gibt es zwei Module. Das Modul `nostr-relay` betreibt die Relay-Software
strfry unter `relay.<host>`. Das Modul `hub` betreibt dieses Container-Image,
standardmäßig mit Armory, unter `hub.<host>`.

Beide sind standardmäßig privat. Sie sind nur aus dem Mesh erreichbar und
verwenden das Zertifikat deines Netzwerks. Für einen halböffentlichen Hub
ergänzt du `public_relays` und `public_mounts`. Für einen öffentlichen Hub
ergänzt du `reverse-proxy.public`, das Zertifikate von Let's Encrypt holt.

Das Relay eines öffentlichen Hubs nimmt Beiträge aus dem Mesh an. Aus dem
Internet nimmt es Beiträge nur von Mitgliedern an, die nachweisen, dass sie
ihren Schlüssel besitzen (NIP-42). Mitglieder sind die Leute auf der Liste, die
die Admins (`write_pubkeys`) signieren. Mit `members: registered` ist jeder
Mitglied, der ein Konto auf dem Hub hat. Mehr dazu in der
[Modulreferenz](../server/modules.md#people).

## kiwi-web-catalog { #kiwi-web-catalog }

[derlocke-ng/kiwi-web-catalog](https://github.com/derlocke-ng/kiwi-web-catalog)
ist ein Katalog, also ein git-Repository, das andere Repositories auflistet. Er
führt Hubs, ihre Apps und das Framework auf und hat dasselbe Format wie der
Katalog für den Desktop. Die Datei `apps.list` enthält eine git-URL pro Zeile.
Eine Zeile kann `path=` tragen, wenn eine App in einem Unterordner des
Hub-Repositorys liegt, und `ref=`, um eine Version festzulegen. Jeder Eintrag
enthält ein `kiwi.manifest` mit der `CATEGORY` `Framework`, `Hub` oder `App`.

Zurzeit stehen darin kiwi-framework, Armory und die zehn Apps von Armory. Für
`kiwi catalog add` ist er **nicht** gedacht. Seine Einträge haben kein
Installationsprogramm, und bisher liest nichts den Katalog automatisch. Laut
README sind die Dateien des Katalogs gemeinfrei (CC0).

Um deinen Hub einzutragen, forkst du den Katalog, fügst eine Zeile hinzu,
achtest darauf, dass dein Repository ein `kiwi.manifest` enthält, und stellst
einen Pull Request.

## Noch nicht umgesetzt { #not-built-yet }

Diese Punkte stehen auf der Roadmap des Frameworks, umgesetzt ist davon noch nichts:

- Der Blog.
- Freigaben als Form der Moderation (NIP-72, kind 4550).
- Einem Space folgen, den dein Hub nicht enthält.
- Die Anmeldung über eine Browser-Erweiterung (NIP-07) oder einen Remote-Signer (NIP-46).
- Ein TURN-Server im kiwi-Stack. Die Arbeit daran wartet in kiwi-modules. Ohne
  TURN finden zwei Handys im Mobilfunknetz oft keine direkte Verbindung
  zueinander.
