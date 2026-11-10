# kiwi-gen: Kiwi Key Generator

Ein browserbasierter Manager für **SSH-Schlüssel, SSH-Zertifikate und
TLS-Zertifikate**. Alles wird lokal in einem verschlüsselten Tresor erstellt und
gespeichert, und nichts wird an irgendeinen Server geschickt.

- Repository: [derlocke-ng/kiwi-gen](https://github.com/derlocke-ng/kiwi-gen), MIT
- Live: [derlocke-ng.github.io/kiwi-gen](https://derlocke-ng.github.io/kiwi-gen/)
- Es ist eine statische Webseite, keine kiwi-updater-App. Es gibt keine Release-Tags.

Nutze es für die SSH-Schlüssel in deiner Fleet-Datei, eine CA für deine eigenen
Dienste oder Client-Zertifikate, alles offline im Browser erzeugt.

## Funktionen { #features }

**Tresor.** Schlüssel und Zertifikate liegen in einem verschlüsselten Tresor:
AES-256-GCM, mit dem Schlüssel per PBKDF2-SHA256 mit 600.000 Iterationen aus deinem
Master-Passwort abgeleitet. Der Tresor wird verschlüsselt im localStorage des
Browsers gespeichert und nur im Speicher entschlüsselt, solange er entsperrt ist.
Exportiere ihn als Datei, um ihn zu sichern oder umzuziehen. Du kannst vorhandene
Schlüssel und Zertifikate importieren (ein Zertifikat mit seinem Schlüssel und
seiner Kette wird zu einem Eintrag), einen anderen Tresor zusammenführen, Notizen
hinzufügen, suchen und sehen, was bald abläuft.

**SSH-Schlüssel.** Ed25519, ECDSA (P-256/384/521) und RSA (3072/4096), im echten
OpenSSH-Format, das `ssh`, `ssh-keygen` und `ssh-add` akzeptieren. Optionale
Passphrasen werden so verschlüsselt, wie `ssh-keygen` es tut (bcrypt-KDF,
aes256-ctr), und der SHA256-Fingerabdruck wird angezeigt.

**SSH-Zertifikate.** Erstelle eine SSH-CA oder lade eine, dann signiere Benutzer-
oder Host-Zertifikate. Du bekommst fertige Zeilen für `sshd_config` und
`known_hosts`.

**TLS-Zertifikate.** Erstelle eine Root- oder Zwischen-CA (ECDSA oder RSA) oder lade
eine vorhandene. Stelle Server-Zertifikate (Hostnamen, Wildcards, IPs) oder
Client-Zertifikate aus und signiere CSRs von anderswo, sodass der private Schlüssel
nie hierher kommen muss. Es erzeugt Full-Chain-Dateien und `.p12`-Bundles.
Zertifikate bestehen `openssl verify -x509_strict` und erfüllen Apples Anforderungen
an TLS-Server-Zertifikate.

**Prüfen & konvertieren.** Lies Zertifikate, CSRs, Schlüssel und SSH-Zertifikate
(PEM oder DER), prüfe, ob ein Schlüssel zu einem Zertifikat passt, konvertiere
private Schlüssel zwischen PKCS#8, PKCS#1 und OpenSSH (mit Hinzufügen oder
Entfernen einer Passphrase) und konvertiere öffentliche Schlüssel zwischen SSH und
PEM.

## Starten { #running-it }

Öffne `index.html` in einem modernen Browser (es funktioniert direkt von der
Festplatte) oder liefere den Ordner aus:

```bash
git clone https://github.com/derlocke-ng/kiwi-gen.git && cd kiwi-gen
python3 -m http.server 8000      # dann http://localhost:8000
```

WebCrypto funktioniert nur in sicheren Kontexten: HTTPS, `localhost` oder
`file://`. Einfaches HTTP von einer anderen Maschine aus funktioniert nicht.

## So funktioniert es { #how-it-works }

Die gesamte Kryptografie nutzt die
[Web Crypto API](https://developer.mozilla.org/docs/Web/API/Web_Crypto_API) des
Browsers. Die Kodierung für OpenSSH, X.509, PKCS#8, PKCS#10 und PKCS#12 steckt in
einer einzigen Datei ohne Abhängigkeiten, `kiwi-crypto.js`. Es gibt keinen
Build-Schritt, und nichts wird von einem CDN geladen. Eine
Content-Security-Policy blockiert alle Netzwerkanfragen, sodass Schlüssel die Seite
nicht verlassen können.

Eine Webseite kann nicht als SSH-Agent arbeiten. Lade die Schlüssel, die du
erstellst, mit `ssh-add` in deinen üblichen `ssh-agent`. Der Tresor ist nur so
sicher wie dein Master-Passwort und dein Browserprofil. Ed25519 braucht einen
aktuellen Browser (Chrome 137+, Firefox 129+, Safari 17+).
