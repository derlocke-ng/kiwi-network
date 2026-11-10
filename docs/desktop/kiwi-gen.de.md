# kiwi-gen: Kiwi Key Generator

kiwi-gen ist eine Webseite, mit der du **SSH-Schlüssel, SSH-Zertifikate und
TLS-Zertifikate** in deinem Browser erzeugst und verwaltest. Alles entsteht auf
deinem eigenen Rechner und wird dort in einem verschlüsselten Tresor
gespeichert. An einen Server wird nichts geschickt.

- Repository: [derlocke-ng/kiwi-gen](https://github.com/derlocke-ng/kiwi-gen), MIT
- Live: [derlocke-ng.github.io/kiwi-gen](https://derlocke-ng.github.io/kiwi-gen/)
- Es ist eine statische Webseite, keine App für kiwi-updater. Release-Tags gibt
  es nicht.

Du kannst damit die SSH-Schlüssel für deine Fleet-Datei erzeugen (die Datei,
die jede Maschine deines Kiwi Network beschreibt), eine Zertifizierungsstelle
(CA) für deine eigenen Dienste oder Client-Zertifikate. All das entsteht
offline im Browser.

## Funktionen { #features }

**Tresor.** Schlüssel und Zertifikate liegen in einem gemeinsamen,
verschlüsselten Tresor. Verschlüsselt wird mit AES-256-GCM, und der Schlüssel
dafür wird mit PBKDF2-SHA256 und 600.000 Iterationen aus deinem Master-Passwort
abgeleitet. Der Tresor liegt verschlüsselt im localStorage des Browsers.
Entschlüsselt wird er nur im Arbeitsspeicher und nur, solange er entsperrt ist.
Um den Tresor zu sichern oder auf einen anderen Rechner zu bringen, exportierst
du ihn als Datei. Vorhandene Schlüssel und Zertifikate kannst du importieren,
und ein Zertifikat, das mit seinem Schlüssel und seiner Kette kommt, wird als
ein Eintrag gespeichert. Außerdem kannst du einen anderen Tresor mit deinem
zusammenführen, Notizen anlegen, suchen und sehen, was bald abläuft.

**SSH-Schlüssel.** kiwi-gen erzeugt Schlüssel vom Typ Ed25519, ECDSA
(P-256/384/521) und RSA (3072/4096). Sie werden im echten OpenSSH-Format
geschrieben, das `ssh`, `ssh-keygen` und `ssh-add` annehmen. Eine Passphrase
ist optional. Setzt du eine, wird der Schlüssel genauso verschlüsselt, wie
`ssh-keygen` es tut (bcrypt-KDF, aes256-ctr). Der SHA256-Fingerprint des
Schlüssels wird angezeigt.

**SSH-Zertifikate.** Du kannst eine SSH-CA erzeugen oder eine vorhandene laden
und damit Benutzer- oder Host-Zertifikate signieren. kiwi-gen liefert dir die
passenden Zeilen für `sshd_config` und `known_hosts` gleich mit.

**TLS-Zertifikate.** Du kannst eine Root-CA oder eine Zwischen-CA (ECDSA oder
RSA) erzeugen oder eine vorhandene laden. Mit der CA stellst du
Server-Zertifikate für Hostnamen, Wildcards und IP-Adressen aus oder
Client-Zertifikate. Du kannst auch einen Certificate Signing Request (CSR)
signieren, der anderswo erzeugt wurde. Der private Schlüssel muss dann nie in
kiwi-gen landen. kiwi-gen erzeugt Dateien mit der vollständigen Kette und
`.p12`-Bundles. Die Zertifikate bestehen `openssl verify -x509_strict` und
erfüllen Apples Anforderungen an TLS-Server-Zertifikate.

**Untersuchen und umwandeln.** kiwi-gen liest Zertifikate, CSRs, Schlüssel und
SSH-Zertifikate im Format PEM oder DER. Es kann prüfen, ob ein Schlüssel zu
einem Zertifikat passt. Private Schlüssel wandelt es zwischen PKCS#8, PKCS#1
und dem OpenSSH-Format um und kann dabei eine Passphrase hinzufügen oder
entfernen. Öffentliche Schlüssel wandelt es zwischen dem SSH- und dem
PEM-Format um.

## Starten { #running-it }

Öffne `index.html` in einem aktuellen Browser. Das funktioniert direkt von der
Festplatte, ohne Webserver. Du kannst den Ordner aber auch ausliefern:

```bash
git clone https://github.com/derlocke-ng/kiwi-gen.git && cd kiwi-gen
python3 -m http.server 8000      # dann http://localhost:8000
```

Die WebCrypto-Funktionen des Browsers arbeiten nur in einem sicheren Kontext,
also auf einer Seite, die über HTTPS, von `localhost` oder über `file://`
geladen wurde. Öffnest du die Seite über einfaches HTTP von einem anderen
Rechner aus, funktioniert sie nicht.

## So funktioniert es { #how-it-works }

Alle kryptografischen Operationen übernimmt die
[Web Crypto API](https://developer.mozilla.org/docs/Web/API/Web_Crypto_API) des
Browsers. Der Code, der die Formate OpenSSH, X.509, PKCS#8, PKCS#10 und PKCS#12
kodiert, steht in einer einzigen Datei, `kiwi-crypto.js`, die keine
Abhängigkeiten hat. Es gibt keinen Build-Schritt, und die Seite lädt nichts von
einem CDN. Eine Content-Security-Policy blockiert alle Netzwerkanfragen, sodass
Schlüssel die Seite nicht verlassen können.

Eine Webseite kann nicht als SSH-Agent arbeiten. Um die erzeugten Schlüssel zu
benutzen, lädst du sie mit `ssh-add` in deinen gewohnten `ssh-agent`. Der
Tresor ist nur so sicher wie dein Master-Passwort und dein Browser-Profil.
Ed25519 braucht einen aktuellen Browser (Chrome 137+, Firefox 129+,
Safari 17+).
