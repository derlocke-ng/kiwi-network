# As apps do framework

O kiwi-framework traz as suas apps com nomes simples. Uma distribuição
**monta-as** num espaço e com um nome próprio. Uma app pode ser montada muitas
vezes: um banco de sementes e uma loja de pedras preciosas são o mesmo código
`market` em dois espaços, cada um com os seus próprios moderadores e relays, como
dois mosaicos num só hub.

| App | O que é | O Armory monta-a como |
|---|---|---|
| `market` | **Um mercado aberto** para a comunidade que uma montagem serve. Os anúncios têm fotos, um preço, de onde e para onde enviam, ou recolha no local. Os compradores encontram-nos por categoria e pelo sítio onde estão, através de etiquetas de pesquisa que os relays conseguem fazer corresponder mas não ler. Os compradores escrevem ao vendedor no chat, com uma mensagem sobre o anúncio já redigida. Os anúncios podem ser reservados, vendidos, renovados e denunciados, e expiram ao fim de 30 a 90 dias. Uma montagem pode exigir que os vendedores tenham aparecido primeiro num feed, ou que tenham sido aprovados por um moderador | Trading Post |
| `feed` | **Um feed da comunidade**: entradas com fotos, hashtags, gostos e comentários para o espaço, para amigos, para um círculo ou só para ti, além de diários (uma série de entradas com uma capa). As entradas podem ser marcadas como 18+ ou como publicidade | Outpost |
| `chat` | **Mensagens**: mensagens privadas e ficheiros para amigos (NIP-17), grupos que ficam até o anfitrião os fechar, salas ao vivo que desaparecem quando ficam vazias, respostas, reações, edições, mensagens fixadas, pesquisa no dispositivo, mensagens temporárias, e chamadas de voz e vídeo até seis pessoas | Uplink |
| `notices` | **Um quadro de avisos** de notas públicas e assinadas com prova de trabalho, votos, denúncias e uma data de expiração | DevBoard |
| `boards` | **Listas e notas partilhadas**: listas de verificação, inventários com quantidades e notas em Markdown, cifradas de ponta a ponta, com links de edição ou só de leitura | Loadout |
| `payload` | **Partilha de ficheiros**: um link que espera, cifrado, nos teus servidores de multimédia; ficheiros para amigos e grupos; ou diretamente de navegador para navegador | Payload |
| `vault` | **Um gestor de palavras-passe**: acessos, notas, cartões, códigos de dois fatores, um gerador e um relatório de saúde, chaves SSH, uma CA SSH, uma CA X.509 e certificados TLS. Selado com uma frase-senha própria | Vault |
| `authenticator` | **Códigos de dois fatores** (TOTP), guardados no mesmo cofre selado | Authenticator |
| `calendar` | **Os teus calendários** do Nextcloud ou de qualquer servidor CalDAV. Nada vai para os relays | Calendar |
| `pong` | **Pong para dois jogadores** entre navegadores | pongjs |

Todos os hubs têm também uma página inicial, definições (a tua conta e
dispositivos, amigos e círculos, pessoas bloqueadas, relays, espaços, servidores
de multimédia, cópias de segurança) e uma página de conta. As notificações vivem
no próprio hub.

## Espaços e montagens { #spaces-and-mounts }

- Um **espaço** é uma comunidade com nome e dono: um id, uma chave de dono, um
  nome, moderadores, relays próprios e uma marca de conteúdo adulto. É inspirado
  nas comunidades moderadas do nostr (NIP-72), por isso outros clientes nostr
  conseguem lê-lo. Cada publicação e cada anúncio pertence a exatamente um
  espaço.
- Uma **montagem** (mount) é código de uma app num espaço, com id, nome e ícone
  próprios. Importar a loja de outra comunidade é uma linha de montagem.
- **Os links indicam a app, o espaço e o item, nunca o anfitrião.** Um hub abre um
  link com a sua própria montagem dessa app e desse espaço. Sem ela, diz de quem é
  o espaço e oferece o caminho de volta.
- **Os espaços são federados.** Dois hubs podem servir o mesmo espaço, e os relays
  de um espaço só transportam o conteúdo dele.

Planeado: hubs que se anunciam com um manifesto assinado para que outros os
encontrem, aprovações de moderação, e pessoas a seguir um espaço que o seu hub
não traz.

## Escrever uma app { #writing-an-app }

```bash
npm run new-app -- <id> "<Name>" <icon>
```

Isto cria o esqueleto de uma app React sobre o kit de interface do framework,
com uma shell, página inicial e página de definições, textos em todas as
línguas, uma entrada no registo e uma montagem. As apps só falam com o framework
através da sua API pública e nunca tocam diretamente no armazenamento nem nas
chaves. Ver [O teu próprio hub](hubs.md).
