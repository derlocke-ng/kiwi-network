# Il desktop

Gli strumenti desktop di Kiwi sono pensati per i **desktop Fedora Atomic**: Fedora
Silverblue e [Bluefin](https://projectbluefin.io/) (in particolare Bluefin-DX).
Sono sistemi basati su immagini, con una `/usr` immutabile e un rollback
semplice. Non esiste un'immagine Kiwi speciale: installi un'immagine standard e ci aggiungi sopra tre
livelli.

1. **[kiwi-updater](kiwi-updater.md)** installa e aggiorna le app da cataloghi
   git: tutto nella tua home, più una parte di proprietà di root solo per le app che
   ne hanno bisogno. Aggiorna anche sé stesso.
2. **[ensconce](ensconce.md)** configura un Bluefin-DX appena installato a partire da semplici file di elenco:
   pacchetti, Flatpak, estensioni GNOME, sincronizzazione Nextcloud, SSH, impostazioni sysctl e di
   alimentazione, la schermata di login e le tue app Kiwi. `--export` clona una macchina.
3. **Le app**, dal [catalogo Kiwi](catalogs.md):

| App | Cosa fa |
|---|---|
| [kiwi-killswitch](kiwi-killswitch.md) | Un kill switch VPN fail-closed per GNOME |
| [Reti dei clienti](../clients/index.md): kiwi-proxy, kiwi-custodia, kiwi-fox | Un'uscita sigillata per ogni VPN o endpoint SOCKS, e box di distribuzioni e browser che ci vivono dentro |
| [kiwi-server](../server/index.md) | Costruisci e gestisci la tua rete |
| [gnome-monitor](gnome-monitor.md) | Salva e cambia le disposizioni degli schermi; spegni e riaccendi i singoli monitor |
| [syncman](syncman.md) | Sincronizzazione bidirezionale di cartelle (salvataggi dei giochi e altro) come servizi utente |
| [kiwi-cli-tools-desktop](cli-tools.md) | `pweb`, `select-server`, `tethering`, `torlink` |

Trovi qui anche [kiwi-gen](kiwi-gen.md), un gestore di chiavi e certificati che gira
offline nel browser.

## Da un'installazione nuova { #from-a-fresh-install }

```bash
# 1. kiwi-updater: ambito utente e di sistema, una sola richiesta di password; il catalogo Kiwi arriva con esso
curl -fsSL https://raw.githubusercontent.com/derlocke-ng/kiwi-updater/main/get-kiwi.sh | bash
kiwi list

# 2. configura la macchina
kiwi install ensconce
ensconce --init && $EDITOR "$(ensconce --config-dir)"/settings.sh
ensconce

# 3. le app che vuoi (oppure elencale nel kiwi-apps.list di ensconce)
kiwi install kiwi-killswitch
kiwi install kiwi-custodia && kiwi-custodia setup
```

**Kiwi Apps** (`kiwi-gui`) nella griglia delle app fa lo stesso con un clic.

## Entrare nella tua rete { #joining-your-network }

Un desktop entra nella mesh come qualsiasi altro dispositivo: `kiwi-server enroll fleet.yaml
laptop --group devices` scrive una configurazione WireGuard, che importi nelle Impostazioni
di GNOME. Importa la CA della fleet (`kiwiCA.pem`) perché i suoi nomi HTTPS siano attendibili.
ensconce installa a livello di sistema ogni `.pem` nella sua directory `certs/`.

[kiwi-killswitch](kiwi-killswitch.md) mantiene poi la macchina fail-closed attorno
a quella connessione. La sua impostazione *trusted kiwi-nodes* permette a un node gateway sulla tua
LAN di fare le veci del tunnel quando sei a casa.
