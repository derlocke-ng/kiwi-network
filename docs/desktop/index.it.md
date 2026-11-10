# Il desktop

La parte desktop di Kiwi Network è il computer su cui lavori: una postazione
Linux che si configura in automatico e prende le sue app da cataloghi git. Un
catalogo è un repository git che elenca delle app. Non devi preparare la
macchina a mano, e quella successiva la configuri allo stesso modo.

Gli strumenti desktop di Kiwi sono pensati per i **desktop Fedora Atomic**:
Fedora Silverblue e [Bluefin](https://projectbluefin.io/), in particolare
Bluefin-DX. Questi sistemi vengono installati e aggiornati come un’unica
immagine completa. La loro directory `/usr` è immutabile, cioè non si può
modificare, e un aggiornamento si può annullare con facilità. Non esiste
un’immagine Kiwi apposita: installi una normale immagine Silverblue o Bluefin e
ci aggiungi sopra tre cose.

1. **[kiwi-updater](kiwi-updater.md)** installa le app dai cataloghi git e le
   tiene aggiornate. Installa tutto nella tua cartella home. Solo un’app che ha
   bisogno di root riceve anche una parte che appartiene a root. kiwi-updater
   aggiorna anche sé stesso.
2. **[ensconce](ensconce.md)** configura un Bluefin-DX appena installato.
   Descrivi la tua configurazione in semplici file di elenco, e ensconce la
   applica: pacchetti, Flatpak, estensioni di GNOME, sincronizzazione con
   Nextcloud, SSH, impostazioni di sysctl e del risparmio energetico, la
   schermata di accesso e le tue app Kiwi. Con `--export` scrive la
   configurazione di una macchina esistente in file di questo tipo, così puoi
   clonare quella macchina.
3. **Le app**, che installi dal [catalogo Kiwi](catalogs.md):

| App | Che cosa fa |
|---|---|
| [kiwi-killswitch](kiwi-killswitch.md) | Un kill switch per la VPN, per GNOME. È fail-closed: finché la VPN non è attiva, tutto il traffico resta bloccato |
| [Reti dei clienti](../clients/index.md): kiwi-proxy, kiwi-custodia, kiwi-fox | Un exit per ogni endpoint VPN o SOCKS. Un exit è un container isolato che può raggiungere soltanto quell’endpoint. Alle box (container con una distribuzione Linux) e ai browser si può collegare un exit, così tutto il loro traffico passa da lì |
| [kiwi-server](../server/index.md) | Lo strumento con cui costruisci e gestisci la tua rete |
| [gnome-monitor](gnome-monitor.md) | Salva le disposizioni degli schermi e passa dall’una all’altra. Spegne e riaccende anche i singoli monitor |
| [syncman](syncman.md) | Sincronizza cartelle in entrambe le direzioni, per esempio i salvataggi dei giochi. La sincronizzazione gira come servizio utente |
| [kiwi-cli-tools-desktop](cli-tools.md) | `pweb`, `select-server`, `tethering`, `torlink` |

In questa sezione trovi anche [kiwi-gen](kiwi-gen.md), un gestore di chiavi e
certificati che gira nel browser e funziona offline.

## Da un’installazione nuova { #from-a-fresh-install }

Questi comandi ti portano da un sistema appena installato a un desktop con le
app Kiwi:

```bash
# 1. kiwi-updater: ambito utente e di sistema, una sola richiesta di password; il catalogo Kiwi è incluso
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

Puoi installare le app anche senza terminale. Con **Kiwi Apps** (`kiwi-gui`),
nella griglia delle applicazioni, installi un’app con un clic.

## Entrare nella tua rete { #joining-your-network }

Un desktop entra nella mesh come qualsiasi altro dispositivo. La mesh è la rete
WireGuard privata che collega i tuoi server e i tuoi dispositivi. Il comando
`kiwi-server enroll fleet.yaml laptop --group devices` scrive un file di
configurazione WireGuard, che poi importi nelle Impostazioni di GNOME. Importa
anche l’autorità di certificazione (CA) della tua fleet, `kiwiCA.pem`, così il
desktop si fida dei certificati HTTPS dei nomi della tua rete. ensconce installa
per tutto il sistema ogni file `.pem` che trova nella sua directory `certs/`.

A quel punto [kiwi-killswitch](kiwi-killswitch.md) protegge la connessione e
tiene la macchina fail-closed: il traffico che non passa dalla connessione viene
bloccato, anche quando la connessione è caduta. A casa può darsi che un node
gateway nella tua LAN faccia già passare il tuo traffico in un tunnel. Con
l’impostazione *trusted kiwi-nodes*, il kill switch accetta quel node gateway al
posto del tunnel.
