# kiwi-updater

O `kiwi` instala e atualiza apps de código aberto a partir de **catálogos git** no
Fedora Silverblue, no Bluefin e noutros sistemas ostree. Uma app é um repositório
git com um `kiwi.manifest` e um `install.sh`. O kiwi clona-o, faz checkout da sua
tag de versão mais recente, corre o seu instalador e mantém-no atualizado em
segundo plano, a ele próprio incluído.

Não há contas, nem loja, nem fornecedor. Um catálogo é um repositório que podes
ler, fazer fork e para o qual podes enviar um pull request.

- Repositório: [derlocke-ng/kiwi-updater](https://github.com/derlocke-ng/kiwi-updater), GPL-3.0-or-later
- Versão mais recente: **v2.4.0**, uma versão de segurança
- O **`kiwi`** é a CLI. Precisa de `git`, coreutils, `util-linux` e `awk`, todos
  na imagem base, mais `ssh-keygen` para as verificações de assinaturas.
- O **Kiwi Apps** (`kiwi-gui`) é a app GTK4: pesquisa, filtros, uma vista de
  detalhe por app com o seu ícone, capturas de ecrã e dependências. Mostra o
  instalador e o diff de uma atualização antes de correr qualquer um deles, e põe
  os teus cliques em fila. Os seus dados vêm da CLI; os ícones e as capturas de
  ecrã são lidos dos clones das apps, por isso nada é descarregado para eles.

## Instalar { #install }

```bash
# recomendado: âmbito de utilizador mais o âmbito de sistema pertencente a root, um só pedido de palavra-passe
curl -fsSL https://raw.githubusercontent.com/derlocke-ng/kiwi-updater/main/get-kiwi.sh | bash

# mínimo: 100 % ao nível do utilizador, só ~/.local, sem root e sem palavra-passe, nunca
curl -fsSL https://raw.githubusercontent.com/derlocke-ng/kiwi-updater/main/get-kiwi.sh | bash -s -- --minimal

# nenhuma ação sem palavra-passe: cada alteração ao sistema pede uma palavra-passe
curl -fsSL https://raw.githubusercontent.com/derlocke-ng/kiwi-updater/main/get-kiwi.sh | bash -s -- --with-system=manual
```

O [catálogo Kiwi](catalogs.md) é registado pela instalação. Vai diretamente para
`kiwi list` ou abre o **Kiwi Apps**.

As apps que são apenas ficheiros na tua pasta pessoal (as ferramentas CLI, o
ensconce, o syncman) ficam completas com a instalação mínima. Uma app com uma
metade root, como o kiwi-killswitch, precisa do âmbito de sistema. Numa
instalação mínima, `kiwi install kiwi-killswitch` configura-o na hora com uma
palavra-passe.

## Comandos { #commands }

```bash
kiwi list [--check]          # todas as apps que esta máquina conhece
kiwi search vpn              # encontra uma app em todos os catálogos registados
kiwi info kiwi-killswitch    # o que é, o que instala, se precisa de root
kiwi install <app>           # um nome, ou um --all explícito
kiwi update [<app>]          # tudo o que tiver uma versão nova
kiwi uninstall <app>         # --purge também apaga a sua configuração
kiwi check                   # sai com 10 se alguma coisa tiver uma atualização

kiwi add <https-url>         # acompanha um repositório diretamente, sem catálogo
kiwi catalog add|list|remove # gere catálogos
kiwi sync                    # atualiza os catálogos agora
kiwi self-update
kiwi trust --system <app>    # esquece a chave de assinatura fixada para uma app de sistema
```

Antes de correres alguma coisa, e quando algo corre mal:

```bash
kiwi info --installer <app>  # o script que uma instalação correria, antes de correr
kiwi diff <app>              # o que uma atualização mudaria, incluindo o seu instalador
kiwi pin <app> v1.2.0        # fica nessa; kiwi unpin <app> para voltar a seguir as versões
kiwi install <app> --dry-run # âmbito, URL, ref, caminho do instalador, e mais nada
kiwi doctor                  # bloqueios obsoletos, versões desalinhadas, ficheiros de lista errados, temporizadores
```

## As versões são tags { #releases-are-tags }

Uma app segue a sua **tag de versão** mais recente, uma que corresponda a
`^v?[0-9]+(\.[0-9]+){0,3}$` (`v1`, `v1.2`, `1.2.3`, `v1.2.3.4`). As pré-versões
e as tags de rascunho nunca passam à frente de uma versão. Um repositório sem tag
de versão segue o seu ramo por omissão. `ref=<tag>` numa linha de lista pede uma
específica.

## Dependências { #dependencies }

`DEPENDS=` num manifesto indica o que uma app precisa. Uma palavra que seja uma
app no teu próprio catálogo ou lista é instalada **primeiro**, no mesmo âmbito, no
momento da instalação. `kiwi install kiwi-plugin-tor`, por exemplo, traz consigo
o kiwi-proxy. Qualquer outra palavra é um programa, verificado com `command -v`.

## Uma app, duas metades { #one-app-two-halves }

Algumas apps são só um binário em `~/.local/bin`. Outras, como um kill switch de
VPN, são um daemon root **e** uma app de ambiente de trabalho **e** uma extensão
GNOME. As metades instalam-se com privilégios diferentes, porque **o root nunca
pode executar um ficheiro em que o utilizador possa escrever**. A app declara-o:

```ini
COMPONENTS=daemon cli gui gnome-extension
SCOPES=user system
ROOT_REASON=installs a root firewall daemon, its D-Bus policy and two systemd units
```

Um catálogo lista essa app uma vez, e o kiwi instala cada metade corretamente.
Antes de pedir a tua palavra-passe, mostra o `ROOT_REASON`.

| Peça | Onde | Porquê |
|---|---|---|
| `kiwi`, Kiwi Apps, apps de utilizador | `~/.local` | não precisa de root; sobrevive a um rebase ostree |
| a cópia do kiwi do próprio root | `/usr/local/bin`, clonada para `/var/lib/kiwi-updater/repos/` | o root nunca corre um ficheiro em que possas escrever |
| apps de sistema | `/var/lib`, `/etc` | graváveis no ostree, pertencentes a root |
| listas | `~/.config/kiwi-updater/apps.list`, `/etc/kiwi-updater/apps.list` | as entradas próprias de uma máquina prevalecem sobre qualquer catálogo |
| chaves de assinatura fixadas | `/etc/kiwi-updater/signers/<app>` | ver abaixo |

O `/usr` imutável nunca é tocado.

## Root, palavras-passe e assinaturas { #root-passwords-and-signatures }

| | Precisa de root | Pede palavra-passe |
|---|---|---|
| tudo no âmbito de utilizador | não | não |
| **atualizar** uma app de sistema | sim | **não**, para uma versão assinada pela chave que o root fixou para essa app. **Sim** para uma versão não assinada, e sempre no modo `manual` |
| **instalar** ou **desinstalar** uma app de sistema | sim | sim |

Desde a 2.4.0:

- **Versões assinadas.** O root fixa uma chave de assinatura SSH por app de
  sistema, a primeira que vê (confiança no primeiro uso). Uma tag de versão
  assinada por essa chave atualiza sem palavra-passe. Uma versão não assinada
  pede uma e diz que não a conseguiu verificar. Uma tag assinada por outra chave,
  ou uma tag não assinada depois de tags assinadas, é recusada até correres
  `kiwi trust --system <app>`. Isto aplica-se ao âmbito de sistema.
- **O root só instala a partir de fontes que lista**: `/etc/kiwi-updater/apps.list`
  e os catálogos registados para root. Para tudo o resto, o kiwi instala a metade
  de utilizador e indica o `kiwi add --system <https-url>` a correr. O Kiwi Apps
  oferece *Register and Install*.
- **Só https.** As fontes `http://` são recusadas em todo o lado.

As atualizações de sistema sem palavra-passe passam por um único auxiliar de
finalidade fixa, `/usr/local/libexec/kiwi-system-update`. Uma regra polkit
permite-o para sessões `wheel` ativas, e ele só aceita nomes de apps como uma
seleção das listas do próprio root.

## Atualizações em segundo plano { #background-updates }

Há um só temporizador, e é teu: `kiwi-updater.timer` corre `kiwi update --all`
seis horas depois da última execução (dez minutos depois do arranque, com algum
atraso aleatório). Atualiza diretamente as metades de utilizador, e as metades de
sistema através do auxiliar acima. Não há temporizador de root. No modo `manual`,
as metades de sistema esperam pelo teu próximo `kiwi update` interativo.

## Confiança { #trust }

Instalar uma app **corre o `install.sh` desse repositório**, e uma app que declara
o âmbito de sistema corre-o **como root**. Os catálogos são selecionados, não
auditados. Acrescenta aqueles em que confias, como acrescentarias um repositório
de pacotes, e usa `kiwi info --installer`, `kiwi diff` e `kiwi pin` para decidir
de olhos abertos. Uma assinatura restringe *quem pode publicar*. Não diz nada
sobre *o que faz aquilo que foi publicado*.

Ainda planeado: um registo alojado de catálogos de confiança
(`kiwi catalog browse`) com as impressões digitais dos signatários por entrada.
