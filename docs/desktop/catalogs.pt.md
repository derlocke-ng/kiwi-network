# Catálogos e publicação de apps

## O catálogo Kiwi { #the-kiwi-catalog }

O [derlocke-ng/kiwi-catalog](https://github.com/derlocke-ng/kiwi-catalog) é o
catálogo de apps da Kiwi Network. A instalação do kiwi-updater regista-o, e
`kiwi catalog add https://github.com/derlocke-ng/kiwi-catalog.git` regista-o à
mão.

| App | Versão | Âmbitos | O que é |
|---|---|---|---|
| [kiwi-updater](kiwi-updater.md) | v2.4.0 | utilizador | o próprio atualizador |
| [kiwi-killswitch](kiwi-killswitch.md) | v0.2.3 | utilizador + sistema | kill switch de VPN fail-closed para o GNOME |
| [ensconce](ensconce.md) | v2.5.0 | utilizador | configuração pós-instalação para o Bluefin-DX |
| [kiwi-cli-tools-desktop](cli-tools.md) | v1.2.1 | utilizador | `pweb`, `select-server`, `tethering`, `torlink` |
| [kiwi-proxy](../clients/kiwi-proxy.md) | v0.7.3 | utilizador | saídas SOCKS5/VPN seladas em Podman sem root |
| [kiwi-fox](../clients/kiwi-fox.md) | v0.7.1 | utilizador | identidades de navegador isoladas em saídas do kiwi-proxy |
| [kiwi-custodia](../clients/kiwi-custodia.md) | v0.2.3 | utilizador | distro boxes cujo tráfego só sai através de uma saída |
| [kiwi-server](../server/index.md) | v2.42.0 | utilizador | construir e gerir a tua própria rede |
| [syncman](syncman.md) | v0.4.1 | utilizador | sincronização de pastas nos dois sentidos |
| [gnome-monitor](gnome-monitor.md) | v0.3.2 | utilizador | disposições de ecrãs para o GNOME |
| [kiwi-plugin-tor](../clients/providers.md) | v0.3.0 | utilizador | fornecedor do kiwi-proxy: Tor |
| [kiwi-plugin-vpn](../clients/providers.md) | v0.2.2 | utilizador | fornecedor do kiwi-proxy: uma VPN através do gluetun |
| [kiwi-plugin-9proxy](../clients/providers.md) | v0.2.0 | utilizador | fornecedor do kiwi-proxy: 9proxy |
| [kiwi-plugin-myst](../clients/providers.md) | v0.5.2 | utilizador | fornecedor do kiwi-proxy: Mysterium |

O kiwi sincroniza o catálogo antes de cada verificação e atualização, por isso
gerir uma frota de ambientes de trabalho é só git:

- **acrescentar uma app**: acrescenta o seu URL ao `apps.list` e faz commit;
- **fixar ou reverter**: junta `ref=<tag>` à sua linha (numa só máquina,
  `kiwi pin <app> <tag>` faz o mesmo);
- **removê-la**: apaga a linha (as cópias instaladas ficam até as desinstalares).

## O teu próprio catálogo { #your-own-catalog }

Um catálogo é um repositório git com um `apps.list` e, opcionalmente, um
`catalog.manifest` que o descreve:

```ini
# catalog.manifest
NAME=my-catalog
DESCRIPTION=What these apps are for
HOMEPAGE=https://…
MAINTAINER=you
```

```
# apps.list: uma linha por app, mesmo quando tem uma metade root e uma metade de utilizador
https://github.com/derlocke-ng/kiwi-updater.git
https://github.com/you/your-tool.git ref=v1.2.0
```

| Opção | Significado |
|---|---|
| `branch=<name>` | acompanhar um ramo em vez das tags de versão |
| `ref=<tag>` | fixar uma versão exata |
| `scope=user\|system` | instalar só essa metade nas máquinas que usam esta lista. É um *filtro*, não uma declaração |

A lista própria de uma máquina (`~/.config/kiwi-updater/apps.list`, ou
`/etc/kiwi-updater/apps.list` para root) prevalece sempre sobre um catálogo.
`kiwi add <url>` acrescenta-lhe uma linha.

## Publicar uma app { #publishing-an-app }

Põe um `kiwi.manifest` e um `install.sh` na raiz do teu repositório. Há modelos
em [`templates/`](https://github.com/derlocke-ng/kiwi-updater/tree/main/templates)
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

Outras chaves: `AUTHOR`, `CATEGORY`, `TAGS`, `SCREENSHOTS`, `ABOUT` (um ficheiro
que o Kiwi Apps mostra), `DEPENDS` e, para tudo o que tenha uma metade de
sistema, `ROOT_REASON`. `ICON=` é um SVG ou PNG de no máximo 1 MiB dentro do
repositório. A maioria das apps Kiwi vai buscar o seu ao
[kiwi-icons](../project/brand.md).

!!! warning "Os comentários vão numa linha própria"
    Um valor vai até ao fim da linha. `COMPONENTS=cli  # … gui …` torna o
    comentário parte do valor, e a app passa então a ser tratada como tendo uma
    GUI.

O kiwi corre o teu instalador uma vez **por âmbito declarado**, com:

| Variável | Valor |
|---|---|
| `KIWI_SCOPE` | `user` ou `system` |
| `KIWI_PREFIX` | `~/.local` ou `/usr/local` |
| `KIWI_APP_DIR` | caminho absoluto do clone |
| `KIWI_ACTION` | `install`, `update` ou `uninstall` |
| `KIWI_GUI` | `0` numa máquina sem interface gráfica, ou com `--cli-only` |
| `KIWI_PURGE` | `1` quando o utilizador pediu `--purge` |
| `PATH` | `$KIWI_PREFIX/bin` primeiro; um caminho de sistema fixo para o âmbito de sistema |

Um instalador de duplo âmbito ramifica com base em `KIWI_SCOPE` e faz só essa
metade de cada vez. Sem `--purge`, deixa a configuração do utilizador onde está.

**Lança com uma tag assinada**, para que uma metade de sistema se atualize sem
palavra-passe:

```bash
git config gpg.format ssh            # assina com a tua chave SSH
git tag -s v1.3.0 -m v1.3.0 && git push origin v1.3.0
```

O `templates/release.yml` do kiwi-updater só publica uma release no GitHub para
uma tag assinada por uma chave em `.github/allowed_signers`, e nunca cria tags
ele próprio. Depois abre um pull request que acrescente o teu URL ao catálogo.
Tudo o que seja de código aberto e realmente utilizável sem conta, sem
subscrição e sem rastreador é bem-vindo.

## Confiança { #trust }

O catálogo é **selecionado, não auditado**. Estar na lista significa que alguém
achou que valia a pena ter a app, não que o seu código tenha sido revisto. Lê
`kiwi info <app>` antes de instalares algo que ainda não conheces, e
`kiwi info --installer <app>` para veres exatamente o que vai correr.
