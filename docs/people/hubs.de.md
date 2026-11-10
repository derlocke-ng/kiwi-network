# Einen eigenen Hub betreiben

Ein Hub besteht aus statischen Dateien, einen zu hosten heißt also, einen Ordner
über HTTPS auszuliefern. Es gibt drei Wege, einen zu betreiben:

- **Armory so benutzen, wie es ist:** [derlocke-ng.github.io/armory](https://derlocke-ng.github.io/armory/).
- **Eine eigene Distribution bauen:** dein Name, deine Relays und Apps, auf
  beliebigem statischem Hosting.
- **Den Hub-Container betreiben:** zum Beispiel in deinem eigenen Kiwi Network, mit
  eigenem Relay, als privater Hub, den nur das Mesh erreicht.

## Arten von Hubs { #kinds-of-hub }

| Art | Wie | Beispiel |
|---|---|---|
| **Öffentlich** | Öffentliche Relays; jeder kann ihn öffnen | Armory |
| **Privat** | Die Relays des Hubs sind gesperrt (`policy.relays: 'locked'`), und die Seiten warten, bis eines davon antwortet (`requireHub`), mit Relays innerhalb eines VPN | ein Firmen-Hub auf dem kiwi-master der Firma |
| **Halböffentlich** | Ein privater Hub mit einem öffentlichen Bereich für ausgewählte Apps (zum Beispiel den Chat) auf öffentlichen Relays | |

Jedes Event gehört zu genau einem Netz (dem des Hubs, dem öffentlichen Bereich oder
dem eines Space) und wechselt nie in ein anderes.

## Deine eigene Distribution { #your-own-distribution }

Armory ist die Vorlage (auf GitHub gibt dir *Use this template* eine Kopie ohne
deren Historie):

1. Bearbeite **`distribution.js`**: ID, Name, Zeichen, Beschreibung, Homepage,
   Repository, Relays, Medienserver, Spaces, Apps und Einbindungen. Um auch die
   Spaces von Armory zu bedienen, kopiere deren `owner` und `id` aus der `hub.json`
   von Armory.
2. Bearbeite **`locales/*.json`**: Titel, Einleitung und Fußzeile und einen
   Kartentext pro Einbindung. Englisch ist der Fallback.
3. Aktualisiere **`kiwi.manifest`** und trag deinen Hub optional in
   [kiwi-web-catalog](#kiwi-web-catalog) ein.
4. Auf GitHub: *Settings → Pages → Source: GitHub Actions*, dann pushen.

```bash
npm install
npm run dev                  # der Hub mit Hot Reload, http://localhost:5173
npm test
npm run build && npm run serve
npm run relay:nostr          # ein lokales Test-Relay unter ws://localhost:7777
npm run new-app -- <id> "<Name>" <icon>   # das Gerüst einer neuen App erzeugen
```

Leg kiwi-framework per Commit oder Tag fest, nie per Branch. Der Build prüft deine
`distribution.js` (zum Beispiel braucht eine öffentliche Einbindung öffentliche
Relays und umgekehrt).

Der Stack ist TypeScript, React 19 und Vite für alles Sichtbare. Die Datenschicht in
`shared/` ist einfaches JavaScript mit JSDoc-Typen. Tests laufen im Test-Runner von
node und, für den Browser, in Playwright.

## Der Hub-Container { #the-hub-container }

Armory ist auch ein Container-Image, `ghcr.io/derlocke-ng/armory`, gebaut aus dem
`container/Dockerfile` des Frameworks (nginx). Beim Start schreibt sein Entrypoint
`hub.local.json` aus `HUB_*`-Variablen, und die Seite liest sie, bevor sie sich
verbindet. Ein Deployment kann so Relays und Richtlinie wählen, aber keinen Code
hinzufügen. Ohne gesetzte Variablen läuft der Hub so, wie er gebaut wurde.

```bash
docker run --rm -p 8080:80 \
  -e HUB_RELAYS=wss://relay.sh3.home \
  -e HUB_RELAYS_LOCKED=true -e HUB_REQUIRE_HUB=true \
  -e HUB_PUBLIC_RELAYS=wss://nos.lol -e HUB_PUBLIC_MOUNTS=uplink \
  ghcr.io/you/your-hub
```

| Variable | Bedeutung |
|---|---|
| `HUB_RELAYS` | die eigenen Relays des Hubs |
| `HUB_PUBLIC_RELAYS` | die Relays des öffentlichen Bereichs (gesetzt und leer: kein öffentlicher Bereich) |
| `HUB_DIRECTORY_RELAYS` | wo Relay-Listen veröffentlicht und nachgeschlagen werden |
| `HUB_RELAYS_LOCKED` | `true`: Leute können die Relays des Hubs nicht ersetzen |
| `HUB_REQUIRE_HUB` | `true`: Seiten warten, solange keines der Relays des Hubs antwortet |
| `HUB_PUBLIC_MOUNTS` | Einbindungen im öffentlichen Bereich, nach ID |
| `HUB_ACCOUNT_MOUNTS` | Einbindungen, die ein Konto verlangen |
| `HUB_REQUIRE_ACCOUNT` | `true`: jede Einbindung verlangt ein Konto |
| `HUB_SPACE_RELAYS` | Relays pro Space: `jobs=wss://…;gems=wss://a,wss://b` |
| `HUB_MODERATORS` | Schlüssel, die jeden Space moderieren, den der Hub definiert |
| `HUB_REGISTER_POW` | Proof-of-Work-Bits für ein neues Konto (Relays nur für Mitglieder) |
| `HUB_CALDAV` | eine Nextcloud; nginx leitet `/remote.php/dav/` an sie weiter, sodass der Kalender kein CORS braucht |
| `HUB_ICE`, `HUB_ICE_USERNAME`, `HUB_ICE_CREDENTIAL` | STUN/TURN-Server für Anrufe und Direktübertragungen. Die TURN-Anmeldung ist in der Seite sichtbar, also gib ihr eine Anmeldung nur für diesen Hub |

`HUB_USER_MOUNTS` wird gelesen, bewirkt aber noch nichts: Einem Space zu folgen, den
der Hub nicht mitbringt, kommt erst noch.

Der Hub muss über HTTPS ausgeliefert werden (WebCrypto braucht einen sicheren
Kontext) und seine Relays über `wss://`. Über einfaches `http://` (außer localhost)
sagt die Seite das und hält an.

### In einem Kiwi Network { #on-a-kiwi-network }

Ein kiwi-master kann sein eigenes Relay und seinen eigenen Hub mitbringen: das Modul
`nostr-relay` (strfry unter `relay.<host>`) und das Modul `hub` (dieses Image,
standardmäßig Armory, unter `hub.<host>`). Sie sind standardmäßig privat: nur aus
dem Mesh erreichbar, mit dem Zertifikat der Fleet. Ein halböffentlicher Hub fügt
`public_relays` und `public_mounts` hinzu. Ein öffentlicher fügt
`reverse-proxy.public` hinzu, das Zertifikate von Let's Encrypt bekommt. Das Relay
nimmt dann Beiträge aus dem Mesh an und aus dem Internet nur von Mitgliedern, die
ihren Schlüssel nachweisen (NIP-42): denen auf der Liste, die die Admins
(`write_pubkeys`) signieren, oder, mit `members: registered`, jedem mit einem Konto
auf dem Hub. Siehe die [Modul-Referenz](../server/modules.md#people).

## kiwi-web-catalog { #kiwi-web-catalog }

[derlocke-ng/kiwi-web-catalog](https://github.com/derlocke-ng/kiwi-web-catalog)
listet Hubs, ihre Apps und das Framework, in derselben Form wie der
Desktop-Katalog: eine `apps.list` mit einer Git-URL pro Zeile (`path=` für eine App
im Repository eines Hubs, `ref=` zum Festlegen) und ein `kiwi.manifest` in jedem
Eintrag mit einer `CATEGORY` von `Framework`, `Hub` oder `App`.

Heute listet er kiwi-framework, Armory und die zehn Apps von Armory. Er ist **nicht**
für `kiwi catalog add` gedacht: Diese Einträge haben keinen Installer, und noch
liest nichts den Katalog automatisch. Die Katalogdateien sind gemeinfrei (CC0, laut
seiner README).

Um deinen Hub hinzuzufügen: forken, eine Zeile hinzufügen, sicherstellen, dass das
Repository ein `kiwi.manifest` hat, und einen Pull Request öffnen.

## Noch nicht gebaut { #not-built-yet }

Diese Punkte stammen aus der eigenen Roadmap des Frameworks:

- Der Blog.
- Freigaben durch Moderatoren (NIP-72 kind 4550).
- Spaces folgen, die ein Hub nicht mitbringt.
- Signer nach NIP-07 und NIP-46.
- Ein TURN-Server im Kiwi-Stack. Er wartet in kiwi-modules; ohne TURN finden zwei
  Telefone im Mobilfunknetz oft keinen direkten Weg.
