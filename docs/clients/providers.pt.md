# Módulos de fornecedores

Um módulo de fornecedor dá ao [kiwi-proxy](kiwi-proxy.md) uma saída que ele
próprio produz, em vez de um SOCKS5 que te deram. Cada um vive no seu próprio
repositório, instala-se através do kiwi-updater no diretório de módulos do
kiwi-proxy e é gerido pelo kiwi-proxy: este constrói a imagem do módulo, ativa-o
quando uma saída precisa dele e desativa-o quando nenhum gateway o usa.

| Módulo | Repositório | Versão | Saída | Precisa de |
|---|---|---|---|---|
| `tor` | [kiwi-plugin-tor](https://github.com/derlocke-ng/kiwi-plugin-tor) | v0.3.0 | a rede Tor, um circuito por saída, qualquer país de saída | nada (gratuito) |
| `vpn` | [kiwi-plugin-vpn](https://github.com/derlocke-ng/kiwi-plugin-vpn) | v0.2.2 | um túnel WireGuard ou OpenVPN através do [gluetun](https://github.com/qdm12/gluetun) | uma subscrição de VPN |
| `9proxy` | [kiwi-plugin-9proxy](https://github.com/derlocke-ng/kiwi-plugin-9proxy) | v0.2.0 | uma saída residencial [9proxy](https://9proxy.com/) | uma conta 9proxy e o seu cliente proprietário (não redistribuído) |
| `mysterium` | [kiwi-plugin-myst](https://github.com/derlocke-ng/kiwi-plugin-myst) | v0.5.2 | a dVPN [Mysterium](https://mysterium.network/), com um seletor de nós por país e tipo de IP | uma identidade de consumidor registada com saldo MYST |

Os quatro são GPL-3.0-or-later, estão no [catálogo Kiwi](../desktop/catalogs.md)
e declaram `DEPENDS=kiwi-proxy`, por isso o kiwi instala primeiro o kiwi-proxy.
O Tor e o Mysterium são a forma rápida de ter mais IPs de saída, por exemplo
para testes.

## Instalar e usar { #install-and-use }

```bash
kiwi install kiwi-plugin-tor
kiwi-proxy module setup tor                      # constrói a sua imagem (kiwi-proxy setup faz todas)
kiwi-proxy module list
kiwi-proxy module countries tor                  # onde o Tor pode sair
kiwi-proxy add tor-de --module tor --country de  # uma saída a partir dele
kiwi-custodia new test --exit tor-de             # uma box nela, ou:
kiwi-fox new test --exit tor-de                  # um perfil de navegador nela
```

No Tor, o país é mantido com `StrictNodes`, por isso o circuito falha em vez de
sair noutro sítio. As saídas do módulo tor deixam passar, por omissão, as
credenciais SOCKS por site do Tor Browser (`--socks-auth passthrough`).

## Como está ligado { #how-it-is-wired }

**Cada fornecedor expõe SOCKS5 e mais nada.** Um contentor de fornecedor precisa
da sua própria saída para o exterior, por isso não pode viver no namespace de um
gateway, onde tudo é descartado exceto um destino. Os dois encontram-se numa
bridge Podman sem root, `kf-providers`, onde cada módulo recebe um endereço fixo:

```
provider container ──── kf-providers bridge ──── gateway ──── box / browser / tool
(its own way out)                                permits only <provider-ip>:port
SOCKS5 only
```

- **O Tor** já fala SOCKS5. O kiwi-proxy envia uma credencial por saída, e o
  `IsolateSOCKSAuth` do Tor dá a cada saída o seu próprio circuito.
- **A VPN e o Mysterium** usam um túnel que não fala SOCKS5, por isso um pequeno
  adaptador microsocks junta-se ao namespace de rede do túnel e oferece SOCKS5
  que passa pelo túnel.
- **O 9proxy** corre o cliente 9proxy, que abre uma porta SOCKS5 numa saída
  residencial.

Um contentor de fornecedor serve todas as saídas do mesmo módulo e lease. Um túnel
que perde a sua sessão falha fechado e é reiniciado.

## Configuração { #configuration }

O estado de cada módulo vive em `~/.local/share/kiwi-proxy/modules-state/<module>/`,
fora de qualquer repositório:

- **vpn**: `vpn.json` com as definições do gluetun (`VPN_SERVICE_PROVIDER`,
  `VPN_TYPE`, `WIREGUARD_ADDRESSES`, …; todas as chaves em maiúsculas vão para o
  gluetun tal como estão), uma lista `leases` opcional e um diretório `gluetun/`
  opcional (por exemplo um `wireguard.conf` para o fornecedor `custom` do
  gluetun). É uma configuração por máquina: as saídas nela diferem pelo país do
  servidor.
- **9proxy**: `config/account.conf`. Põe o cliente proprietário em
  `module/containers/vendor/` do plugin e acrescenta `COPY vendor/ /opt/9proxy/`
  ao seu `Containerfile` antes de `kiwi-proxy module setup 9proxy`. Sem ele, a
  imagem constrói-se, mas o fornecedor recusa-se a arrancar em vez de abrir uma
  porta.
- **mysterium**: `kiwi-proxy module config mysterium keystore=/path/to/0x….json
  --ask passphrase`, ou *Configure…* na app Kiwi Proxy. A frase-senha passa a ser
  um segredo Podman. Uma identidade mantém uma ligação de cada vez.

## Estado { #status }

O Tor não precisa de conta. O Mysterium foi verificado de ponta a ponta em
2026-11-07. Os módulos VPN e 9proxy estão completos e têm testes unitários, mas
não foram corridos de ponta a ponta com uma subscrição ou conta reais, como dizem
os seus READMEs.
