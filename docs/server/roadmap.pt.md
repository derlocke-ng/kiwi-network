# O que aí vem

Esta página descreve aquilo em que o kiwi-server deverá vir a tornar-se e que
partes desse plano já existem.

!!! info "Concebido, ainda não implementado"
    Esta página resume o
    [desenho do plano de controlo](https://github.com/derlocke-ng/kiwi-server/blob/main/docs/design/control-plane.md)
    do kiwi-server, acordado em outubro de 2026. Nada do que aqui se descreve
    existe ainda, a não ser que a linha diga *implementado*. O
    [roteiro](https://github.com/derlocke-ng/kiwi-server/blob/main/docs/ROADMAP.md)
    acompanha a ordem do trabalho.

Hoje, o kiwi-server é uma ferramenta de desktop. O ficheiro fleet, os segredos e
a CA (a autoridade de certificação da rede) ficam no teu próprio computador. O
plano é transformá-lo num **serviço** que possa correr num node. Assim, passa a
ser possível criar e gerir uma rede sem um desktop Linux, a partir de um
telemóvel, e várias pessoas podem geri-la em conjunto. As máquinas continuam a poder ser reproduzidas a
partir do ficheiro fleet. O plano de controlo é a parte que guarda esse ficheiro
e corre o programa que gera, a partir dele, a configuração de cada máquina.

## As camadas { #the-layers }

O desenho divide o software em cinco camadas.

1. **O kiwi-modules** contém os módulos e o contrato de geração, que define
   como se gera a configuração de uma máquina. *Implementado.*
2. **O kiwi-stack** é a parte que corre na máquina. O ponto de partida é
   o `kiwi-stack apply`, que instala na máquina uma configuração gerada.
   *Implementado.*
3. **O núcleo do kiwi-server** trata do ficheiro fleet, das máquinas, dos
   sistemas de destino, das ISOs, da CA, da adição de dispositivos e do
   `apply`. Tal como hoje, não tem interface gráfica própria (headless).
   *Implementado.*
4. **O módulo de controlo** é o núcleo empacotado num contentor, com uma API e
   uma interface web. Corre num node como qualquer outro módulo.
5. **Os clientes** são os programas com que trabalhas com o módulo de controlo.
   A interface web vem primeiro. A aplicação GTK mantém-se e comunica ou com a
   CLI local, ou com um controlador (um módulo de controlo em funcionamento)
   através da mesh, a rede WireGuard privada. A CLI também se mantém. Toda a
   lógica fica no núcleo, e nenhum cliente tem lógica própria.

## O node de controlo { #the-control-node }

O controlador corre num node em casa, a que se chama *node de controlo*. Só os
administradores lhe podem aceder, e apenas a partir da mesh, e o seu disco está
cifrado. Guarda a seed, a chave da CA, o ficheiro fleet e todas as
configurações.

O **master alugado passa a ser um relay que se pode substituir**. Faz passar o
tráfego da rede e guarda apenas aquilo de que precisa para funcionar: as suas
chaves e peers WireGuard, as suas próprias palavras-passe e o seu certificado.
Se perderes o master, voltas a aplicá-lo a partir do node de controlo. Se
perderes o node de controlo, restauras o backup do ficheiro fleet.

## Utilizadores { #users }

Um bloco `users:` define utilizadores, cada um com um de dois papéis. Um
**administrador da rede** (fleet admin) pode fazer tudo. Um **administrador de
node** (node admin) está limitado às suas próprias máquinas. Vê o estado, os
registos, as cargas de trabalho e os backups dessas máquinas e pode adicionar
dispositivos aos grupos que o administrador da rede permitir. Não vê nada do
master, da CA nem dos outros nodes. Para iniciar sessão, um utilizador precisa
de uma palavra-passe e, além disso, de um certificado de cliente emitido pela
CA da rede ou de WebAuthn. Todas as alterações ficam escritas num registo de
auditoria.

## Juntar uma máquina à rede { #joining-a-machine }

Há duas maneiras de uma máquina entrar na rede, e ambas se mantêm:

- **Uma ISO por máquina** que traz a função dessa máquina, que é o atual
  `build --offline`. Serve para instalações sem ligação à rede.
- **Uma ISO de arranque genérica** por sistema de destino, gerada uma única vez
  pela CI e sem segredos nenhuns. No primeiro arranque, a máquina vai buscar a
  sua função ao controlador com um **token de adesão** que só serve uma vez.
  Uma máquina instalada à mão, ou um VPS, junta-se com uma única linha:
  `curl https://control.<host>.<tld>/join/<token> | sudo bash`.

A ideia é que todas as máquinas da família CoreOS corram **uma única imagem
bootc**, uma imagem de contentor arrancável que é igual para todas. A máquina
recebe a sua função no primeiro arranque.

## Federação e multi-hop { #federation-and-multi-hop }

A federação liga Kiwi Networks separadas. Redes que confiam na CA umas das
outras e delegam nomes umas nas outras passam a ser clientes umas das outras. Um
master tem três modos de saída, que definem como o seu tráfego chega à
Internet. Com o terceiro, o master de uma rede envia o seu tráfego para a
Internet através do master de outra rede. A isto chama-se **multi-hop**, e o
segundo master só vê o primeiro. Quem gere vários masters desta forma tem um
serviço de VPN próprio, com masters de entrada num país, masters de saída
noutros países e o Tor dentro da rede.

## O orchard { #the-orchard }

O orchard («pomar» em inglês) é o serviço planeado para quem gere muitos
masters para outras pessoas. É uma aplicação à parte ou um plugin do
kiwi-server. Cria VPS através das API dos fornecedores de alojamento e dá a cada
master a sua instalação e um token de registo. Recebe de cada master um
heartbeat, ou seja, um relatório de estado regular (versão, estado, disco,
última atualização). Distribui as atualizações mudando a tag da imagem de cada
canal de atualização.

O orchard não consegue iniciar sessão num master, ler um ficheiro fleet nem
alterar um node. Cada cliente, ou seja, cada pessoa cujo master é gerido por
outra, mantém a sua rede no seu próprio node de controlo, em casa. O ficheiro
fleet e as chaves ficam lá, por isso o fornecedor de alojamento que corre a
máquina virtual do master não consegue ler os dados da rede desse cliente. O
master de cada cliente corre numa máquina virtual só sua. O orchard precisa de
um driver para as API dos fornecedores, e o suporte da netcup no
kiwi-server (`kiwi-server vps`, *implementado*) é a primeira peça.

## Mais fornecedores de alojamento e arranque pela rede { #more-hosters-and-network-boot }

*Planeado.* O objetivo é que uma máquina possa ser instalada de forma
totalmente automática, esteja onde estiver.

- **Fornecedores de alojamento como plugins.** Hoje, o suporte da netcup está
  integrado no kiwi-server. O plano é ter um repositório à parte para as API
  dos fornecedores, para que qualquer pessoa possa acrescentar a AWS, a Hetzner
  e outros. Um plugin funcionaria como funciona hoje o suporte da netcup: cria
  ou apaga um servidor, põe-lhe a instalação e arranca-o.
- **O Wake-on-LAN e o arranque PXE** estão planeados para as máquinas em casa.
  O Wake-on-LAN liga uma máquina através da rede, e o PXE permite-lhe arrancar
  a partir da rede. Um node acorda então e instala-se a si próprio pela rede,
  sem precisar de nenhuma pen USB.

## Também na lista { #also-on-the-list }

O roteiro inclui ainda um master de reserva, o podman rootless, IPv6 de ponta a
ponta, placas ARM, intervalos de portas e um módulo para jogos, bem como o restauro
dos dados de um node no primeiro arranque.
