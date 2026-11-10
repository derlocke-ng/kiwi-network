# kiwi-gen: Kiwi Key Generator

kiwi-gen è una pagina web che crea e gestisce **chiavi SSH, certificati SSH e
certificati TLS** nel tuo browser. Tutto viene creato sul tuo computer e lì
conservato in una cassaforte cifrata, e niente viene inviato ad alcun server.

- Repository: [derlocke-ng/kiwi-gen](https://github.com/derlocke-ng/kiwi-gen), MIT
- Online: [derlocke-ng.github.io/kiwi-gen](https://derlocke-ng.github.io/kiwi-gen/)
- È una pagina web statica, non un’app di kiwi-updater. Non ha tag di release.

Puoi usarlo per creare le chiavi SSH per il tuo file fleet (il file che descrive
tutte le macchine della tua Kiwi Network), un’autorità di certificazione (CA)
per i tuoi servizi oppure dei certificati client. Tutto viene generato offline,
nel browser.

## Funzioni { #features }

**Cassaforte.** Chiavi e certificati sono conservati in un’unica cassaforte
cifrata. È cifrata con AES-256-GCM, e la chiave di cifratura viene ricavata
dalla tua password principale con PBKDF2-SHA256 e 600.000 iterazioni. La
cassaforte è salvata in forma cifrata nel localStorage del browser. Viene
decifrata soltanto in memoria, e soltanto finché resta sbloccata. Per farne il
backup o spostarla, esportala in un file. Puoi importare chiavi e certificati
esistenti, e un certificato che arriva con la sua chiave e la sua catena viene
salvato come un unico elemento. Puoi anche unire un’altra cassaforte alla tua,
aggiungere note, cercare e vedere che cosa scade a breve.

**Chiavi SSH.** kiwi-gen crea chiavi Ed25519, ECDSA (P-256/384/521) e RSA
(3072/4096). Le scrive nel vero formato OpenSSH, che `ssh`, `ssh-keygen` e
`ssh-add` accettano. La passphrase è facoltativa. Se ne imposti una, la chiave
viene cifrata nello stesso modo in cui lo fa `ssh-keygen` (KDF bcrypt,
aes256-ctr). Viene mostrata l’impronta SHA256 della chiave.

**Certificati SSH.** Puoi creare una CA SSH o caricarne una esistente, e poi
firmare con essa certificati utente o certificati host. kiwi-gen ti dà le righe
corrispondenti per `sshd_config` e `known_hosts`, pronte da usare.

**Certificati TLS.** Puoi creare una CA radice o una CA intermedia (ECDSA o
RSA), oppure caricarne una esistente. Con la CA emetti certificati server per
nomi host, wildcard e indirizzi IP, oppure certificati client. Puoi anche
firmare una richiesta di firma del certificato (CSR) creata altrove, così la
chiave privata non deve mai entrare in kiwi-gen. kiwi-gen produce file con la
catena completa e pacchetti `.p12`. I certificati superano
`openssl verify -x509_strict` e rispettano i requisiti di Apple per i
certificati dei server TLS.

**Analisi e conversione.** kiwi-gen legge certificati, CSR, chiavi e certificati
SSH in formato PEM o DER. Può verificare che una chiave corrisponda a un
certificato. Converte le chiavi private tra i formati PKCS#8, PKCS#1 e OpenSSH,
e durante la conversione può aggiungere o togliere una passphrase. Converte
anche le chiavi pubbliche tra il formato SSH e il formato PEM.

## Come avviarlo { #running-it }

Apri `index.html` in un browser recente. Funziona direttamente dal disco, senza
un server web. Puoi anche pubblicare la cartella:

```bash
git clone https://github.com/derlocke-ng/kiwi-gen.git && cd kiwi-gen
python3 -m http.server 8000      # poi http://localhost:8000
```

Le funzioni WebCrypto del browser funzionano soltanto in un contesto sicuro,
cioè in una pagina caricata via HTTPS, da `localhost` oppure da `file://`. Se
apri la pagina in semplice HTTP da un’altra macchina, non funziona.

## Come funziona { #how-it-works }

Tutte le operazioni crittografiche sono eseguite dalla
[Web Crypto API](https://developer.mozilla.org/docs/Web/API/Web_Crypto_API) del
browser. Il codice che produce i formati OpenSSH, X.509, PKCS#8, PKCS#10 e
PKCS#12 sta in un solo file, `kiwi-crypto.js`, che non ha dipendenze. Non c’è
alcuna fase di build, e la pagina non carica nulla da una CDN. Una
Content-Security-Policy blocca tutte le richieste di rete, quindi le chiavi non
possono uscire dalla pagina.

Una pagina web non può fare da agente SSH. Per usare le chiavi che crei,
caricale nel tuo solito `ssh-agent` con `ssh-add`. La cassaforte è sicura
quanto la tua password principale e il tuo profilo del browser. Ed25519 richiede
un browser recente (Chrome 137+, Firefox 129+, Safari 17+).
