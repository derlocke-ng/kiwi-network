# kiwi-server

O kiwi-server é a ferramenta com que crias e geres uma Kiwi Network. Descreves
todas as máquinas num único ficheiro, `fleet.yaml`, e o kiwi-server prepara-as
a partir dele, para que não tenhas de instalar e configurar cada uma à mão.

Para cada máquina, o kiwi-server gera uma **ISO de instalação automática**: uma
imagem de instalação que instala o Fedora CoreOS, o uCore ou o Debian sem fazer
perguntas e que, no fim, desliga a máquina. Depois, o kiwi-server **aplica** a
função da máquina por SSH, e é isso que a torna num `kiwi-master` ou num
`kiwi-node`. A partir daí, continua a tratar de todas as tuas máquinas:
adiciona clientes WireGuard, lê o estado de cada máquina, guarda os segredos
(palavras-passe e chaves), faz backup do ficheiro fleet e desbloqueia discos
cifrados.

O kiwi-server existe como ferramenta de linha de comandos (CLI), `kiwi-server`,
e como aplicação GTK4, **Kiwi Server**. Ambas são instaladas em `~/.local` e
não precisam de permissões de root.

- Repositório: [derlocke-ng/kiwi-server](https://github.com/derlocke-ng/kiwi-server), GPL-3.0-or-later
- Última versão: **v2.42.0**. Está disponível no [catálogo Kiwi](../desktop/catalogs.md).
- O kiwi-server assenta no [kiwi-modules](single.md) v0.23.0, que contém os
  módulos e o programa que gera a partir deles a configuração de cada máquina, e
  no [kiwi-stack](single.md) v0.5.0, que é a parte que corre em cada máquina. O
  kiwi-server traz uma cópia de cada um (vendored), fixada numa tag.

```
fleet.yaml + secrets/
   │  kiwi-server: merge defaults, work out DNS records, the master's mesh address,
   │  LAN neighbours, and a certificate from the fleet CA per host
   ▼
kiwi-modules renders each host's stack  →  compose file, podman quadlets, configs, units
   │
   ├─ build ─▶ <host>.iso      base system only: hostname, network, admin user, updates;
   │                            installs to the named disk WITHOUT ASKING, then powers off
   └─ apply ─▶ over SSH        role script + stack → kiwi-stack starts and verifies it
```

## Instalação { #install }

```bash
kiwi install kiwi-server        # com o kiwi-updater
```

Também o podes instalar a partir de um clone do repositório: executa
`./install.sh install` e depois `kiwi-server doctor`.

O kiwi-server precisa do Python 3.9 ou mais recente, com o PyYAML e o Jinja2, e
dos programas `openssl` e `ssh`. O cofre de segredos precisa do `age`. Para
gerar ISOs precisas do `butane`, do `coreos-installer` e do `xorriso` e, para o
Debian, também do `cpio`, do `gzip` e do `curl`. No Silverblue ou no Bluefin,
não acrescentes estes pacotes ao sistema base (layering). Em vez disso, constrói
as ferramentas das ISOs como uma única imagem de contentor:

```bash
kiwi-server toolchain build     # usada automaticamente quando faltam as ferramentas
```

O `qrencode` (para `enroll --qr`), o `shellcheck` e o `docker compose` são
opcionais.

## Do zero a uma rede a funcionar { #from-nothing-to-a-running-network }

Os comandos abaixo levam-te de uma pasta vazia até uma rede a funcionar, com um
master, um node e os teus próprios dispositivos:

```bash
kiwi-server init                          # um fleet.yaml com comentários
$EDITOR fleet.yaml                        # máquinas, funções, a tua chave SSH, o disco de instalação
kiwi-server secrets init fleet.yaml       # opcional: secrets/ num único cofre cifrado com age
kiwi-server validate fleet.yaml

# o master
kiwi-server build fleet.yaml sorbet         # → output/sorbet/sorbet.iso
#   arranca a máquina com a ISO; ela instala-se e desliga-se; volta a ligá-la
kiwi-server apply fleet.yaml sorbet --ssh core@203.0.113.5

# cada node: primeiro o cliente WireGuard, depois a ISO, depois a função
kiwi-server enroll fleet.yaml papaya         # → secrets/papaya.home.conf
kiwi-server build fleet.yaml papaya
kiwi-server apply fleet.yaml papaya --ssh core@192.168.1.25

# os teus próprios dispositivos
kiwi-server enroll fleet.yaml laptop --group devices
kiwi-server status fleet.yaml             # o que cada máquina comunica
```

Por predefinição, uma ISO de instalação **não contém nenhum dos segredos da
stack**. Contém apenas o sistema base. A função e a respetiva stack só chegam à
máquina depois, com o `apply`. Se uma máquina não estiver acessível por SSH,
`build --offline` põe na ISO a função completa e os seus segredos. Não carregues
uma ISO destas para o armazenamento de ISOs de um fornecedor de alojamento, e
apaga-a depois da instalação.

**Se não quiseres usar nenhuma ISO,** `kiwi-server script fleet.yaml papaya`
mostra o script para uma máquina que tenhas instalado tu próprio. Com
`--offline`, o script contém a função completa.

Num VPS da netcup, `kiwi-server vps install fleet.yaml sorbet` apaga o servidor
e instala a ISO através da API da netcup, sem ninguém ter de estar à consola.
Por enquanto, a netcup é o único fornecedor de alojamento com que isto
funciona. Outros estão [planeados](roadmap.md#more-hosters-and-network-boot).

## Comandos { #commands }

| Comando | O que faz |
|---|---|
| `init [fleet.yaml]` | Escreve o ficheiro fleet de exemplo. `--domain` define o domínio, que por predefinição é `home`. |
| `validate fleet.yaml [host…]` | Verifica o ficheiro fleet. Gera todas as stacks, para que também se encontrem erros nos módulos. |
| `list` / `show fleet.yaml <host>` | O primeiro lista as máquinas e o que já foi gerado para cada uma. O segundo mostra a configuração efetiva de uma máquina, com os segredos ocultos. |
| `render fleet.yaml [host…]` | Escreve os scripts das funções, as stacks e as configurações de instalação em `output/<host>/`. |
| `build fleet.yaml [host…]` | Gera a configuração e depois constrói a ISO. Por predefinição, a ISO contém apenas o sistema base; com `--offline`, contém a função completa. |
| `script fleet.yaml <host>` | Mostra o script para qualquer máquina. Com `--offline`, o script contém a função completa. |
| `apply fleet.yaml <host…>` | Volta a gerar a configuração, envia a função para a máquina por SSH e executa-a lá (`--ssh USER@ADDR`, `--no-run`). |
| `status fleet.yaml [host…]` | Mostra o que as máquinas comunicam: função, stack, problemas, discos, backups e certificados. |
| `enroll fleet.yaml <host\|name>` | Cria um cliente WireGuard no master, ou vai buscar um que já exista (`--group`, `--split`, `--qr`, `--address`, `--existing`). |
| `secrets init\|unlock\|lock\|status` | Gere `secrets/` como um único ficheiro cifrado com age, que é aberto em memória quando o desbloqueias (`--for 8h`). |
| `secrets show fleet.yaml <host> [setting]` | Mostra as palavras-passe geradas para uma máquina. |
| `ca fleet.yaml` | Mostra a CA da rede. |
| `mtu fleet.yaml <node\|device\|address>` | Mede a MTU real de um túnel e diz-te que valor deves definir (`--write`). |
| `openwrt fleet.yaml` | Escreve um script que liga um router OpenWrt à mesh ([Routers](../network/routers.md)). |
| `backup` / `restore` / `prune` | Faz backup da pasta do ficheiro fleet para nodes, restaura-a a partir deles e elimina os backups antigos das máquinas ([Operação](operations.md)). |
| `unlock fleet.yaml <host>` | Reencaminha um anel Tang para uma máquina que, no arranque, está à espera de que o seu disco cifrado seja desbloqueado ([Operação](operations.md)). |
| `vps login\|list\|probe\|install` | Trabalha com a API do Server Control Panel da netcup. |
| `roles [-v]`, `modules [-v]`, `targets` | Mostram o que está disponível, com todas as definições e os respetivos valores predefinidos. |
| `toolchain [status\|build]`, `doctor` | Gerem as ferramentas das ISOs e verificam este computador. |

Todos os comandos aceitam `--porcelain` (resultado em JSON), `-o/--output-dir`,
`--quiet` e `-v`. `kiwi-server <command> -h` explica um comando em particular.

## A aplicação { #the-app }

A aplicação **Kiwi Server** abre a última rede em que trabalhaste. A barra
lateral tem uma vista geral, uma linha para cada máquina e as predefinições. Em
*Overview*, a página de uma máquina mostra informação atual de
`kiwi-server status`. Enquanto a janela estiver em primeiro plano, a aplicação
vai buscá-la uma vez por minuto, por SSH e só em leitura. Em *Settings* há um
formulário construído a partir das funções e dos módulos. *Apply*, *Build* e
*Render* executam a ferramenta de linha de comandos e mostram o resultado à
medida que vai sendo produzido. Antes de começar, *Build* lista os discos que
vai apagar. *Unlock* e *Lock* abrem e fecham o cofre de segredos. A aplicação
escreve YAML simples, por isso, quando guarda um ficheiro fleet que tenhas
escrito à mão, os comentários perdem-se.

## O que deves ter presente { #mind }

!!! danger "As ISOs apagam o disco que lhes foi indicado"
    Uma ISO de instalação apaga o disco para o qual foi gerada logo que uma
    máquina arranca a partir dela, sem perguntar nada. Põe etiquetas nas tuas
    ISOs. É precisamente por isso que o `build` exige a definição `disk:`.

- **O resultado contém segredos:** hashes de palavras-passe, chaves WireGuard,
  chaves TLS e chaves LUKS. Os ficheiros são escritos com o modo 0600, e o git
  ignora `output/`. Trata as ISOs feitas com `--offline` com o mesmo cuidado.
- **As palavras-passe dos serviços são geradas** a partir de `secrets/seed`, se
  não as puseres no ficheiro fleet. O `validate` avisa-te das palavras-passe
  escritas no ficheiro fleet, e `kiwi-server secrets show` mostra as que foram
  geradas. Uma máquina recusa um `apply` feito com outra seed.
- **As chaves de anfitrião SSH** ficam registadas em `secrets/known_hosts` da
  primeira vez que o kiwi-server se liga a uma máquina. Se mais tarde a chave de
  uma máquina mudar, a ligação é recusada. Depois de reinstalares uma máquina,
  apaga a linha dela nesse ficheiro.
- **O script de uma função corre como root.** Antes de confiares numa função
  que não escreveste, lê o resultado de `kiwi-server script fleet.yaml <host>
  --offline`.
- **Quando uma função falha, isso fica registado.** A máquina guarda o ficheiro
  `/var/lib/kiwi-server/role.failed`, que indica o passo e o comando que
  falharam, e o `status` mostra-o.

## Estado { #status }

Todo o processo, do ficheiro fleet até uma máquina a funcionar, foi testado em
hardware real em outubro e novembro de 2026. O Debian, o uCore e o Fedora
CoreOS passaram pelo processo completo em dois VPS, num mini PC e numa máquina
virtual. Num exercício que simulava a avaria de um node, uma máquina Debian com
o disco cifrado foi reconstruída em cerca de 14 minutos. Os backups de um node
foram restaurados noutro (do papaya para o lychee). A MTU do túnel foi medida e
afinada em ligações reais, incluindo ligações móveis. Os testes automáticos
(CI) geram todas as funções, passam o shellcheck por todos os scripts e validam
todas as configurações Butane. Comparam também, byte a byte, quatro stacks de
referência, as chamadas golden stacks, com o resultado guardado.

A federação entre redes ainda não foi testada. Tudo funciona com IPv4. A ISO de
Debian só existe para amd64. Um plano de controlo (`kiwi-server serve`) está
planeado e concebido, mas ainda não implementado.

Continua a ler: [O ficheiro fleet](fleet.md) · [Funções](roles.md) · [Módulos](modules.md) ·
[Máquinas](machines.md) · [Operação](operations.md) ·
[Uma máquina sem ficheiro fleet](single.md)
