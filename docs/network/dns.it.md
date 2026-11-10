# DNS, nomi e certificati

Ogni macchina e ogni servizio di una Kiwi Network ha un nome, per esempio
`cloud.papaya.home`, e lo apri in HTTPS con un certificato di cui i tuoi
dispositivi si fidano. Questa pagina spiega come vengono risolti i nomi nella
rete, come sono composti e da dove arrivano i certificati. I server DNS sono
dei Pi-hole, che con una lista di blocco comune bloccano anche i domini
indesiderati.

## Un’unica catena di resolver { #one-resolver-chain }

Tutte le query DNS della rete percorrono la stessa catena di server DNS:

```
LAN device ──▶ gateway node's Pi-hole ──▶ master's Pi-hole ──▶ gluetun DNS-over-TLS (Quad9)
VPN client ───────────────────────────────▶ master's Pi-hole       └─ leaves through the VPN exit
```

- **I client VPN** (portatili, telefoni) mandano le loro query al Pi-hole del
  master, su `10.8.0.1`.
- **Il Pi-hole di un node** interroga per primo il Pi-hole del master. Così
  tutta la rete usa la stessa lista di blocco, e ogni query arriva a Internet
  attraverso l’uscita del master, cioè la connessione del master a Internet.
  Il secondo server è Quad9 (`9.9.9.9`, `149.112.112.112`, impostato con
  `fallback_dns`). I server vengono interrogati rigorosamente in quest’ordine,
  quindi Quad9 risponde soltanto quando il master non è raggiungibile.
- **Il Pi-hole del master** inoltra le query al resolver DNS-over-TLS del
  proprio client VPN. Per impostazione predefinita questo resolver è Quad9
  (`dot_providers`).
- **I nomi del dominio della fleet** vengono inoltrati al master e da lì non
  vanno mai oltre: il master contrassegna il dominio come locale.

Ogni macchina con uno stack ha i nomi della fleet anche nel proprio file
`/etc/hosts`, dove i suoi nomi puntano alla macchina stessa. I backup e il
rinnovo dei certificati riescono così a risolvere i nomi anche senza un
Pi-hole. Su Fedora CoreOS e uCore la macchina usa come resolver il Pi-hole del
proprio stack.

**Vicini sulla stessa LAN.** Se altri node della fleet hanno un indirizzo
statico nella sottorete di un node, il Pi-hole e il file hosts di quel node
rispondono con il loro **indirizzo LAN**. Il traffico tra due macchine della
stessa LAN resta così in quella LAN. Il master continua a rispondere con gli
indirizzi della mesh.

## Nomi: `service.hostname.home` { #names-servicehostnamehome }

Ogni host ha il nome `<host>.<domain>`, per esempio `papaya.home`. Ogni
servizio che gira su quell’host riceve un nome che è un sottodominio di quello
dell’host:
`cloud.papaya.home`, `vault.papaya.home`, `portainer.papaya.home`,
`dl.lychee.home`, e sul master `wg.sorbet.home`, `pihole.sorbet.home`,
`hub.sorbet.home`, `relay.sorbet.home`. Ogni nome dichiarato da un modulo
finisce nei record DNS della fleet con l’**indirizzo dell’host nella mesh**.
Qualsiasi Pi-hole della fleet sa risolvere tutti i nomi di host e tutti i nomi
di servizio. L’impostazione che lo regola è `fleet_records`, e la tecnica si
chiama split-horizon DNS, perché a questi nomi si risponde soltanto
all’interno della tua rete. Con `extra_records` puoi aggiungere record tuoi.

Il dominio predefinito è **`.home`**. È stato scelto perché ICANN non lo
delegherà come dominio di primo livello (TLD) pubblico. Un nome della tua fleet
non può quindi finire in un registro pubblico, e nessun altro può registrarlo
né ottenere per quel nome un certificato di cui i browser si fidino. `.kiwi`,
invece, è un vero TLD, ed è per questo che Kiwi Network non lo usa più.
kiwi-server controlla il dominio che scegli. `home`, `corp`, `mail`,
`internal`, `arpa` e `test` vengono accettati senza osservazioni. `.local`
viene rifiutato, perché è riservato a mDNS. `.lan` produce un avviso, perché i
router rispondono già in proprio alle query per quel dominio. Un avviso lo
producono anche i TLD pubblici.

I nomi *esterni* al dominio della fleet, che ti servono per un hub o un relay
pubblico, ricevono certificati Let’s Encrypt se il reverse proxy del master è
pubblico.

## I proxy SOCKS5 di Mullvad per nome { #mullvad-socks5-proxies-by-name }

I proxy SOCKS5 di Mullvad hanno indirizzi in un intervallo privato, e questa
funzione ti permette di usarli per nome. Da kiwi-server 2.2.0 il Pi-hole del
master risolve il nome di ogni **proxy SOCKS5 di Mullvad**, sia quello
completo, come `de-fra-wg-socks5-001.relays.mullvad.net`, sia uno breve, come
`de-fra-001.mullvad.home`. gluetun scarta le risposte DNS che puntano a
indirizzi privati: è la sua protezione contro il DNS rebinding. Senza questi
record, quindi, quei nomi verrebbero risolti soltanto dai resolver di riserva.
Un timer sull’host (`km-mullvad-socks.timer`, ogni 6 ore) aggiorna l’elenco da
[derlocke-ng/mullvad-socks5](https://github.com/derlocke-ng/mullvad-socks5).
Di quell’elenco vengono accettati soltanto i nomi `*.relays.mullvad.net` con
indirizzi `10.x`, così l’elenco non può mai dirottare un altro nome.

La funzione è attiva nel preset del master, perché l’uscita del preset è
Mullvad. Per disattivarla, imposta `mullvad_socks: false` nel blocco `dns:` del
master.

## Una sola CA per tutta la fleet { #one-ca-for-the-fleet }

Un’autorità di certificazione (CA) firma i certificati che i tuoi servizi usano
per HTTPS. Con `tls.auto: true`, che è il valore predefinito, kiwi-server tiene
**un’unica autorità di certificazione** per tutta la fleet in `secrets/ca/`. La
CA è composta dai file `kiwiCA.key` e `kiwiCA.pem`, usa RSA-4096 ed è valida
3650 giorni. kiwi-server la crea la prima volta che un host ha bisogno di un
certificato. Ogni host su cui gira il reverse proxy riceve un certificato per
`<hostname>` e `*.<hostname>`. Questo certificato vale 825 giorni, la durata
massima che i browser accettano ancora, e viene rinnovato quando mancano meno
di 30 giorni alla scadenza. Ogni macchina costruita da kiwi-server installa la
CA tra i certificati attendibili del sistema.

Se imposti dei **vincoli sui nomi** (name constraints), la CA può firmare
soltanto nomi del dominio della fleet: `tls: { name_constraints: [home] }`. La
fleet di esempio li imposta, mentre il valore predefinito integrato non prevede
alcun vincolo. Con il vincolo, chi rubasse `kiwiCA.key` non potrebbe usarla per
nessun altro nome. È importante, perché tutte le macchine si fidano della CA.

```bash
kiwi-server ca fleet.yaml        # mostra la CA della fleet
```

Importa `kiwiCA.pem` sui tuoi dispositivi (browser, telefoni), così si
fideranno di `https://cloud.papaya.home`. Se preferisci usare certificati tuoi,
imposta `tls_fullchain` e `tls_privkey` nel modulo reverse-proxy.

!!! warning "Tieni privata la cartella `secrets/`"
    `kiwiCA.key` firma certificati di cui si fidano tutte le tue macchine.
    Tieni `secrets/` e `output/` fuori da git (`output/` è già nel `.gitignore`
    di kiwi-server).
