# Como funciona a rede

Uma Kiwi Network é uma **malha WireGuard com um hub**, o *kiwi-master*. Todas as
outras máquinas (nodes em casa ou no escritório, portáteis, telemóveis, routers)
ligam-se ao master e encontram as restantes na malha. Tudo isto é descrito num
ficheiro fleet e construído pelo [kiwi-server](../server/index.md).

```
                          Internet
                             ▲
                             │  the mesh's traffic leaves through a commercial VPN
                             │  (gluetun · Mullvad in the preset): the double hop
            ┌────────────────┴──────────────────────────────┐
            │ kiwi-master   (a VPS, or any box people can reach) │
            │   wg-easy    WireGuard server · 10.8.0.1       │ ◀── UDP 51820: the one port
            │   gluetun    the master's own exit             │     it publishes by default
            │   Pi-hole    DNS for the mesh                  │
            │   Tor        SOCKS5 for mesh clients           │
            │   nginx      admin pages, optional hub & relay │
            └────────────────▲──────────────────────────────┘
                             │  WireGuard mesh 10.8.0.0/16 · everyone dials out
     ┌───────────────────────┼─────────────────────┬────────────────────────┐
 kiwi-node (cloud)     kiwi-node (gateway)     devices & guests        routers
 Nextcloud, Vaultwarden routes its LAN through  in client groups:       OpenWrt, FritzBox …
 behind nginx           the VPN; Pi-hole, DHCP  devices, guests,        bring a whole LAN in
                        relay, downloads, SFTP  routers, pentest
```

## O master { #the-master }

O papel `master` corre cinco módulos. O Pi-hole, o Tor e o nginx vivem dentro do
namespace de rede do servidor WireGuard e regressam com ele.

- **vpn-server** (wg-easy) é o ponto de entrada de todos os clientes e nodes, e
  emite as respetivas configurações WireGuard. O kiwi-server pode criá-las por ti
  (`kiwi-server enroll`).
- **vpn-client** (gluetun) liga-se a um fornecedor de VPN comercial: Mullvad na
  predefinição, qualquer fornecedor do gluetun em geral. A rota predefinida do
  servidor WireGuard aponta para ele, por isso o tráfego da malha sai através do
  fornecedor e não do endereço próprio do master. Isto é o **salto duplo**. Um
  master sem vpn-client sai diretamente.
- **dns** (Pi-hole 6) responde no endereço de malha do master, `10.8.0.1`. Ver
  [DNS, nomes e certificados](dns.md).
- **tor** oferece SOCKS5 em `10.8.0.1:9050` aos clientes da malha, com nós de
  entrada e de saída fixados num conjunto de países (por omissão `de,ch,at,nl,fr`,
  `StrictNodes`).
- **reverse-proxy** (nginx) serve as páginas de administração, `wg.<master>` e
  `pihole.<master>`, aos grupos de administração na malha.

Um master pode também ter um **relay nostr** e um **hub** para as
[pessoas na tua rede](../people/hubs.md#on-a-kiwi-network), além de Portainer
e cópias de segurança.

### O que está acessível a partir da Internet { #what-is-reachable-from-the-internet }

Por omissão, o master publica **uma porta**: WireGuard, UDP 51820. As páginas de
administração só respondem à malha. Duas definições acrescentam mais:

- `reverse-proxy.public: true` publica as portas 80 e 443, com certificados
  Let's Encrypt para nomes fora do domínio da fleet. Tudo o resto continua a
  responder só à malha, e as páginas de administração respondem 403 a quem vem de
  fora. Isto serve para um hub ou relay público.
- `vpn-server.unlock_relay` abre as portas TCP dos
  [anéis Tang](../server/operations.md#encrypted-disks-and-unlocking) para
  máquinas atrás de NAT.

O SSH fica como o sistema operativo o tem (só chaves, por omissão). O kiwi-server
usa-o para `apply` e `status`.

## Grupos de clientes { #client-groups }

Os clientes do wg-easy são organizados em **grupos** por endereço. Cada grupo
decide o que os seus membros conseguem alcançar:

| Grupo | Sub-rede | Alcança | Vê outros clientes | Páginas de administração |
|---|---|---|---|---|
| `guests` | `10.8.1.0/24` | os nodes | não | não |
| `pentest` | `10.8.2.0/24` | nada na malha | não | não |
| `devices` | `10.8.3.0/24` | tudo | sim | sim |
| `routers` | `10.8.4.0/24` | tudo | sim | não |

```bash
kiwi-server enroll fleet.yaml phone --group devices --qr   # um código QR para a app WireGuard
kiwi-server enroll fleet.yaml anna  --group guests --split # só a malha passa pelo túnel
```

Todos os grupos podem sair para a Internet através da saída, a não ser que
definas `internet: false`. Os clientes fora de qualquer grupo (`10.8.0.x`) são a
malha simples: alcançam tudo e veem as páginas de administração enquanto
`admin_from_mesh` estiver ativo. Os grupos são uma definição do módulo vpn-server
(`groups`), por isso podes alterá-los ou acrescentar os teus (`reach` aceita
`all`, `nodes`, nomes de anfitrião, endereços ou sub-redes). O antigo
`isolated_subnet` único ainda existe, mas está desativado por omissão.

## Nodes { #nodes }

O vpn-client de um node não fala com uma VPN comercial. Usa a configuração
WireGuard que o master emitiu para ele (`kiwi-server enroll` escreve
`secrets/<hostname>.conf`, e o node vai buscá-la sozinho). Um node não precisa de
nenhuma porta aberta na Internet: liga-se ao master, por isso funciona atrás do
NAT de um router doméstico.

O papel `node` tem três predefinições:

| Predefinição | O que a máquina passa a ser |
|---|---|
| `gateway` (por omissão) | Um gateway de LAN. Os clientes da LAN que o usam como gateway predefinido saem através da VPN e conseguem alcançar a malha. O Pi-hole serve a LAN (opcionalmente como o seu servidor DHCP). O Transmission e o JDownloader correm *dentro* do namespace de rede do cliente VPN, por isso não têm rota nenhuma quando o túnel está em baixo. Com nginx, Portainer e SFTP. |
| `cloud` | Nextcloud (a partir dos contentores do projeto AIO, sem o contentor master do AIO) com Collabora, mais Vaultwarden, atrás do nginx, mais Portainer |
| `minimal` | Apenas o cliente VPN e o nginx, para módulos à tua escolha |

Os nodes podem também correr cópias de segurança, um servidor de cópias de
segurança, Tang e (para experimentar) OpenCloud, Immich e Paperless-ngx. Ver a
[lista de módulos](../server/modules.md).

Os serviços de um node estão acessíveis na sua LAN e no seu **endereço de malha**
(p. ex. `10.8.0.25`). O tráfego da malha para esse endereço nas portas 80 e 443 é
encaminhado para o proxy inverso.

## Nomes { #names }

As máquinas recebem nomes do pomar: **masters com nomes de pratos de fruta**
(`crumble`, `sorbet`, `compote`, `chutney`, `strudel`, `cobbler`, `trifle`,
`cider`) e **nodes com nomes de frutos** (`papaya`, `lychee`, `guava`, `quince`,
`damson`), para que o tipo de máquina se leia em cada linha de registo. É uma
convenção, e qualquer nome funciona. Os serviços ficam por baixo do seu
anfitrião: `cloud.papaya.home`, `vault.papaya.home`, `wg.sorbet.home`. Ver
[DNS, nomes e certificados](dns.md).

## Saídas { #ways-out }

Um master é um servidor WireGuard com uma saída, e a saída tem três modos:

| Modo | Como a malha chega à Internet | Estado |
|---|---|---|
| **provider** | através de uma VPN comercial (gluetun): o salto duplo e a predefinição do master | construído |
| **direct** | diretamente pela ligação própria do master. Lista os módulos do master sem `vpn-client` | construído |
| **master** | através do *master de outra rede*, como cliente num dos seus grupos que pode chegar à Internet e a mais nada: multi-hop | projetado; precisa de inscrição entre redes, ou seja, de federação |

Todos os masters oferecem também o SOCKS5 do Tor à malha, seja qual for a saída.

## Uma malha por rede { #one-mesh-per-network }

Cada rede tem a sua própria malha. Por omissão é `10.8.0.0/16`: masters e nodes
em `10.8.0.0/24`, depois guests `.1`, pentest `.2`, devices `.3` e routers
`.4`. Uma segunda rede usa outro intervalo, por exemplo `10.9.0.0/16`, para que
um dispositivo que esteja em ambas as consiga distinguir. Hoje o intervalo está
espalhado por várias definições (`mesh_subnet`, o `server_ip` do vpn-server,
`wg_subnet`, `wg_default_address` e `groups`, e o `socks_policy_accept` do Tor),
e o ficheiro fleet define-as todas.

## Endereçamento { #addressing }

| O quê | Por omissão |
|---|---|
| A malha inteira (encaminhada em todos os anfitriões) | `10.8.0.0/16` por omissão (`mesh_subnet`) |
| Clientes do wg-easy | `10.8.0.0/24`; o servidor é `10.8.0.1` |
| Grupos de clientes | `10.8.1.0/24` … `10.8.4.0/24` |
| Rede da stack | `172.64.0.0/24` num master, `172.128.0.0/24` num node |
| MTU do WireGuard | `1376` (`wg_mtu`), medido com [`kiwi-server mtu`](../server/operations.md#tunnel-mtu) |
| MTU da bridge da stack | `1500` (`bridge_mtu`) |

Cada anfitrião da stack encaminha a malha através do seu cliente VPN (no master,
através do servidor WireGuard), por isso o anfitrião e os seus contentores
alcançam todos os nodes.

## Manter tudo fresco { #keeping-it-fresh }

Cada máquina recebe dois temporizadores das suas definições de stack: um
**reinício diário da VPN** (`07:00`, para um endereço de saída novo) e uma
**atualização semanal** (domingo às 00:00, que corre `podman auto-update` enquanto
`auto_update: registry` estiver definido). O sistema operativo atualiza-se sozinho
e só reinicia na [tua janela](../server/machines.md#updates).

## Uma LAN inteira na malha { #a-whole-lan-in-the-mesh }

Um router pode juntar-se à malha como cliente WireGuard no grupo `routers`, ou
enviar a sub-rede da malha para um node gateway com uma rota estática. A partir
daí, todos os dispositivos dessa LAN alcançam todos os nodes sem correr
WireGuard. Ver [Routers](routers.md).
