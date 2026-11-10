# Máquinas: instalar, aplicar, atualizar

Esta página acompanha uma máquina desde a sua entrada no ficheiro fleet até um
sistema a funcionar que se atualiza sozinho. O kiwi-server gera uma imagem de
instalação que instala o sistema operativo sem ninguém ao teclado. Depois,
prepara a máquina para a sua função por SSH, com o comando `apply`. A partir
daí, a máquina instala ela própria as atualizações e só reinicia nas horas que
tiveres autorizado.

## Sistemas de destino { #targets }

O sistema de destino é o sistema operativo que o kiwi-server instala numa
máquina.

| Sistema de destino | O que é instalado | Meio de instalação |
|---|---|---|
| `coreos` | Fedora CoreOS, canal stable | A ISO live oficial, personalizada com a configuração Ignition da máquina (Butane `fcos` 1.6.0). A instalação não precisa de ligação à rede |
| `ucore` | Fedora CoreOS, que depois muda sozinho (rebase) para uma imagem `ghcr.io/ublue-os/ucore*`. As imagens são `ucore-minimal`, `ucore` e `ucore-hci`, também com `-nvidia` / `-zfs`. O rebase funciona como o exemplo de autorebase do próprio uCore | O mesmo que para o CoreOS, mais as unidades de autorebase |
| `debian` | Debian stable (trixie), amd64 | A imagem netinst oficial, com o preseed (o ficheiro com as respostas para o instalador) no seu initrd, para que o instalador tenha as respostas logo desde a primeira pergunta. Os ficheiros da máquina ficam na imagem, em `/kiwi-server`. A imagem continua a arrancar tanto em BIOS como em UEFI |

Em todos os sistemas de destino, o utilizador de administração pode usar o sudo
sem palavra-passe. O SSH só aceita chaves, a não ser que definas
`ssh_password_auth: true`.

## Meio de instalação { #install-media }

O primeiro comando gera a imagem de instalação (ISO) de uma máquina. O segundo
copia-a para uma pen USB.

```bash
kiwi-server build fleet.yaml sorbet      # → output/sorbet/sorbet.iso
sudo dd if=output/sorbet/sorbet.iso of=/dev/sdX bs=4M status=progress oflag=sync
```

- A ISO instala no disco indicado em `disk:` **sem perguntar**, e apaga tudo o
  que lá estiver. Quando a instalação termina, **desliga a máquina**
  (`install.on_done: poweroff`, ou `reboot` se a quiseres reiniciar). Põe
  etiquetas nas tuas pens USB.
- Por predefinição, o meio de instalação contém **apenas o sistema base**: o
  nome da máquina, as definições de rede, o utilizador de administração com as
  chaves SSH e a política de atualizações. Não contém nenhum dos segredos da
  stack. A máquina só recebe a sua função mais tarde, quando executares o
  `apply`.
- Com `--offline`, a função completa e os seus segredos vão para a ISO. Isto
  destina-se a uma máquina que não está acessível por SSH. Quem tiver essa ISO
  tem também esses segredos.
- O instalador live lista os discos da máquina (`lsblk`) e tem uma shell, onde
  entras com a palavra-passe de consola e as chaves SSH definidas no ficheiro
  fleet.

## Aplicar { #apply }

O `apply` prepara uma máquina para a sua função, por SSH.

```bash
kiwi-server apply fleet.yaml papaya                         # pelo nome, pelo endereço ou pelo endereço na mesh
kiwi-server apply fleet.yaml papaya --ssh core@192.168.1.25 # da primeira vez, pelo endereço
```

Primeiro, o `apply` volta a gerar a configuração da máquina, ou seja, produz de
novo os ficheiros dela a partir do ficheiro fleet. Depois, copia por SSH o
script da função para `/var/lib/kiwi-server/role.sh`. É este script que prepara
a máquina para a sua função, e o `apply` executa-o como root. A seguir, associa
o disco aos seus anéis Tang, que são servidores que permitem a uma máquina
cifrada desbloquear o disco no arranque. Num master, guarda também o estado do
WireGuard juntamente com os segredos da rede. Numa máquina Debian cifrada, o
primeiro `apply` substitui a chave temporária usada na instalação.

A ligação SSH usa a chave da própria rede e compara a chave de anfitrião da
máquina com `secrets/known_hosts`. O `apply` e o `status` conseguem chegar a
uma máquina pelo nome, pelo endereço estático, pelo endereço público do master
ou pelo endereço na mesh, que é o endereço da máquina na rede WireGuard
privada. Só usam um endereço cuja chave de anfitrião já esteja registada.

Numa função construída a partir de módulos, o script da função entrega a stack
ao `kiwi-stack`. A stack é o conjunto de contentores que a máquina corre para
os seus módulos. O `kiwi-stack` segue então estes passos:

1. Instala ou ativa o podman 4.4 ou mais recente, ou o docker, e garante que o
   utilizador de serviço existe. No Debian, o podman vem com o `netavark`, o
   `aardvark-dns` e o `catatonit`.
2. Carrega módulos do kernel e define sysctls. Se a stack tiver o Pi-hole, o
   aardvark-dns do podman passa para a porta 5533, e a própria máquina passa a
   resolver nomes através do Pi-hole da stack. Acrescenta ainda a mesh às redes
   em que a firewalld confia.
3. Recusa uma stack gerada a partir de outra seed. A seed é o segredo a partir
   do qual se geram as palavras-passe da rede. Se a seed for a mesma, desempacota
   a stack em `docker_dir`. Instala os quadlets, que são as unidades systemd dos
   contentores, em `/etc/containers/systemd`, e instala as unidades da máquina.
   Remove também tudo o que tenha sido instalado por um módulo que já não faz
   parte da stack.
4. Abre as portas da stack na firewalld ou no ufw, se um deles estiver ativo.
5. Descarrega todas as imagens de contentores e depois arranca o
   `kiwi-stack.service`, que por sua vez arranca o `kiwi-stack.target`.
6. Executa `kiwi-stack verify`, que verifica se todos os contentores estão a
   correr. Se algum não estiver, o `apply` falha e indica o passo que falhou.

Se voltares a aplicar a mesma configuração gerada, nada muda na máquina. Se
aplicares uma configuração nova, é substituído o que mudou. Tem em conta que
cada `apply` reinicia todos os contentores da stack, mesmo que nada tenha
mudado.

## Primeiro arranque { #first-boot }

No primeiro arranque, o `kiwi-role.service` executa uma vez o script da função,
`/var/lib/kiwi-server/role.sh`. Começa depois de a rede estar ativa e espera
até 120 segundos pelo DNS. O ficheiro `role.done` marca a função como
concluída e só é escrito quando todos os contentores estão a correr. Se o
script falhar, deixa o ficheiro `/var/lib/kiwi-server/role.failed`, que indica
o passo e o comando que falharam, e volta a ser executado no arranque seguinte.
O registo fica em `/var/log/kiwi-server-role.log`. No uCore, o script da função
espera até a máquina estar a correr a imagem uCore assinada. Para voltares a
executar o script à mão, usa `sudo bash /var/lib/kiwi-server/role.sh --force`.

## Atualizações { #updates }

As máquinas vão instalando continuamente as atualizações do sistema operativo.
O **reinício** que as ativa só acontece dentro da janela de manutenção que
definires com `updates.days`, `time` e `length_minutes`, na hora local.

| Sistema de destino | Instala as atualizações | Reinicia |
|---|---|---|
| `coreos` | o Zincati, continuamente | só dentro da janela (`strategy = "periodic"`) |
| `ucore` | o `rpm-ostreed-automatic.timer` descarrega-as e prepara-as (stage) | o `kiwi-staged-reboot.timer`, dentro da janela |
| `debian` | o unattended-upgrades, diariamente | o `kiwi-reboot-if-required.timer`, dentro da janela, se uma atualização exigir reinício |

`updates.days: []` permite o reinício em qualquer dia, e `updates.enabled: false`
desliga as atualizações e os reinícios. Uma máquina cifrada não reinicia
sozinha se precisar de um anel Tang que alguém tenha de lhe reencaminhar à mão.
Caso contrário, ficaria parada no arranque até alguém a desbloquear.

Os contentores são atualizados segundo um calendário próprio. Uma vez por
semana, ao domingo às 00:00, o `kiwi-stack update` executa `podman auto-update`,
desde que esteja definido `auto_update: registry`. O cliente VPN é reiniciado
todos os dias às 07:00, o que lhe dá um novo endereço de saída. O endereço de
saída é o endereço público que os sites veem quando o tráfego sai da VPN.

## Na máquina: `kiwi-stack` { #on-the-machine-kiwi-stack }

O `kiwi-stack` é o comando que executas na própria máquina para consultar e
controlar a stack.

```bash
sudo kiwi-stack status          # contentores, unidades da máquina, verificação
sudo kiwi-stack verify          # todos os contentores a correr?
sudo kiwi-stack logs [service]  # a partir do journal
sudo kiwi-stack start | stop | restart
sudo kiwi-stack update          # podman auto-update + prune
sudo kiwi-stack vpn-restart     # o cliente VPN e todos os contentores no seu namespace
sudo kiwi-stack backup | snapshots | restore [--at TIME] MODULE...   # com o módulo backup
sudo kiwi-stack apply DIR       # um pacote com a stack, sem script de função
```

Os ficheiros da stack ficam em `docker_dir` (por predefinição
`/home/user/docker`), e as suas definições em `/etc/kiwi-server/stack.env`. As
unidades systemd são o `kiwi-stack.service`, o `kiwi-stack-vpn-restart.timer` e
o `kiwi-stack-update.timer`, a que se juntam as unidades que um módulo
acrescente.

## O que se obtém ao gerar a configuração { #what-a-render-produces }

Ao gerar a configuração de uma máquina a partir do ficheiro fleet, o
kiwi-server escreve-a em `output/<host>/`, que passa a conter estes ficheiros.

| Ficheiro | O que é |
|---|---|
| `<host>.role.sh` | A função como um único script. Contém as definições, a stack embutida, o comando e a biblioteca do kiwi-stack e o corpo da função. O ficheiro tem o modo 0600 |
| `<host>.stack/` | O pacote com a stack, para que o possas rever. Contém `docker-compose.yml`, `quadlets/`, os ficheiros de configuração dos módulos, as unidades da máquina e `stack.sh`. Também o podes instalar à mão com `kiwi-stack apply` |
| `<host>.bu`, `<host>.ign` | No CoreOS e no uCore, a configuração Butane e a Ignition |
| `<host>.preseed.cfg`, `<host>.kiwi-server/` | No Debian, o ficheiro de preseed e os ficheiros que ele copia para a máquina |
| `<host>.iso` | A imagem de instalação, que instala sem ninguém ao teclado |
