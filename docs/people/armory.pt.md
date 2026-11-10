# Armory

**Ferramentas web peer-to-peer, armadas com nostr.** Cada ferramenta corre
inteiramente no teu navegador e sincroniza através dos relays que escolheres. Não
há registo, nem servidor nosso, nem rastreio, e tudo é cifrado antes de sair do
teu dispositivo. Instala-o como app web a partir da página inicial.

- **Abre-o:** [derlocke-ng.github.io/armory](https://derlocke-ng.github.io/armory/)
- Repositório: [derlocke-ng/armory](https://github.com/derlocke-ng/armory), GPL-3.0-or-later
- Uma distribuição do [kiwi-framework](index.md) 0.32.1 (fixado por commit).
  Ainda não há tags de versão.
- Em inglês, alemão, francês, espanhol, italiano, neerlandês, polaco e português.

O Armory chamava-se antes weaponized.js.

## As ferramentas { #the-tools }

| Ferramenta | O que faz |
|---|---|
| [**Loadout**](https://derlocke-ng.github.io/armory/loadout/) | Listas de compras e de tarefas partilhadas, inventários da casa e notas em Markdown entre os teus dispositivos e com quem os partilhares. Cifrado de ponta a ponta, com links de edição ou só de leitura. Funciona offline, e os teus dispositivos repõem o que os relays esquecem. |
| [**Uplink**](https://derlocke-ng.github.io/armory/uplink/) | Mensagens e ficheiros para amigos (NIP-17, selados no teu dispositivo), grupos que ficam até o anfitrião os fechar, e salas ao vivo em que entra quem tiver o link e que desaparecem quando ficam vazias. Respostas, reações, edições, mensagens fixadas, pesquisa no dispositivo, mensagens temporárias, e chamadas de voz e vídeo até seis pessoas. |
| [**Payload**](https://derlocke-ng.github.io/armory/payload/) | Partilha de ficheiros: um link que espera, cifrado, nos teus servidores de multimédia até o apagares; ficheiros para amigos e grupos no Uplink; ou diretamente do teu navegador para o deles, sem ficarem guardados em lado nenhum. |
| [**Vault**](https://derlocke-ng.github.io/armory/vault/) | Um gestor de palavras-passe: acessos, notas, cartões e códigos de dois fatores em cada dispositivo onde inicias sessão. Um gerador, um relatório de saúde (palavras-passe fracas, reutilizadas, antigas e, se o ativares, expostas em fugas de dados), importações e exportações, chaves SSH, uma autoridade de certificação SSH, uma CA X.509 e certificados TLS. Selado com uma frase-senha própria. Sem preenchimento automático. |
| [**Authenticator**](https://derlocke-ng.github.io/armory/authenticator/) | Códigos de dois fatores (TOTP) para as tuas contas noutros sítios: adiciona um a partir de um código QR, de um link ou segredo, ou de uma exportação do Google Authenticator. Guardados no mesmo cofre selado. |
| [**Calendar**](https://derlocke-ng.github.io/armory/calendar/) | Os teus calendários do teu próprio Nextcloud ou de qualquer servidor CalDAV: os próximos dias ou um mês, eventos que se repetem, lembretes enquanto uma página está aberta. Nada vai para os relays; o acesso fica selado na tua conta. O teu servidor tem de permitir a origem do Armory (CORS). |
| [**Outpost**](https://derlocke-ng.github.io/armory/outpost/) | Relatórios e diários de cultivo: entradas com fotos, semana a semana, para todos no Outpost, os teus amigos, um círculo ou só tu. Hashtags, gostos e comentários. Selado no teu dispositivo, fotos cifradas. |
| [**Trading Post**](https://derlocke-ng.github.io/armory/tradingpost/) | Um mercado de cânhamo: sementes, estacas e equipamento com fotos, encontrados por categoria e pelo sítio para onde enviam. «Message seller» abre o Uplink. Para quem tem conta (sem verificação de idade). Os vendedores têm de aparecer primeiro no Outpost (três publicações, cada uma com gostos de três pessoas) ou ser aprovados por um moderador. |
| [**DevBoard**](https://derlocke-ng.github.io/armory/devboard/) | Um quadro de avisos para freelancers: diz que estás a contratar ou disponível, assinado com a tua chave, apoiado por prova de trabalho, votado, e desaparece quando expira (24 horas a 30 dias). Público por desenho. |
| [**pongjs**](https://derlocke-ng.github.io/armory/pongjs/) | Pong retro para dois jogadores entre dois navegadores. Partilha um link ou código QR ou escolhe um jogo aberto, ou treina contra o computador offline. |

Está planeado um blogue.

Cada ferramenta é uma das apps do framework, montada com o nome do Armory: o
Loadout é `boards`, o Uplink `chat`, o Outpost `feed`, o Trading Post `market`, o
DevBoard `notices`, o pongjs `pong`.

## Uma conta, todas as ferramentas { #one-account-every-tool }

Inicia sessão ou cria uma conta na página inicial (nome de utilizador e
palavra-passe, ou uma chave nostr) e todas as ferramentas a usam. As listas que
fizeste num dispositivo antes de iniciar sessão são transferidas. Sem conta, cada
dispositivo usa a sua própria chave.

A página de definições abrange o hub inteiro: a tua conta e dispositivos, amigos e
círculos, pessoas bloqueadas, relays, espaços e servidores de multimédia,
notificações e cópias de segurança cifradas.

## Relays e servidores de multimédia { #relays-and-media-servers }

Os relays por omissão do Armory são `wss://nos.lol`, `wss://relay.damus.io`,
`wss://nostr.mom` e `wss://relay.primal.net`. Os seus servidores de multimédia
(Blossom) por omissão são `nostr.download`, `blossom.yakihonne.com`,
`blossom.band` (só fotos) e `blossom.primal.net`. Podes escolher os teus nas
definições.

Os relays só passam os dados, mas não conseguem ler o que foi cifrado antes. O
[modelo de privacidade](index.md#privacy-model) lista o que conseguem ver.

## Moderação { #moderation }

Os moderadores do Armory moderam o Outpost, o Trading Post e o DevBoard. As
entradas do Outpost podem ser marcadas como 18+ ou como publicidade pelo seu
autor, por duas denúncias ou por um moderador. Essas entradas só são mostradas a
pessoas com conta.

## O teu próprio Armory { #your-own-armory }

O Armory é o modelo para o teu próprio hub. Faz um fork (ou usa-o como modelo),
altera `distribution.js` e as traduções e publica-o. Ver
[O teu próprio hub](hubs.md).
