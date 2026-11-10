# Hubs, não plataformas

A rede liga as tuas máquinas. Os **hubs** ligam pessoas. Um hub é um conjunto de
apps web (um mercado aberto, um feed, chat, partilha de ficheiros, listas
partilhadas, um gestor de palavras-passe, um calendário) que correm inteiramente
no navegador e sincronizam através de relays [nostr](https://nostr.com)
escolhidos pela comunidade. Não há servidor de contas nem backend pelo meio, e
tudo o que é privado é cifrado no dispositivo antes de sair dele. Qualquer pessoa
pode correr um hub para qualquer comunidade. Ver
[as apps do framework](apps.md).

Três repositórios compõem isto:

| Repositório | O que é |
|---|---|
| [**kiwi-framework**](https://github.com/derlocke-ng/kiwi-framework) | O motor: identidade e contas, relays e sincronização, pessoas e partilha, moderação, o kit de design, as páginas do hub e dez apps. Não traz nada que um utilizador abra por si só. v0.32.1, GPL-3.0-or-later |
| [**Armory**](armory.md) | A primeira **distribuição**: um hub construído com o framework, com um nome, relays por omissão e as dez apps montadas com nomes próprios. O modelo a partir do qual fazes um fork para o teu. GPL-3.0-or-later. **Ao vivo:** [derlocke-ng.github.io/armory](https://derlocke-ng.github.io/armory/) |
| [**kiwi-web-catalog**](hubs.md#kiwi-web-catalog) | Um catálogo git de hubs e das suas apps, com a mesma forma do [kiwi-catalog](../desktop/catalogs.md) do ambiente de trabalho |

## Como tudo se encaixa { #how-it-fits-together }

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

## As palavras { #the-words }

- **Hub**: o que uma distribuição produz. Ficheiros estáticos, por isso alojar um
  é servir uma pasta. Todos os hubs têm uma página inicial, definições e uma
  página de conta.
- **Distribuição**: um hub construído sobre o framework, com um nome e um
  aspeto, relays por omissão e um conjunto escolhido de apps em espaços
  escolhidos. Tudo o que um fork muda vive num só ficheiro, `distribution.js`,
  mais as suas traduções.
- **App**: uma pasta com um manifesto que encaixa em qualquer distribuição. As
  apps só falam com a API pública do framework e nunca tocam diretamente no
  armazenamento nem nas chaves.
- **Espaço**: uma comunidade com nome e dono, com os seus próprios moderadores e,
  opcionalmente, os seus próprios relays (inspirado nas comunidades moderadas do
  NIP-72). Outro hub pode servir o mesmo espaço indicando o seu endereço.
- **Montagem** (mount): código de uma app num espaço, com nome, rota e ícone
  próprios. Uma app pode ser montada muitas vezes. O *Trading Post* do Armory é a
  app `market` do framework montada no espaço `tradingpost` do Armory.

Duas pessoas em distribuições diferentes são amigas, partilham e conversam
exatamente como numa só, porque a identidade e os dados são eventos nostr, não
pertencem ao hub.

## Contas e chaves { #accounts-and-keys }

- Cada dispositivo recebe uma chave na primeira visita, guardada no navegador.
- Uma **conta** é um nome de utilizador e uma palavra-passe, construída sobre
  eventos nostr simples, sem nenhum registo central: a palavra-passe é reforçada
  com scrypt e desbloqueia a tua chave. Ninguém pode tomar nem substituir uma
  conta sem a palavra-passe. **Não há reposição da palavra-passe.**
- Também podes iniciar sessão com uma chave nostr existente (`nsec`, hex ou
  `ncryptsec`). Os signers por extensão do navegador e remotos (NIP-07, NIP-46)
  estão planeados, não construídos.
- Uma conta funciona em todas as apps do hub e em todos os dispositivos onde
  inicias sessão.

## Modelo de privacidade { #privacy-model }

**O que é cifrado.** O conteúdo é selado no navegador antes de ir para qualquer
lado: AES-256-GCM com chaves derivadas por HKDF. As mensagens privadas são
mensagens NIP-17 em gift wraps NIP-59. Cada ficheiro recebe uma chave
AES-256-GCM aleatória antes de ir para um servidor de multimédia, e as fotos são
recodificadas, o que elimina os metadados da câmara. O Vault é selado com uma
frase-senha própria (scrypt + AES-256-GCM). As chamadas vão de navegador para
navegador, cifradas pelo WebRTC.

**Local primeiro.** Cada escrita vai primeiro para a base de dados do próprio
navegador e depois para os relays. As leituras vêm do dispositivo, por isso as
apps funcionam offline. Quando um dispositivo volta a ligar-se, repõe o que um
relay esqueceu: os dados só se perdem se todos os dispositivos que os tinham
desaparecerem *e* não houver cópia de segurança.

**O que os outros conseguem ver.** Os repositórios são explícitos quanto aos
limites:

- Os relays veem metadados: quem escreve para que endereços, quando, quanto e a
  partir de que endereço IP. Usa uma VPN ou o Tor se isso for importante.
- A chave de um espaço não é um segredo. Mantém as publicações de uma comunidade
  longe da vista simples. Os gostos, as denúncias e quem comentou o quê são
  visíveis para os relays.
- As notas do DevBoard e as denúncias de moderação são públicas por desenho.
- A tua chave vive no armazenamento do navegador. Todos os sites GitHub Pages de
  uma conta partilham uma origem, por isso um hub no seu próprio (sub)domínio é
  a configuração mais forte.
- As transferências diretas e as chamadas revelam os endereços IP dos dois
  navegadores um ao outro e aos servidores STUN (os da Google e da Cloudflare por
  omissão; um hub pode definir os seus).
- «Nenhum servidor nosso» significa nenhum no caminho crítico. As apps continuam
  a usar os relays, os servidores de multimédia e, para o calendário, o servidor
  CalDAV que tu ou o teu hub escolhem.

## Moderação { #moderation }

Três camadas: a tua própria lista de bloqueios (cifrada, só tu a podes ler), as
denúncias (públicas, assinadas) e a política dos próprios relays. Um espaço tem
moderadores. A denúncia de um moderador recolhe uma publicação de imediato. Caso
contrário, são precisas três denúncias de pessoas que não estejam bloqueadas. As
publicações podem ser marcadas como 18+ ou como publicidade, e essas só são mostradas
a pessoas com conta.

## Continua a ler { #read-on }

- [O Armory e as suas apps](armory.md)
- [O teu próprio hub](hubs.md)
- A [arquitetura](https://github.com/derlocke-ng/kiwi-framework/blob/main/docs/architecture.md)
  e o [protocolo de comunicação](https://github.com/derlocke-ng/kiwi-framework/blob/main/docs/protocol.md)
  do próprio framework
