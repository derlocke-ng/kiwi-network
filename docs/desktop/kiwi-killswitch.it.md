# kiwi-killswitch

kiwi-killswitch è un **kill switch per la VPN** per GNOME su Fedora Silverblue e
Bluefin. Un kill switch fa in modo che il tuo computer non mandi traffico al di
fuori della VPN, per esempio quando la connessione VPN cade o quando passi a
un’altra rete. Questo è **fail-closed**: il firewall blocca tutto ciò che non è
esplicitamente consentito, quindi quando qualcosa si guasta il traffico viene
bloccato, non lasciato passare.

Il firewall è gestito soltanto da un daemon che gira con i permessi di root. Lo
comandi con un interruttore nelle impostazioni rapide di GNOME, con un’app GTK4
oppure con uno strumento da riga di comando (CLI). Tutti e tre inviano le loro
richieste al daemon attraverso il bus di sistema D-Bus, e non chiedono mai una
password.

Protegge **una** sola connessione VPN alla volta, WireGuard oppure OpenVPN. Non
collega la VPN al posto tuo: le connessioni le avvii tu dalle Impostazioni di
GNOME, e il kill switch imposta le regole del firewall per la connessione che è
davvero attiva, in modo che nessun traffico possa uscire dal computer per
un’altra strada.

- Repository: [derlocke-ng/kiwi-killswitch](https://github.com/derlocke-ng/kiwi-killswitch), GPL-3.0-or-later
- Ultima release: **v0.2.3**. È nel [catalogo Kiwi](catalogs.md) e ha due
  ambiti, utente + sistema: una metà viene installata nella tua cartella home,
  l’altra appartiene a root.
- Funziona con GNOME Shell dalla versione 45 alla 50.

```
┌─ your session (unprivileged) ─────────────┐   ┌─ root ──────────────────────┐
│  GNOME Quick Settings toggle              │   │  kiwi-killswitchd           │
│  kiwi-killswitch-settings (GTK4)          │──▶│   nftables  (inet + netdev) │
│  kiwi-killswitch (CLI)                    │   │   systemd-resolved steering │
└───────────────────────────────────────────┘   │   NM + kernel event watcher │
             D-Bus system bus, group `wheel`    └─────────────────────────────┘
```

Un’estensione di GNOME è un processo senza permessi di root. Non può modificare
il firewall, e non deve poterlo fare. Per questo è il daemon a occuparsi di
tutti i blocchi, mentre l’interfaccia utente si limita a mandargli delle
richieste.

## Che cosa fa { #what-it-does }

- **È fail-closed.** Il firewall usa `policy drop` per il traffico in uscita, in
  entrata e inoltrato, sia per IPv4 sia per IPv6. Questo significa che ogni
  pacchetto viene scartato, a meno che una regola non lo consenta. Un nuovo
  insieme di regole sostituisce il precedente in un unico passaggio atomico. Il
  traffico può uscire soltanto attraverso il tunnel protetto. Se la VPN cade, se
  riavvii o se passi dal Wi-Fi al tethering, tutto resta bloccato finché non
  torna disponibile una strada consentita.
- **Le nuove interfacce di rete vengono bloccate.** Se attivi il tethering
  USB o accendi il Wi-Fi mentre il kill switch è armato, cioè attivo, la nuova
  interfaccia è bloccata per impostazione predefinita. Non viene lasciata
  passare solo perché nessuna regola la nomina.
- **Ci sono tre livelli di filtraggio.** *Standard* filtra il traffico in uscita
  e in entrata. *Strict* è il livello predefinito e filtra anche il traffico
  **inoltrato**. Serve perché container, macchine virtuali e Waydroid fanno
  passare il loro traffico attraverso l’host, e i pacchetti inoltrati non
  passano mai dall’hook di output. *Paranoid* aggiunge una catena **netdev
  egress** su ogni scheda di rete (NIC). È l’unico livello che vede il traffico
  dei raw socket.
- **Le query DNS non possono aggirare il tunnel.** Scegli tu quale resolver DNS
  usare mentre il kill switch è armato. Puoi mandare le query DNS attraverso la
  VPN, usare il resolver della rete in cui ti trovi oppure un resolver scelto da
  te. Il resolver della rete viene usato soltanto sulla rete di un kiwi-node
  fidato. Il kill switch applica la tua scelta attraverso le impostazioni per
  singolo collegamento di systemd-resolved. Come seconda protezione, una regola
  nftables scarta qualsiasi altra risoluzione dei nomi.
- **Per un server VPN indicato con un nome host, il daemon non si fida del
  normale DNS.** Risolve da sé il nome host del server VPN. Per farlo usa
  DNS-over-HTTPS, si collega a un indirizzo IP fissato in anticipo e verifica il
  certificato. Tutte le risposte vengono messe in cache.
- **Prima scegli una connessione, poi applichi.** Le modifiche vengono prima
  raccolte e hanno effetto soltanto quando le applichi. Puoi quindi passare da
  «LAN di casa + kiwi-node» a «tethering + VPN» *quando sei già in tethering*.
  Con *Apply* tutte le modifiche vengono eseguite in un’unica transazione
  atomica, e in nessun momento intermedio il kill switch viene disarmato.
- **kiwi-node fidati.** La tua rete può avere un gateway che fa già passare il
  tuo traffico in un tunnel. In una rete Kiwi è un
  [node gateway](../server/roles.md#node). Sulla sua rete un gateway del genere
  può prendere il posto della VPN. Il kill switch lo riconosce dal suo indirizzo
  IP **e** dal suo indirizzo MAC. Questa funzione va attivata da te: il kill
  switch non decide mai da solo che un gateway è fidato.
- **Si può collegare una sola VPN.** È raggiungibile soltanto il server della
  connessione scelta. Qualsiasi altro tunnel tu avvii non riesce a collegarsi, e
  l’interfaccia utente ne mostra il nome.
- **Le regole restano al loro posto.** Ci sono ancora dopo un riavvio, dopo
  logout e login e dopo un riavvio di NetworkManager. Un’unità separata carica
  le regole di blocco *prima che la rete si attivi*.

## Installazione { #install }

kiwi-killswitch richiede `nftables`, `NetworkManager` e `python3-gobject`, e per
WireGuard anche `wireguard-tools`. Su Silverblue e Bluefin ci sono già tutti.
Nella `/usr` immutabile non viene scritto nulla. Il tuo utente deve far parte
del gruppo `wheel`.

```bash
kiwi install kiwi-killswitch   # entrambe le metà; se serve, prepara l’ambito di sistema di kiwi
```

Puoi installarlo anche da un clone del repository. Esegui prima
`sudo ./install.sh install`, che installa il daemon, la CLI, la policy D-Bus e le
unità systemd. Poi esegui `./install.sh install`, che installa l’estensione di
GNOME e l’app delle impostazioni. Esci e rientra nella sessione, così GNOME
carica l’estensione. Quando disinstalli, il kill switch viene prima disarmato,
quindi la disinstallazione non può lasciarti con la rete bloccata.

## Uso { #use }

Apri **Impostazioni rapide → Kill Switch** per armare e disarmare il kill switch
e per scegliere quale VPN proteggere. Per tutto il resto apri **Kiwi Kill
Switch** dalla griglia delle applicazioni. La CLI ha questi comandi:

```bash
kiwi-killswitch status                   # che cosa è in vigore in questo momento
kiwi-killswitch list                     # le connessioni VPN note a NetworkManager
kiwi-killswitch vpn <name>               # prepara quale connessione proteggere
kiwi-killswitch set dns_mode tunnel
kiwi-killswitch apply                    # un’unica transazione atomica
kiwi-killswitch arm                      # oppure: arm <vpn>
kiwi-killswitch disarm
kiwi-killswitch pending                  # che cosa è in attesa di essere applicato; revert lo scarta
```

!!! warning "Armare il kill switch via SSH"
    Quando armi il kill switch, una sessione SSH che arriva da una sottorete non
    elencata in `mgmt_subnets` viene interrotta. È il comportamento corretto di
    un kill switch. Se lavori via SSH, imposta prima questi valori:
    ```bash
    kiwi-killswitch set mgmt_subnets 192.168.0.0/16
    kiwi-killswitch set allow_in_ports 22
    kiwi-killswitch apply
    ```

**Ripristino.** La CLI non ha bisogno della rete, quindi per eseguire
`kiwi-killswitch disarm` basta sempre una console di testo (TTY). Se manca
proprio il daemon, cancella le sue tabelle del firewall con
`sudo nft delete table inet kiwi_ks` e
`sudo nft delete table netdev kiwi_ks_egress`.

**Macchine virtuali.** Una VM in bridge non fa mai passare il suo traffico
attraverso l’host, quindi il kill switch non la riguarda. In questo caso evita
`paranoid`, perché quel livello filtra sulla scheda di rete fisica. Una VM in
NAT fa passare il suo traffico attraverso l’host. Con `strict` quel traffico
esce attraverso il tunnel e viene bloccato quando il tunnel non è attivo. Aggiungi la
sottorete della VM a `mgmt_subnets`, così le sue richieste DHCP e DNS
raggiungono l’host. La tabella mostra che cosa consente ciascuna impostazione:

| Impostazione | In uscita | In entrata | Fuori dal tunnel |
|---|---|---|---|
| `allow_lan` | sì (automatico) | no | no |
| `bypass_subnets` | sì | no | no |
| `mgmt_subnets` | sì | sì | sì |

**Verificare che funzioni.** Arma il kill switch, poi disattiva la VPN con
`nmcli connection down …`. A quel punto `curl --max-time 5 ifconfig.me` deve
**andare in timeout**, e non deve mostrare il tuo vero indirizzo IP. Non
giudicare il risultato confrontando gli indirizzi IP pubblici che vedi. Per
dimostrare che il traffico passa dal tunnel, esegui `wg show <iface> transfer`
oppure `ip route get 1.1.1.1`.

## Altri firewall e limiti noti { #coexistence-and-known-limits }

- **firewalld può restare attivo.** Le sue catene girano con priorità 10, quelle
  del kill switch con −10.
- **Non** usarlo insieme a un altro kill switch che ha una propria tabella che
  scarta il traffico in uscita.
- Se non usi `nftables.service`, lascialo stare. Quando questo servizio viene
  fermato, cancella tutte le tabelle di nftables. Il daemon ricarica le sue
  regole nel giro di pochi secondi, ma per quei secondi le regole mancano, e non
  c’è alcun motivo di provocarlo.
- Una VPN il cui server è indicato con un **nome host** non riesce a
  ricollegarsi mentre il kill switch è armato, a meno che il DNS non sia
  impostato su *a resolver I choose* (un resolver scelto da te). Il motivo è che NetworkManager e
  OpenVPN risolvono il nome attraverso il resolver di sistema, e il resolver di
  sistema è bloccato finché non c’è un tunnel attivo. Le connessioni il cui
  server è indicato con un indirizzo IP non hanno questo problema.
- **Un resolver scelto da te è raggiungibile al di fuori del tunnel** mentre il
  tunnel non è attivo. Attiva DNS-over-TLS per quel resolver.
- **Un node fidato salvato senza indirizzo MAC** viene riconosciuto soltanto
  dall’indirizzo del suo gateway.
- **Il controllo senza password** funziona grazie alla policy D-Bus per il
  gruppo `wheel`. Questo significa anche che qualsiasi programma eseguito con il
  tuo utente può spegnere il kill switch senza chiederti nulla.
- Blocca le fughe di dati a livello di rete. Non è Tails né Whonix. Non fa nulla
  contro il fingerprinting del browser, contro WebRTC o contro un’app che manda
  dati al suo produttore attraverso il tunnel.
- È uno strumento personale e non è stato sottoposto a una verifica
  indipendente. `tests/run.sh` prova il daemon reale con un vero nftables. Ogni
  gruppo di test gira nel proprio namespace, e i test non hanno bisogno di root.
- I suoi tag di release non sono ancora firmati. Con kiwi-updater 2.4, quindi,
  la sua metà root chiede la tua password quando viene aggiornata.

kiwi-killswitch nasce da tre strumenti precedenti dello stesso autore. L’ordine
di avvio viene da `gnome-vpn-killswitch`, il riconoscimento del gateway da
`kiwi-vpn-monitor` e l’architettura del daemon da `nova-killswitch`.
