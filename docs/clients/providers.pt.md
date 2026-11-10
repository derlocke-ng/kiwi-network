# Módulos de fornecedor

No [kiwi-proxy](kiwi-proxy.md), um exit é uma ligação a um upstream, guardada
com um nome, pela qual as tuas boxes e os teus navegadores enviam o tráfego.
Normalmente é uma ligação que te deram, como o proxy SOCKS5 que dá acesso à
rede de um cliente. Um módulo de fornecedor serve para o outro caso: é ele que
cria o exit, através do Tor, de uma subscrição de VPN, do 9proxy ou da
Mysterium. O Tor e a Mysterium, em particular, servem para teres mais
endereços IP para testes.

Cada módulo está num repositório próprio. O kiwi-updater instala-o no
diretório de módulos do kiwi-proxy, e a partir daí é o kiwi-proxy que o gere:
constrói a imagem de contentor do módulo, arranca o módulo quando um exit
precisa dele e para-o quando já nenhum gateway o usa. Um gateway é o
contentor que o kiwi-proxy corre para um exit enquanto esse exit está ativo.

| Módulo | Repositório | Versão | Exit | Requisitos |
|---|---|---|---|---|
| `tor` | [kiwi-plugin-tor](https://github.com/derlocke-ng/kiwi-plugin-tor) | v0.3.0 | a rede Tor, com um circuito por exit e qualquer país de saída | nenhum (é gratuito) |
| `vpn` | [kiwi-plugin-vpn](https://github.com/derlocke-ng/kiwi-plugin-vpn) | v0.2.2 | um túnel WireGuard ou OpenVPN através do [gluetun](https://github.com/qdm12/gluetun) | uma subscrição de VPN |
| `9proxy` | [kiwi-plugin-9proxy](https://github.com/derlocke-ng/kiwi-plugin-9proxy) | v0.2.0 | um exit residencial do [9proxy](https://9proxy.com/) | uma conta 9proxy e o cliente proprietário do 9proxy, que não é redistribuído |
| `mysterium` | [kiwi-plugin-myst](https://github.com/derlocke-ng/kiwi-plugin-myst) | v0.5.2 | a dVPN da [Mysterium](https://mysterium.network/) (uma VPN descentralizada), com uma lista de nós que podes escolher por país e por tipo de IP | uma identidade de consumidor registada, com saldo em MYST |

Os quatro módulos têm a licença GPL-3.0-or-later e estão no
[catálogo Kiwi](../desktop/catalogs.md). Cada um declara `DEPENDS=kiwi-proxy`,
por isso o kiwi-updater instala primeiro o kiwi-proxy. O Tor e a Mysterium
são a forma rápida de obter mais endereços IP para os exits, por exemplo para
testes.

## Instalação e utilização { #install-and-use }

```bash
kiwi install kiwi-plugin-tor
kiwi-proxy module setup tor                      # construir a imagem dele (o kiwi-proxy setup constrói todas)
kiwi-proxy module list
kiwi-proxy module countries tor                  # por que países o Tor pode sair
kiwi-proxy add tor-de --module tor --country de  # um exit criado por ele
kiwi-custodia new test --exit tor-de             # uma box nesse exit, ou:
kiwi-fox new test --exit tor-de                  # um perfil do navegador nesse exit
```

Num exit Tor, o país é imposto com a opção `StrictNodes` do Tor. Um circuito
que não consiga sair por esse país falha, e nunca sai por outro país. Os
exits do módulo tor passam adiante as credenciais SOCKS que o Tor Browser
envia para cada site. É essa a predefinição deles
(`--socks-auth passthrough`).

## Como um fornecedor se liga a um gateway { #how-it-is-wired }

**Todos os fornecedores oferecem SOCKS5 e mais nada.** Um contentor de
fornecedor precisa de uma ligação própria à Internet. Por isso, não pode
correr no namespace de rede de um gateway, onde tudo é descartado exceto o
tráfego para um único destino. Em vez disso, o fornecedor e o gateway ficam
ligados por uma rede bridge do Podman rootless, `kf-providers`, na qual cada
módulo tem um endereço fixo:

```
provider container ──── kf-providers bridge ──── gateway ──── box / browser / tool
(its own way out)                                permits only <provider-ip>:port
SOCKS5 only
```

- O **Tor** oferece SOCKS5 por si próprio. O kiwi-proxy envia uma credencial
  diferente para cada exit, e a opção `IsolateSOCKSAuth` do Tor dá então a
  cada exit o seu próprio circuito, ou seja, o seu próprio caminho pela rede
  Tor.
- A **VPN e a Mysterium** usam um túnel, e um túnel não oferece SOCKS5. Por
  isso, um pequeno adaptador, o microsocks, entra no namespace de rede do
  túnel. Oferece SOCKS5 e envia o tráfego pelo túnel.
- O **9proxy** corre o cliente do 9proxy, que abre uma porta SOCKS5 ligada a
  um exit residencial.

Um único contentor de fornecedor serve todos os exits que usam o mesmo módulo
e a mesma lease. Uma lease é um dos exits que um módulo oferece para
escolheres, por exemplo o país de um servidor VPN ou um nó da Mysterium. Se um
túnel perder a sessão, todo o tráfego fica bloqueado (fail-closed) e o túnel é
reiniciado.

## Configuração { #configuration }

O estado de cada módulo fica guardado em
`~/.local/share/kiwi-proxy/modules-state/<module>/`, fora de qualquer
repositório:

- **vpn**: o ficheiro `vpn.json` contém as definições do gluetun, como
  `VPN_SERVICE_PROVIDER`, `VPN_TYPE` e `WIREGUARD_ADDRESSES`. Todas as chaves
  em maiúsculas são passadas ao gluetun tal como estão. O ficheiro pode também
  ter uma lista `leases`. Um diretório opcional `gluetun/` guarda outros
  ficheiros, por exemplo um `wireguard.conf` para o fornecedor `custom` do
  gluetun. Há uma configuração destas por máquina, e os exits que a usam só
  diferem no país do servidor.
- **9proxy**: o ficheiro de configuração é o `config/account.conf`. O cliente
  proprietário não vem incluído. Antes de executares
  `kiwi-proxy module setup 9proxy`, coloca o cliente no diretório
  `module/containers/vendor/` do plugin e acrescenta
  `COPY vendor/ /opt/9proxy/` ao `Containerfile` do plugin. Sem o cliente, a
  imagem é construída na mesma, mas o fornecedor recusa-se a arrancar e não
  abre nenhuma porta.
- **mysterium**: executa `kiwi-proxy module config mysterium keystore=/path/to/0x….json
  --ask passphrase` ou usa *Configure…* na aplicação Kiwi Proxy. A frase-senha
  é guardada como segredo do Podman. Uma identidade só pode ter uma ligação de
  cada vez.

## Estado { #status }

O Tor não precisa de conta. O módulo da Mysterium foi verificado de ponta a
ponta a 7 de novembro de 2026. Segundo os respetivos READMEs, os módulos VPN e
9proxy estão completos e têm testes unitários, mas ainda não foram
experimentados de ponta a ponta com uma subscrição ou uma conta reais.
