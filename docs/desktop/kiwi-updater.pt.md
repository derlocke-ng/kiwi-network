# kiwi-updater

O kiwi-updater instala aplicações de código aberto no teu computador e
mantém-nas atualizadas. O comando chama-se `kiwi`. Vai buscar as aplicações a
**catálogos git** e funciona no Fedora Silverblue, no Bluefin e noutros
sistemas ostree. Um catálogo é um repositório git com uma lista de
aplicações. Uma aplicação é um repositório git com um ficheiro `kiwi.manifest`
e um script `install.sh`. O kiwi clona o repositório da aplicação, faz
checkout da tag de versão mais recente e corre o instalador. A partir daí,
atualiza a aplicação em segundo plano, e atualiza-se a si próprio da mesma
forma.

Não precisas de conta, e não há loja de aplicações nem empresa por trás. Um
catálogo é um repositório que podes ler, de que podes fazer fork e para o qual
podes enviar pull requests.

- Repositório: [derlocke-ng/kiwi-updater](https://github.com/derlocke-ng/kiwi-updater), GPL-3.0-or-later
- Última versão: **v2.4.0**, uma versão de segurança
- **`kiwi`** é a ferramenta de linha de comandos (CLI). Precisa do `git`, do
  coreutils, do `util-linux` e do `awk`, que fazem todos parte da imagem
  base. Para verificar assinaturas, precisa também do `ssh-keygen`.
- **Kiwi Apps** (`kiwi-gui`) é a aplicação gráfica, feita com GTK4. Podes
  pesquisar e filtrar as aplicações, e cada uma tem uma página de detalhes com
  o ícone, capturas de ecrã e dependências. Antes de instalar uma aplicação, a
  Kiwi Apps mostra-te o instalador, e antes de a atualizar mostra-te o que a
  atualização muda. Se clicares em várias ações seguidas, ela põe-nas numa
  fila. Os dados vêm da CLI. Os ícones e as capturas de ecrã são lidos dos
  clones locais das aplicações, por isso a Kiwi Apps não descarrega nada para
  os mostrar.

## Instalação { #install }

O kiwi trabalha com dois âmbitos. O âmbito de utilizador é tudo o que está na
tua pasta pessoal e nunca precisa de root. O âmbito de sistema é uma parte que
pertence ao root, para as aplicações que precisam de root. Ao instalar,
escolhes quanto do âmbito de sistema queres:

```bash
# recomendado: âmbito de utilizador mais o âmbito de sistema do root, um único pedido de palavra-passe
curl -fsSL https://raw.githubusercontent.com/derlocke-ng/kiwi-updater/main/get-kiwi.sh | bash

# mínimo: 100% ao nível do utilizador, só ~/.local, sem root e sem palavra-passe, nunca
curl -fsSL https://raw.githubusercontent.com/derlocke-ng/kiwi-updater/main/get-kiwi.sh | bash -s -- --minimal

# nenhuma ação sem palavra-passe: cada alteração ao sistema pede a palavra-passe
curl -fsSL https://raw.githubusercontent.com/derlocke-ng/kiwi-updater/main/get-kiwi.sh | bash -s -- --with-system=manual
```

A instalação regista o [catálogo Kiwi](catalogs.md), por isso podes executar
`kiwi list` ou abrir a **Kiwi Apps** de imediato.

Algumas aplicações são apenas ficheiros na tua pasta pessoal, por exemplo as
ferramentas de linha de comandos, o ensconce e o syncman. Estas aplicações
ficam completas com a instalação mínima. Uma aplicação com uma metade que
corre como root, como o kiwi-killswitch, precisa do âmbito de sistema. Numa
instalação mínima, `kiwi install kiwi-killswitch` prepara o âmbito de sistema
nesse momento e pede a tua palavra-passe uma vez.

## Comandos { #commands }

```bash
kiwi list [--check]          # todas as aplicações que esta máquina conhece
kiwi search vpn              # procurar uma aplicação em todos os catálogos registados
kiwi info kiwi-killswitch    # o que é, o que instala, se precisa de root
kiwi install <app>           # um nome, ou --all explícito
kiwi update [<app>]          # tudo o que tiver uma versão nova
kiwi uninstall <app>         # --purge apaga também a configuração
kiwi check                   # código de saída 10 se houver alguma atualização

kiwi add <https-url>         # seguir um repositório diretamente, sem catálogo
kiwi catalog add|list|remove # gerir catálogos
kiwi sync                    # atualizar os catálogos agora
kiwi self-update
kiwi trust --system <app>    # esquecer a chave de assinatura fixada para uma aplicação de sistema
```

Os comandos seguintes mostram-te o que uma aplicação vai fazer antes de a
executares, e ajudam quando alguma coisa corre mal:

```bash
kiwi info --installer <app>  # o script que uma instalação correria, antes de o correr
kiwi diff <app>              # o que uma atualização mudaria, incluindo o instalador
kiwi pin <app> v1.2.0        # ficar nesta versão; kiwi unpin <app> para voltar a seguir as versões
kiwi install <app> --dry-run # âmbito, URL, ref, caminho do instalador, e mais nada
kiwi doctor                  # locks esquecidos, versões desencontradas, listas com erros, temporizadores
```

## As versões são tags { #releases-are-tags }

O kiwi usa as tags do git como versões. Uma aplicação segue a sua **tag de
versão** mais recente. Uma tag de versão é uma tag que corresponde a
`^v?[0-9]+(\.[0-9]+){0,3}$`, por exemplo `v1`, `v1.2`, `1.2.3` ou `v1.2.3.4`.
As tags de pré-versão e as tags temporárias não correspondem, por isso nunca
são usadas no lugar de uma versão. Um repositório sem tags de versão segue o
seu ramo predefinido. Para pedires uma versão específica, acrescenta
`ref=<tag>` à linha da aplicação numa lista.

## Dependências { #dependencies }

A linha `DEPENDS=` de um manifesto indica aquilo de que uma aplicação precisa.
Se uma palavra dessa linha for o nome de uma aplicação do teu catálogo ou da
tua lista, o kiwi instala essa aplicação **primeiro**, no mesmo âmbito, no
momento em que instalas a aplicação que precisa dela. Por exemplo,
`kiwi install kiwi-plugin-tor` instala também o kiwi-proxy. Qualquer outra
palavra é tratada como o nome de um programa, e o kiwi verifica com
`command -v` se esse programa existe.

## Uma aplicação, duas metades { #one-app-two-halves }

Algumas aplicações são apenas um programa em `~/.local/bin`. Outras, como um
kill switch de VPN, são compostas por um daemon que corre como root, **mais**
uma aplicação gráfica **mais** uma extensão do GNOME. Uma aplicação destas tem
duas metades, uma de utilizador e uma de sistema, e as duas são instaladas
com privilégios diferentes. A razão é que **o root nunca pode executar um
ficheiro em que o utilizador possa escrever**. A aplicação declara as suas
partes e os seus âmbitos no manifesto:

```ini
COMPONENTS=daemon cli gui gnome-extension
SCOPES=user system
ROOT_REASON=installs a root firewall daemon, its D-Bus policy and two systemd units
```

Um catálogo lista uma aplicação destas uma única vez, e o kiwi instala cada
metade no âmbito certo. Antes de te pedir a palavra-passe, o kiwi mostra-te o
`ROOT_REASON`.

| Parte | Onde | Porquê |
|---|---|---|
| `kiwi`, Kiwi Apps, aplicações de utilizador | `~/.local` | não precisa de root e mantém-se quando o sistema muda (rebase) para outra imagem ostree |
| a cópia do kiwi que pertence ao root | `/usr/local/bin`, clonada em `/var/lib/kiwi-updater/repos/` | o root nunca corre um ficheiro em que tu possas escrever |
| aplicações de sistema | `/var/lib`, `/etc` | nos sistemas ostree, estes diretórios podem ser escritos e pertencem ao root |
| listas | `~/.config/kiwi-updater/apps.list`, `/etc/kiwi-updater/apps.list` | as entradas da lista da própria máquina têm prioridade sobre qualquer catálogo |
| chaves de assinatura fixadas | `/etc/kiwi-updater/signers/<app>` | vê a secção seguinte |

O kiwi nunca altera nada no `/usr` imutável.

## Root, palavras-passe e assinaturas { #root-passwords-and-signatures }

A tabela mostra que ações precisam de root e quais pedem palavra-passe.

| | Precisa de root | Pede palavra-passe |
|---|---|---|
| qualquer coisa no âmbito de utilizador | não | não |
| **atualizar** uma aplicação de sistema | sim | **não**, se a versão estiver assinada com a chave que o root fixou para essa aplicação. **Sim**, se a versão não estiver assinada, e sempre no modo `manual` |
| **instalar** ou **desinstalar** uma aplicação de sistema | sim | sim |

Desde a versão 2.4.0, aplicam-se estas regras:

- **Versões assinadas.** Para cada aplicação de sistema, o root fixa uma
  chave de assinatura SSH. Fixar uma chave significa memorizá-la e, a partir
  daí, aceitar apenas essa chave. O root fixa a primeira chave que vê para a
  aplicação, o que se chama confiança no primeiro uso (trust on first use).
  Se uma tag de versão estiver assinada com a chave fixada, a atualização é
  instalada sem palavra-passe. Se uma versão não estiver assinada, o kiwi
  pede a tua palavra-passe e avisa que não a conseguiu verificar. O kiwi
  recusa uma tag assinada com outra chave, e recusa uma tag sem assinatura
  quando as anteriores estavam assinadas. Continua a recusá-las até
  executares `kiwi trust --system <app>`. Estas regras aplicam-se ao âmbito
  de sistema.
- **O root só instala a partir das fontes que ele próprio tem nas suas
  listas.** Essas fontes são o `/etc/kiwi-updater/apps.list` e os catálogos
  registados para o root. Se uma aplicação vier de outra fonte, o kiwi
  instala apenas a metade de utilizador e indica-te o comando
  `kiwi add --system <https-url>` que tens de executar. Nesse caso, a Kiwi
  Apps oferece a opção *Register and Install* (registar e instalar).
- **Só https.** O kiwi recusa fontes `http://` em todo o lado.

As atualizações de sistema sem palavra-passe são feitas por um único programa
auxiliar, `/usr/local/libexec/kiwi-system-update`, que só serve para isso. Uma
regra do polkit permite aos utilizadores do grupo `wheel` executá-lo quando a
sessão deles está ativa. O programa auxiliar só aceita nomes de aplicações, e
um nome só pode selecionar uma aplicação das listas do próprio root.

## Atualizações em segundo plano { #background-updates }

Há um único temporizador (timer) do systemd para as atualizações em segundo
plano, e é um temporizador de utilizador: corre como o teu utilizador e não
como root. O `kiwi-updater.timer` executa `kiwi update --all` seis horas
depois da última execução e dez minutos depois do arranque, com um pequeno
atraso aleatório. Esta execução atualiza diretamente as metades de utilizador
e atualiza as metades de sistema através do programa auxiliar descrito acima.
Não há nenhum temporizador do root. No modo `manual`, o temporizador não
atualiza as metades de sistema. Essas ficam à espera até executares tu
próprio `kiwi update`.

## Confiança { #trust }

Quando instalas uma aplicação, o kiwi **corre o `install.sh` do repositório
dessa aplicação**. Se a aplicação declarar o âmbito de sistema, o kiwi corre
este script **como root**. Os catálogos são selecionados, mas não auditados.
Isto quer dizer que alguém escolheu as aplicações, não que o código delas
tenha sido revisto. Acrescenta apenas catálogos em que confias, tal como
farias com um repositório de pacotes. Usa `kiwi info --installer`, `kiwi diff`
e `kiwi pin` para veres o que uma aplicação faz antes de decidires. Uma
assinatura limita *quem pode publicar* uma versão. Não diz nada sobre *o que
essa versão faz*.

Há uma coisa ainda planeada: um registo alojado de catálogos de confiança, com
o comando `kiwi catalog browse` e com as impressões digitais dos signatários
de cada entrada.
