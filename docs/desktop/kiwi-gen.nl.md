# kiwi-gen: Kiwi Key Generator

Een beheerder in de browser voor **SSH-sleutels, SSH-certificaten en
TLS-certificaten**. Alles wordt lokaal aangemaakt en opgeslagen in een
versleutelde kluis, en er wordt niets naar een server gestuurd.

- Repository: [derlocke-ng/kiwi-gen](https://github.com/derlocke-ng/kiwi-gen), MIT
- Live: [derlocke-ng.github.io/kiwi-gen](https://derlocke-ng.github.io/kiwi-gen/)
- Het is een statische webpagina, geen kiwi-updater-app. Er zijn geen release-tags.

Gebruik het voor de SSH-sleutels in je fleet-bestand, een CA voor je eigen
diensten, of clientcertificaten, allemaal offline gegenereerd in de browser.

## Functies { #features }

**Kluis.** Sleutels en certificaten worden in één versleutelde kluis bewaard:
AES-256-GCM, met de sleutel afgeleid van je hoofdwachtwoord via PBKDF2-SHA256 met
600.000 iteraties. De kluis wordt versleuteld opgeslagen in de localStorage van
de browser en alleen in het geheugen ontsleuteld zolang hij ontgrendeld is.
Exporteer hem als bestand om er een back-up van te maken of hem te verplaatsen.
Je kunt bestaande sleutels en certificaten importeren (een certificaat met zijn
sleutel en keten wordt één item), een andere kluis samenvoegen, notities
toevoegen, zoeken, en zien wat binnenkort verloopt.

**SSH-sleutels.** Ed25519, ECDSA (P-256/384/521) en RSA (3072/4096), in echt
OpenSSH-formaat dat `ssh`, `ssh-keygen` en `ssh-add` accepteren. Optionele
wachtzinnen worden versleuteld zoals `ssh-keygen` dat doet (bcrypt-KDF,
aes256-ctr), en de SHA256-vingerafdruk wordt getoond.

**SSH-certificaten.** Maak een SSH-CA aan of laad er een, en onderteken daarna
gebruikers- of hostcertificaten. Je krijgt kant-en-klare regels voor
`sshd_config` en `known_hosts`.

**TLS-certificaten.** Maak een root- of tussen-CA aan (ECDSA of RSA), of laad een
bestaande. Geef servercertificaten uit (hostnamen, wildcards, IP's) of
clientcertificaten, en onderteken CSR's van elders zodat de privésleutel nooit
hierheen hoeft te komen. Het maakt full-chain-bestanden en `.p12`-bundels.
Certificaten doorstaan `openssl verify -x509_strict` en voldoen aan de eisen van
Apple voor TLS-servercertificaten.

**Inspecteren en converteren.** Lees certificaten, CSR's, sleutels en
SSH-certificaten (PEM of DER), controleer of een sleutel bij een certificaat
hoort, converteer privésleutels tussen PKCS#8, PKCS#1 en OpenSSH (waarbij je een
wachtzin kunt toevoegen of verwijderen), en converteer publieke sleutels tussen SSH
en PEM.

## Het draaien { #running-it }

Open `index.html` in een moderne browser (het werkt direct vanaf schijf), of
serveer de map:

```bash
git clone https://github.com/derlocke-ng/kiwi-gen.git && cd kiwi-gen
python3 -m http.server 8000      # daarna http://localhost:8000
```

WebCrypto werkt alleen in beveiligde contexten: HTTPS, `localhost` of `file://`.
Gewone HTTP vanaf een andere machine werkt niet.

## Hoe het werkt { #how-it-works }

Alle cryptografie gebruikt de
[Web Crypto API](https://developer.mozilla.org/docs/Web/API/Web_Crypto_API) van
de browser. De codering voor OpenSSH, X.509, PKCS#8, PKCS#10 en PKCS#12 zit in
één bestand zonder afhankelijkheden, `kiwi-crypto.js`. Er is geen buildstap en
er wordt niets van een CDN geladen. Een Content-Security-Policy blokkeert alle
netwerkverzoeken, zodat sleutels de pagina niet kunnen verlaten.

Een webpagina kan niet als SSH-agent optreden. Laad de sleutels die je maakt in
je gewone `ssh-agent` met `ssh-add`. De kluis is maar zo veilig als je
hoofdwachtwoord en je browserprofiel. Ed25519 vereist een actuele browser
(Chrome 137+, Firefox 129+, Safari 17+).
