# ensconce

Configuração pós-instalação modular para o [Bluefin-DX](https://projectbluefin.io/).
O ensconce transforma uma instalação nova do Bluefin na tua estação de trabalho
configurada, a partir de ficheiros de lista simples: pacotes em camadas,
Flatpaks, extensões GNOME, sincronização Nextcloud, uma configuração SSH
sincronizada, definições do ambiente de trabalho e do ecrã de início de sessão, e
as tuas apps Kiwi.

- Repositório: [derlocke-ng/ensconce](https://github.com/derlocke-ng/ensconce),
  GPL-3.0-or-later (segundo o seu manifesto; o README diz GPL-3.0)
- Versão mais recente: **v2.5.0**. Está no [catálogo Kiwi](catalogs.md), âmbito de utilizador.

```bash
kiwi install ensconce
ensconce --init          # cria ~/.config/ensconce a partir dos exemplos
ensconce                 # corre a configuração
```

Ou a partir de um clone: `./ensconce.sh --init`, edita `config/`, depois `./ensconce.sh`.

## Passos { #steps }

Cada fase é um script em `steps/`, corrido por ordem:

| # | Passo | Faz |
|---|---|---|
| 01 | `rebase` | muda para o Bluefin-DX |
| 02 | `ujust` | grupos de programador e ferramentas CLI |
| 03 | `repos` | acrescenta repositórios RPM |
| 04 | `packages` | sobrepõe pacotes RPM em camadas |
| 05 | `flatpaks` | instala apps Flatpak (`FLATPAK_LANGUAGES` escolhe as suas traduções) |
| 06 | `overrides` | substituições de permissões Flatpak |
| 07 | `extensions` | extensões do GNOME Shell |
| 08 | `cacert` | certificados de CA personalizados |
| 09 | `nextcloud` | pré-configura a sincronização de pastas do Nextcloud |
| 10 | `dconf` | definições do ambiente de trabalho GNOME |
| 11 | `gdm` | o ecrã de início de sessão |
| 12 | `ssh` | uma configuração SSH sincronizada, com o Bitwarden ou o GNOME como agente SSH |
| 13 | `kiwi` | instala o kiwi-updater (`KIWI_INSTALL=recommended\|manual\|minimal`) e todas as apps de `kiwi-apps.list` |
| 14 | `sysctl` | drop-ins de `sysctl.d/` (um exemplo limita o dirty writeback para SSDs lentos) |
| 15 | `power` | `SYSTEM_SLEEP=off` mascara os targets de suspensão |

O ensconce verifica primeiro o ambiente (uma imagem Bluefin, `rpm-ostree`,
`flatpak`, `dconf`, `jq`, `curl`). Guarda o seu progresso e retoma depois dos
reinícios, e mantém a máquina acordada durante toda a execução, repondo depois as
tuas definições de energia.

```bash
ensconce --dry-run                  # pré-visualiza sem alterar nada
ensconce --skip rebase,ujust        # salta passos
ensconce --only extensions,dconf    # corre só estes
ensconce --status | --list-steps | --reset
ensconce --log [file]               # guarda a saída
ensconce --config-dir               # imprime o diretório de configuração ativo
```

## Configuração { #configuration }

O diretório de configuração é o primeiro que existir de entre: `$ENSCONCE_CONFIG`,
`~/.config/ensconce/` (instalado através do kiwi), `config/` num clone e
`config.example/` (com um aviso).

| Ficheiro / diretório | Finalidade |
|---|---|
| `settings.sh` | URLs de servidores e interruptores: SSH, kiwi-updater, línguas Flatpak, suspensão |
| `packages.list`, `flatpaks.list`, `extensions.list` | um item por linha |
| `kiwi-apps.list` | as apps Kiwi a instalar |
| `repos.d/`, `flatpak-overrides/` | ficheiros de repositório; substituições por app no formato próprio do Flatpak |
| `nextcloud/folders.list` | pastas a sincronizar como `localPath\|remotePath[\|tags]` |
| `nextcloud/exclude.lst`, `exclude.d/` | exclusões de sincronização globais e por pasta (com etiqueta) |
| `certs/` | certificados de CA (`.pem`), por exemplo o `kiwiCA.pem` da tua fleet |
| `sysctl.d/` | definições do kernel |
| `dconf-settings.ini`, `gtk3-bookmarks` | definições do GNOME, marcadores do Nautilus |
| `gdm/dconf.d/`, `gdm/monitors.xml` | as definições e a disposição de ecrãs do ecrã de início de sessão |

Uma etiqueta de exclusão por pasta como `browser` coloca `exclude.d/browser.lst`
nessa pasta, o que impede que as bases de dados de um perfil de navegador sejam
sincronizadas (e corrompidas), enquanto o `user.js` continua a sincronizar.

## Clonar uma máquina { #cloning-a-machine }

`--export` lê o sistema em funcionamento e escreve uma árvore de configuração do
ensconce, o inverso dos passos:

```bash
ensconce --export ./my-setup        # na máquina configurada
ensconce --init                     # na nova
cp -rT ./my-setup "$(ensconce --config-dir)"
ensconce --dry-run && ensconce
```

Só captura o que acrescentaste: os pacotes pedidos em vez da imagem inteira, as
extensões que vêm de facto de extensions.gnome.org, os teus próprios ficheiros de
repositório, e subárvores dconf selecionadas em vez de um despejo completo.
Trata-o como um ponto de partida. `certs/` e `nextcloud/` podem conter material
privado.

O ensconce é uma app de **âmbito de utilizador**. Os passos que precisam de root
pedem-no eles próprios. Acrescenta o teu próprio passo como `steps/NN-<name>.sh`
com uma função `step_<name>()`.
