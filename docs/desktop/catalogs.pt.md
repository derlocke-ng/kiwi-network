# Catálogos e publicação de aplicações

Um catálogo é uma lista de aplicações que o kiwi-updater pode instalar. É um
repositório git, por isso podes lê-lo, copiá-lo e propor alterações. Esta
página descreve o catálogo Kiwi, mostra como criar um catálogo teu, por
exemplo para todos os computadores de que tratas, e explica como publicar uma
aplicação para que outras pessoas a possam instalar com o kiwi.

## O catálogo Kiwi { #the-kiwi-catalog }

O [derlocke-ng/kiwi-catalog](https://github.com/derlocke-ng/kiwi-catalog) é o
catálogo de aplicações da Kiwi Network. É registado automaticamente quando
instalas o kiwi-updater. Para o registares à mão, executa
`kiwi catalog add https://github.com/derlocke-ng/kiwi-catalog.git`.

A tabela lista as aplicações do catálogo. A coluna *Âmbitos* mostra onde cada
aplicação é instalada: `user` é o âmbito de utilizador, ou seja, a tua pasta
pessoal, e `system` é o âmbito de sistema, uma parte que pertence ao root.

| Aplicação | Versão | Âmbitos | O que é |
|---|---|---|---|
| [kiwi-updater](kiwi-updater.md) | v2.4.0 | user | o próprio atualizador |
| [kiwi-killswitch](kiwi-killswitch.md) | v0.2.3 | user + system | kill switch de VPN para o GNOME. É fail-closed: enquanto a VPN não estiver ativa, todo o tráfego fica bloqueado |
| [ensconce](ensconce.md) | v2.5.0 | user | configura um Bluefin-DX acabado de instalar |
| [kiwi-cli-tools-desktop](cli-tools.md) | v1.2.1 | user | `pweb`, `select-server`, `tethering`, `torlink` |
| [kiwi-proxy](../clients/kiwi-proxy.md) | v0.7.3 | user | exits para ligações SOCKS5 e VPN. Um exit é um contentor isolado no Podman rootless |
| [kiwi-fox](../clients/kiwi-fox.md) | v0.7.1 | user | identidades de navegador isoladas que usam exits do kiwi-proxy |
| [kiwi-custodia](../clients/kiwi-custodia.md) | v0.2.3 | user | boxes (contentores com uma distribuição Linux) cujo tráfego só passa por um exit |
| [kiwi-server](../server/index.md) | v2.42.0 | user | a ferramenta com que constróis e geres a tua própria rede |
| [syncman](syncman.md) | v0.4.1 | user | sincroniza pastas nos dois sentidos |
| [gnome-monitor](gnome-monitor.md) | v0.3.2 | user | guarda disposições dos ecrãs no GNOME e alterna entre elas |
| [kiwi-plugin-tor](../clients/providers.md) | v0.3.0 | user | módulo de fornecedor para o kiwi-proxy: Tor |
| [kiwi-plugin-vpn](../clients/providers.md) | v0.2.2 | user | módulo de fornecedor para o kiwi-proxy: uma VPN através do gluetun |
| [kiwi-plugin-9proxy](../clients/providers.md) | v0.2.0 | user | módulo de fornecedor para o kiwi-proxy: 9proxy |
| [kiwi-plugin-myst](../clients/providers.md) | v0.5.2 | user | módulo de fornecedor para o kiwi-proxy: Mysterium |

O kiwi descarrega a versão atual do catálogo antes de cada verificação e de
cada atualização. Por isso, consegues gerir as aplicações de vários
computadores apenas com o git:

- **Para acrescentar uma aplicação**, junta o URL dela ao `apps.list` e faz
  commit.
- **Para fixar uma aplicação numa versão ou para a reverter**, acrescenta
  `ref=<tag>` à linha dela. Numa única máquina, `kiwi pin <app> <tag>` faz o
  mesmo.
- **Para remover uma aplicação**, apaga a linha dela. As cópias já instaladas
  continuam instaladas até as desinstalares.

## O teu próprio catálogo { #your-own-catalog }

Um catálogo é um repositório git com um ficheiro `apps.list`. Pode também ter
um ficheiro `catalog.manifest`, onde o catálogo se descreve a si próprio:

```ini
# catalog.manifest
NAME=my-catalog
DESCRIPTION=What these apps are for
HOMEPAGE=https://…
MAINTAINER=you
```

```
# apps.list: uma linha por aplicação, mesmo quando tem uma metade root e uma metade de utilizador
https://github.com/derlocke-ng/kiwi-updater.git
https://github.com/you/your-tool.git ref=v1.2.0
```

Uma linha do `apps.list` pode ter estas opções a seguir ao URL:

| Opção | Significado |
|---|---|
| `branch=<name>` | seguir um ramo em vez das tags de versão |
| `ref=<tag>` | ficar exatamente nesta versão |
| `scope=user\|system` | instalar apenas essa metade da aplicação nas máquinas que usam esta lista. Esta opção é um *filtro*. Não declara que âmbitos a aplicação tem |

Cada máquina tem também uma lista própria: `~/.config/kiwi-updater/apps.list`
para o teu utilizador e `/etc/kiwi-updater/apps.list` para o root. Uma
entrada na lista da própria máquina tem sempre prioridade sobre um catálogo.
`kiwi add <url>` acrescenta uma linha a esta lista.

## Publicar uma aplicação { #publishing-an-app }

Para publicares uma aplicação, coloca um ficheiro `kiwi.manifest` e um script
`install.sh` no diretório de topo do teu repositório. Há modelos no diretório
[`templates/`](https://github.com/derlocke-ng/kiwi-updater/tree/main/templates)
do kiwi-updater.

```ini
NAME=my-tool
DESCRIPTION=Short description
# COMPONENTS: cli gui daemon service gnome-extension config module
COMPONENTS=cli
# SCOPES: user, system ou ambos
SCOPES=user
VERSION=0.1.0
HOMEPAGE=https://…
LICENSE=GPL-3.0-or-later
ICON=data/my-tool.svg
INSTALLER=install.sh
```

Um manifesto pode ter mais chaves: `AUTHOR`, `CATEGORY`, `TAGS`,
`SCREENSHOTS`, `ABOUT` (um ficheiro que a Kiwi Apps mostra), `DEPENDS` e
`ROOT_REASON`. Todas as aplicações com uma metade de sistema precisam de
`ROOT_REASON`. `ICON=` indica um ficheiro SVG ou PNG dentro do repositório,
com 1 MiB no máximo. A maioria das aplicações Kiwi vai buscar o ícone ao
[kiwi-icons](../project/brand.md).

!!! warning "Põe os comentários numa linha à parte"
    Um valor vai até ao fim da linha. Se escreveres
    `COMPONENTS=cli  # … gui …`, o comentário passa a fazer parte do valor, e
    o kiwi trata a aplicação como se ela tivesse uma interface gráfica.

O kiwi corre o teu instalador uma vez **para cada âmbito que a aplicação
declara**, e define para ele estas variáveis:

| Variável | Valor |
|---|---|
| `KIWI_SCOPE` | `user` ou `system` |
| `KIWI_PREFIX` | `~/.local` ou `/usr/local` |
| `KIWI_APP_DIR` | caminho absoluto do clone |
| `KIWI_ACTION` | `install`, `update` ou `uninstall` |
| `KIWI_GUI` | `0` numa máquina headless (sem ambiente gráfico) ou com `--cli-only` |
| `KIWI_PURGE` | `1` quando o utilizador pediu `--purge` |
| `PATH` | `$KIWI_PREFIX/bin` vem primeiro. O âmbito de sistema recebe um caminho de sistema fixo |

O instalador de uma aplicação com os dois âmbitos tem de verificar
`KIWI_SCOPE` e, em cada execução, fazer apenas o trabalho dessa metade. Se o
utilizador não pediu `--purge`, deixa a configuração dele onde está.

**Publica cada versão como uma tag assinada.** Só assim é possível atualizar
uma metade de sistema sem palavra-passe:

```bash
git config gpg.format ssh            # assinar com a tua chave SSH
git tag -s v1.3.0 -m v1.3.0 && git push origin v1.3.0
```

O kiwi-updater inclui um workflow de publicação, `templates/release.yml`. Este
workflow só publica uma versão no GitHub para uma tag assinada com uma chave
que conste de `.github/allowed_signers`, e nunca cria tags. Por fim, abre um
pull request que acrescente o teu URL ao catálogo. É bem-vinda qualquer
aplicação de código aberto que possa mesmo ser usada sem conta, sem
subscrição e sem rastreamento.

## Confiança { #trust }

O catálogo é **selecionado, mas não auditado**. Uma aplicação está na lista
porque alguém achou que valia a pena tê-la, não porque o código dela tenha
sido revisto. Antes de instalares uma aplicação que não conheces, lê o que
`kiwi info <app>` mostra. Executa `kiwi info --installer <app>` para veres
exatamente o que vai correr.
