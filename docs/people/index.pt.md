# Hubs, não plataformas

O **kiwi-framework** é um software que permite a qualquer comunidade ter o seu
próprio **hub**. Um hub é um site com um conjunto de aplicações para os membros
da comunidade: um mercado aberto, um feed, um chat, partilha de ficheiros,
listas partilhadas, um gestor de palavras-passe e um calendário. Qualquer
pessoa pode gerir um hub para qualquer comunidade, e essa comunidade deixa de
depender de uma plataforma central que guarda as contas e os dados de toda a
gente.

As aplicações correm inteiramente no navegador. Sincronizam-se através de
relays [nostr](https://nostr.com), que são servidores que guardam mensagens
assinadas e as passam adiante, e é a comunidade que escolhe os relays que o
seu hub usa. Não há servidor de contas nem qualquer outro servidor entre o
navegador e os relays, e tudo o que é privado é cifrado no dispositivo antes
de ser enviado. As outras partes da Kiwi Network ligam as tuas máquinas. Os
hubs ligam pessoas. Cada aplicação está descrita em
[As aplicações do framework](apps.md).

O Armory é o primeiro hub construído com o framework. É um exemplo e é também
o modelo que outras comunidades copiam para criarem o seu próprio hub.

O software está distribuído por três repositórios:

| Repositório | O que é |
|---|---|
| [**kiwi-framework**](https://github.com/derlocke-ng/kiwi-framework) | O software geral a partir do qual se constrói qualquer hub. Inclui identidade e contas, relays e sincronização, amigos e partilha, moderação, o kit de design, as páginas do hub e dez aplicações. Sozinho, o framework não é um site que se possa abrir: só uma distribuição o transforma num hub. A versão atual é a v0.32.1 e a licença é GPL-3.0-or-later. |
| [**Armory**](armory.md) | A primeira **distribuição**, ou seja, um hub concreto feito com o framework. Acrescenta um nome, relays predefinidos e as dez aplicações, cada uma com um nome dado pelo Armory. É o modelo de que fazes fork para criares o teu próprio hub. A licença é GPL-3.0-or-later. **Online:** [derlocke-ng.github.io/armory](https://derlocke-ng.github.io/armory/) |
| [**kiwi-web-catalog**](hubs.md#kiwi-web-catalog) | Um catálogo, ou seja, um repositório git com uma lista de hubs e das suas aplicações. Tem o mesmo formato que o [kiwi-catalog](../desktop/catalogs.md) do ambiente de trabalho. |

## Como tudo se encaixa { #how-it-fits-together }

O diagrama mostra como o framework se transforma num hub no teu navegador e
com que servidores o navegador comunica a partir daí.

```
kiwi-framework  (engine: shared data layer, React UI, hub pages, apps)
      │  pinned by commit or tag
      ▼
a distribution  (Armory: distribution.js + locales/ + app overlays)
      │  build → static files
      ▼
any static host (GitHub Pages)  or  the hub container (nginx + HUB_* settings)
      │  HTTPS
      ▼
┌──────────────── your browser: all the logic and all the crypto ────────────────┐
│  wss://   nostr relays: the hub's own, a public area, one network per space    │
│  https:// Blossom media servers: encrypted files, addressed by their SHA-256   │
│  WebRTC   browser to browser: direct file transfers, calls, pong               │
└─────────────────────────────────────────────────────────────────────────────────┘
```

## Os termos usados aqui { #the-words }

- **Hub**: o site que uma comunidade usa. Um hub é o que obténs quando
  compilas uma distribuição. É composto apenas por ficheiros estáticos, por
  isso alojar um hub é simplesmente servir uma pasta de ficheiros. Todos os
  hubs têm uma página inicial, uma página de definições e uma página de conta.
- **Distribuição**: o framework juntamente com as escolhas que fazem dele um
  hub concreto: um nome e um aspeto, relays predefinidos e um conjunto
  escolhido de aplicações em espaços escolhidos. Quando fazes fork de uma
  distribuição, tudo o que alteras está num único ficheiro, `distribution.js`,
  e nas respetivas traduções.
- **Aplicação**: uma pasta com um ficheiro de manifesto. Pode ser acrescentada
  a qualquer distribuição. As aplicações usam apenas a API pública do
  framework e nunca acedem diretamente ao armazenamento nem às chaves.
- **Espaço**: uma comunidade com nome, dono, moderadores próprios e, se
  quiser, relays próprios. Segue o modelo das comunidades moderadas do nostr
  (NIP-72). Outro hub pode servir o mesmo espaço, bastando-lhe indicar o
  endereço desse espaço.
- **Montagem**: uma aplicação usada num espaço. Cada montagem tem nome
  próprio, rota própria (o seu endereço dentro do hub) e ícone próprio. A
  mesma aplicação pode ser montada muitas vezes. Por exemplo, o *Trading Post*
  do Armory é a aplicação `market` do framework montada no espaço
  `tradingpost` do Armory.

Duas pessoas que usam hubs de distribuições diferentes podem ser amigas,
partilhar coisas e conversar exatamente como se usassem o mesmo hub. Isto é
possível porque a identidade e os dados de cada pessoa são eventos nostr, ou
seja, mensagens assinadas guardadas nos relays, e não pertencem a nenhum hub.

## Contas e chaves { #accounts-and-keys }

- Na primeira vez que abres um hub num dispositivo, o navegador cria uma chave
  para esse dispositivo e guarda-a.
- Uma **conta** é um nome de utilizador e uma palavra-passe. Assenta em
  eventos nostr normais, e não existe nenhum registo central de contas. A tua
  palavra-passe passa pelo scrypt, uma função propositadamente lenta de
  calcular, e o resultado desbloqueia a tua chave. Ninguém consegue apoderar-se
  de uma conta nem substituí-la sem a palavra-passe. **Não há forma de repor a
  palavra-passe.**
- Também podes iniciar sessão com uma chave nostr que já tenhas, em formato
  `nsec`, hexadecimal ou `ncryptsec`. Iniciar sessão através de uma extensão
  do navegador (NIP-07) ou de um assinador remoto (NIP-46) está planeado, mas
  ainda não foi implementado.
- Uma única conta funciona em todas as aplicações do hub e em todos os
  dispositivos onde iniciares sessão.

## Modelo de privacidade { #privacy-model }

**O que é cifrado.** O navegador cifra o conteúdo antes de o enviar para
qualquer lado. Usa AES-256-GCM, com chaves derivadas por HKDF. As mensagens
privadas são mensagens NIP-17 dentro de gift wraps NIP-59. Um gift wrap é uma
segunda camada de cifragem: o relay fica apenas a saber que uma determinada
chave recebeu uma mensagem embrulhada. Antes de ser enviado para um servidor de
multimédia, cada ficheiro é cifrado com uma chave AES-256-GCM aleatória, que
só serve para esse ficheiro. As fotos são primeiro recodificadas, o que elimina os metadados que
as câmaras acrescentam. O Vault é cifrado com uma frase-senha própria
(scrypt + AES-256-GCM). As chamadas vão diretamente de navegador para
navegador e são cifradas pelo WebRTC.

**Primeiro no dispositivo.** Tudo o que escreves é guardado primeiro na base
de dados do próprio navegador e só depois enviado para os relays. As
aplicações leem os dados dessa base de dados local, por isso também funcionam
sem ligação. Quando um dispositivo volta a ligar-se, envia ao relay os dados
que este já não tenha. Assim, os dados só se perdem se todos os dispositivos
que os tinham desaparecerem *e* não houver backup.

**O que os outros podem ver.** Os próprios repositórios indicam os limites:

- Os relays veem metadados: quem escreve para que endereços, quando, quanto e
  a partir de que endereço IP. Se isso te importa, usa uma VPN ou o Tor.
- A chave de um espaço não é segredo. Serve apenas para que as publicações de
  uma comunidade não fiquem legíveis para qualquer um. Os relays conseguem ver
  os gostos, as denúncias e quem comentou o quê.
- As notas do DevBoard e as denúncias de moderação são públicas, e isso é
  intencional.
- A tua chave fica guardada no armazenamento do navegador. Todos os sites do
  GitHub Pages de uma mesma conta partilham a mesma origem, e os navegadores
  separam o armazenamento dos sites por origem. Por isso, um hub com domínio
  ou subdomínio próprio é a opção mais segura.
- Numa transferência direta de ficheiros ou numa chamada, cada navegador fica
  a conhecer o endereço IP do outro, e os servidores STUN que os ajudam a
  ligar-se também veem os dois endereços. Por predefinição, são os servidores
  STUN da Google e da Cloudflare. Um hub pode definir os seus.
- «Sem servidor nosso» quer dizer que as aplicações não dependem de nenhum
  servidor gerido pelo projeto. Continuam a usar relays, servidores de
  multimédia e, no caso do calendário, um servidor CalDAV. Quem os escolhe és
  tu ou o teu hub.

## Moderação { #moderation }

A moderação tem três camadas. A primeira é a tua própria lista de bloqueio,
cifrada para que só tu a possas ler. A segunda são as denúncias, que são
públicas e assinadas. A terceira é a política de cada relay.

Cada espaço tem moderadores. Quando um moderador denuncia uma publicação, ela
fica recolhida de imediato. Caso contrário, uma publicação fica recolhida
depois de três denúncias de pessoas que não estejam bloqueadas. Uma publicação
pode ser marcada como 18+ ou como publicidade, e as publicações marcadas só
são mostradas a quem tem conta.

## Para continuar { #read-on }

- [O Armory e as suas aplicações](armory.md)
- [O teu próprio hub](hubs.md)
- A [arquitetura](https://github.com/derlocke-ng/kiwi-framework/blob/main/docs/architecture.md)
  e o [protocolo de comunicação](https://github.com/derlocke-ng/kiwi-framework/blob/main/docs/protocol.md)
  do próprio framework
