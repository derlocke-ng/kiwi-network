# kiwi-killswitch

Un **kill switch VPN fail-closed** per GNOME su Fedora Silverblue e Bluefin. Un unico
demone root gestisce il firewall. Un interruttore nelle Impostazioni rapide di GNOME, un'app GTK4 e una
CLI lo comandano tramite il bus di sistema D-Bus, senza mai chiedere una password.

Protegge **una** connessione VPN alla volta, WireGuard o OpenVPN. Non
connette la VPN al posto tuo: avvii le connessioni nelle Impostazioni di GNOME, e il
kill switch costruisce un firewall a prova di fughe attorno a ciò che è effettivamente attivo.

- Repository: [derlocke-ng/kiwi-killswitch](https://github.com/derlocke-ng/kiwi-killswitch), GPL-3.0-or-later
- Ultima release: **v0.2.3**. È nel [catalogo Kiwi](catalogs.md), ambiti user + system.
- GNOME Shell da 45 a 50.

```
┌─ your session (unprivileged) ─────────────┐   ┌─ root ──────────────────────┐
│  GNOME Quick Settings toggle              │   │  kiwi-killswitchd           │
│  kiwi-killswitch-settings (GTK4)          │──▶│   nftables  (inet + netdev) │
│  kiwi-killswitch (CLI)                    │   │   systemd-resolved steering │
└───────────────────────────────────────────┘   │   NM + kernel event watcher │
             D-Bus system bus, group `wheel`    └─────────────────────────────┘
```

Un'estensione di GNOME è un processo senza privilegi. Non può e non deve toccare il
firewall, quindi l'applicazione delle regole sta nel demone e la UI si limita a chiedere.

## Cosa fa { #what-it-does }

- **Fail-closed.** `policy drop` in uscita, in entrata e sull'inoltro, IPv4 e IPv6,
  sostituite in modo atomico. Il traffico esce solo attraverso il tunnel protetto. Se la
  VPN cade, se riavvii o se passi dal Wi-Fi al tethering, tutto resta
  bloccato finché non torna un percorso consentito.
- **Le nuove interfacce non possono far trapelare nulla.** Collega un tethering USB o attiva il Wi-Fi mentre
  il kill switch è armato, e la nuova interfaccia è bloccata di default, non consentita per omissione.
- **Tre livelli di applicazione.** *Standard* filtra l'uscita e l'entrata. *Strict*
  (il default) filtra anche il traffico **inoltrato**, perché container, VM e
  Waydroid passano attraverso l'host e i pacchetti inoltrati non passano mai dall'hook
  di uscita. *Paranoid* aggiunge una catena **netdev egress** su ogni scheda di rete, l'unico livello
  che vede il traffico dei raw socket.
- **Il DNS non può andarsene in giro.** Scegli tra quello attraverso la VPN, quello della rete stessa (solo con
  kiwi-node fidati) o un resolver scelto da te. Viene applicato tramite le
  impostazioni per collegamento di systemd-resolved, con una rete di sicurezza nftables che scarta
  ogni altra risoluzione.
- **Gli endpoint con hostname sono fissati, non affidati al DNS.** Il demone risolve da sé
  l'hostname di un server VPN, via DNS-over-HTTPS verso un IP fissato con un
  certificato verificato, e mette in cache ogni risposta.
- **Scegli una connessione, poi Applica.** Le modifiche vengono preparate, così puoi passare da
  "LAN di casa + kiwi-node" a "tethering + VPN" *mentre sei già in tethering*, e poi
  applicarle come un'unica transazione atomica, senza alcun intervallo disarmato.
- **kiwi-node fidati.** Un gateway che fa già da tunnel per te (un
  [node gateway](../server/roles.md#node)), riconosciuto per IP **e** MAC, può fare le veci
  della VPN sulla propria rete. È opzionale e non viene mai dedotto.
- **Una VPN, applicata.** È raggiungibile solo il server della connessione selezionata. Qualsiasi
  altro tunnel che avvii non può connettersi, e la UI lo indica per nome.
- **Sopravvive a tutto.** Riavvii, logout e login, riavvii di NetworkManager:
  le regole restano. Un'unità separata installa un blocco totale *prima che la rete
  sia attiva*.

## Installazione { #install }

Richiede `nftables`, `NetworkManager`, `python3-gobject` e, per WireGuard,
`wireguard-tools`, tutti presenti su Silverblue e Bluefin. Nulla viene scritto nella
`/usr` immutabile. Il tuo utente deve essere in `wheel`.

```bash
kiwi install kiwi-killswitch   # both halves; sets up kiwi's system scope if needed
```

Oppure da un clone: `sudo ./install.sh install` (il demone, la CLI, la policy del bus e le
unità systemd), poi `./install.sh install` (l'estensione di GNOME e l'app delle
impostazioni). Esci e rientra perché GNOME carichi l'estensione. La disinstallazione prima disarma,
quindi non può lasciarti chiuso fuori.

## Uso { #use }

Apri **Impostazioni rapide → Kill Switch** per armare, disarmare e scegliere quale VPN è
protetta, oppure **Kiwi Kill Switch** nella griglia delle app per tutto il resto.

```bash
kiwi-killswitch status                   # cosa viene applicato in questo momento
kiwi-killswitch list                     # le connessioni VPN che NetworkManager conosce
kiwi-killswitch vpn <name>               # prepara quale proteggere
kiwi-killswitch set dns_mode tunnel
kiwi-killswitch apply                    # una sola transazione atomica
kiwi-killswitch arm                      # oppure: arm <vpn>
kiwi-killswitch disarm
kiwi-killswitch pending                  # cosa è in preparazione; revert lo scarta
```

!!! warning "Armare via SSH"
    Armare interrompe una sessione da una subnet che non è in `mgmt_subnets`. È il
    comportamento corretto per un kill switch. Impostala prima:
    ```bash
    kiwi-killswitch set mgmt_subnets 192.168.0.0/16
    kiwi-killswitch set allow_in_ports 22
    kiwi-killswitch apply
    ```

**Ripristino.** La CLI non ha bisogno della rete, quindi basta sempre una TTY:
`kiwi-killswitch disarm`. Se il demone stesso non c'è più:
`sudo nft delete table inet kiwi_ks` e `sudo nft delete table netdev kiwi_ks_egress`.

**Macchine virtuali.** Una VM in bridge non passa mai attraverso l'host, quindi il kill
switch la lascia stare (evita `paranoid`, che filtra sulla scheda fisica).
Una VM in NAT passa attraverso l'host. `strict` la fa uscire dal tunnel e la blocca
quando il tunnel è giù. Aggiungi la sua subnet a `mgmt_subnets` perché il suo DHCP e il suo DNS
raggiungano l'host:

| Impostazione | In uscita | In entrata | Fissata fuori dal tunnel |
|---|---|---|---|
| `allow_lan` | sì (auto) | no | no |
| `bypass_subnets` | sì | no | no |
| `mgmt_subnets` | sì | sì | sì |

**Verifica.** Armalo, poi spegni la VPN (`nmcli connection down …`).
`curl --max-time 5 ifconfig.me` deve andare in **timeout**, non mostrare il tuo IP reale. Non
giudicarlo confrontando gli IP d'uscita: dimostra l'uso del tunnel con
`wg show <iface> transfer` o `ip route get 1.1.1.1`.

## Convivenza e limiti noti { #coexistence-and-known-limits }

- **firewalld può restare attivo.** Le sue catene girano con priorità 10 e le nostre con −10.
- **Non** eseguirlo insieme a un altro kill switch che gestisce una tabella output-drop.
- Lascia stare `nftables.service` se non lo usi. Fermarlo svuota ogni
  tabella. Il demone ripristina le sue regole in pochi secondi, ma non c'è motivo
  di aprire quella finestra.
- Una VPN con un endpoint indicato per **hostname** non può riconnettersi mentre il kill switch è armato, a meno che il DNS non sia
  impostato su *un resolver scelto da me*. NetworkManager e OpenVPN risolvono il nome
  tramite il resolver di sistema, che è bloccato finché nessun tunnel è attivo.
  Le connessioni con un IP letterale non ne sono toccate.
- **Un resolver scelto da te è raggiungibile fuori dal tunnel** mentre il tunnel è
  giù. Attiva per esso DNS-over-TLS.
- **Un node fidato salvato senza MAC** viene riconosciuto solo dall'indirizzo del suo gateway.
- **Il controllo senza password** è la policy del bus D-Bus per il gruppo `wheel`. Significa anche
  che qualsiasi programma che gira con il tuo utente può spegnere l'interruttore senza chiedere.
- Ferma le fughe a livello di rete. Non è Tails o Whonix e non fa nulla contro
  il fingerprinting del browser, WebRTC o un'app che comunica con l'esterno attraverso il tunnel.
- È uno strumento personale e non è stato verificato in modo indipendente. `tests/run.sh`
  mette alla prova il vero demone con il vero nftables, ogni gruppo di test nel proprio
  namespace, senza root.
- I suoi tag di release non sono ancora firmati, quindi con kiwi-updater 2.4 la sua metà root
  chiede la tua password quando si aggiorna.

Discende da `gnome-vpn-killswitch` (ordine di avvio),
`kiwi-vpn-monitor` (rilevamento del gateway) e `nova-killswitch` (l'architettura del
demone), dello stesso autore.
