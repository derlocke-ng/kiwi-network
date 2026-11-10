# Máquinas: instalar, aplicar, atualizar

## Targets { #targets }

| Target | O que é instalado | Suporte de instalação |
|---|---|---|
| `coreos` | Fedora CoreOS, stream stable | a ISO live de origem, personalizada com o Ignition do anfitrião (Butane `fcos` 1.6.0); a instalação não precisa de rede |
| `ucore` | Fedora CoreOS que faz rebase de si mesmo para uma imagem `ghcr.io/ublue-os/ucore*` (`ucore-minimal`, `ucore`, `ucore-hci`, com `-nvidia` / `-zfs`), como o exemplo de autorebase do próprio uCore | como no CoreOS, mais as unidades de autorebase |
| `debian` | Debian stable (trixie), amd64 | o netinst de origem com o preseed no seu initrd, para que responda logo a partir da primeira pergunta, e os ficheiros do anfitrião em `/kiwi-server`; mantém o arranque BIOS e UEFI |

O utilizador admin tem sudo sem palavra-passe em todo o lado. O SSH só aceita
chaves, a não ser que definas `ssh_password_auth: true`.

## Suporte de instalação { #install-media }

```bash
kiwi-server build fleet.yaml sorbet      # → output/sorbet/sorbet.iso
sudo dd if=output/sorbet/sorbet.iso of=/dev/sdX bs=4M status=progress oflag=sync
```

- Uma ISO instala em `disk:` **sem perguntar** e depois **desliga a máquina**
  (`install.on_done: poweroff`, ou `reboot`). Etiqueta as tuas pens.
- Por omissão, o suporte de instalação leva **apenas o sistema base**: nome de
  anfitrião, rede, utilizador admin e chaves, política de atualizações. Não leva
  nenhum dos segredos da stack. O papel vem depois, com `apply`.
- `--offline` põe na ISO o papel inteiro e os seus segredos, para uma máquina que
  o SSH não consegue alcançar. Quem tiver essa ISO tem esses segredos.
- O instalador live mostra os discos (`lsblk`) e tem uma shell com a
  palavra-passe de consola e as chaves da fleet.

## Aplicar { #apply }

```bash
kiwi-server apply fleet.yaml papaya                         # por nome, endereço ou endereço de malha
kiwi-server apply fleet.yaml papaya --ssh core@192.168.1.25 # da primeira vez, por endereço
```

O `apply` renderiza de novo o anfitrião e envia o seu script de papel por SSH
para `/var/lib/kiwi-server/role.sh`. Corre o script como root, depois associa o
disco aos seus anéis Tang e, num master, guarda o estado do WireGuard com os
segredos da fleet. Numa máquina Debian cifrada, o primeiro apply substitui a
chave de instalação de uso único. O SSH usa a chave própria da fleet e verifica
as chaves de anfitrião em `secrets/known_hosts`. `apply` e `status` encontram uma
máquina pelo nome, pelo endereço estático, pelo endereço público do master ou
pelo endereço de malha, mas só em endereços cuja chave de anfitrião esteja
registada.

Para um papel de módulos, o script entrega a stack ao `kiwi-stack`:

1. Instala ou ativa o podman 4.4+ (no Debian com `netavark`,
   `aardvark-dns` e `catatonit`) ou o docker, e o utilizador de serviço.
2. Carrega módulos do kernel e define sysctls. Com o Pi-hole, o aardvark-dns
   passa para a porta 5533 e o anfitrião resolve através do Pi-hole da stack.
   Também passa a confiar na malha no firewalld.
3. Recusa uma stack renderizada a partir de outra seed. Desempacota a stack em
   `docker_dir`, instala os quadlets em `/etc/containers/systemd` e as unidades
   do anfitrião, e remove o que um módulo que saiu tinha instalado.
4. Abre as portas da stack no firewalld ou no ufw, se um deles estiver ativo.
5. Puxa todas as imagens e depois arranca `kiwi-stack.service`
   (→ `kiwi-stack.target`).
6. Corre `kiwi-stack verify`: todos os contentores têm de estar a correr, ou o
   apply falha e diz que passo falhou.

Aplicar de novo a mesma renderização não muda nada, e uma nova renderização
substitui o que mudou. Mas um novo apply reinicia todos os contentores da stack.

## Primeiro arranque { #first-boot }

O `kiwi-role.service` corre `/var/lib/kiwi-server/role.sh` uma vez, depois de a
rede estar ativa (espera até 120 segundos pelo DNS). `role.done` só é escrito
quando todos os contentores estão a correr. Uma falha deixa
`/var/lib/kiwi-server/role.failed` (o passo e o comando) e é repetida no arranque
seguinte. O registo é `/var/log/kiwi-server-role.log`. No uCore, o papel espera
até a imagem estar assinada. `sudo bash /var/lib/kiwi-server/role.sh --force`
corre-o de novo.

## Atualizações { #updates }

As atualizações instalam-se continuamente. O **reinício** para as aplicar só
acontece dentro da tua janela (`updates.days`, `time`, `length_minutes`, hora
local):

| Target | Instala atualizações | Reinicia |
|---|---|---|
| `coreos` | Zincati, continuamente | só na janela (`strategy = "periodic"`) |
| `ucore` | `rpm-ostreed-automatic.timer` prepara-as | `kiwi-staged-reboot.timer` na janela |
| `debian` | unattended-upgrades, diariamente | `kiwi-reboot-if-required.timer` na janela, quando é necessário |

`updates.days: []` significa qualquer dia, e `updates.enabled: false` desativa
tudo. Uma máquina cifrada cujo anel Tang tenha de ser reencaminhado para dentro
não reinicia sozinha.

Os contentores têm o seu próprio calendário: um `kiwi-stack update` semanal
(domingo às 00:00) corre `podman auto-update` enquanto `auto_update: registry`
estiver definido. Um reinício diário do cliente VPN às 07:00 dá um endereço de
saída novo.

## Na máquina: `kiwi-stack` { #on-the-machine-kiwi-stack }

```bash
sudo kiwi-stack status          # contentores, unidades do anfitrião, verificação
sudo kiwi-stack verify          # todos os contentores a correr?
sudo kiwi-stack logs [service]  # a partir do journal
sudo kiwi-stack start | stop | restart
sudo kiwi-stack update          # podman auto-update + prune
sudo kiwi-stack vpn-restart     # o cliente VPN e todos os contentores no seu namespace
sudo kiwi-stack backup | snapshots | restore [--at TIME] MODULE...   # com o módulo backup
sudo kiwi-stack apply DIR       # um pacote de stack, sem script de papel
```

A stack vive em `docker_dir` (por omissão `/home/user/docker`), e as suas
definições em `/etc/kiwi-server/stack.env`. As unidades são `kiwi-stack.service`,
`kiwi-stack-vpn-restart.timer` e `kiwi-stack-update.timer`, mais as que um módulo
acrescente.

## O que uma renderização produz { #what-a-render-produces }

`output/<host>/` contém:

| Ficheiro | O quê |
|---|---|
| `<host>.role.sh` | o papel como um só script: definições, a stack (incorporada), o comando e a biblioteca kiwi-stack, e o corpo do papel. Modo 0600 |
| `<host>.stack/` | o pacote da stack, para revisão: `docker-compose.yml`, `quadlets/`, configurações dos módulos, unidades do anfitrião e `stack.sh`. `kiwi-stack apply` pode instalá-lo à mão |
| `<host>.bu`, `<host>.ign` | CoreOS e uCore: Butane e Ignition |
| `<host>.preseed.cfg`, `<host>.kiwi-server/` | Debian: o preseed e os ficheiros que ele copia |
| `<host>.iso` | o instalador sem intervenção |
