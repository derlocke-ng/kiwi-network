# kiwi-gen: Kiwi Key Generator

Un gestore nel browser per **chiavi SSH, certificati SSH e certificati
TLS**. Tutto viene creato e conservato in locale in un vault cifrato,
e nulla viene inviato ad alcun server.

- Repository: [derlocke-ng/kiwi-gen](https://github.com/derlocke-ng/kiwi-gen), MIT
- Online: [derlocke-ng.github.io/kiwi-gen](https://derlocke-ng.github.io/kiwi-gen/)
- È una pagina web statica, non un'app di kiwi-updater. Non ci sono tag di release.

Usalo per le chiavi SSH nel tuo file fleet, per una CA per i tuoi servizi o per
certificati client, tutti generati offline nel browser.

## Funzionalità { #features }

**Vault.** Chiavi e certificati sono conservati in un unico vault cifrato: AES-256-GCM,
con la chiave derivata dalla tua password principale tramite PBKDF2-SHA256 con 600.000
iterazioni. Il vault è salvato cifrato nel localStorage del browser e
decifrato solo in memoria mentre è sbloccato. Esportalo come file per farne un backup o
spostarlo. Puoi importare chiavi e certificati esistenti (un certificato con la sua
chiave e la sua catena diventa un unico elemento), unire un altro vault, aggiungere note, cercare e
vedere cosa scade a breve.

**Chiavi SSH.** Ed25519, ECDSA (P-256/384/521) e RSA (3072/4096), nel vero
formato OpenSSH accettato da `ssh`, `ssh-keygen` e `ssh-add`. Le passphrase
opzionali vengono cifrate come fa `ssh-keygen` (KDF bcrypt,
aes256-ctr), e viene mostrato il fingerprint SHA256.

**Certificati SSH.** Crea una CA SSH o caricane una, poi firma certificati utente o host.
Ti fornisce righe pronte per `sshd_config` e `known_hosts`.

**Certificati TLS.** Crea una CA radice o intermedia (ECDSA o RSA), oppure caricane
una esistente. Emetti certificati server (hostname, wildcard, IP) o certificati
client, e firma CSR provenienti da altrove, così la chiave privata non deve mai arrivare
qui. Produce file full-chain e bundle `.p12`. I certificati superano
`openssl verify -x509_strict` e soddisfano i requisiti di Apple per i certificati server
TLS.

**Ispeziona e converti.** Leggi certificati, CSR, chiavi e certificati SSH (PEM
o DER), verifica che una chiave corrisponda a un certificato, converti le chiavi private tra
PKCS#8, PKCS#1 e OpenSSH (aggiungendo o togliendo una passphrase), e converti le chiavi
pubbliche tra SSH e PEM.

## Eseguirlo { #running-it }

Apri `index.html` in un browser moderno (funziona direttamente dal disco), oppure servi
la cartella:

```bash
git clone https://github.com/derlocke-ng/kiwi-gen.git && cd kiwi-gen
python3 -m http.server 8000      # poi http://localhost:8000
```

WebCrypto funziona solo in contesti sicuri: HTTPS, `localhost` o `file://`. L'HTTP
semplice da un'altra macchina non funziona.

## Come funziona { #how-it-works }

Tutta la crittografia usa la
[Web Crypto API](https://developer.mozilla.org/docs/Web/API/Web_Crypto_API) del browser. La
codifica OpenSSH, X.509, PKCS#8, PKCS#10 e PKCS#12 sta in un unico file senza dipendenze,
`kiwi-crypto.js`. Non c'è un passo di build e nulla viene caricato da una CDN. Una
Content-Security-Policy blocca tutte le richieste di rete, quindi le chiavi non possono lasciare la
pagina.

Una pagina web non può fare da agente SSH. Carica le chiavi che crei nel tuo solito
`ssh-agent` con `ssh-add`. Il vault è sicuro solo quanto la tua password principale
e il tuo profilo del browser. Ed25519 richiede un browser recente (Chrome 137+,
Firefox 129+, Safari 17+).
