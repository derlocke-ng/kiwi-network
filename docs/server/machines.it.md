# Macchine: installazione, apply, aggiornamenti

## Target { #targets }

| Target | Cosa viene installato | Supporto di installazione |
|---|---|---|
| `coreos` | Fedora CoreOS, stream stable | la ISO live ufficiale, personalizzata con l'Ignition dell'host (Butane `fcos` 1.6.0); per l'installazione non serve la rete |
| `ucore` | Fedora CoreOS che esegue da solo il rebase su un'immagine `ghcr.io/ublue-os/ucore*` (`ucore-minimal`, `ucore`, `ucore-hci`, con `-nvidia` / `-zfs`), come nell'esempio di autorebase di uCore | come per CoreOS, più le unità di autorebase |
| `debian` | Debian stable (trixie), amd64 | la netinst ufficiale con il preseed nel suo initrd, così risponde fin dalla prima domanda, e i file dell'host sotto `/kiwi-server`; avvio BIOS e UEFI mantenuti |

L'utente amministratore ha sudo senza password ovunque. SSH accetta solo chiavi, a meno che tu
non imposti `ssh_password_auth: true`.

## Supporti di installazione { #install-media }

```bash
kiwi-server build fleet.yaml sorbet      # → output/sorbet/sorbet.iso
sudo dd if=output/sorbet/sorbet.iso of=/dev/sdX bs=4M status=progress oflag=sync
```

- Una ISO installa su `disk:` **senza chiedere** e poi **spegne la
  macchina** (`install.on_done: poweroff`, oppure `reboot`). Etichetta le tue chiavette.
- Di default i supporti contengono **solo il sistema di base**: hostname, rete, utente
  amministratore e chiavi, politica di aggiornamento. Nessuno dei segreti dello stack è su di essi. Il
  ruolo arriva dopo, con `apply`.
- `--offline` mette sulla ISO l'intero ruolo e i suoi segreti, per una macchina che
  SSH non può raggiungere. Chi ha quella ISO ha quei segreti.
- L'installer live mostra i dischi (`lsblk`) e ha una shell con la password della console
  e le chiavi della fleet.

## Apply { #apply }

```bash
kiwi-server apply fleet.yaml papaya                         # per nome, indirizzo o indirizzo mesh
kiwi-server apply fleet.yaml papaya --ssh core@192.168.1.25 # la prima volta, per indirizzo
```

`apply` rifà il render dell'host e invia il suo script di ruolo via SSH in
`/var/lib/kiwi-server/role.sh`. Esegue lo script come root, poi lega il disco
ai suoi anelli Tang e, su un master, salva lo stato di WireGuard con i segreti
della fleet. Su una macchina Debian cifrata, il primo apply sostituisce la chiave
di installazione monouso. SSH usa la chiave della fleet e controlla le chiavi host con
`secrets/known_hosts`. `apply` e `status` trovano una macchina per nome, indirizzo
statico, indirizzo pubblico del master o indirizzo mesh, ma solo indirizzi
la cui chiave host è registrata.

Per un ruolo a moduli, lo script passa lo stack a `kiwi-stack`:

1. Installa o abilita podman 4.4+ (su Debian con `netavark`,
   `aardvark-dns` e `catatonit`) o docker, e l'utente di servizio.
2. Carica i moduli del kernel e imposta i sysctl. Con Pi-hole, aardvark-dns si sposta sulla
   porta 5533 e l'host risolve attraverso il Pi-hole dello stack. Inoltre considera attendibile
   la mesh in firewalld.
3. Rifiuta uno stack generato da un seed diverso. Estrae lo stack in
   `docker_dir`, installa i quadlet in `/etc/containers/systemd` e le unità
   dell'host, e rimuove ciò che aveva installato un modulo che non c'è più.
4. Apre le porte dello stack in firewalld o ufw, se uno dei due è attivo.
5. Scarica ogni immagine, poi avvia `kiwi-stack.service`
   (→ `kiwi-stack.target`).
6. Esegue `kiwi-stack verify`: ogni container deve essere in esecuzione, altrimenti l'apply
   fallisce e dice quale passo è fallito.

Applicare di nuovo lo stesso render non cambia nulla, e un nuovo render sostituisce ciò che
è cambiato. Un nuovo apply riavvia comunque ogni container dello stack.

## Primo avvio { #first-boot }

`kiwi-role.service` esegue `/var/lib/kiwi-server/role.sh` una volta, dopo che la
rete è attiva (aspettando il DNS fino a 120 secondi). `role.done` viene scritto solo
quando ogni container è in esecuzione. Un errore lascia `/var/lib/kiwi-server/role.failed`
(il passo e il comando) e viene ritentato all'avvio successivo. Il log è
`/var/log/kiwi-server-role.log`. Su uCore il ruolo aspetta finché l'immagine non è
firmata. `sudo bash /var/lib/kiwi-server/role.sh --force` lo esegue di nuovo.

## Aggiornamenti { #updates }

Gli aggiornamenti si installano di continuo. Il **riavvio** per applicarli avviene solo dentro la tua
finestra (`updates.days`, `time`, `length_minutes`, ora locale):

| Target | Installa gli aggiornamenti | Si riavvia |
|---|---|---|
| `coreos` | Zincati, di continuo | solo nella finestra (`strategy = "periodic"`) |
| `ucore` | `rpm-ostreed-automatic.timer` li prepara | `kiwi-staged-reboot.timer` nella finestra |
| `debian` | unattended-upgrades, ogni giorno | `kiwi-reboot-if-required.timer` nella finestra, quando serve |

`updates.days: []` significa qualsiasi giorno, e `updates.enabled: false` disattiva
tutto. Una macchina cifrata il cui anello Tang deve essere inoltrato dall'esterno non si
riavvia da sola.

I container hanno un loro calendario: un `kiwi-stack update` settimanale (domenica
00:00) esegue `podman auto-update` finché è impostato `auto_update: registry`. Un riavvio
quotidiano del client VPN alle 07:00 dà un indirizzo d'uscita nuovo.

## Sulla macchina: `kiwi-stack` { #on-the-machine-kiwi-stack }

```bash
sudo kiwi-stack status          # container, unità host, verifica
sudo kiwi-stack verify          # ogni container in esecuzione?
sudo kiwi-stack logs [service]  # dal journal
sudo kiwi-stack start | stop | restart
sudo kiwi-stack update          # podman auto-update + prune
sudo kiwi-stack vpn-restart     # il client VPN e ogni container nel suo namespace
sudo kiwi-stack backup | snapshots | restore [--at TIME] MODULE...   # con il modulo backup
sudo kiwi-stack apply DIR       # un bundle di stack, senza script di ruolo
```

Lo stack si trova in `docker_dir` (default `/home/user/docker`), e le sue impostazioni
in `/etc/kiwi-server/stack.env`. Le unità sono `kiwi-stack.service`,
`kiwi-stack-vpn-restart.timer` e `kiwi-stack-update.timer`, più quelle che aggiunge
un modulo.

## Cosa produce un render { #what-a-render-produces }

`output/<host>/` contiene:

| File | Cosa |
|---|---|
| `<host>.role.sh` | il ruolo come unico script: impostazioni, lo stack (incorporato), il comando e la libreria kiwi-stack, e il corpo del ruolo. Permessi 0600 |
| `<host>.stack/` | il bundle dello stack, da esaminare: `docker-compose.yml`, `quadlets/`, configurazioni dei moduli, unità host e `stack.sh`. `kiwi-stack apply` può installarlo a mano |
| `<host>.bu`, `<host>.ign` | CoreOS e uCore: Butane e Ignition |
| `<host>.preseed.cfg`, `<host>.kiwi-server/` | Debian: il preseed e i file che copia |
| `<host>.iso` | l'installer automatico |
