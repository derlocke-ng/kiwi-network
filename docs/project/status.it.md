# Repository e stato

Questa pagina elenca tutti i repository del progetto Kiwi Network: che cosa
sono, qual è la loro ultima release e con quale licenza sono distribuiti. In
fondo trovi ciò che manca o che non è ancora stato testato.

Tutti i repository si trovano su [github.com/derlocke-ng](https://github.com/derlocke-ng).
Un repository «ha una release» quando ha un tag di versione, perché è il tag di
versione che kiwi-updater installa. Le versioni sono aggiornate a novembre
2026.

## La rete { #the-network }

| Repository | Che cos’è | Release | Catalogo | Licenza |
|---|---|---|---|---|
| [kiwi-server](https://github.com/derlocke-ng/kiwi-server) | costruisce e gestisce la rete: trasforma il file fleet in ISO di installazione e applica via SSH il ruolo di ogni macchina | v2.42.0 | sì | GPL-3.0+ |
| [kiwi-modules](https://github.com/derlocke-ng/kiwi-modules) | i 20 moduli e il loro generatore, che trasforma un file macchina in un bundle dello stack | v0.23.0 | no | GPL-3.0+ |
| [kiwi-stack](https://github.com/derlocke-ng/kiwi-stack) | la parte che gira sulla macchina: installa un bundle e lo tiene in funzione | v0.5.0 | no | GPL-3.0+ |
| [mullvad-socks5](https://github.com/derlocke-ng/mullvad-socks5) | elenchi e record DNS dei proxy SOCKS5 di Mullvad, ricostruiti ogni 6 ore | il branch `list` | no | MIT (README) |

## Persone { #people }

| Repository | Che cos’è | Release | Licenza |
|---|---|---|---|
| [kiwi-framework](https://github.com/derlocke-ng/kiwi-framework) | il framework con cui si costruiscono hub federati per le comunità, basati su nostr | v0.32.1 | GPL-3.0+ |
| [Armory](https://github.com/derlocke-ng/armory) | il primo hub costruito con kiwi-framework, con dieci strumenti web peer-to-peer ([online](https://derlocke-ng.github.io/armory/)) | segue `main` (0.1.0) | GPL-3.0+ |
| [kiwi-web-catalog](https://github.com/derlocke-ng/kiwi-web-catalog) | un catalogo di hub e delle loro app | (un elenco) | CC0 (README) |

## Il desktop { #the-desktop }

| Repository | Che cos’è | Release | Catalogo | Licenza |
|---|---|---|---|---|
| [kiwi-updater](https://github.com/derlocke-ng/kiwi-updater) | installa e aggiorna app da cataloghi git | v2.4.0 | sì | GPL-3.0+ |
| [kiwi-catalog](https://github.com/derlocke-ng/kiwi-catalog) | il catalogo delle app Kiwi | (un elenco) | n.d. | non indicata |
| [ensconce](https://github.com/derlocke-ng/ensconce) | configura Bluefin-DX dopo l’installazione | v2.5.0 | sì | GPL-3.0+ |
| [kiwi-killswitch](https://github.com/derlocke-ng/kiwi-killswitch) | un kill switch VPN fail-closed per GNOME: quando la connessione VPN cade, il traffico viene bloccato | v0.2.3 | sì | GPL-3.0+ |
| [kiwi-proxy](https://github.com/derlocke-ng/kiwi-proxy) | exit SOCKS5 e VPN in Podman rootless, cioè connessioni con un nome, ognuna chiusa in un container la cui unica rotta è quella connessione | v0.7.3 | sì | GPL-3.0+ |
| [kiwi-custodia](https://github.com/derlocke-ng/kiwi-custodia) | box con distribuzioni Linux (distribuzioni Linux in container), il cui traffico può arrivare a Internet solo attraverso un exit di kiwi-proxy | v0.2.3 | sì | GPL-3.0+ |
| [kiwi-fox](https://github.com/derlocke-ng/kiwi-fox) | identità del browser isolate, che si collegano attraverso gli exit di kiwi-proxy | v0.7.1 | sì | GPL-3.0+ |
| [kiwi-plugin-tor](https://github.com/derlocke-ng/kiwi-plugin-tor) | provider per kiwi-proxy: Tor | v0.3.0 | sì | GPL-3.0+ |
| [kiwi-plugin-vpn](https://github.com/derlocke-ng/kiwi-plugin-vpn) | provider per kiwi-proxy: una VPN tramite gluetun | v0.2.2 | sì | GPL-3.0+ |
| [kiwi-plugin-9proxy](https://github.com/derlocke-ng/kiwi-plugin-9proxy) | provider per kiwi-proxy: 9proxy | v0.2.0 | sì | GPL-3.0+ |
| [kiwi-plugin-myst](https://github.com/derlocke-ng/kiwi-plugin-myst) | provider per kiwi-proxy: Mysterium | v0.5.2 | sì | GPL-3.0+ |
| [gnome-monitor](https://github.com/derlocke-ng/gnome-monitor) | disposizioni degli schermi per GNOME | v0.3.2 | sì | GPL-3.0+ |
| [syncman](https://github.com/derlocke-ng/syncman) | sincronizzazione delle cartelle in entrambe le direzioni, eseguita come servizi utente di systemd | v0.4.1 | sì | GPL-3.0+ |
| [kiwi-cli-tools-desktop](https://github.com/derlocke-ng/kiwi-cli-tools-desktop) | `pweb`, `select-server`, `tethering`, `torlink` | v1.2.1 | sì | GPL-3.0+ |
| [kiwi-gen](https://github.com/derlocke-ng/kiwi-gen) | crea chiavi e certificati SSH e TLS offline, nel browser ([online](https://derlocke-ng.github.io/kiwi-gen/)) | pagina web | no | MIT |
| [kiwi-icons](https://github.com/derlocke-ng/kiwi-icons) | le icone delle app ([anteprima](https://derlocke-ng.github.io/kiwi-icons/)) | nessun tag | no | non indicata |
| [kiwi-network](https://github.com/derlocke-ng/kiwi-network) | questo sito e questa documentazione | n.d. | n.d. | AGPL-3.0 |

## Lacune note { #known-gaps }

Queste lacune sono indicate dagli stessi repository:

- **kiwi-server**: è stato dimostrato che funziona su hardware reale, tra
  ottobre e novembre 2026. In quelle prove i backup dei node sono stati
  ripristinati da un node all’altro, e la MTU del tunnel è stata regolata,
  anche per le connessioni mobili. Quattro aggiunte si trovano nei branch
  `several-servers` di kiwi-server e kiwi-modules e non sono ancora state
  rilasciate: più server di backup, il ripristino automatico di una macchina
  ricostruita, un timer per eliminare i vecchi snapshot e un health check che
  riavvia una connessione bloccata con il provider VPN commerciale. Non è
  ancora stato dimostrato che la federazione tra reti funzioni. Tutto funziona
  solo con IPv4, e la ISO di Debian esiste solo per amd64. Il control plane è
  progettato, non ancora realizzato.
- **kiwi-modules**: i moduli OpenCloud, Immich e Paperless-ngx sono
  contrassegnati come «da provare». Un server TURN per le chiamate aspetta di
  essere unito.
- **kiwi-stack**: non esiste un modo per tornare indietro (rollback). Puoi
  soltanto ripristinare i dati e applicare di nuovo un bundle più vecchio.
- **kiwi-framework**: mancano ancora diverse parti: il blog, le approvazioni
  della moderazione, la possibilità di seguire spazi che un hub non include e
  i firmatari NIP-07/NIP-46.
- **kiwi-updater**: è previsto un registro online dei cataloghi affidabili. I
  tag di release delle altre app non sono ancora firmati. Per questo la parte
  di kiwi-killswitch che gira come root chiede una password quando viene
  aggiornata.
- **kiwi-proxy**: il suo modulo per kiwi-server non è ancora stato eseguito su
  una macchina. Gli exit trasportano soltanto TCP e IPv4. Il modulo VPN
  conserva una sola configurazione per macchina.
- **Moduli provider**: i moduli VPN e 9proxy non sono stati verificati da un
  capo all’altro con un account reale. Il modulo Mysterium è stato verificato
  il 7 novembre 2026.
- **kiwi-custodia**: alcune parti devono ancora essere misurate su una
  macchina reale: tun2socks in un gateway rootless e i compositor diversi da
  quello di GNOME.
- **Licenze**: kiwi-icons, kiwi-catalog e mullvad-socks5 non hanno un file
  LICENSE, e kiwi-killswitch indica la sua licenza solo nel README e nel
  manifest.
