# Operações

O trabalho do dia a dia numa fleet em funcionamento, tudo a partir da máquina do
operador.

## Estado { #status }

```bash
kiwi-server status fleet.yaml            # todos os anfitriões
kiwi-server status fleet.yaml papaya        # um
```

Cada máquina reporta por SSH (só de leitura): o seu papel, a sua stack, os
problemas (um papel que falhou, um contentor parado), os seus discos e se estão
cifrados ou bloqueados, as suas cópias de segurança e quanto tempo falta aos seus
certificados. Um node de cópias de segurança reporta também a sua capacidade. A
app Kiwi Server mostra o mesmo na *Overview* de cada anfitrião.

## Segredos { #secrets }

Tudo o que é secreto vive em `secrets/`, ao lado do ficheiro fleet: a seed da qual
derivam todas as palavras-passe geradas, a CA da fleet, as configurações
WireGuard, as chaves LUKS e as chaves de anfitrião SSH.

```bash
kiwi-server secrets init fleet.yaml      # secrets/ passa a ser um ficheiro cifrado com age
kiwi-server secrets unlock fleet.yaml    # abre-o para a memória (--for 8h; 0 mantém-no aberto)
kiwi-server secrets lock fleet.yaml
kiwi-server secrets status fleet.yaml
kiwi-server secrets show fleet.yaml papaya [setting]   # as palavras-passe geradas de um anfitrião
```

`secrets init` guarda uma chave no GNOME Keyring e mostra uma **chave de
recuperação** uma vez. Enquanto o cofre está aberto, tudo o que corre como tu
consegue lê-lo.

## Cópia de segurança da própria fleet { #backing-up-the-fleet-itself }

Depois de cada renderização ou construção bem-sucedida, o diretório da fleet é
cifrado (AES-256 com PBKDF2, 600 000 iterações) e copiado para os nodes listados
em `backup.hosts`, que guardam as dez mais recentes. Numa máquina nova:

```bash
kiwi-server restore --from core@lychee.home  # o diretório da fleet de volta
kiwi-server backup fleet.yaml --local /mnt/usb   # ou uma cópia para um diretório, a qualquer momento
```

## Cópia de segurança dos dados das máquinas { #backing-up-the-machines-data }

Dá a um node o módulo `backup-server` (um restic REST server) e, a cada máquina
de que se deve fazer cópia de segurança, o módulo `backup`, a apontar para ele:

```yaml
lychee:
  node:
    modules: [vpn-client, reverse-proxy, backup-server]
    backup-server: { clients: [papaya.home, sorbet.home] }
papaya:
  node:
    modules: [vpn-client, reverse-proxy, cloud, vault, portainer, backup]
    backup: { server: https://backup.lychee.home }
```

Todas as noites às 03:00 (nos 15 minutos seguintes), o restic envia, cifrado, o
que cada módulo pede para guardar. Cada máquina só consegue alcançar o seu
próprio repositório, e só lhe pode acrescentar. Por isso, a remoção de
snapshots antigos corre a partir da máquina do operador:

```bash
sudo kiwi-stack backup | snapshots | restore [--at TIME] MODULE...   # na máquina
kiwi-server prune fleet.yaml            # guarda 7 diários, 4 semanais, 6 mensais
```

Foi testado um restauro de node para node: as cópias de segurança do papaya no
lychee.

### Na próxima versão { #coming-in-the-next-release }

!!! info "No ramo `several-servers`"
    Este trabalho foi enviado para os ramos `several-servers` do kiwi-modules e
    do kiwi-server, mas ainda não foi integrado nem lançado. Os vários servidores
    e o restauro automático foram testados em hardware. A verificação de saúde
    da VPN não foi.

- **Vários servidores de cópias de segurança.** `backup.servers` aceita uma
  lista, e cada servidor recebe uma cópia completa só sua. Se um servidor
  falhar, só falta a cópia dele. Um restauro usa a cópia mais recente do
  servidor que a tiver, e `kiwi-stack snapshots` lista-as servidor a servidor. O
  `server` único continua a funcionar.
- **Uma máquina reconstruída restaura-se sozinha.** Se uma máquina se encontrar
  nas cópias de segurança mas não tiver feito nenhuma delas (uma reconstrução),
  restaura todos os módulos sozinha antes da sua primeira cópia de segurança, e
  depois faz cópias como antes (`backup.restore:
  auto`, o valor por omissão). Com `hold`, espera por `kiwi-stack restore` ou por
  `kiwi-stack backup --new`.
- **Limpeza com temporizador.** `kiwi-server prune fleet.yaml --every week` (ou
  `day`) instala um temporizador de utilizador systemd no teu computador, o único
  sítio que tem as chaves que podem apagar. Uma execução perdida acontece no
  início de sessão seguinte. `kiwi-server status` mostra cada cópia de
  segurança e avisa quando um node de cópias de segurança não é limpo há três
  semanas.
- **Uma saída comercial bloqueada recomeça.** O gluetun recebe uma verificação de
  saúde. Ao fim de cinco minutos sem saúde, o contentor é terminado, e o seu
  próximo arranque escolhe outro servidor.

## Discos cifrados e desbloqueio { #encrypted-disks-and-unlocking }

- **Debian** (`debian.encrypt: true`) instala com uma chave de uso único que
  escreves no primeiro arranque (`secrets/luks/<host>.once`). O primeiro `apply`
  substitui-a por `secrets/luks/<host>.key`, e um master recebe também uma chave
  de volume nova. Perder esse ficheiro de chave bloqueia o disco, por isso mantém
  a cópia de segurança da fleet.
- **CoreOS / uCore** cifram na instalação através do Ignition (com cerca de 4 GiB
  de RAM no primeiro arranque).
- **Os anéis Tang** permitem que máquinas cifradas se desbloqueiem no arranque sem
  ninguém presente. Um node corre o módulo `tang` (cada anel é um servidor Tang
  com as suas próprias chaves, `infra` na porta 7500 por omissão), e o bloco
  `unlock:` de um anfitrião associa o seu disco a anéis com um limiar.
- **O SSH no initramfs** (`unlock.ssh: true`: dropbear no Debian, dracut-sshd no
  CoreOS) usa a sua própria chave restrita, `secrets/unlock_ed25519`, que só pode
  executar o desbloqueio.
- `kiwi-server unlock fleet.yaml <host>` reencaminha um anel para uma máquina que
  espera no arranque, e `--manual` entrega a própria chave. Um anel `operator` é
  servido a partir da tua própria máquina enquanto for preciso.
  `vpn-server.unlock_relay` alcança máquinas atrás de NAT.

## MTU do túnel { #tunnel-mtu }

O WireGuard acrescenta os seus próprios cabeçalhos, por isso um túnel transporta
pacotes mais pequenos do que a linha por baixo dele, e um caminho móvel
transporta-os ainda mais pequenos. Um pacote demasiado grande para alguma ligação
pelo caminho é descartado ou fragmentado, e as ligações ficam paradas. O Kiwi
trata disto em três camadas:

- **Duas definições.** `wg_mtu` (por omissão **1376**, um múltiplo de 16 porque o
  WireGuard preenche até 16) é o MTU do gluetun, das configurações de cliente do
  wg-easy e de `wg0`. `bridge_mtu` (por omissão **1500**) é o MTU da rede da
  stack. `validate` recusa um `wg_mtu` cujo pacote preenchido, mais 80 bytes de
  cabeçalhos, não caiba na bridge, e qualquer valor abaixo de 1280, o mínimo com
  que o IPv6 funciona.
- **O MSS é limitado nos dois sentidos** a `wg_mtu - 40`, no wg-easy e no cliente
  VPN, para que o TCP nunca tente um segmento que não possa passar.
- **O TCP sonda por si mesmo.** O cliente VPN corre com
  `net.ipv4.tcp_mtu_probing=1` e `tcp_base_mss=1024`, por isso uma ligação que
  encontre um caminho que descarta pacotes grandes em silêncio encontra um
  tamanho que funciona em vez de ficar pendurada.

### Medir um caminho: `kiwi-server mtu` { #measuring-a-path-kiwi-server-mtu }

```bash
kiwi-server mtu fleet.yaml papaya --ssh core@<address>   # um node
kiwi-server mtu fleet.yaml phone --ssh core@<master>     # um dispositivo de secrets/devices/
kiwi-server mtu fleet.yaml papaya --write                # e escreve wg_mtu no ficheiro fleet
```

A sonda envia pings com don't-fragment através do túnel, de dentro do namespace
que o contém. Mede um node a partir do seu próprio cliente VPN (cuja firewall
descarta os pings que chegam) e um dispositivo a partir do servidor WireGuard.
Começa com um ping normal, depois experimenta todos os múltiplos de 16 a partir
de 1280 e reporta o maior que chega **inteiro**. Enquanto faz os pings, lê os
contadores de remontagem do kernel, para que uma resposta que foi fragmentada
pelo caminho e voltou a ser montada não conte como cabendo.

Também diz o que definir. Para um **dispositivo**, é o `MTU =` do próprio
dispositivo na sua configuração WireGuard, e mais ninguém é afetado. Para um
**node**, é o `wg_mtu` nesse node e no seu master, que `--write` põe no ficheiro
fleet (alterando só essas linhas). Um pacote que só é fragmentado à saída e
remontado pela outra ponta não pode ser visto a partir desta ponta.

Os valores por omissão foram medidos na fleet de teste. Para um telemóvel com
dados móveis, onde os caminhos são muitas vezes só IPv6 atrás de 464XLAT com
encapsulamento aninhado, mede o próprio telemóvel e baixa o seu `MTU =` se a
sonda o indicar.

## VPSes da netcup { #netcup-vpses }

```bash
kiwi-server vps login fleet.yaml         # início de sessão device-flow; o token vai para secrets/
kiwi-server vps list fleet.yaml
kiwi-server vps install fleet.yaml sorbet  # apaga o servidor e instala a ISO do anfitrião
```

`vps install` pergunta primeiro, a não ser que passes `--yes`. Recusa uma ISO que
leve segredos de papel, um `disk:` errado e a cifragem de disco do CoreOS com
menos de 3500 MiB de RAM.
