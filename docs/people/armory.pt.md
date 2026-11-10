# Armory

O Armory é o primeiro hub construído com o kiwi-framework, o software que
permite a qualquer comunidade ter o seu próprio hub. Na linguagem do
framework, o Armory é uma **distribuição**: o framework juntamente com um
nome, relays predefinidos e um conjunto escolhido de aplicações. O Armory
inclui as dez aplicações do framework e dá-lhes nomes seus. O mercado e o feed
estão pensados para quem cultiva cânhamo. Esse tema foi escolhido por este hub
e não pelo framework, e outra comunidade usaria as mesmas aplicações para o
seu próprio tema. Podes usar o Armory tal como está ou copiá-lo como modelo
para o teu próprio hub.

Todas as ferramentas correm inteiramente no teu navegador. Sincronizam-se
através de relays, que são servidores que guardam os teus dados e os passam
adiante, e és tu que escolhes que relays usar. Não precisas de te registar, o
projeto não tem nenhum servidor seu para o Armory e nada te rastreia. Tudo é
cifrado antes de sair do teu dispositivo. Podes instalar o Armory como
aplicação web a partir da página inicial.

- **Abrir:** [derlocke-ng.github.io/armory](https://derlocke-ng.github.io/armory/)
- O repositório é o [derlocke-ng/armory](https://github.com/derlocke-ng/armory),
  e a licença é GPL-3.0-or-later.
- O Armory é uma distribuição do [kiwi-framework](index.md) 0.32.1, fixado
  num commit específico. O Armory em si ainda não tem tags de versão.
- Está disponível em inglês, alemão, francês, espanhol, italiano, neerlandês,
  polaco e português.

Antes, o Armory chamava-se weaponized.js.

## As ferramentas { #the-tools }

| Ferramenta | O que faz |
|---|---|
| [**Loadout**](https://derlocke-ng.github.io/armory/loadout/) | Listas de compras e de tarefas partilhadas, inventários da casa e notas em markdown. Mantêm-se sincronizadas em todos os teus dispositivos e com as pessoas com quem as partilhas. Tudo é cifrado de ponta a ponta, e partilhas uma lista com um link que permite editar ou apenas ver. O Loadout funciona sem ligação, e os teus dispositivos devolvem aos relays o que os relays tenham perdido. |
| [**Uplink**](https://derlocke-ng.github.io/armory/uplink/) | Mensagens e ficheiros para amigos (NIP-17, cifrados no teu dispositivo). Os grupos existem até o anfitrião os fechar. Qualquer pessoa com o link pode entrar numa sala ao vivo, e a sala desaparece quando sai a última pessoa. O Uplink tem respostas, reações, edição de mensagens, mensagens fixadas, pesquisa no teu dispositivo e mensagens que desaparecem. As chamadas de voz e de vídeo funcionam com até seis pessoas. |
| [**Payload**](https://derlocke-ng.github.io/armory/payload/) | Partilha de ficheiros de três formas. Podes criar um link para ficheiros que ficam cifrados nos teus servidores de multimédia até os apagares. Podes enviar ficheiros a amigos e grupos no Uplink. Ou podes enviar ficheiros diretamente do teu navegador para o navegador de outra pessoa, e nesse caso não ficam guardados em lado nenhum. |
| [**Vault**](https://derlocke-ng.github.io/armory/vault/) | Um gestor de palavras-passe para acessos, notas, cartões e códigos de dois fatores, disponível em todos os dispositivos onde inicias sessão. Tem um gerador de palavras-passe e um relatório de saúde, que encontra palavras-passe fracas, repetidas e antigas e, se ativares essa verificação, também as que apareceram em fugas de dados. O Vault importa e exporta entradas. Também gere chaves SSH, uma autoridade de certificação SSH, uma CA X.509 e certificados TLS. É cifrado com uma frase-senha própria. Não preenche palavras-passe nos sites por ti. |
| [**Authenticator**](https://derlocke-ng.github.io/armory/authenticator/) | Códigos de dois fatores (TOTP) para as tuas contas noutros serviços. Adicionas uma conta a partir de um código QR, de um link ou de um segredo, ou de uma exportação do Google Authenticator. Os códigos ficam guardados no mesmo cofre cifrado que o Vault usa. |
| [**Calendar**](https://derlocke-ng.github.io/armory/calendar/) | Os teus calendários do teu próprio Nextcloud ou de qualquer outro servidor CalDAV. Mostra os próximos dias ou um mês, trata os eventos que se repetem e lembra-te dos eventos enquanto houver uma página aberta. Nada é enviado para os relays, e os dados de acesso ao teu servidor ficam guardados, cifrados, na tua conta. O teu servidor tem de aceitar pedidos vindos da origem do Armory (CORS). |
| [**Outpost**](https://derlocke-ng.github.io/armory/outpost/) | O feed do Armory, usado para relatórios e diários de cultivo. Publicas entradas com fotos, semana a semana. Cada entrada pode ser para todos no Outpost, para os teus amigos, para um círculo de amigos ou só para ti. As entradas podem ter hashtags, gostos e comentários. São cifradas no teu dispositivo, tal como as fotos. |
| [**Trading Post**](https://derlocke-ng.github.io/armory/tradingpost/) | O mercado do Armory, usado para cânhamo: sementes, estacas e equipamento. Os anúncios têm fotos, e os compradores encontram-nos por categoria e pelos locais para onde o vendedor envia. O botão para escrever ao vendedor abre o Uplink. Precisas de uma conta para usar o Trading Post, e não há verificação de idade. Para poder vender, uma pessoa tem de ter publicado no Outpost (três publicações, cada uma com gostos de três pessoas) ou ter sido aprovada por um moderador. |
| [**DevBoard**](https://derlocke-ng.github.io/armory/devboard/) | Um quadro de avisos para freelancers. Publicas uma nota a dizer que estás a contratar ou que estás disponível. Cada nota é assinada com a tua chave e exige uma prova de trabalho, um pequeno cálculo que torna caro publicar em massa. Os outros podem votar nas notas. Uma nota desaparece quando expira, entre 24 horas e 30 dias depois de publicada. Todas as notas são públicas, e isso é intencional. |
| [**pongjs**](https://derlocke-ng.github.io/armory/pongjs/) | Pong retro para dois jogadores, cada um no seu navegador. Para começar um jogo, partilha um link ou um código QR, ou escolhe um dos jogos abertos. Também podes treinar contra o computador, sem ligação. |

Está planeado um blogue.

Cada ferramenta é uma das aplicações do framework, com um nome dado pelo
Armory. O Loadout é a aplicação `boards` do framework, o Uplink é a `chat`, o
Outpost é a `feed`, o Trading Post é a `market`, o DevBoard é a `notices` e o
pongjs é a `pong`.

## Uma conta para todas as ferramentas { #one-account-every-tool }

Inicias sessão ou crias uma conta na página inicial, com nome de utilizador e
palavra-passe ou com uma chave nostr. A partir daí, todas as ferramentas usam
essa conta. As listas que criaste num dispositivo antes de iniciares sessão
passam para a conta. Se não usares conta, cada dispositivo funciona com a sua
própria chave.

A página de definições vale para o hub inteiro. Abrange a tua conta e os teus
dispositivos, os amigos e os círculos, as pessoas bloqueadas, os relays, os
espaços e os servidores de multimédia, as notificações e os backups cifrados.

## Relays e servidores de multimédia { #relays-and-media-servers }

Os relays predefinidos do Armory são `wss://nos.lol`, `wss://relay.damus.io`,
`wss://nostr.mom` e `wss://relay.primal.net`. Os servidores de multimédia
guardam os ficheiros que envias e usam um protocolo chamado Blossom. Os
servidores de multimédia predefinidos do Armory são `nostr.download`,
`blossom.yakihonne.com`, `blossom.band` (que só aceita fotos) e
`blossom.primal.net`. Podes escolher os teus próprios relays e servidores de
multimédia nas definições.

Os relays guardam os dados e passam-nos adiante, mas não conseguem ler nada
que tenha sido cifrado antes do envio. O que os relays conseguem ver está
descrito no [modelo de privacidade](index.md#privacy-model).

## Moderação { #moderation }

Os moderadores do Armory são responsáveis pelo Outpost, pelo Trading Post e
pelo DevBoard. Uma entrada do Outpost pode ser marcada como 18+ ou como
publicidade. Essa marca pode ser posta pelo autor, por um moderador ou por
duas denúncias. As entradas marcadas só são mostradas a quem tem conta.

## O teu próprio Armory { #your-own-armory }

O Armory é também o modelo para o teu próprio hub. Faz fork do repositório ou
usa-o como template no GitHub, altera o `distribution.js` e as traduções, e publica o
resultado. Os passos estão descritos em [O teu próprio hub](hubs.md).
