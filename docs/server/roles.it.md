# Ruoli

Il ruolo stabilisce a che cosa serve una macchina nella tua Kiwi Network. Nel
file fleet assegni un ruolo a ogni host, e kiwi-server prepara la macchina di
conseguenza. Una macchina può essere un semplice sistema di base, il master a
cui si collegano tutti i dispositivi e i node, oppure un node su cui girano i
tuoi servizi. Ogni ruolo funziona su tutti e tre i sistemi di destinazione,
cioè i sistemi operativi che kiwi-server sa installare.

| Ruolo | Che cosa diventa la macchina | Moduli |
|---|---|---|
| `bare` | Soltanto il sistema di base, con un utente amministratore, SSH e gli aggiornamenti automatici | nessuno |
| `master` | Il **kiwi-master**. È il punto di accesso WireGuard della rete e manda il traffico Internet della rete attraverso una VPN commerciale (il doppio hop). Esegue anche Pi-hole per il DNS che blocca la pubblicità, Tor e le pagine di amministrazione | `vpn-client`, `vpn-server`, `dns`, `tor`, `reverse-proxy` |
| `node`, preset `gateway` | Un **kiwi-node** che fa passare attraverso la VPN il traffico di una rete locale (LAN). Esegue anche Pi-hole, un relay DHCP, un gestore di download e SFTP | `vpn-client`, `dns`, `dhcp-relay`, `reverse-proxy`, `downloader`, `gateway`, `portainer`, `sftp` |
| `node`, preset `cloud` | Un **kiwi-node** su cui girano Nextcloud e Vaultwarden | `vpn-client`, `reverse-proxy`, `cloud`, `vault`, `portainer` |
| `node`, preset `minimal` | Un **kiwi-node** con i soli due moduli di base, a cui aggiungi i moduli che vuoi | `vpn-client`, `reverse-proxy` |

Per il ruolo `node` esistono diversi preset. Un preset è un elenco di moduli già
pronto. I vecchi nomi di ruolo `node-gw` e `node-cloud` funzionano ancora e
corrispondono ai preset `gateway` e `cloud`.

I ruoli `master` e `node` sono costruiti con i moduli, e ogni modulo è un
servizio. kiwi-server trasforma i moduli di un host in uno **stack**, cioè
l’insieme dei container che la macchina esegue. Per impostazione predefinita lo
stack è fatto di quadlet di podman, cioè unità systemd che eseguono container.
Con `runtime: docker` lo esegue invece docker compose. Sulla macchina è
`kiwi-stack` ad avviare lo stack e a tenerlo in funzione. Vedi
[Moduli](modules.md).

## `master` { #master }

Il ruolo `master` cambia questi valori predefiniti dei moduli:

- `vpn-client`: `vpn_provider: mullvad`, `mss_clamp: true`
- `dns`: `network_mode: vpn-server`, `mullvad_socks: true`
- `tor` e `reverse-proxy`: `network_mode: vpn-server`

Con queste impostazioni Pi-hole, Tor e nginx condividono il namespace di rete
del server WireGuard. Un namespace di rete è l’insieme di interfacce di rete e
indirizzi che un container vede. I tre servizi sono quindi raggiungibili
all’indirizzo del master nella mesh, cioè il suo indirizzo nella rete WireGuard
privata. I container di un master si chiamano `km-…` e sono collegati alla rete
`knet-master` (`172.64.0.0/24`).

Un master può eseguire anche `nostr-relay` e `hub` (per un
[hub per le persone](../people/hubs.md)), `portainer` e `backup`. Per usarli,
aggiungili alla lista `modules:` del master. Il relay e l’hub girano soltanto
sui master.

```yaml
sorbet:
  role: master
  master:
    modules: [vpn-client, vpn-server, dns, tor, reverse-proxy, nostr-relay, hub]
```

## `node` { #node }

È il preset a stabilire quali moduli esegue un node. Se scrivi una lista
`modules:` tua, questa sostituisce quella del preset, e i moduli richiesti da
quelli elencati vengono aggiunti automaticamente. I container di un node si
chiamano `kn-…` e sono collegati alla rete `knet-node` (`172.128.0.0/24`).

```yaml
papaya:
  role: node
  node:
    preset: cloud
    modules: [vpn-client, reverse-proxy, cloud, vault, portainer, backup]
    backup: { server: https://backup.lychee.home }   # su lychee gira il modulo backup-server
```

Il preset gateway rende inoltre disponibile sul node la pagina web di Pi-hole
su `127.0.0.1:8080` (`expose_web_ui: true`). Che questa impostazione sia attiva
o no, il reverse proxy serve la pagina in TLS su `pihole.<hostname>`.

## Scrivere un ruolo { #writing-a-role }

Puoi scrivere un ruolo tuo. Un ruolo è una cartella `roles/<name>/` che
contiene un `role.yaml` e un `apply.sh`. Un ruolo costruito con i moduli elenca
i suoi moduli in `role.yaml` e include le impostazioni comuni dello stack. Il
suo `apply.sh` si riduce allora a una sola chiamata.

```yaml
name: node-media
title: kiwi-node (media)
targets: [coreos, ucore, debian]
node_type: node
modules: [vpn-client, reverse-proxy, downloader, portainer]
settings_include: [common/stack]
module_defaults:
  downloader: { jdownloader: false }
```

```bash
ks_role_apply() { ks_stack_apply; }
```

Un ruolo senza moduli fa il proprio lavoro direttamente in `ks_role_apply()`.
Può usare la libreria in `roles/common/lib.sh`, che proviene da kiwi-stack. Le
impostazioni dichiarate in `role.yaml` arrivano allo script come variabili con
il nome `KS_ROLE_<KEY>`. Lo script gira come root con `set -euo pipefail`. I
test del progetto generano ogni ruolo presente nel repository e lo passano a
shellcheck.
