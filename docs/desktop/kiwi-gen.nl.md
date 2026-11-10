# kiwi-gen: Kiwi Key Generator

kiwi-gen is een webpagina waarmee je **SSH-sleutels, SSH-certificaten en
TLS-certificaten** in je browser aanmaakt en beheert. Alles wordt op je eigen
computer gemaakt en daar in een versleutelde kluis bewaard, en er gaat niets
naar een server.

- Repository: [derlocke-ng/kiwi-gen](https://github.com/derlocke-ng/kiwi-gen), MIT
- Online: [derlocke-ng.github.io/kiwi-gen](https://derlocke-ng.github.io/kiwi-gen/)
- Het is een statische webpagina, geen app voor kiwi-updater. Er zijn geen
  release-tags.

Je kunt er de SSH-sleutels mee maken voor je fleetbestand (het bestand dat elke
machine van je Kiwi Network beschrijft), een certificaatautoriteit (CA) voor je
eigen diensten, of clientcertificaten. Alles wordt offline in de browser
gegenereerd.

## Functies { #features }

**Kluis.** Sleutels en certificaten staan samen in één versleutelde kluis. Die
is versleuteld met AES-256-GCM, en de sleutel daarvoor wordt met PBKDF2-SHA256
in 600.000 iteraties afgeleid van je hoofdwachtwoord. De kluis staat versleuteld
in de localStorage van de browser. Ze wordt alleen in het geheugen ontsleuteld,
en alleen zolang ze ontgrendeld is. Wil je een back-up van de kluis maken of
haar verhuizen, exporteer haar dan als bestand. Je kunt bestaande sleutels en
certificaten importeren, en een certificaat met bijbehorende sleutel en keten
wordt als één item bewaard. Je kunt ook een andere kluis met de jouwe
samenvoegen, notities toevoegen, zoeken en zien wat binnenkort verloopt.

**SSH-sleutels.** kiwi-gen maakt sleutels van het type Ed25519, ECDSA
(P-256/384/521) en RSA (3072/4096). Ze worden in het echte OpenSSH-formaat
geschreven, dat `ssh`, `ssh-keygen` en `ssh-add` accepteren. Een wachtzin is
optioneel. Stel je er een in, dan wordt de sleutel op dezelfde manier
versleuteld als `ssh-keygen` dat doet (bcrypt-KDF, aes256-ctr). De
SHA256-vingerafdruk van de sleutel wordt getoond.

**SSH-certificaten.** Je kunt een SSH-CA aanmaken of een bestaande laden, en
daarmee gebruikerscertificaten of hostcertificaten ondertekenen. kiwi-gen geeft
je de bijpassende regels voor `sshd_config` en `known_hosts`, klaar voor
gebruik.

**TLS-certificaten.** Je kunt een root-CA of een tussen-CA aanmaken (ECDSA of
RSA), of een bestaande laden. Met de CA geef je servercertificaten uit voor
hostnamen, wildcards en IP-adressen, of clientcertificaten. Je kunt ook een
certificaataanvraag (CSR) ondertekenen die ergens anders is gemaakt, zodat de
privésleutel nooit in kiwi-gen hoeft te komen. kiwi-gen maakt bestanden met de
volledige keten en `.p12`-bundels. De certificaten doorstaan
`openssl verify -x509_strict` en voldoen aan de eisen van Apple voor
TLS-servercertificaten.

**Bekijken en omzetten.** kiwi-gen leest certificaten, CSR’s, sleutels en
SSH-certificaten in PEM- of DER-formaat. Het kan controleren of een sleutel bij
een certificaat hoort. Het zet privésleutels om tussen PKCS#8, PKCS#1 en het
OpenSSH-formaat, en kan daarbij een wachtzin toevoegen of verwijderen. Ook
publieke sleutels zet het om tussen het SSH- en het PEM-formaat.

## Gebruiken { #running-it }

Open `index.html` in een moderne browser. Dat werkt rechtstreeks vanaf de
schijf, zonder webserver. Je kunt de map ook via een webserver aanbieden:

```bash
git clone https://github.com/derlocke-ng/kiwi-gen.git && cd kiwi-gen
python3 -m http.server 8000      # daarna http://localhost:8000
```

De WebCrypto-functies van de browser werken alleen in een beveiligde context:
een pagina die via HTTPS is geladen, vanaf `localhost` of vanaf `file://`. Open
je de pagina via gewoon HTTP vanaf een andere machine, dan werkt ze niet.

## Hoe het werkt { #how-it-works }

Alle cryptografische bewerkingen doet de
[Web Crypto API](https://developer.mozilla.org/docs/Web/API/Web_Crypto_API) van
de browser. De code die de formaten OpenSSH, X.509, PKCS#8, PKCS#10 en PKCS#12
codeert, staat in één bestand, `kiwi-crypto.js`, zonder afhankelijkheden. Er is
geen buildstap, en de pagina laadt niets van een CDN. Een
Content-Security-Policy blokkeert alle netwerkverzoeken, dus sleutels kunnen de
pagina niet verlaten.

Een webpagina kan niet als SSH-agent werken. Wil je de sleutels gebruiken die je
maakt, laad ze dan met `ssh-add` in je gewone `ssh-agent`. De kluis is zo
veilig als je hoofdwachtwoord en je browserprofiel. Voor Ed25519 heb je een
recente browser nodig (Chrome 137+, Firefox 129+, Safari 17+).
