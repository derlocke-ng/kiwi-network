# Como funciona a rede

Uma Kiwi Network junta as tuas máquinas numa única rede privada, estejam onde
estiverem: servidores em casa ou no escritório, portáteis, telemóveis e até
redes domésticas inteiras atrás de um router. As máquinas comunicam entre si
como se estivessem na mesma rede local, e só uma delas precisa de estar
acessível a partir da Internet. Esta página explica como essa rede é construída
e para que serve cada uma das suas partes.

A rede privada é uma **mesh WireGuard**. O WireGuard é o software de VPN que
cifra as ligações, e *a mesh* é o nome que estas páginas dão à rede privada que
todas as tuas máquinas partilham. No centro da mesh está uma máquina, o
*kiwi-master*. Todas as outras (nodes em casa ou no escritório, portáteis,
telemóveis, routers) abrem elas próprias a ligação ao master e, a partir daí,
conseguem chegar a todas as outras através da mesh. A rede inteira está descrita num único
ficheiro, o ficheiro fleet (`fleet.yaml`), e é a partir dele que o
[kiwi-server](../server/index.md) a constrói.

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

O master é a máquina a que todas as outras se ligam. A sua função, `master`,
inclui os cinco módulos descritos a seguir. O Pi-hole, o Tor e o nginx partilham
o namespace de rede do servidor WireGuard. Um namespace de rede é o conjunto
próprio de interfaces, endereços e rotas de um contentor. Estes três serviços
usam, portanto, a rede do servidor WireGuard em vez de terem uma rede sua, e é
por isso que são reiniciados juntamente com ele.

- **vpn-server** (wg-easy) é o servidor WireGuard. Todos os clientes e todos os
  nodes se ligam a ele, e é ele que emite as respetivas configurações
  WireGuard. O kiwi-server pode criá-las por ti (`kiwi-server enroll`).
- **vpn-client** (gluetun) liga o master a um fornecedor de VPN comercial. O
  preset do master usa a Mullvad, mas serve qualquer fornecedor compatível com
  o gluetun. A rota predefinida do servidor WireGuard aponta para este cliente
  VPN. Assim, o tráfego da mesh para a Internet é enviado através do
  fornecedor, e os sites veem o endereço do fornecedor e não o do master. Esta
  ligação é a *saída* do master, ou seja, o caminho pelo qual o tráfego da mesh
  chega à Internet. Como o tráfego passa por duas VPN seguidas, primeiro a tua
  e depois a do fornecedor, esta configuração chama-se **duplo salto** (double
  hop). Um master sem vpn-client envia o tráfego diretamente para a Internet, a
  partir do seu próprio endereço.
- **dns** (Pi-hole 6) é o servidor DNS da mesh. Responde no endereço do master
  na mesh, `10.8.0.1`. Vê [DNS, nomes e certificados](dns.md).
- **tor** disponibiliza aos clientes da mesh um proxy SOCKS5 em
  `10.8.0.1:9050`. Os nós de entrada e de saída do Tor estão limitados a um
  conjunto de países (por predefinição `de,ch,at,nl,fr`, imposto com
  `StrictNodes`).
- **reverse-proxy** (nginx) serve as páginas de administração, isto é, as
  interfaces web do wg-easy e do Pi-hole, em `wg.<master>` e `pihole.<master>`.
  Só as serve dentro da mesh, e apenas aos clientes autorizados a vê-las (vê
  «Grupos de clientes», mais abaixo).

Um master também pode correr um **relay nostr** e um **hub** para as
[pessoas da tua rede](../people/hubs.md#on-a-kiwi-network). Um hub é o site de
uma comunidade, que corre no navegador, e um relay nostr é o tipo de servidor
através do qual os hubs se sincronizam. Ao master podes ainda acrescentar o
Portainer e os backups.

### O que está acessível a partir da Internet { #what-is-reachable-from-the-internet }

Por predefinição, o master tem **uma única porta** aberta para a Internet: a do
WireGuard, UDP 51820. As páginas de administração só abrem a partir de dentro
da mesh. Há duas definições que abrem mais portas:

- `reverse-proxy.public: true` abre as portas 80 e 443 e obtém certificados
  Let's Encrypt para nomes fora do domínio da tua rede. Tudo o resto continua
  acessível apenas a partir da mesh, e as páginas de administração respondem
  com o erro 403 aos pedidos vindos de fora. Esta definição destina-se a um hub
  ou a um relay público.
- `vpn-server.unlock_relay` abre as portas TCP dos
  [anéis Tang](../server/operations.md#encrypted-disks-and-unlocking) para
  máquinas que estão atrás de NAT. O Tang é um servidor que permite a uma
  máquina com o disco cifrado desbloqueá-lo no arranque, e um anel é um
  servidor Tang com as suas próprias chaves.

O kiwi-server deixa o SSH tal como o sistema operativo o configura, o que, por
predefinição, significa que só é possível iniciar sessão com chaves. O próprio
kiwi-server usa o SSH para o `apply` e para o `status`.

## Grupos de clientes { #client-groups }

Os clientes do servidor WireGuard (wg-easy) são distribuídos por **grupos**,
consoante o endereço que têm. Cada grupo define aquilo a que os seus membros
podem aceder:

| Grupo | Sub-rede | Acede a | Vê os outros clientes | Páginas de administração |
|---|---|---|---|---|
| `guests` | `10.8.1.0/24` | os nodes | não | não |
| `pentest` | `10.8.2.0/24` | nada na mesh | não | não |
| `devices` | `10.8.3.0/24` | tudo | sim | sim |
| `routers` | `10.8.4.0/24` | tudo | sim | não |

```bash
kiwi-server enroll fleet.yaml phone --group devices --qr   # um código QR para a aplicação WireGuard
kiwi-server enroll fleet.yaml anna  --group guests --split # só o tráfego da mesh passa pelo túnel
```

Os membros de qualquer grupo também têm acesso à Internet pela saída do master, a
não ser que definas `internet: false` para o grupo. Um cliente cujo endereço
fica fora de todos os grupos (`10.8.0.x`) é um membro normal da mesh: tem acesso a
tudo e pode abrir as páginas de administração, desde que `admin_from_mesh`
esteja ativo.

Os grupos são uma definição do módulo vpn-server (`groups`), pelo que podes
alterá-los ou acrescentar os teus. A definição `reach` de um grupo aceita `all`,
`nodes`, nomes de máquinas, endereços ou sub-redes. A definição mais antiga,
`isolated_subnet`, que criava um único grupo isolado, continua a existir, mas
está desligada por predefinição.

## Nodes { #nodes }

Um node é uma máquina em casa ou no escritório onde correm os teus serviços.
Também tem um módulo vpn-client, mas num node este módulo não se liga a um
fornecedor de VPN comercial: liga-se ao master, com a configuração WireGuard
que o master emitiu para esse node. O `kiwi-server enroll` guarda essa
configuração em `secrets/<hostname>.conf`, e o node usa-a sem teres de definir
mais nada. Um node não precisa de nenhuma porta aberta para a Internet, porque
é ele que abre a ligação ao master. É por isso que funciona atrás do NAT de um
router doméstico.

A função `node` tem três presets, ou seja, três listas de módulos já prontas:

| Preset | Em que se torna a máquina |
|---|---|
| `gateway` (predefinido) | Um gateway para a rede local (LAN). Os dispositivos da LAN que usam esta máquina como gateway predefinido chegam à Internet através da VPN e têm acesso à mesh. O Pi-hole é o servidor DNS da LAN e, se quiseres, também o seu servidor DHCP. O Transmission e o JDownloader, os programas para descarregar ficheiros, correm *dentro* do namespace de rede do cliente VPN, pelo que ficam sem qualquer rota enquanto o túnel estiver em baixo. O preset inclui ainda o nginx, o Portainer e SFTP. |
| `cloud` | A tua própria cloud: Nextcloud com Collabora para ficheiros, calendários e documentos, e Vaultwarden para as palavras-passe. Estes serviços ficam atrás do nginx, e o Portainer também vem incluído. O Nextcloud é construído a partir dos contentores do projeto AIO, sem o contentor master do AIO. |
| `minimal` | Apenas o cliente VPN e o nginx. Os módulos que quiseres, acrescentas tu. |

Os nodes também podem fazer backups, servir de servidor de backups e correr o
Tang. O OpenCloud, o Immich e o Paperless-ngx estão incluídos para os
experimentares. Vê a [lista de módulos](../server/modules.md).

Os serviços de um node estão acessíveis a partir da LAN dele e no **endereço do
node na mesh** (por exemplo, `10.8.0.25`). O tráfego que chega da mesh a esse
endereço nas portas 80 e 443 é reencaminhado para o proxy inverso do node.

## Nomes { #names }

Os nomes das máquinas seguem uma convenção. **Os masters têm nomes de pratos de
fruta** (`crumble`, `sorbet`, `compote`, `chutney`, `strudel`, `cobbler`,
`trifle`, `cider`) e **os nodes, nomes de frutas** (`papaya`, `lychee`, `guava`,
`quince`, `damson`). Assim, em qualquer linha de um registo percebes logo que
tipo de máquina está por trás de um nome. É apenas uma convenção, e qualquer
nome serve. O nome de um serviço forma-se a partir do nome da máquina onde ele
corre: `cloud.papaya.home`, `vault.papaya.home`, `wg.sorbet.home`. Vê
[DNS, nomes e certificados](dns.md).

## Como a mesh chega à Internet { #ways-out }

Um master é um servidor WireGuard com uma saída, que é o caminho pelo qual o
tráfego da mesh chega à Internet. A saída tem três modos:

| Modo | Como a mesh chega à Internet | Estado |
|---|---|---|
| **provider** | Através de um fornecedor de VPN comercial (gluetun). É o duplo salto, e é o que o preset do master configura. | implementado |
| **direct** | Diretamente, pela ligação à Internet do próprio master. Para teres este modo, indica os módulos do master sem `vpn-client`. | implementado |
| **master** | Através do *master de outra rede*. O teu master é lá um cliente, num grupo que pode chegar à Internet e a mais nada. A isto chama-se multi-hop. | concebido; depende de se poder adicionar máquinas de uma rede a outra, ou seja, da federação |

Seja qual for o modo de saída, todos os masters disponibilizam também à mesh o
proxy SOCKS5 do Tor.

## Uma mesh por rede { #one-mesh-per-network }

Cada rede tem a sua própria mesh, com o seu intervalo de endereços. O intervalo
predefinido é `10.8.0.0/16`. Os masters e os nodes ficam em `10.8.0.0/24`, e os
grupos vêm a seguir: guests em `.1`, pentest em `.2`, devices em `.3` e routers
em `.4`. Uma segunda rede usa outro intervalo, por exemplo `10.9.0.0/16`, para
que um dispositivo que pertença às duas as consiga distinguir. Por enquanto, o
intervalo não é uma definição única: está repartido por várias (`mesh_subnet`;
`server_ip`, `wg_subnet`, `wg_default_address` e `groups`, do vpn-server; e
`socks_policy_accept`, do Tor). O ficheiro fleet define-as todas.

## Endereçamento { #addressing }

| O quê | Predefinição |
|---|---|
| Toda a mesh (encaminhada em todas as máquinas) | `10.8.0.0/16` por predefinição (`mesh_subnet`) |
| Clientes do wg-easy | `10.8.0.0/24`; o servidor é `10.8.0.1` |
| Grupos de clientes | `10.8.1.0/24` … `10.8.4.0/24` |
| Rede da stack | `172.64.0.0/24` num master, `172.128.0.0/24` num node |
| MTU do WireGuard | `1376` (`wg_mtu`), medida com [`kiwi-server mtu`](../server/operations.md#tunnel-mtu) |
| MTU da bridge da stack | `1500` (`bridge_mtu`) |

A stack de uma máquina é o conjunto de contentores que os seus módulos põem a
correr. Todas as máquinas com uma stack encaminham o intervalo de endereços da
mesh pelo seu cliente VPN ou, no caso do master, pelo servidor WireGuard. Assim,
a máquina e os seus contentores chegam a todos os nodes.

## Reinícios e atualizações automáticos { #keeping-it-fresh }

Cada máquina recebe dois temporizadores, configurados nas definições da sua
stack. O primeiro é um **reinício diário da VPN**, às `07:00`, que dá à máquina
um novo endereço de saída. O segundo é uma **atualização semanal**, ao domingo
às 00:00, que executa `podman auto-update` desde que esteja definido
`auto_update: registry`. O sistema operativo também se atualiza sozinho, e só
reinicia [na janela de manutenção que definires](../server/machines.md#updates).

## Uma LAN inteira na mesh { #a-whole-lan-in-the-mesh }

Um router pode entrar na mesh como cliente WireGuard, no grupo `routers`. Em
alternativa, pode enviar o tráfego destinado à sub-rede da mesh para um node
gateway, através de uma rota estática. Em ambos os casos, todos os dispositivos
da LAN desse router chegam a todos os nodes sem terem de correr o WireGuard.
Vê [Routers](routers.md).
