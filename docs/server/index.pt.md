# kiwi-server

O kiwi-server cria e gere uma Kiwi Network. Descreves todas as máquinas num só
`fleet.yaml`. O kiwi-server faz uma **ISO de instalação sem intervenção** para
cada anfitrião, que instala Fedora CoreOS, uCore ou Debian e desliga a máquina.
Depois **aplica** o papel por SSH e transforma a máquina num `kiwi-master` ou
num `kiwi-node`. A partir daí continua a trabalhar com a fleet: inscreve
clientes WireGuard, lê o estado de saúde de cada máquina, guarda os segredos, faz
cópias de segurança da fleet e desbloqueia discos cifrados.

Tem uma CLI, `kiwi-server`, e uma app GTK4, **Kiwi Server**. Ambas se instalam em
`~/.local` e não precisam de root.

- Repositório: [derlocke-ng/kiwi-server](https://github.com/derlocke-ng/kiwi-server), GPL-3.0-or-later
- Versão mais recente: **v2.42.0**. Está no [catálogo Kiwi](../desktop/catalogs.md).
- Assente em [kiwi-modules](single.md) v0.23.0 (os módulos e o seu renderizador)
  e [kiwi-stack](single.md) v0.5.0 (o lado da máquina), incluídos no repositório
  e fixados por tag.

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

## Instalar { #install }

```bash
kiwi install kiwi-server        # com o kiwi-updater
```

Ou a partir de um checkout: `./install.sh install`, depois `kiwi-server doctor`.

Precisa de Python 3.9+ com PyYAML e Jinja2, `openssl` e `ssh`. O cofre de
segredos precisa de `age`. Construir ISOs precisa de `butane`, `coreos-installer`
e `xorriso` (mais `cpio`, `gzip` e `curl` para Debian). No Silverblue ou no
Bluefin, constrói-as como uma imagem de contentor em vez de sobrepor pacotes:

```bash
kiwi-server toolchain build     # usada automaticamente quando faltam as ferramentas
```

`qrencode` (para `enroll --qr`), `shellcheck` e `docker compose` são opcionais.

## Do nada a uma rede a funcionar { #from-nothing-to-a-running-network }

```bash
kiwi-server init                          # um fleet.yaml comentado
$EDITOR fleet.yaml                        # anfitriões, papéis, a tua chave SSH, o disco de instalação
kiwi-server secrets init fleet.yaml       # opcional: secrets/ como um cofre cifrado com age
kiwi-server validate fleet.yaml

# o master
kiwi-server build fleet.yaml sorbet         # → output/sorbet/sorbet.iso
#   arranca-a; instala e desliga-se; liga-a de novo
kiwi-server apply fleet.yaml sorbet --ssh core@203.0.113.5

# cada node: primeiro o seu cliente WireGuard, depois o suporte de instalação, depois o papel
kiwi-server enroll fleet.yaml papaya         # → secrets/papaya.home.conf
kiwi-server build fleet.yaml papaya
kiwi-server apply fleet.yaml papaya --ssh core@192.168.1.25

# os teus próprios dispositivos
kiwi-server enroll fleet.yaml laptop --group devices
kiwi-server status fleet.yaml             # o que cada máquina reporta
```

Por omissão, o suporte de instalação não leva **nenhum dos segredos da stack**:
só o sistema base. O papel e a sua stack chegam com `apply`. Se uma máquina não
estiver acessível por SSH, `build --offline` põe na ISO o papel inteiro e os seus
segredos. Mantém uma ISO dessas fora do armazenamento de ISOs de um fornecedor e
apaga-a depois da instalação.

**Nenhuma ISO?** `kiwi-server script fleet.yaml papaya` imprime o script para uma
máquina que instalaste tu mesmo (`--offline` para o papel inteiro).

Num VPS da netcup, `kiwi-server vps install fleet.yaml sorbet` apaga o servidor e
instala a ISO através da API da netcup.

## Comandos { #commands }

| Comando | O que faz |
|---|---|
| `init [fleet.yaml]` | escreve o ficheiro fleet de exemplo (`--domain`, por omissão `home`) |
| `validate fleet.yaml [host…]` | verifica-o, renderizando todas as stacks para apanhar erros de módulos |
| `list` / `show fleet.yaml <host>` | os anfitriões e o que foi gerado / a configuração efetiva de um anfitrião, com os segredos ocultos |
| `render fleet.yaml [host…]` | scripts de papel, stacks e configurações de instalação para `output/<host>/` |
| `build fleet.yaml [host…]` | renderiza e depois faz a ISO: sistema base por omissão, `--offline` para o papel inteiro |
| `script fleet.yaml <host>` | o script para qualquer máquina (`--offline` para o papel inteiro) |
| `apply fleet.yaml <host…>` | renderiza de novo, envia o papel por SSH e corre-o (`--ssh USER@ADDR`, `--no-run`) |
| `status fleet.yaml [host…]` | o que as máquinas reportam: papel, stack, problemas, discos, cópias de segurança, certificados |
| `enroll fleet.yaml <host\|name>` | cria ou vai buscar um cliente WireGuard no master (`--group`, `--split`, `--qr`, `--address`, `--existing`) |
| `secrets init\|unlock\|lock\|status` | `secrets/` como um único ficheiro cifrado com age, aberto para a memória (`--for 8h`) |
| `secrets show fleet.yaml <host> [setting]` | as palavras-passe geradas de um anfitrião |
| `ca fleet.yaml` | a CA da fleet |
| `mtu fleet.yaml <node\|device\|address>` | mede o MTU real de um túnel e diz o que definir (`--write`) |
| `openwrt fleet.yaml` | um script que junta um router OpenWrt à malha ([Routers](../network/routers.md)) |
| `backup` / `restore` / `prune` | o diretório da fleet para os nodes e de volta; cópias de segurança antigas das máquinas removidas ([Operações](operations.md)) |
| `unlock fleet.yaml <host>` | reencaminha um anel Tang para uma máquina que espera no arranque ([Operações](operations.md)) |
| `vps login\|list\|probe\|install` | a API do Server Control Panel da netcup |
| `roles [-v]`, `modules [-v]`, `targets` | o que está disponível, com cada definição e o seu valor por omissão |
| `toolchain [status\|build]`, `doctor` | as ferramentas de ISO; verificar esta máquina |

Todos os comandos aceitam `--porcelain` (JSON), `-o/--output-dir`, `--quiet` e
`-v`. `kiwi-server <command> -h` explica um comando.

## A app { #the-app }

O **Kiwi Server** abre a tua última fleet. A barra lateral tem uma visão geral,
uma linha por anfitrião e os valores por omissão. A *Overview* de um anfitrião
mostra factos em tempo real de `kiwi-server status` (consultados uma vez por
minuto enquanto a janela tem o foco, só de leitura, por SSH). As suas *Settings*
são um formulário construído a partir dos papéis e módulos. *Apply*, *Build* e
*Render* correm a CLI e mostram a sua saída em direto, e *Build* lista os discos
que vai apagar antes de começar. *Unlock* e *Lock* abrem e fecham o cofre de
segredos. A app escreve YAML simples, por isso os comentários de um ficheiro
fleet escrito à mão perdem-se quando ela guarda.

## Atenção { #mind }

!!! danger "As ISOs apagam o disco que lhes for indicado"
    No arranque, sem perguntar. Etiqueta-as. `disk:` é obrigatório para `build`
    exatamente por essa razão.

- **A saída contém segredos**: hashes de palavras-passe, chaves WireGuard, chaves
  TLS, chaves LUKS. Os ficheiros são escritos com 0600 e `output/` é ignorado
  pelo git. Trata da mesma forma as ISOs feitas com `--offline`.
- **As palavras-passe dos serviços são geradas** a partir de `secrets/seed`
  quando as deixas fora do ficheiro fleet. `validate` avisa sobre palavras-passe
  escritas nele. `kiwi-server secrets show` imprime-as. Uma máquina recusa um
  apply feito com uma seed diferente.
- **As chaves de anfitrião SSH** ficam registadas em `secrets/known_hosts` no
  primeiro contacto, e uma chave alterada é recusada (depois de uma
  reinstalação, apaga a linha).
- **Um script de papel corre como root.** Lê `kiwi-server script fleet.yaml <host>
  --offline` antes de confiares num papel que não escreveste.
- **Um papel que falha di-lo.** A máquina guarda `/var/lib/kiwi-server/role.failed`
  (o passo e o comando), e `status` mostra-o.

## Estado { #status }

O pipeline foi comprovado em hardware em outubro e novembro de 2026. Debian,
uCore e Fedora CoreOS arrancaram de ponta a ponta em dois VPSes, um mini PC e uma
VM, e um exercício de node morto reconstruiu uma máquina Debian cifrada em cerca
de 14 minutos. Cópias de segurança de nodes foram restauradas de um node para
outro (de papaya para lychee), e o MTU do túnel foi medido e afinado em caminhos
reais, incluindo móveis. A CI renderiza todos os papéis, passa o shellcheck em
todos os scripts, valida todas as configurações Butane e fixa quatro stacks de
referência byte a byte.

Ainda não comprovado: a federação entre redes. Tudo é IPv4. A ISO Debian é só
amd64. Um plano de controlo planeado (`kiwi-server serve`) está projetado, mas
não construído.

Continua a ler: [O ficheiro fleet](fleet.md) · [Papéis](roles.md) · [Módulos](modules.md) ·
[Máquinas](machines.md) · [Operações](operations.md) ·
[Uma máquina sem fleet](single.md)
