# Papéis

Um papel é aquilo em que uma máquina se torna. Todos os papéis correm nos três
targets.

| Papel | O que a máquina passa a ser | Módulos |
|---|---|---|
| `bare` | o sistema base: utilizador admin, SSH, atualizações automáticas | nenhum |
| `master` | o **kiwi-master**: ponto de entrada WireGuard com o salto duplo, Pi-hole, Tor e as páginas de administração | `vpn-client`, `vpn-server`, `dns`, `tor`, `reverse-proxy` |
| `node`, predefinição `gateway` | um **kiwi-node** que encaminha uma LAN através da VPN, com Pi-hole, DHCP relay, uma estação de transferências e SFTP | `vpn-client`, `dns`, `dhcp-relay`, `reverse-proxy`, `downloader`, `gateway`, `portainer`, `sftp` |
| `node`, predefinição `cloud` | um **kiwi-node** com Nextcloud e Vaultwarden | `vpn-client`, `reverse-proxy`, `cloud`, `vault`, `portainer` |
| `node`, predefinição `minimal` | um **kiwi-node** para preencher com módulos à tua escolha | `vpn-client`, `reverse-proxy` |

`node-gw` e `node-cloud` continuam a funcionar como nomes das predefinições
`gateway` e `cloud`.

Os papéis de módulos renderizam uma **stack**: quadlets podman por omissão
(docker compose com `runtime: docker`), que o `kiwi-stack` arranca e mantém a
correr. Ver [Módulos](modules.md).

## `master` { #master }

A predefinição altera estes valores por omissão dos módulos:

- `vpn-client`: `vpn_provider: mullvad`, `mss_clamp: true`
- `dns`: `network_mode: vpn-server`, `mullvad_socks: true`
- `tor` e `reverse-proxy`: `network_mode: vpn-server`

Assim, o Pi-hole, o Tor e o nginx vivem no namespace de rede do servidor
WireGuard e respondem no endereço de malha do master. Os contentores chamam-se
`km-…` e estão na rede `knet-master` (`172.64.0.0/24`).

Um master pode acrescentar `nostr-relay` e `hub` (um [hub para pessoas](../people/hubs.md)),
`portainer` e `backup` aos seus `modules:`. O relay e o hub só correm em
masters.

```yaml
sorbet:
  role: master
  master:
    modules: [vpn-client, vpn-server, dns, tor, reverse-proxy, nostr-relay, hub]
```

## `node` { #node }

A predefinição escolhe a lista de módulos. `modules:` substitui-a, e os módulos
obrigatórios entram sozinhos. Os contentores chamam-se `kn-…` e estão na rede
`knet-node` (`172.128.0.0/24`).

```yaml
papaya:
  role: node
  node:
    preset: cloud
    modules: [vpn-client, reverse-proxy, cloud, vault, portainer, backup]
    backup: { server: https://backup.lychee.home }   # o lychee corre o módulo backup-server
```

A predefinição gateway ativa a página web própria do Pi-hole
(`expose_web_ui: true`) em `127.0.0.1:8080`. O proxy inverso serve-a por TLS em
`pihole.<hostname>` em qualquer caso.

## Escrever um papel { #writing-a-role }

Um papel é um diretório `roles/<name>/` com um `role.yaml` e um `apply.sh`. Um
papel de módulos lista os seus módulos e inclui as definições de stack
partilhadas, e o seu `apply.sh` é uma só chamada:

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

Um papel sem módulos faz o seu próprio trabalho em `ks_role_apply()`, usando a
biblioteca em `roles/common/lib.sh` (que vem do kiwi-stack). As definições em
`role.yaml` passam a `KS_ROLE_<KEY>`. O script corre como root com
`set -euo pipefail`. Os testes renderizam e passam o shellcheck em todos os
papéis da árvore.
