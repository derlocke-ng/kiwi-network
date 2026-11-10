# Ruoli

Un ruolo è ciò che una macchina diventa. Ogni ruolo gira su tutti e tre i target.

| Ruolo | Cosa diventa la macchina | Moduli |
|---|---|---|
| `bare` | il sistema di base: utente amministratore, SSH, aggiornamenti automatici | nessuno |
| `master` | il **kiwi-master**: punto d'ingresso WireGuard con il doppio hop, Pi-hole, Tor e le pagine di amministrazione | `vpn-client`, `vpn-server`, `dns`, `tor`, `reverse-proxy` |
| `node`, preset `gateway` | un **kiwi-node** che instrada una LAN attraverso la VPN, con Pi-hole, DHCP relay, una stazione di download e SFTP | `vpn-client`, `dns`, `dhcp-relay`, `reverse-proxy`, `downloader`, `gateway`, `portainer`, `sftp` |
| `node`, preset `cloud` | un **kiwi-node** con Nextcloud e Vaultwarden | `vpn-client`, `reverse-proxy`, `cloud`, `vault`, `portainer` |
| `node`, preset `minimal` | un **kiwi-node** da riempire con i moduli che scegli tu | `vpn-client`, `reverse-proxy` |

`node-gw` e `node-cloud` funzionano ancora come nomi per i preset `gateway` e `cloud`.

I ruoli a moduli producono uno **stack**: di default podman quadlet (docker compose
con `runtime: docker`), che `kiwi-stack` avvia e mantiene in funzione. Vedi
[Moduli](modules.md).

## `master` { #master }

Il preset cambia questi default dei moduli:

- `vpn-client`: `vpn_provider: mullvad`, `mss_clamp: true`
- `dns`: `network_mode: vpn-server`, `mullvad_socks: true`
- `tor` e `reverse-proxy`: `network_mode: vpn-server`

Così Pi-hole, Tor e nginx vivono nel namespace di rete del server WireGuard e
rispondono all'indirizzo mesh del master. I container si chiamano `km-…` sulla
rete `knet-master` (`172.64.0.0/24`).

Un master può aggiungere ai suoi `modules:` `nostr-relay` e `hub` (un [hub per le persone](../people/hubs.md)),
`portainer` e `backup`. Il relay e l'hub girano solo sui
master.

```yaml
sorbet:
  role: master
  master:
    modules: [vpn-client, vpn-server, dns, tor, reverse-proxy, nostr-relay, hub]
```

## `node` { #node }

Il preset sceglie l'elenco dei moduli. `modules:` lo sostituisce, e i moduli richiesti
si aggiungono da soli. I container si chiamano `kn-…` sulla rete `knet-node`
(`172.128.0.0/24`).

```yaml
papaya:
  role: node
  node:
    preset: cloud
    modules: [vpn-client, reverse-proxy, cloud, vault, portainer, backup]
    backup: { server: https://backup.lychee.home }   # lychee esegue il modulo backup-server
```

Il preset gateway attiva la pagina web di Pi-hole (`expose_web_ui: true`) su
`127.0.0.1:8080`. Il reverse proxy la serve comunque via TLS su `pihole.<hostname>`.

## Scrivere un ruolo { #writing-a-role }

Un ruolo è una directory `roles/<name>/` con un `role.yaml` e un `apply.sh`. Un
ruolo a moduli elenca i suoi moduli e include le impostazioni comuni dello stack, e il suo
`apply.sh` è una sola chiamata:

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

Un ruolo senza moduli fa il proprio lavoro in `ks_role_apply()`, usando la
libreria in `roles/common/lib.sh` (che proviene da kiwi-stack). Le impostazioni in
`role.yaml` diventano `KS_ROLE_<KEY>`. Lo script gira come root con
`set -euo pipefail`. I test eseguono il render di ogni ruolo dell'albero e lo passano a shellcheck.
