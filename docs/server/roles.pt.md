# Funções

A função define para que serve uma máquina na tua Kiwi Network. No ficheiro
fleet, atribuis uma função a cada máquina, e o kiwi-server prepara a máquina
para ela. Uma máquina pode ser apenas um sistema base, o master a que se ligam
todos os dispositivos e nodes, ou um node onde correm os teus serviços. Todas as
funções funcionam nos três sistemas de destino, ou seja, nos três sistemas
operativos que o kiwi-server sabe instalar.

| Função | Em que se torna a máquina | Módulos |
|---|---|---|
| `bare` | Apenas o sistema base, com um utilizador de administração, SSH e atualizações automáticas | nenhum |
| `master` | O **kiwi-master**. É o ponto de entrada WireGuard da rede e envia o tráfego da rede para a Internet através de uma VPN comercial (o duplo salto). Corre também o Pi-hole, um DNS que bloqueia a publicidade, o Tor e as páginas de administração | `vpn-client`, `vpn-server`, `dns`, `tor`, `reverse-proxy` |
| `node`, preset `gateway` | Um **kiwi-node** que faz passar pela VPN o tráfego de uma rede local (LAN). Corre também o Pi-hole, um relay DHCP, uma estação de downloads e SFTP | `vpn-client`, `dns`, `dhcp-relay`, `reverse-proxy`, `downloader`, `gateway`, `portainer`, `sftp` |
| `node`, preset `cloud` | Um **kiwi-node** que corre o Nextcloud e o Vaultwarden | `vpn-client`, `reverse-proxy`, `cloud`, `vault`, `portainer` |
| `node`, preset `minimal` | Um **kiwi-node** só com os dois módulos básicos, ao qual acrescentas os módulos que quiseres | `vpn-client`, `reverse-proxy` |

A função `node` existe em vários presets. Um preset é uma lista de módulos já
pronta. Os nomes de função antigos `node-gw` e `node-cloud` continuam a
funcionar e correspondem aos presets `gateway` e `cloud`.

As funções `master` e `node` são construídas a partir de módulos, e cada módulo
é um serviço. O kiwi-server transforma os módulos de uma máquina numa
**stack**, que é o conjunto de contentores que a máquina corre. Por
predefinição, a stack é composta por quadlets do podman, que são unidades
systemd que correm contentores. Com `runtime: docker`, é o docker compose que a
põe a correr. Na máquina, é o `kiwi-stack` que arranca a stack e a mantém a
funcionar. Vê [Módulos](modules.md).

## `master` { #master }

A função `master` altera estas predefinições dos módulos:

- `vpn-client`: `vpn_provider: mullvad`, `mss_clamp: true`
- `dns`: `network_mode: vpn-server`, `mullvad_socks: true`
- `tor` e `reverse-proxy`: `network_mode: vpn-server`

Com estas definições, o Pi-hole, o Tor e o nginx partilham o namespace de rede
do servidor WireGuard. Um namespace de rede é o conjunto de interfaces de rede
e de endereços que um contentor vê. Os três serviços ficam, por isso,
acessíveis no endereço do master na mesh, ou seja, no endereço que o master tem
na rede WireGuard privada. Os contentores de um master chamam-se `km-…` e estão
ligados à rede `knet-master` (`172.64.0.0/24`).

Um master pode também correr o `nostr-relay` e o `hub` (para um
[hub para as pessoas](../people/hubs.md)), o `portainer` e o `backup`. Para os
usares, acrescenta-os à lista `modules:` do master. O relay e o hub só correm em
masters.

```yaml
sorbet:
  role: master
  master:
    modules: [vpn-client, vpn-server, dns, tor, reverse-proxy, nostr-relay, hub]
```

## `node` { #node }

É o preset que define que módulos corre um node. Se escreveres a tua própria
lista `modules:`, ela substitui a do preset, e os módulos de que os módulos
indicados dependem são acrescentados automaticamente. Os contentores de um node
chamam-se `kn-…` e estão ligados à rede `knet-node` (`172.128.0.0/24`).

```yaml
papaya:
  role: node
  node:
    preset: cloud
    modules: [vpn-client, reverse-proxy, cloud, vault, portainer, backup]
    backup: { server: https://backup.lychee.home }   # o lychee corre o módulo backup-server
```

O preset gateway disponibiliza também a página web do próprio Pi-hole em
`127.0.0.1:8080`, no node (`expose_web_ui: true`). Com esta definição ligada ou
não, o proxy inverso serve essa página por TLS em `pihole.<hostname>`.

## Escrever uma função { #writing-a-role }

Podes escrever a tua própria função. Uma função é uma pasta `roles/<name>/`
com um `role.yaml` e um `apply.sh`. Uma função construída a partir de módulos
indica os seus módulos no `role.yaml` e inclui as definições comuns da stack.
O seu `apply.sh` fica então reduzido a uma única chamada.

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

Uma função sem módulos faz ela própria o trabalho em `ks_role_apply()`. Pode
usar a biblioteca em `roles/common/lib.sh`, que vem do kiwi-stack. As
definições que o `role.yaml` declara chegam ao script como variáveis com o nome
`KS_ROLE_<KEY>`. O script corre como root, com `set -euo pipefail`. Os testes
do projeto geram todas as funções da árvore e passam-lhes o shellcheck.
