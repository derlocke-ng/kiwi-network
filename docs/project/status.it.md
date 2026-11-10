# Repository e stato

Ogni repository si trova sotto [github.com/derlocke-ng](https://github.com/derlocke-ng).
"Rilasciato" significa un tag di versione, che è ciò che kiwi-updater installa. Le versioni
sono aggiornate a novembre 2026.

## La rete { #the-network }

| Repository | Cos'è | Release | Catalogo | Licenza |
|---|---|---|---|---|
| [kiwi-server](https://github.com/derlocke-ng/kiwi-server) | costruisce e gestisce la rete: file fleet → ISO di installazione → apply via SSH | v2.42.0 | sì | GPL-3.0+ |
| [kiwi-modules](https://github.com/derlocke-ng/kiwi-modules) | i 20 moduli e il loro renderer: un file macchina → un bundle di stack | v0.23.0 | no | GPL-3.0+ |
| [kiwi-stack](https://github.com/derlocke-ng/kiwi-stack) | il lato macchina: mette un bundle su una macchina e lo tiene in funzione | v0.5.0 | no | GPL-3.0+ |
| [mullvad-socks5](https://github.com/derlocke-ng/mullvad-socks5) | i proxy SOCKS5 di Mullvad come elenchi e record DNS, ricostruiti ogni 6 ore | il branch `list` | no | MIT (README) |

## Persone { #people }

| Repository | Cos'è | Release | Licenza |
|---|---|---|---|
| [kiwi-framework](https://github.com/derlocke-ng/kiwi-framework) | il motore degli hub di comunità federati su nostr | v0.32.1 | GPL-3.0+ |
| [Armory](https://github.com/derlocke-ng/armory) | il primo hub: dieci strumenti web peer-to-peer ([online](https://derlocke-ng.github.io/armory/)) | segue `main` (0.1.0) | GPL-3.0+ |
| [kiwi-web-catalog](https://github.com/derlocke-ng/kiwi-web-catalog) | un catalogo di hub e delle loro app | (un elenco) | CC0 (README) |

## Il desktop { #the-desktop }

| Repository | Cos'è | Release | Catalogo | Licenza |
|---|---|---|---|---|
| [kiwi-updater](https://github.com/derlocke-ng/kiwi-updater) | installa e aggiorna app da cataloghi git | v2.4.0 | sì | GPL-3.0+ |
| [kiwi-catalog](https://github.com/derlocke-ng/kiwi-catalog) | il catalogo delle app Kiwi | (un elenco) | n/d | nessuna indicata |
| [ensconce](https://github.com/derlocke-ng/ensconce) | configurazione post-installazione per Bluefin-DX | v2.5.0 | sì | GPL-3.0+ |
| [kiwi-killswitch](https://github.com/derlocke-ng/kiwi-killswitch) | kill switch VPN fail-closed per GNOME | v0.2.3 | sì | GPL-3.0+ |
| [kiwi-proxy](https://github.com/derlocke-ng/kiwi-proxy) | uscite SOCKS5/VPN sigillate in Podman rootless | v0.7.3 | sì | GPL-3.0+ |
| [kiwi-custodia](https://github.com/derlocke-ng/kiwi-custodia) | box di distribuzioni il cui traffico esce solo attraverso un'uscita | v0.2.3 | sì | GPL-3.0+ |
| [kiwi-fox](https://github.com/derlocke-ng/kiwi-fox) | identità del browser isolate sulle uscite di kiwi-proxy | v0.7.1 | sì | GPL-3.0+ |
| [kiwi-plugin-tor](https://github.com/derlocke-ng/kiwi-plugin-tor) | provider per kiwi-proxy: Tor | v0.3.0 | sì | GPL-3.0+ |
| [kiwi-plugin-vpn](https://github.com/derlocke-ng/kiwi-plugin-vpn) | provider per kiwi-proxy: una VPN tramite gluetun | v0.2.2 | sì | GPL-3.0+ |
| [kiwi-plugin-9proxy](https://github.com/derlocke-ng/kiwi-plugin-9proxy) | provider per kiwi-proxy: 9proxy | v0.2.0 | sì | GPL-3.0+ |
| [kiwi-plugin-myst](https://github.com/derlocke-ng/kiwi-plugin-myst) | provider per kiwi-proxy: Mysterium | v0.5.2 | sì | GPL-3.0+ |
| [gnome-monitor](https://github.com/derlocke-ng/gnome-monitor) | disposizioni degli schermi per GNOME | v0.3.2 | sì | GPL-3.0+ |
| [syncman](https://github.com/derlocke-ng/syncman) | sincronizzazione bidirezionale di cartelle come servizi utente | v0.4.1 | sì | GPL-3.0+ |
| [kiwi-cli-tools-desktop](https://github.com/derlocke-ng/kiwi-cli-tools-desktop) | `pweb`, `select-server`, `tethering`, `torlink` | v1.2.1 | sì | GPL-3.0+ |
| [kiwi-gen](https://github.com/derlocke-ng/kiwi-gen) | chiavi e certificati SSH e TLS, offline nel browser ([online](https://derlocke-ng.github.io/kiwi-gen/)) | pagina web | no | MIT |
| [kiwi-icons](https://github.com/derlocke-ng/kiwi-icons) | le icone delle app ([anteprima](https://derlocke-ng.github.io/kiwi-icons/)) | nessun tag | no | nessuna indicata |
| [kiwi-network](https://github.com/derlocke-ng/kiwi-network) | questo sito e questa documentazione | n/d | n/d | AGPL-3.0 |

## Lacune note { #known-gaps }

Dai repository stessi:

- **kiwi-server**: provato su hardware reale tra ottobre e novembre 2026, con i backup
  dei node ripristinati da un node all'altro e l'MTU del tunnel regolato, compresi i
  percorsi mobili. Più server di backup, il ripristino automatico di una macchina ricostruita,
  un timer per la pulizia e un controllo di salute per un'uscita commerciale bloccata sono nei
  branch `several-servers` di kiwi-server e kiwi-modules, non ancora rilasciati. La federazione tra reti non è ancora provata. Solo IPv4, e la
  ISO Debian è solo amd64. Il control plane è progettato, non realizzato.
- **kiwi-modules**: OpenCloud, Immich e Paperless-ngx sono "in prova". Un server
  TURN per le chiamate è in attesa di essere unito.
- **kiwi-stack**: nessun rollback oltre al ripristino dei dati e alla riapplicazione di un
  bundle precedente.
- **kiwi-framework**: il blog, le approvazioni di moderazione, il seguire spazi che un hub
  non include e i firmatari NIP-07/NIP-46 devono ancora arrivare.
- **kiwi-updater**: è pianificato un registro ospitato di cataloghi fidati. I tag di release
  delle altre app non sono ancora firmati, quindi la metà root di kiwi-killswitch chiede
  una password per aggiornarsi.
- **kiwi-proxy**: il suo modulo kiwi-server non è mai stato eseguito su una macchina. Le uscite sono solo TCP
  e IPv4. Il modulo VPN contiene una sola configurazione per macchina.
- **Moduli dei provider**: VPN e 9proxy non sono validati dall'inizio alla fine con un
  account reale; Mysterium sì (7 novembre 2026).
- **kiwi-custodia**: alcune parti devono ancora essere misurate su una macchina reale
  (tun2socks in un gateway rootless, compositor diversi da GNOME).
- **Licenze**: kiwi-icons, kiwi-catalog e mullvad-socks5 non hanno un file LICENSE,
  e kiwi-killswitch indica la sua licenza solo nel README e nel manifest.
