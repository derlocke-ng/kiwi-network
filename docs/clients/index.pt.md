# Trabalhar com muitas redes de clientes

Dez clientes remotos significam muitas vezes dez VPNs ou endpoints SOCKS, um para
chegar à rede de cada cliente. Corrê-los todos no anfitrião é uma confusão: dez
túneis ao mesmo tempo, rotas que entram em conflito e uma rede a vazar para a
seguinte. As apps de ambiente de trabalho Kiwi dão, em vez disso, a cada um uma
**saída selada**: um contentor cuja única rota é esse upstream. As tuas
ferramentas juntam-se à saída de que precisam, e nada mais muda no anfitrião.

| App | O que faz |
|---|---|
| [**kiwi-proxy**](kiwi-proxy.md) | O motor. Uma **saída** é um upstream com nome: um SOCKS5 que te deram, ou um que um módulo de fornecedor cria. Ativá-la cria um **gateway**, um namespace de rede cuja única rota é esse upstream. As apps do anfitrião podem usá-la como uma porta SOCKS5 local |
| [**kiwi-custodia**](kiwi-custodia.md) | **Distro boxes numa saída**: Fedora, Ubuntu, Debian, Kali, Arch, openSUSE, Rocky ou Alpine num contentor sem root com a sua própria pasta pessoal. *Tudo* na box sai pela saída: gestores de pacotes, jogos, binários estáticos que nunca ouviram falar de um proxy |
| [**kiwi-fox**](kiwi-fox.md) | **Perfis de navegador numa saída**: Camoufox, Firefox ou Tor Browser, cada perfil com o seu próprio armazenamento |
| [**Módulos de fornecedores**](providers.md) | Saídas a partir do Tor, de uma VPN (gluetun), do 9proxy ou do Mysterium. O Tor e o Mysterium são a forma rápida de ter mais IPs de saída, úteis para testes |

```
 client A: socks5://…  ─┐                                   ┌─ box "client-a" (Fedora: ssh, ansible, dnf …)
 client B: socks5://…  ─┼─ kiwi-proxy exits ─▶ gateways ───┼─ browser profile "client-b"
 Tor / Mysterium / VPN ─┘   one per upstream   only route   └─ curl, mail, any app: socks5h://127.0.0.1:1082
                                               is the exit
```

## Como se mantém limpo { #how-it-stays-clean }

- **Fail closed.** A firewall de um gateway descarta tudo exceto o seu único
  upstream. Se o gateway morrer, o que se lhe juntou perde a rota. O kill switch
  é a ausência de uma rota, não um software que tenha de reparar nisso.
- **Nada corre se não for usado.** Um gateway que uma box ou um navegador ativou
  desaparece quando o último sai. Só as saídas que inicias com `kiwi-proxy up`
  ficam ativas.
- **O que está separado continua separado.** O que está na mesma saída partilha-a
  (um IP, um namespace). Os clientes que não se devem cruzar recebem saídas
  diferentes, e cada box tem a sua própria pasta pessoal, por isso as chaves SSH e
  os perfis de navegador não se misturam.
- **Sem root, sem rotas no anfitrião.** Tudo corre em Podman sem root, e a rede
  do próprio anfitrião fica intacta.
- **O DNS também passa pela saída.** Por omissão, os nomes são resolvidos por DoH
  através da saída, com listas de bloqueio de anúncios. Para os **nomes de
  anfitrião internos** de um cliente, entrega antes os nomes ao lado do cliente
  com `--dns remote` (também o modo para o Tor e para nomes `.onion`).

## Limites { #limits }

Estes vêm dos repositórios:

- **Só TCP, só IPv4.** O UDP não sai para lado nenhum (sem QUIC, sem multimédia
  WebRTC), e o IPv6 não tem rota.
- **Uma configuração VPN por máquina.** O módulo de fornecedor VPN guarda uma
  configuração do gluetun (um `vpn.json`, uma configuração WireGuard
  personalizada), e as suas saídas só diferem no país do servidor. Para várias
  VPNs próprias de clientes lado a lado, o caminho hoje é um endpoint SOCKS5 por
  cliente.
- **Uma box é custódia de rede, não uma sandbox.** Partilha o teu ecrã, o bus de
  sessão e a área de transferência, como o distrobox. O que não consegue fazer é
  chegar à rede a não ser através da sua saída.
- **Mysterium:** uma identidade mantém uma ligação de cada vez.

## Começar { #get-started }

```bash
kiwi install kiwi-custodia            # traz consigo o kiwi-proxy
kiwi-custodia setup                   # imagens e dados DNS

kiwi-proxy add client-a socks5://user:pass@jump.client-a.example:1080 --dns remote
kiwi-custodia new client-a --exit client-a --distro fedora
kiwi-custodia enter client-a          # uma shell cuja única saída é o SOCKS5 do cliente A
```
