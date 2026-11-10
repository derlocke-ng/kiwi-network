# Trabalhar com muitas redes de clientes

Se trabalhas à distância para muitos clientes, normalmente precisas de uma
ligação VPN ou SOCKS separada para chegar à rede de cada um. Com dez clientes,
são dez ligações. Ter todas a correr no teu computador dá problemas: há dez
túneis ativos ao mesmo tempo, as rotas entram em conflito umas com as outras,
e o tráfego destinado à rede de um cliente pode ir parar à rede de outro.

As aplicações de ambiente de trabalho da Kiwi permitem-te trabalhar na rede de
cada cliente de forma isolada. O computador anfitrião não fica cheio de túneis
e rotas, e não tens dez ligações VPN a correr ao mesmo tempo. Cada ligação é
colocada num contentor próprio, e a única rota para fora desse contentor leva
a esse cliente. A uma ligação destas chama-se **exit**. As tuas ferramentas
correm num contentor ou num perfil do navegador que usa o exit de que
precisam, e nada mais muda no anfitrião.

| Aplicação | O que faz |
|---|---|
| [**kiwi-proxy**](kiwi-proxy.md) | O motor sobre o qual as outras aplicações assentam. Um **exit** é uma ligação a um upstream, guardada com um nome. O upstream é o proxy para onde o teu tráfego é enviado: um proxy SOCKS5 que te deram ou um proxy criado por um módulo de fornecedor. Quando ativas um exit, o kiwi-proxy cria um **gateway** para ele. O gateway é um namespace de rede (um conjunto próprio de interfaces, rotas e regras de firewall) cuja única rota leva a esse upstream. Os programas do anfitrião podem usar um exit através de uma porta SOCKS5 local |
| [**kiwi-custodia**](kiwi-custodia.md) | **Distribuições Linux em boxes que usam um exit.** Uma box do kiwi-custodia é um contentor rootless (que corre sem permissões de root) com Fedora, Ubuntu, Debian, Kali, Arch, openSUSE, Rocky ou Alpine e com uma pasta pessoal própria. *Todo* o tráfego de rede da box passa pelo exit, incluindo o dos gestores de pacotes, dos jogos e dos programas com ligação estática que ignoram as definições de proxy |
| [**kiwi-fox**](kiwi-fox.md) | **Perfis do navegador que usam um exit.** Cada perfil corre o Camoufox, o Firefox ou o Tor Browser e tem o seu próprio armazenamento |
| [**Módulos de fornecedor**](providers.md) | Módulos que criam exits através do Tor, de uma VPN (com o gluetun), do 9proxy ou da Mysterium. O Tor e a Mysterium são uma forma rápida de obter mais endereços IP, o que dá jeito para testes |

```
 client A: socks5://…  ─┐                                   ┌─ box "client-a" (Fedora: ssh, ansible, dnf …)
 client B: socks5://…  ─┼─ kiwi-proxy exits ─▶ gateways ───┼─ browser profile "client-b"
 Tor / Mysterium / VPN ─┘   one per upstream   only route   └─ curl, mail, any app: socks5h://127.0.0.1:1082
                                               is the exit
```

## Como os exits se mantêm separados { #how-it-stays-clean }

- **Um gateway é fail-closed.** Isto quer dizer que uma falha corta o tráfego
  e nunca abre outro caminho. A firewall de um gateway descarta tudo o que não
  seja dirigido ao único upstream desse gateway. Se o gateway parar, tudo o
  que depende dele fica sem rota. Nenhum programa tem de detetar a falha e
  reagir, porque sem o gateway simplesmente não há rota.
- **Só corre o que estás a usar.** Quando uma box ou um navegador arranca um
  gateway, esse gateway é removido logo que pare a última box ou o último
  navegador que o usa. Só os exits que inicias tu próprio com `kiwi-proxy up`
  continuam a correr.
- **Os clientes ficam separados.** As boxes e os navegadores no mesmo exit
  partilham-no, por isso têm o mesmo endereço IP e o mesmo namespace de rede.
  Clientes que não se podem ver uns aos outros ficam em exits diferentes. Cada
  box tem também a sua própria pasta pessoal, por isso as chaves SSH e os
  perfis do navegador de um cliente não estão disponíveis na box de outro.
- **Sem permissões de root e sem rotas no anfitrião.** Tudo corre no Podman
  rootless, que corre os contentores como o teu próprio utilizador. A rede do
  anfitrião não é alterada.
- **As consultas DNS também passam pelo exit.** Por predefinição, os nomes são
  resolvidos com DNS over HTTPS (DoH) através do exit, e os domínios de
  publicidade que constam das listas de bloqueio ficam inacessíveis. Para resolver
  os **nomes internos** de um cliente, usa antes `--dns remote`. Os nomes são
  então passados para o lado do cliente e resolvidos lá. O Tor e os nomes
  `.onion` também precisam deste modo.

## Limites { #limits }

Estes limites estão indicados nos próprios repositórios:

- **Só TCP e só IPv4.** O UDP não é reencaminhado, por isso o QUIC e o áudio e
  vídeo do WebRTC não funcionam. Não há rota para IPv6.
- **Uma configuração VPN por máquina.** O módulo de fornecedor VPN tem uma
  única configuração do gluetun, com um `vpn.json` e uma configuração
  WireGuard personalizada. Os exits deste módulo só diferem no país do
  servidor. Se precisas das VPN próprias de vários clientes ao mesmo tempo,
  hoje a forma de o fazer é ter um endpoint SOCKS5 para cada cliente.
- **Uma box restringe a rede, mas não é uma sandbox.** Tal como um contentor
  do distrobox, tem acesso ao teu ambiente gráfico, ao bus da tua sessão e à
  área de transferência. O que não consegue é chegar à rede de outra forma que
  não seja através do seu exit.
- **Mysterium:** uma identidade só pode ter uma ligação de cada vez.

## Começar { #get-started }

Os comandos seguintes instalam as aplicações, guardam como exit o proxy SOCKS5
de um cliente e abrem uma shell numa box Fedora que usa esse exit:

```bash
kiwi install kiwi-custodia            # traz o kiwi-proxy consigo
kiwi-custodia setup                   # imagens e dados de DNS

kiwi-proxy add client-a socks5://user:pass@jump.client-a.example:1080 --dns remote
kiwi-custodia new client-a --exit client-a --distro fedora
kiwi-custodia enter client-a          # uma shell cujo único caminho para fora é o SOCKS5 do cliente A
```
