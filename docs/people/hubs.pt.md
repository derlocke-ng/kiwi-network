# O teu próprio hub

Esta página explica como pôr a funcionar um hub para a tua comunidade. Um hub
é o site que o kiwi-framework dá a uma comunidade: um mercado aberto, um
feed, um chat e outras aplicações que correm no navegador. Um hub é composto
apenas por ficheiros estáticos, por isso alojá-lo é servir uma pasta de
ficheiros por HTTPS. Há três maneiras de ter um:

- **Usar o Armory tal como está.** O Armory é o primeiro hub construído com o
  framework e está aberto a todos em
  [derlocke-ng.github.io/armory](https://derlocke-ng.github.io/armory/).
- **Criar a tua própria distribuição.** Uma distribuição é o framework com o
  teu nome, os teus relays e a tua escolha de aplicações. Podes publicá-la em
  qualquer alojamento de sites estáticos.
- **Correr o contentor do hub.** Podes, por exemplo, corrê-lo dentro da tua
  própria Kiwi Network, juntamente com o teu próprio relay. O resultado é um
  hub privado, acessível apenas a partir da mesh, ou seja, da rede privada que
  liga as tuas máquinas.

## Tipos de hub { #kinds-of-hub }

| Tipo | Como | Exemplo |
|---|---|---|
| **Público** | O hub usa relays públicos, e qualquer pessoa o pode abrir. | Armory |
| **Privado** | As pessoas não podem substituir os relays do hub (`policy.relays: 'locked'`), e as páginas esperam até que um desses relays responda (`requireHub`). Os relays estão dentro de uma VPN. | o hub de uma empresa, no kiwi-master dela |
| **Semipúblico** | Um hub privado que tem também uma área pública. Algumas aplicações escolhidas, por exemplo o chat, usam aí relays públicos. | |

Os relays de um hub formam redes separadas: a rede própria do hub, a área
pública e as redes dos seus espaços. Cada evento, ou seja, cada mensagem nostr
assinada, pertence a uma destas redes e nunca é passado para outra.

## A tua própria distribuição { #your-own-distribution }

Começa pelo Armory, que é o modelo. No GitHub, *Use this template* dá-te uma
cópia do repositório sem o histórico. Depois segue estes passos:

1. Edita o **`distribution.js`**. Este ficheiro define o id, o nome, o
   símbolo, a descrição, a página principal, o repositório, os relays, os
   servidores de multimédia, os espaços, as aplicações e as montagens. Se o
   teu hub também tiver de servir os espaços do Armory, copia o `owner` e o
   `id` deles do `hub.json` do Armory.
2. Edita os **`locales/*.json`**. Estes ficheiros contêm o título, o texto de
   introdução e o rodapé, e um texto de cartão para cada montagem. Quando
   falta uma tradução, é usado o inglês.
3. Atualiza o **`kiwi.manifest`**. Se quiseres, acrescenta também o teu hub ao
   [kiwi-web-catalog](#kiwi-web-catalog).
4. No GitHub, escolhe *Settings → Pages → Source: GitHub Actions* e depois
   faz push.

Estes são os comandos que usas enquanto trabalhas numa distribuição:

```bash
npm install
npm run dev                  # o hub com recarregamento automático, http://localhost:5173
npm test
npm run build && npm run serve
npm run relay:nostr          # um relay de teste local em ws://localhost:7777
npm run new-app -- <id> "<Name>" <icon>   # criar o esqueleto de uma nova aplicação
```

Fixa o kiwi-framework num commit ou numa tag, nunca num ramo. A compilação
verifica o teu `distribution.js`. Por exemplo, um hub com uma montagem
pública tem de ter relays públicos, e um hub com relays públicos tem de ter
uma montagem pública.

Tudo o que vês no navegador está escrito em TypeScript com React 19 e é
compilado com o Vite. A camada de dados em `shared/` é JavaScript simples com
tipos JSDoc. Os testes correm com o executor de testes do próprio node, e os
que precisam de um navegador correm no Playwright.

## O contentor do hub { #the-hub-container }

O Armory também existe como imagem de contentor, `ghcr.io/derlocke-ng/armory`.
A imagem é construída a partir do `container/Dockerfile` do framework e serve
o hub com o nginx. Quando o contentor arranca, o script de entrada escreve o
ficheiro `hub.local.json` a partir das variáveis `HUB_*`, e a página lê este
ficheiro antes de se ligar. Desta forma, cada instalação pode escolher os
relays e a política, mas não pode acrescentar código. Se não for definida
nenhuma variável, o hub funciona tal como foi compilado.

Este exemplo arranca um hub com um relay próprio, que as pessoas não podem
substituir, e com uma montagem num relay público:

```bash
docker run --rm -p 8080:80 \
  -e HUB_RELAYS=wss://relay.sh3.home \
  -e HUB_RELAYS_LOCKED=true -e HUB_REQUIRE_HUB=true \
  -e HUB_PUBLIC_RELAYS=wss://nos.lol -e HUB_PUBLIC_MOUNTS=uplink \
  ghcr.io/you/your-hub
```

| Variável | Significado |
|---|---|
| `HUB_RELAYS` | Os relays próprios do hub. |
| `HUB_PUBLIC_RELAYS` | Os relays da área pública. Se a variável estiver definida mas vazia, não há área pública. |
| `HUB_DIRECTORY_RELAYS` | Os relays onde as listas de relays são publicadas e consultadas. |
| `HUB_RELAYS_LOCKED` | Com `true`, as pessoas não podem substituir os relays do hub. |
| `HUB_REQUIRE_HUB` | Com `true`, as páginas ficam à espera enquanto nenhum dos relays do hub responder. |
| `HUB_PUBLIC_MOUNTS` | As montagens que usam a área pública, indicadas pelo id. |
| `HUB_ACCOUNT_MOUNTS` | As montagens que pedem uma conta. |
| `HUB_REQUIRE_ACCOUNT` | Com `true`, todas as montagens pedem uma conta. |
| `HUB_SPACE_RELAYS` | Os relays de cada espaço, escritos como `jobs=wss://…;gems=wss://a,wss://b`. |
| `HUB_MODERATORS` | As chaves das pessoas que moderam todos os espaços definidos pelo hub. |
| `HUB_REGISTER_POW` | O número de bits de prova de trabalho de que uma nova conta precisa. Serve para relays que só aceitam membros. |
| `HUB_CALDAV` | Um servidor Nextcloud. O nginx reencaminha `/remote.php/dav/` para ele, por isso o calendário não precisa de CORS. |
| `HUB_ICE`, `HUB_ICE_USERNAME`, `HUB_ICE_CREDENTIAL` | Os servidores STUN/TURN para chamadas e transferências diretas, que ajudam dois navegadores a ligarem-se um ao outro. As credenciais do TURN ficam visíveis na página, por isso cria credenciais TURN usadas apenas por este hub. |

O `HUB_USER_MOUNTS` é lido, mas ainda não tem efeito. Pertence a uma
funcionalidade que ainda está para vir: seguir um espaço que o hub não inclui.

O hub tem de ser servido por HTTPS, porque o WebCrypto precisa de um contexto
seguro. Os relays têm de ser servidos por `wss://`. Se o hub for aberto por
`http://` simples num endereço que não seja localhost, a página avisa e não
continua.

### Um hub na tua Kiwi Network { #on-a-kiwi-network }

Um kiwi-master é o único servidor de uma Kiwi Network acessível a partir da
Internet. Pode correr um relay e um hub próprios, e para isso existem dois
módulos. O módulo `nostr-relay` corre o software de relay strfry em `relay.<host>`. O
módulo `hub` corre esta imagem de contentor, por predefinição com o Armory, em
`hub.<host>`.

Por predefinição, os dois são privados. Só estão acessíveis a partir da mesh e
usam o certificado da tua rede. Para um hub semipúblico, acrescenta
`public_relays` e `public_mounts`. Para um hub público, acrescenta
`reverse-proxy.public`, que obtém certificados Let's Encrypt.

O relay de um hub público aceita publicações vindas da mesh. A partir da
Internet, só aceita publicações de membros que provem que têm a sua chave
(NIP-42). Os membros são as pessoas da lista assinada pelos administradores
(`write_pubkeys`). Com `members: registered`, é membro qualquer pessoa que
tenha conta no hub. Vê a [referência dos módulos](../server/modules.md#people).

## kiwi-web-catalog { #kiwi-web-catalog }

O [derlocke-ng/kiwi-web-catalog](https://github.com/derlocke-ng/kiwi-web-catalog)
é um catálogo, ou seja, um repositório git que lista outros repositórios.
Lista hubs, as suas aplicações e o framework, e tem o mesmo formato que o
catálogo do ambiente de trabalho. O ficheiro `apps.list` tem um URL git por
linha. Uma linha pode ter `path=`, para uma aplicação que está dentro do
repositório de um hub, e `ref=`, para fixar uma versão. Cada entrada contém um
`kiwi.manifest` com uma `CATEGORY` que é `Framework`, `Hub` ou `App`.

Hoje lista o kiwi-framework, o Armory e as dez aplicações do Armory. **Não**
foi feito para ser usado com `kiwi catalog add`. As entradas não têm
instalador, e ainda nada lê o catálogo automaticamente. Segundo o README, os
ficheiros do catálogo estão no domínio público (CC0).

Para acrescentares o teu hub, faz fork do catálogo, acrescenta uma linha,
confirma que o teu repositório contém um `kiwi.manifest` e abre um pull
request.

## Ainda não implementado { #not-built-yet }

Estes pontos estão no plano de desenvolvimento do próprio framework e ainda
não existem:

- O blogue.
- Aprovações de moderação (NIP-72 kind 4550).
- Seguir um espaço que o teu hub não inclui.
- Iniciar sessão através de uma extensão do navegador (NIP-07) ou de um
  assinador remoto (NIP-46).
- Um servidor TURN na kiwi stack. O trabalho para isso está à espera no
  kiwi-modules. Sem TURN, dois telemóveis em dados móveis muitas vezes não
  conseguem estabelecer uma ligação direta.
