# As aplicações do framework

O kiwi-framework é o software que permite a uma comunidade ter o seu próprio
hub. Esta página descreve as dez aplicações que vêm com ele, entre as quais um
mercado aberto, um feed da comunidade, um chat e a partilha de ficheiros.

O framework dá às suas aplicações nomes simples, como `market`. Uma
distribuição, ou seja, um hub concreto feito com o framework, **monta** as
aplicações que quer. Montar uma aplicação é usá-la num espaço, isto é, numa
comunidade com moderadores e relays próprios, e dar-lhe um nome escolhido pelo
hub. A mesma aplicação pode ser montada muitas vezes. Um banco de sementes e
uma loja de pedras preciosas, por exemplo, são o mesmo código `market` em dois
espaços. Cada um tem os seus moderadores e os seus relays, e os dois aparecem
como dois mosaicos no mesmo hub.

| Aplicação | O que é | Nome da montagem no Armory |
|---|---|---|
| `market` | **Um mercado aberto** para a comunidade servida por uma montagem. Um anúncio tem fotos, um preço e, conforme o caso, os locais de onde e para onde o vendedor envia ou a possibilidade de levantamento em mão. Os compradores encontram os anúncios por categoria e pela sua própria localização. A pesquisa usa etiquetas que os relays conseguem comparar, mas não conseguem ler. O comprador escreve ao vendedor no chat, onde já encontra uma mensagem sobre o anúncio pronta a enviar. Um anúncio pode ser reservado, marcado como vendido, renovado e denunciado, e expira ao fim de 30 a 90 dias. Uma montagem pode exigir que os vendedores já tenham participado num feed ou que tenham sido aprovados por um moderador. | Trading Post |
| `feed` | **Um feed da comunidade.** As pessoas publicam entradas com fotos e hashtags, e os outros podem pôr gosto e comentar. Uma entrada pode ser para todo o espaço, para os teus amigos, para um círculo (um grupo dos teus amigos) ou só para ti. Um diário é uma série de entradas com uma capa. As entradas podem ser marcadas como 18+ ou como publicidade. | Outpost |
| `chat` | **Mensagens.** Envias mensagens privadas e ficheiros aos teus amigos (NIP-17). Os grupos existem até o anfitrião os fechar, e as salas ao vivo desaparecem quando sai a última pessoa. O chat tem respostas, reações, edição de mensagens, mensagens fixadas, pesquisa no dispositivo e mensagens que desaparecem. As chamadas de voz e de vídeo funcionam com até seis pessoas. | Uplink |
| `notices` | **Um quadro de avisos** para notas públicas. Cada nota é assinada pelo autor e exige uma prova de trabalho, um pequeno cálculo que torna caro publicar em massa. As notas podem ser votadas e denunciadas, e expiram. | DevBoard |
| `boards` | **Listas e notas partilhadas**: listas de verificação, inventários com quantidades e notas em markdown. São cifradas de ponta a ponta e partilham-se com links que permitem editar ou apenas ver. | Loadout |
| `payload` | **Partilha de ficheiros** de três formas: um link para ficheiros guardados, cifrados, nos teus servidores de multimédia, ficheiros enviados a amigos e grupos, ou envio direto de um navegador para outro. | Payload |
| `vault` | **Um gestor de palavras-passe** para acessos, notas, cartões e códigos de dois fatores. Tem um gerador de palavras-passe e um relatório de saúde. Também gere chaves SSH, uma CA SSH, uma CA X.509 e certificados TLS. É cifrado com uma frase-senha própria. | Vault |
| `authenticator` | **Códigos de dois fatores** (TOTP). Ficam guardados no mesmo cofre cifrado que as entradas do gestor de palavras-passe. | Authenticator |
| `calendar` | **Os teus calendários** do Nextcloud ou de qualquer outro servidor CalDAV. Nada é enviado para os relays. | Calendar |
| `pong` | **Pong para dois jogadores**, cada um no seu navegador. | pongjs |

Todos os hubs têm ainda uma página inicial, uma página de conta e uma página
de definições. As definições abrangem a tua conta e os teus dispositivos, os
amigos e os círculos, as pessoas bloqueadas, os relays, os espaços, os
servidores de multimédia e os backups. As notificações não são uma aplicação à
parte. Fazem parte do próprio hub.

## Espaços e montagens { #spaces-and-mounts }

- Um **espaço** é uma comunidade com nome e dono. Tem um id, a chave do dono,
  um nome, moderadores, relays próprios e uma indicação que o assinala como
  espaço para adultos. Segue o modelo das comunidades moderadas do nostr
  (NIP-72), por isso outros clientes nostr conseguem lê-lo. Cada publicação e
  cada anúncio pertencem a um único espaço.
- Uma **montagem** é uma aplicação usada num espaço, com id, nome e ícone
  próprios. Para pores no teu hub a loja de outra comunidade, basta
  uma linha que defina a montagem.
- **Um link indica a aplicação, o espaço e o item, mas nunca o endereço do
  hub.** Um hub abre esse link com a sua própria montagem dessa aplicação e
  desse espaço. Se não tiver essa montagem, diz-te de quem é o espaço e
  oferece-te uma forma de voltar atrás.
- **Os espaços são federados**, ou seja, um espaço não está preso a um hub.
  Dois hubs podem servir o mesmo espaço. Os relays de um espaço só transportam
  o conteúdo desse espaço.

Há três coisas planeadas que ainda não foram implementadas. Os hubs vão
anunciar-se com um manifesto assinado, para que outros os possam encontrar. As
aprovações vão ser acrescentadas como forma de moderação. E as pessoas vão
poder seguir um espaço que o seu hub não inclui.

## Escrever uma aplicação { #writing-an-app }

Este comando cria o esqueleto de uma nova aplicação na tua distribuição:

```bash
npm run new-app -- <id> "<Name>" <icon>
```

O resultado é uma aplicação React que usa o kit de interface do framework.
Tem uma estrutura base (a moldura à volta das páginas da aplicação), uma
página inicial e uma página de definições, os textos em todas as línguas, uma
entrada no registo de aplicações e uma montagem. As aplicações usam apenas a
API pública do framework e nunca acedem diretamente ao armazenamento nem às
chaves. Para compilares e publicares um hub, vê
[O teu próprio hub](hubs.md).
