# DNS, nomi e certificati

## Un'unica catena di resolver { #one-resolver-chain }

Il DNS è un'unica catena per tutta la rete:

```
LAN device ──▶ gateway node's Pi-hole ──▶ master's Pi-hole ──▶ gluetun DNS-over-TLS (Quad9)
VPN client ───────────────────────────────▶ master's Pi-hole       └─ leaves through the VPN exit
```

- **I client VPN** (portatili, telefoni) chiedono al Pi-hole del master su `10.8.0.1`.
- **Il Pi-hole di un node** chiede prima al Pi-hole del master, così la rete condivide
  una sola blocklist e ogni risoluzione esce dall'uscita del master. Quad9
  (`9.9.9.9`, `149.112.112.112`, `fallback_dns`) segue in ordine rigoroso e
  risponde solo mentre il master non è raggiungibile.
- **Il Pi-hole del master** inoltra al resolver DNS-over-TLS del suo client VPN
  (Quad9 di default, `dot_providers`).
- **I nomi sotto il dominio della fleet** vengono inoltrati al master e non
  ne escono mai. Il master marca il dominio come locale.

Ogni host con uno stack ha anche i nomi della fleet in `/etc/hosts` (i suoi nomi
puntano a sé stesso), così backup e rinnovi dei certificati si risolvono senza un
Pi-hole. Su Fedora CoreOS e uCore l'host stesso risolve attraverso il Pi-hole del suo
stack.

**Vicini sulla stessa LAN.** Il Pi-hole e il file hosts di un node rispondono con
l'**indirizzo LAN** dei node della fleet che hanno un indirizzo statico nella sua subnet, così
il traffico tra due macchine nella stessa stanza resta nella stanza. Il master
continua a rispondere con gli indirizzi mesh.

## Nomi: `service.hostname.home` { #names-servicehostnamehome }

Ogni host è `<host>.<domain>` (`papaya.home`), e ogni servizio che esegue è un nome
sotto di esso: `cloud.papaya.home`, `vault.papaya.home`, `portainer.papaya.home`,
`dl.lychee.home`, e sul master `wg.sorbet.home`, `pihole.sorbet.home`,
`hub.sorbet.home`, `relay.sorbet.home`. Ogni nome annunciato da un modulo finisce nei record DNS della fleet
all'**indirizzo mesh** dell'host. Ogni Pi-hole della fleet risolve ogni nome di host e
di servizio (split-horizon, `fleet_records`). Aggiungi i tuoi con
`extra_records`.

Il dominio predefinito è **`.home`**, perché ICANN non lo delegherà come
dominio di primo livello pubblico. Un nome della fleet non può mai finire in un registro pubblico, e
nessun altro può registrarlo o ottenere per esso un certificato considerato attendibile dai browser.
`.kiwi` è un vero TLD, ed è per questo che la fleet lo ha abbandonato. kiwi-server
controlla la tua scelta: `home`, `corp`, `mail`, `internal`, `arpa` e `test` passano
senza commenti, `.local` viene rifiutato (appartiene a mDNS), `.lan` riceve un avviso
(i router lo risolvono da soli) e i TLD pubblici ricevono un avviso.

I nomi *fuori* dal dominio della fleet, per un hub o un relay pubblico, ricevono certificati
Let's Encrypt quando il reverse proxy del master è pubblico.

## Proxy SOCKS5 di Mullvad per nome { #mullvad-socks5-proxies-by-name }

Da kiwi-server 2.2.0 il Pi-hole del master risponde per ogni **proxy SOCKS5 di
Mullvad**, sia come `de-fra-wg-socks5-001.relays.mullvad.net` sia nella forma breve
`de-fra-001.mullvad.home`. gluetun rifiuta queste risposte con indirizzi privati (protezione dal DNS
rebinding), quindi senza i record i nomi si risolverebbero solo
attraverso i resolver di riserva. Un timer dell'host (`km-mullvad-socks.timer`, ogni 6
ore) aggiorna l'elenco da
[derlocke-ng/mullvad-socks5](https://github.com/derlocke-ng/mullvad-socks5).
Da lì vengono accettati solo nomi `*.relays.mullvad.net` con indirizzi `10.x`, così
l'elenco non può mai reindirizzare nessun altro nome.

È attivo nel preset del master, la cui uscita è Mullvad. Disattivalo con
`mullvad_socks: false` nel blocco `dns:` del master.

## Una CA per la fleet { #one-ca-for-the-fleet }

Con `tls.auto: true` (il default), kiwi-server mantiene **un'autorità di
certificazione** per la fleet in `secrets/ca/` (`kiwiCA.key`, `kiwiCA.pem`, RSA-4096,
valida 3650 giorni), creata la prima volta che un host ha bisogno di un certificato. Ogni host che esegue il reverse proxy riceve un certificato per
`<hostname>` e `*.<hostname>` (825 giorni, la durata massima che i browser accettano ancora,
rinnovato quando mancano meno di 30 giorni), e ogni macchina che
kiwi-server costruisce installa la CA nel suo archivio di fiducia.

Imposta i **name constraints** e la CA potrà firmare solo nomi sotto il dominio
della fleet: `tls: { name_constraints: [home] }`. La fleet di esempio lo fa; il
default integrato è nessun vincolo. Una `kiwiCA.key` rubata diventa allora inutile per
qualsiasi altra cosa, e questo conta perché ogni macchina si fida di lei.

```bash
kiwi-server ca fleet.yaml        # mostra la CA della fleet
```

Importa `kiwiCA.pem` sui tuoi dispositivi (browser, telefoni) perché
`https://cloud.papaya.home` sia attendibile. Per usare invece certificati tuoi, imposta
`tls_fullchain` e `tls_privkey` nel modulo reverse-proxy.

!!! warning "Tieni privata `secrets/`"
    `kiwiCA.key` firma certificati di cui si fida ognuna delle tue macchine. Tieni
    `secrets/` e `output/` fuori da git (`output/` è già nel
    `.gitignore` di kiwi-server).
