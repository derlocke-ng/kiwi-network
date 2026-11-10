# kiwi-proxy

Saídas SOCKS5 e VPN seladas em Podman sem root, para navegadores, ferramentas de
teste, aplicações do anfitrião e máquinas kiwi-server.

- Repositório: [derlocke-ng/kiwi-proxy](https://github.com/derlocke-ng/kiwi-proxy), GPL-3.0-or-later
- Versão mais recente: **v0.7.3**. Está no [catálogo Kiwi](../desktop/catalogs.md), âmbito de utilizador.
- Uma CLI (`kiwi-proxy`), uma app GTK4 (**Kiwi Proxy**) e unidades de utilizador
  systemd. É o motor de proxy que antes vivia no kiwi-fox, separado para servir
  mais do que uma app.

Uma **saída** é um upstream, com nome: um SOCKS5 que te deram, ou um que um
[módulo de fornecedor](providers.md) produz (Tor, um túnel VPN, 9proxy,
Mysterium). Uma saída são apenas dados. Ativá-la cria um **gateway**:

```
gateway container   owns the network namespace
                    nftables: default drop, one permitted destination
                    forwarder 127.0.0.1:1080: adds the upstream's credentials
                    dnscrypt-proxy 127.0.0.2:53: DNS through the same exit, with blocklists
```

O que quer que se junte ao namespace do gateway (um navegador kiwi-fox, uma box
kiwi-custodia, um contentor de ferramentas) não tem outra rota senão esse
upstream. Se o gateway morrer, os seus membros perdem a rota.

## Instalar { #install }

```bash
kiwi install kiwi-proxy      # o kiwi-fox e o kiwi-custodia trazem-no consigo
kiwi-proxy setup             # a imagem do gateway, dados DNS, imagens dos módulos de fornecedor
```

Precisa de Podman sem root, Python 3.12+ com pydantic, e GTK4 + libadwaita para a
app. As palavras-passe vão para o porta-chaves do ambiente de trabalho
(`secret-tool`), ou para ficheiros 0600 numa máquina que não o tenha.

## Usar { #use }

```bash
kiwi-proxy add client-a socks5://user:pass@host:1080   # uma saída; ainda nada corre
kiwi-proxy add tor-de --module tor --country de        # uma saída a partir de um módulo de fornecedor
kiwi-proxy list
kiwi-proxy check client-a      # o que o mundo vê através dela
kiwi-proxy up client-a         # ativa o seu gateway e mantém-no ativo
kiwi-proxy down client-a       # desativa-o, com quem se lhe juntou
kiwi-proxy ps                  # gateways ativos, seja qual for a app que os iniciou
kiwi-proxy reap                # desativa gateways que ninguém usa
kiwi-proxy-gui                 # "Kiwi Proxy" na grelha de aplicações
```

Os endpoints são `socks5://user:pass@host:port`, `http://…`, `https://…`, ou o
formato de fornecedor `host:port:user:pass`. `kiwi-proxy test ENDPOINT` testa um
sem criar nada.

### Saídas para aplicações do anfitrião { #exits-for-host-applications }

Qualquer programa no anfitrião pode usar uma saída através de uma porta SOCKS5
publicada, uma porta por saída:

```bash
kiwi-proxy add se socks5://10.64.0.1:1080 --expose 1081
kiwi-proxy add nl socks5://10.65.0.1:1080 --expose 1082
kiwi-proxy up se && kiwi-proxy up nl
curl --proxy socks5h://127.0.0.1:1082 https://ifconfig.co/json
```

Por omissão, a porta escuta em `127.0.0.1`. Outro endereço precisa de um nome de
utilizador (`--expose-user`) ou de um `--expose-open` explícito.
`systemctl --user enable --now kiwi-proxy@NAME` mantém uma saída ativa desde o
início de sessão.

### DNS { #dns }

- **Modo resolvedor** (o valor por omissão): o dnscrypt-proxy resolve por DoH
  através da saída (Google, Cloudflare, Quad9 ou Mullvad como upstream), com
  listas de bloqueio (OISD) atualizadas diariamente.
- **Modo remoto** (`--dns remote`): os nomes vão para o próprio upstream, para o
  Tor e para nomes `.onion`. As listas de bloqueio continuam a aplicar-se.

### Regras do gateway { #rules-of-the-gateway }

- O UDP não sai para lado nenhum: sem QUIC, sem multimédia WebRTC, sem DNS em
  texto simples.
- Para o mundo, uma saída é IPv4. Um nome sem endereço IPv4 é recusado.
- Um gateway que um consumidor ativou desaparece quando o seu último membro sai.
  Um ativado com `kiwi-proxy up` fica até `kiwi-proxy down`.
- Uma saída, um gateway, qualquer número de membros. Os membros que têm de ficar
  separados usam saídas diferentes.

## A app { #the-app }

O **Kiwi Proxy** acrescenta e edita saídas (um SOCKS5 que te deram, ou um módulo
de fornecedor, com uma lista de países pesquisável ou um seletor de nós), ativa-as
e desativa-as, oferece uma como porta SOCKS5 neste computador e copia o seu
endereço, verifica o que o mundo vê, mostra quem se juntou a um gateway e os
respetivos registos, e instala e configura módulos de fornecedor.

## Numa máquina kiwi-server { #on-a-kiwi-server-machine }

O kiwi-proxy traz também um módulo kiwi-server que aloja saídas para toda a malha
(um gateway por saída, publicado no endereço de malha do anfitrião). Ainda não
está na árvore do kiwi-server e ainda não correu numa máquina, como diz a sua
documentação. Os módulos de fornecedor são um mecanismo do ambiente de trabalho e
não correm aí.

Para ler mais: [arquitetura](https://github.com/derlocke-ng/kiwi-proxy/blob/main/docs/architecture.md),
[consumidores](https://github.com/derlocke-ng/kiwi-proxy/blob/main/docs/consumers.md),
[sistema de plugins](https://github.com/derlocke-ng/kiwi-proxy/blob/main/docs/plugin-system.md).
