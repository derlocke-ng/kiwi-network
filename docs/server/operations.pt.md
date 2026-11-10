# Operação

Esta página trata do trabalho que vem depois de as máquinas estarem instaladas
e a funcionar: acompanhar o estado delas, guardar os segredos em segurança,
fazer backup do ficheiro fleet e dos dados das máquinas, desbloquear discos
cifrados, afinar a MTU do túnel e instalar num servidor da netcup. Fazes tudo
isto com o kiwi-server a partir do teu próprio computador, o *computador de
administração*, onde estão o ficheiro fleet e os segredos.

## Estado { #status }

O `kiwi-server status` mostra como estão as tuas máquinas, todas ou apenas a
que indicares:

```bash
kiwi-server status fleet.yaml            # todas as máquinas
kiwi-server status fleet.yaml papaya        # uma
```

O kiwi-server liga-se a cada máquina por SSH e limita-se a ler. Cada máquina
comunica a sua função e a sua stack (o conjunto de contentores e serviços que
corre), eventuais problemas, como uma função que falhou ou um contentor parado,
os seus discos e se estão cifrados ou bloqueados, os seus backups e durante
quanto tempo os seus certificados ainda são válidos. Um node de backups indica
também a capacidade. A aplicação Kiwi Server mostra a mesma informação em
*Overview*, na página de cada máquina.

## Segredos { #secrets }

Tudo o que é secreto fica em `secrets/`, a pasta ao lado do ficheiro fleet. Lá
estão a seed de onde derivam todas as palavras-passe geradas, a autoridade de
certificação (CA) da própria rede, as configurações WireGuard, as chaves LUKS
dos discos cifrados e as chaves de anfitrião SSH. O kiwi-server pode manter esta
pasta cifrada e abri-la só enquanto estiveres a trabalhar com ela:

```bash
kiwi-server secrets init fleet.yaml      # secrets/ passa a ser um único ficheiro cifrado com age
kiwi-server secrets unlock fleet.yaml    # abre-o em memória (--for 8h; 0 deixa-o aberto)
kiwi-server secrets lock fleet.yaml
kiwi-server secrets status fleet.yaml
kiwi-server secrets show fleet.yaml papaya [setting]   # as palavras-passe geradas para uma máquina
```

O `secrets init` cria o cofre cifrado. Guarda uma chave no GNOME Keyring e
mostra-te uma **chave de recuperação**, que só é mostrada uma vez. Enquanto o
cofre estiver aberto, qualquer programa que corra com a tua conta de utilizador
o pode ler.

## Backup do próprio ficheiro fleet { #backing-up-the-fleet-itself }

A pasta do ficheiro fleet contém o ficheiro fleet e `secrets/`, e o kiwi-server
faz backup dela por iniciativa própria. Depois de cada `render` ou `build` bem
sucedido (os dois passos que geram a configuração das máquinas e as ISOs de
instalação), cifra a pasta (AES-256 com PBKDF2, 600 000 iterações) e copia-a
para os nodes indicados em `backup.hosts`. Cada um destes nodes guarda as dez
cópias mais recentes. Num computador novo, recuperas a pasta a partir de um
desses nodes. Também podes, a qualquer momento, guardar uma cópia numa pasta à
tua escolha:

```bash
kiwi-server restore --from core@lychee.home  # recupera a pasta do ficheiro fleet
kiwi-server backup fleet.yaml --local /mnt/usb   # ou uma cópia numa pasta, a qualquer momento
```

## Backup dos dados das máquinas { #backing-up-the-machines-data }

O backup dos dados das máquinas é feito com o restic, um programa de backups. Um
node guarda os backups: dá-lhe o módulo `backup-server`, que corre um servidor
REST do restic. Cada máquina de que queres fazer backup recebe o módulo
`backup`, com uma definição que aponta para esse servidor:

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

Todas as noites às 03:00, ou até 15 minutos depois, o restic envia para o
servidor de backups, cifrados, os dados que cada módulo quer guardar. Uma
máquina só chega ao seu próprio repositório no servidor e só pode acrescentar
backups, nunca apagar nada. É por isso que o comando que elimina os snapshots
antigos corre no computador de administração. Um snapshot é o nome que o restic
dá ao estado guardado numa execução de backup. O primeiro comando abaixo é para
a própria máquina, o segundo para o teu computador:

```bash
sudo kiwi-stack backup | snapshots | restore [--at TIME] MODULE...   # na máquina
kiwi-server prune fleet.yaml            # mantém 7 diários, 4 semanais, 6 mensais
```

O restauro foi testado entre dois nodes: os backups do papaya foram
restaurados no lychee.

### Na próxima versão { #coming-in-the-next-release }

!!! info "No ramo `several-servers`"
    Este trabalho já está nos ramos `several-servers` do kiwi-modules e do
    kiwi-server, mas ainda não foi integrado nem publicado. O uso de vários
    servidores de backups e o restauro automático foram testados em hardware.
    A verificação de estado da VPN não foi.

- **Vários servidores de backups.** `backup.servers` aceita uma lista de
  servidores, e cada servidor recebe uma cópia completa só sua. Se um servidor
  falhar, só a cópia dele é afetada. Um restauro usa a cópia mais recente, seja
  qual for o servidor que a tenha, e `kiwi-stack snapshots` lista os snapshots
  servidor a servidor. A definição `server`, com um único servidor, continua a
  funcionar.
- **Uma máquina reconstruída restaura-se a si própria.** Uma máquina
  reconstruída encontra no servidor backups de si mesma, embora não tenha feito
  nenhum deles. Nesse caso, restaura sozinha todos os módulos antes de fazer o
  seu primeiro backup e, a partir daí, faz backups como antes. Esta é a
  predefinição, `backup.restore: auto`. Com `hold`, a máquina espera até
  executares `kiwi-stack restore` ou `kiwi-stack backup --new`.
- **Eliminação dos snapshots antigos com um temporizador.**
  `kiwi-server prune fleet.yaml --every week` (ou `day`) instala no teu
  computador um temporizador (timer) de utilizador do systemd. O teu computador
  é o único sítio onde estão as chaves que têm permissão para apagar. Se uma
  execução ficar por fazer, é feita quando voltares a iniciar sessão. O `kiwi-server status`
  mostra cada cópia de backup e avisa quando os snapshots antigos de um node de
  backups não são eliminados há três semanas.
- **Uma ligação bloqueada ao fornecedor de VPN comercial recupera sozinha.** O
  gluetun, o contentor do cliente VPN, passa a ter uma verificação de estado
  (health check), que confirma regularmente se a ligação continua a funcionar.
  Quando a verificação falha durante cinco minutos, o contentor é terminado e, ao
  arrancar de novo, escolhe outro servidor.

## Discos cifrados e desbloqueio { #encrypted-disks-and-unlocking }

Um disco cifrado tem de ser desbloqueado sempre que a máquina arranca. Esta
secção descreve como cada sistema de destino (o sistema operativo com que uma
máquina é instalada) cifra o disco e como o disco pode ser desbloqueado com ou
sem alguém presente.

- **O Debian** (`debian.encrypt: true`) é instalado com uma chave temporária,
  que escreves no primeiro arranque. Encontra-la em `secrets/luks/<host>.once`.
  O primeiro `apply` substitui-a por `secrets/luks/<host>.key`, e um master
  recebe nessa altura também uma nova chave de volume. Se perderes esse
  ficheiro de chave, o disco fica bloqueado, por isso mantém o backup do
  ficheiro fleet em dia.
- **O CoreOS e o uCore** cifram o disco durante a instalação, através do
  Ignition, a ferramenta que configura uma máquina CoreOS no primeiro arranque.
  Para isso, a máquina precisa de cerca de 4 GiB de RAM no primeiro arranque.
- **Os anéis Tang** permitem às máquinas cifradas desbloquear os discos no
  arranque sem ninguém presente. O Tang é um pequeno servidor a quem uma
  máquina pede ajuda, pela rede, para desbloquear o disco. Um node corre o
  módulo `tang`, e cada anel é um servidor Tang com as suas próprias chaves.
  Por predefinição há um anel, `infra`, na porta 7500. O bloco `unlock:` de uma
  máquina associa o disco a um ou mais anéis e define um limiar, ou seja, o
  número de anéis que têm de responder.
- **O SSH no initramfs** (`unlock.ssh: true`) permite-te aceder a uma máquina
  que está à espera de que o disco seja desbloqueado. O initramfs é o pequeno
  sistema que corre antes de o disco estar aberto. O servidor SSH que lá corre é
  o dropbear no Debian e o dracut-sshd no CoreOS. Aceita uma chave própria,
  com acesso restrito, `secrets/unlock_ed25519`, que só serve para fazer o
  desbloqueio.
- `kiwi-server unlock fleet.yaml <host>` reencaminha um anel para uma máquina
  que está à espera no arranque, para que ela possa usar um anel a que não
  chega sozinha. Com `--manual`, entrega diretamente a chave. Um anel chamado
  `operator` é servido a partir do teu próprio computador enquanto for
  necessário. O `vpn-server.unlock_relay` torna um anel acessível através do
  master para as máquinas atrás de NAT.

## MTU do túnel { #tunnel-mtu }

A MTU é o maior pacote que uma ligação de rede transporta inteiro. O WireGuard
acrescenta os seus próprios cabeçalhos a cada pacote, pelo que um túnel
transporta pacotes mais pequenos do que a ligação por baixo dele, e uma ligação
móvel transporta-os ainda mais pequenos. Um pacote grande demais para uma das
ligações do percurso é descartado ou fragmentado, e as ligações ficam
bloqueadas. A Kiwi Network resolve isto de três maneiras:

- **Duas definições.** `wg_mtu` é a MTU do gluetun (o cliente VPN), das
  configurações de cliente emitidas pelo wg-easy (o servidor WireGuard) e da
  interface WireGuard `wg0`. A predefinição é **1376**, um múltiplo de 16,
  porque o WireGuard completa cada pacote até ao múltiplo de 16 bytes seguinte.
  `bridge_mtu` é a MTU da rede da stack, que liga os contentores de uma máquina.
  A predefinição é **1500**. O `validate` recusa um `wg_mtu` que, depois de
  completado e somado a 80 bytes de cabeçalhos, não caiba na bridge. Recusa
  também qualquer valor abaixo de 1280, a MTU mínima com que o IPv6 funciona.
- **O MSS é limitado nos dois sentidos.** O MSS é a maior quantidade de dados
  que o TCP põe num pacote. O wg-easy e o cliente VPN limitam-no ambos a
  `wg_mtu - 40`, para que o TCP nunca tente um segmento que não consiga passar.
- **O TCP encontra sozinho um tamanho que funcione.** O cliente VPN corre com
  `net.ipv4.tcp_mtu_probing=1` e `tcp_base_mss=1024`. Quando uma ligação passa
  por um percurso que descarta pacotes grandes sem avisar, o TCP experimenta
  pacotes mais pequenos até encontrar um tamanho que funcione, em vez de ficar
  pendurado.

### Medir um percurso: `kiwi-server mtu` { #measuring-a-path-kiwi-server-mtu }

Para saberes o que o percurso até um node ou um dispositivo aguenta na
realidade, mede-o:

```bash
kiwi-server mtu fleet.yaml papaya --ssh core@<address>   # um node
kiwi-server mtu fleet.yaml phone --ssh core@<master>     # um dispositivo de secrets/devices/
kiwi-server mtu fleet.yaml papaya --write                # e escreve wg_mtu no ficheiro fleet
```

A medição envia pings pelo túnel com a flag don't-fragment, para que não possam
ser fragmentados pelo caminho. Envia-os a partir do namespace de rede onde está
o túnel. Um namespace de rede é um ambiente de rede separado dentro de uma
máquina, como o que um contentor tem. Um node é medido a partir do seu próprio
cliente VPN, porque a firewall do cliente descarta os pings que chegam. Um
dispositivo é medido a partir do servidor WireGuard. A medição começa com um
ping normal, depois experimenta todos os múltiplos de 16 a partir de 1280 e
indica o maior tamanho que chega **inteiro**. Enquanto envia os pings, lê os
contadores de reconstrução de fragmentos do kernel. Assim, uma resposta que foi
fragmentada pelo caminho e voltou a ser montada não conta como tendo cabido.

A medição diz-te também o que deves definir. Para um **dispositivo**, é a linha
`MTU =` na configuração WireGuard do próprio dispositivo, e mais ninguém é
afetado. Para um **node**, é o `wg_mtu` desse node e do seu master. Com
`--write`, a medição escreve o valor no ficheiro fleet e só altera essas
linhas. Há uma coisa que não se consegue ver deste lado: um pacote que só é
fragmentado à saída e que o outro extremo volta a montar.

As predefinições foram medidas na rede de testes. Um telemóvel com dados
móveis precisa de uma medição própria, porque os percursos móveis são muitas
vezes só IPv6, atrás de 464XLAT, com encapsulamento dentro de encapsulamento.
Mede o próprio telemóvel e baixa o `MTU =` dele, se a medição o indicar.

## VPS da netcup { #netcup-vpses }

A netcup é um fornecedor de alojamento e, por enquanto, é o único com que o
kiwi-server consegue instalar sozinho um servidor alugado (um VPS). Fá-lo
através da API do Server Control Panel da netcup. Outros fornecedores de
alojamento estão [planeados](roadmap.md#more-hosters-and-network-boot), sob a
forma de plugins.

```bash
kiwi-server vps login fleet.yaml         # início de sessão device-flow; o token vai para secrets/
kiwi-server vps list fleet.yaml
kiwi-server vps install fleet.yaml sorbet  # apaga o servidor e instala a ISO da máquina
```

O `vps install` apaga o servidor, por isso pede confirmação, a não ser que
passes `--yes`. Recusa-se a instalar em três casos: quando a ISO traz segredos
da função, quando `disk:` indica o disco errado e quando um disco CoreOS vai ser
cifrado num servidor com menos de 3500 MiB de RAM.
