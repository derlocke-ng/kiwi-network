# Para onde vai

!!! info "Projetado, não construído"
    Esta página resume o
    [projeto do plano de controlo](https://github.com/derlocke-ng/kiwi-server/blob/main/docs/design/control-plane.md)
    do kiwi-server, acordado em outubro de 2026. A não ser que uma linha diga
    *construído*, nada disto existe ainda. O
    [roadmap](https://github.com/derlocke-ng/kiwi-server/blob/main/docs/ROADMAP.md)
    acompanha a ordem.

Hoje o kiwi-server é uma ferramenta de ambiente de trabalho: o ficheiro fleet, os
segredos e a CA vivem na máquina do operador. O plano é torná-lo um **serviço**
que possa correr num node, para que uma rede possa ser criada e gerida sem um
ambiente de trabalho Linux, a partir de um telemóvel e por mais de uma pessoa. As
máquinas continuam reprodutíveis a partir do ficheiro fleet. O plano de controlo
é apenas aquilo que guarda esse ficheiro e corre o renderizador.

## As camadas { #the-layers }

1. **kiwi-modules**: os módulos e o contrato de renderização para uma máquina. *Construído.*
2. **kiwi-stack**: o lado da máquina, a partir de `kiwi-stack apply`. *Construído.*
3. **kiwi-server core**: a fleet, os anfitriões, os targets, as ISOs, a CA, a
   inscrição e o apply, sem interface gráfica, como hoje. *Construído.*
4. **O módulo de controlo**: o core como contentor, com uma API e uma interface
   web, a correr como módulo num node como qualquer outro.
5. **Clientes**: primeiro a interface web. A app GTK fica e fala com a CLI local
   ou com um controlador através da malha, e a CLI também fica. Nenhum front end
   ganha lógica própria.

## O node de controlo { #the-control-node }

O controlador corre num node em casa (o *node de controlo*), acessível a partir
da malha só para administradores, num disco cifrado. Guarda a seed, a chave da
CA, o ficheiro fleet e todas as configurações.

O **master alugado passa a ser infraestrutura de relay substituível**.
Guarda apenas o que precisa para correr: as suas chaves e peers WireGuard, as suas
próprias palavras-passe e o seu certificado. Perdê-lo custa um novo apply a partir
do node de controlo. Perder o node de controlo custa um restauro da cópia de
segurança da fleet.

## Utilizadores { #users }

Um bloco `users:` com dois papéis: um **administrador da fleet**, que pode fazer
tudo, e **administradores de node**, ligados aos seus próprios anfitriões. Um
administrador de node vê o estado, os registos, as cargas de trabalho e as cópias
de segurança desses anfitriões, e inscreve dispositivos nos grupos que o
administrador da fleet permite, mas não vê nada do master, da CA nem dos outros
nodes. O início de sessão é uma palavra-passe mais um certificado de cliente da
CA da fleet ou WebAuthn, e todas as alterações vão para um registo de auditoria.

## Juntar uma máquina { #joining-a-machine }

Os dois caminhos ficam:

- **Uma ISO por anfitrião** com o seu papel (o `build --offline` de hoje), para
  instalações offline.
- **Uma ISO de bootstrap genérica** por target, construída uma vez pela CI e sem
  segredos. No primeiro arranque vai buscar o seu papel ao controlador com um
  **token de adesão** de uso único. Uma máquina instalada à mão ou um VPS
  junta-se com uma linha:
  `curl https://control.<host>.<tld>/join/<token> | sudo bash`.

Cada máquina da linhagem CoreOS deverá correr **uma imagem bootc**, com o papel a
chegar no primeiro arranque.

## Federação e multi-hop { #federation-and-multi-hop }

Redes que confiam na CA umas das outras e delegam nomes umas às outras tornam-se
clientes umas das outras. Com o terceiro modo de saída, o master de uma rede pode
sair para a Internet através do master de outra: **multi-hop**, em que o segundo
master só vê o primeiro. Vários masters geridos por um operador formam então um
serviço de VPN próprio: masters de entrada num país, masters de saída noutros,
Tor lá dentro.

## O orchard { #the-orchard }

O orchard («o pomar») é para quem gere muitos masters para outras pessoas. É uma app separada
ou um plugin do kiwi-server que cria VPSes através das APIs dos fornecedores,
entrega a cada master a sua instalação e um token de registo, recolhe um sinal de
vida de cada master (versão, saúde, disco, última atualização) e distribui
atualizações movendo tags de imagem por canal.

Não consegue iniciar sessão num master, ler uma fleet nem tocar num node. O node
de controlo de cada cliente, em casa, guarda a sua rede. Quem aloja o master não
a consegue ler e corre uma VM por cliente. O suporte da netcup no kiwi-server
(`kiwi-server
vps`, *construído*) é a primeira peça do seu driver de fornecedores.

## Também na lista { #also-on-the-list }

Um master de reserva, podman sem root, IPv6 de ponta a ponta, placas ARM,
intervalos de portas e um módulo de jogos, e um restauro dos dados de um node no
primeiro arranque.
