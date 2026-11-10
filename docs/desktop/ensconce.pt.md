# ensconce

O ensconce configura por ti um [Bluefin-DX](https://projectbluefin.io/) acabado
de instalar, para que não tenhas de configurar cada máquina nova à mão.
Descreves o teu posto de trabalho em ficheiros de lista simples, e o ensconce
transforma a instalação nova nesse posto de trabalho. Trata dos pacotes em
camada, dos Flatpaks, das extensões do GNOME, da sincronização do Nextcloud,
de uma configuração SSH sincronizada entre as tuas máquinas, das definições do
ambiente de trabalho e do ecrã de início de sessão, e das tuas aplicações
Kiwi. Os pacotes em camada (layered packages) são pacotes RPM acrescentados
por cima da imagem do sistema. A configuração é modular, ou seja, está
dividida em passos separados que podes correr ou saltar.

- Repositório: [derlocke-ng/ensconce](https://github.com/derlocke-ng/ensconce).
  Segundo o manifesto, a licença é GPL-3.0-or-later. O README diz
  GPL-3.0.
- Última versão: **v2.5.0**. Está no [catálogo Kiwi](catalogs.md) e é
  instalada no âmbito de utilizador, ou seja, na tua pasta pessoal.

```bash
kiwi install ensconce
ensconce --init          # criar ~/.config/ensconce a partir dos exemplos
ensconce                 # correr a configuração
```

Também o podes correr a partir de um clone do repositório. Executa
`./ensconce.sh --init`, edita os ficheiros em `config/` e depois executa
`./ensconce.sh`.

## Passos { #steps }

A configuração está dividida em passos. Cada passo é um script em `steps/`, e
os passos correm por esta ordem:

| # | Passo | O que faz |
|---|---|---|
| 01 | `rebase` | muda o sistema para o Bluefin-DX |
| 02 | `ujust` | configura os grupos de utilizadores para desenvolvimento e as ferramentas de linha de comandos |
| 03 | `repos` | acrescenta repositórios RPM |
| 04 | `packages` | instala pacotes RPM em camada |
| 05 | `flatpaks` | instala aplicações Flatpak. `FLATPAK_LANGUAGES` define em que línguas são instaladas as traduções |
| 06 | `overrides` | define permissões próprias (overrides) para os Flatpaks |
| 07 | `extensions` | instala extensões do GNOME Shell |
| 08 | `cacert` | instala certificados de CA personalizados |
| 09 | `nextcloud` | prepara de antemão a sincronização de pastas do Nextcloud |
| 10 | `dconf` | aplica as definições do ambiente de trabalho GNOME |
| 11 | `gdm` | configura o ecrã de início de sessão |
| 12 | `ssh` | prepara a configuração SSH sincronizada, com o Bitwarden ou o GNOME como agente SSH |
| 13 | `kiwi` | instala o kiwi-updater da forma escolhida em `KIWI_INSTALL=recommended\|manual\|minimal` e depois todas as aplicações do `kiwi-apps.list` |
| 14 | `sysctl` | instala os ficheiros de definições do kernel que estão em `sysctl.d/`. Um ficheiro de exemplo limita a quantidade de dados por escrever que o kernel guarda em memória, o que ajuda em SSDs lentos |
| 15 | `power` | com `SYSTEM_SLEEP=off`, mascara os targets de suspensão do systemd, para que a máquina nunca entre em suspensão |

Antes de começar, o ensconce verifica o ambiente: o sistema tem de ser uma
imagem Bluefin, e o `rpm-ostree`, o `flatpak`, o `dconf`, o `jq` e o `curl`
têm de estar disponíveis. O ensconce vai guardando o progresso, por isso,
depois de um reinício, continua onde parou. Mantém a máquina acordada durante
toda a execução e, no fim, repõe as tuas definições de energia.

Estas opções controlam uma execução:

```bash
ensconce --dry-run                  # pré-visualizar sem alterar nada
ensconce --skip rebase,ujust        # saltar passos
ensconce --only extensions,dconf    # correr apenas estes
ensconce --status | --list-steps | --reset
ensconce --log [file]               # guardar o resultado
ensconce --config-dir               # mostrar o diretório de configuração ativo
```

## Configuração { #configuration }

O ensconce procura o diretório de configuração em quatro sítios e usa o
primeiro que existir. Começa por `$ENSCONCE_CONFIG`, depois
`~/.config/ensconce/`, que é o usado quando o ensconce foi instalado com o
kiwi, depois `config/` num clone e, por fim, `config.example/`. Quando acaba
por usar `config.example/`, mostra um aviso.

| Ficheiro / diretório | Para que serve |
|---|---|
| `settings.sh` | os URLs dos servidores e as opções para o SSH, o kiwi-updater, as línguas dos Flatpaks e a suspensão |
| `packages.list`, `flatpaks.list`, `extensions.list` | os pacotes, Flatpaks e extensões do GNOME a instalar, um por linha |
| `kiwi-apps.list` | as aplicações Kiwi a instalar |
| `repos.d/`, `flatpak-overrides/` | ficheiros de repositório, e permissões próprias para aplicações Flatpak individuais, no formato do próprio Flatpak |
| `nextcloud/folders.list` | as pastas a sincronizar, escritas como `localPath\|remotePath[\|tags]` |
| `nextcloud/exclude.lst`, `exclude.d/` | o que fica fora da sincronização, para todas as pastas e para pastas individuais que tenham uma etiqueta |
| `certs/` | certificados de CA (`.pem`), por exemplo o `kiwiCA.pem` da tua rede |
| `sysctl.d/` | definições do kernel |
| `dconf-settings.ini`, `gtk3-bookmarks` | definições do GNOME e marcadores do Nautilus |
| `gdm/dconf.d/`, `gdm/monitors.xml` | as definições do ecrã de início de sessão e a disposição dos monitores nele |

Uma etiqueta em `nextcloud/folders.list` dá a uma pasta exclusões próprias.
Por exemplo, a etiqueta `browser` coloca o `exclude.d/browser.lst` nessa
pasta. As bases de dados de um perfil do navegador deixam então de ser
sincronizadas, porque a sincronização as pode corromper, mas o `user.js`
continua a ser sincronizado.

## Clonar uma máquina { #cloning-a-machine }

O `--export` faz o contrário dos passos: lê o sistema em funcionamento e
escreve, a partir dele, um diretório de configuração do ensconce. Depois podes
configurar uma máquina nova com esse diretório:

```bash
ensconce --export ./my-setup        # na máquina já configurada
ensconce --init                     # na máquina nova
cp -rT ./my-setup "$(ensconce --config-dir)"
ensconce --dry-run && ensconce
```

A exportação contém apenas o que acrescentaste ao sistema. Lista os pacotes
que pediste e não a imagem inteira. Lista apenas as extensões que vêm mesmo de
extensions.gnome.org. Contém os teus próprios ficheiros de repositório e, em
vez de uma cópia completa do dconf, apenas algumas subárvores escolhidas.
Trata a exportação como um ponto de partida. `certs/` e `nextcloud/` podem
conter material privado.

O ensconce é uma aplicação de **âmbito de utilizador**. Os passos que precisam
de root pedem-no eles próprios. Para acrescentares um passo teu, cria um
ficheiro `steps/NN-<name>.sh` com uma função `step_<name>()`.
