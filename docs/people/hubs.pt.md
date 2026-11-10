# O teu próprio hub

Um hub são ficheiros estáticos, por isso alojar um é servir uma pasta por HTTPS.
Há três formas de correr um:

- **Usa o Armory tal como está:** [derlocke-ng.github.io/armory](https://derlocke-ng.github.io/armory/).
- **Faz a tua própria distribuição:** o teu nome, relays e apps, em qualquer
  alojamento estático.
- **Corre o contentor do hub:** por exemplo dentro da tua própria Kiwi Network,
  com o teu próprio relay, como hub privado a que só a malha consegue chegar.

## Tipos de hub { #kinds-of-hub }

| Tipo | Como | Exemplo |
|---|---|---|
| **Público** | Relays públicos; qualquer pessoa o pode abrir | Armory |
| **Privado** | Os relays do hub estão bloqueados (`policy.relays: 'locked'`) e as páginas esperam até um deles responder (`requireHub`), com relays dentro de uma VPN | o hub de uma empresa no seu kiwi-master |
| **Semipúblico** | Um hub privado com uma área pública para apps escolhidas (o chat, por exemplo) em relays públicos | |

Cada evento pertence a uma rede (a do próprio hub, a área pública ou a de um
espaço) e nunca passa para outra.

## A tua própria distribuição { #your-own-distribution }

O Armory é o modelo (no GitHub, *Use this template* dá-te uma cópia sem o seu
histórico):

1. Edita **`distribution.js`**: id, nome, marca, descrição, página inicial,
   repositório, relays, servidores de multimédia, espaços, apps e montagens. Para
   servires também os espaços do Armory, copia o `owner` e o `id` deles do
   `hub.json` do Armory.
2. Edita **`locales/*.json`**: o título, o texto de abertura e o rodapé, e um
   texto de cartão por montagem. O inglês é a língua de recurso.
3. Atualiza **`kiwi.manifest`** e, opcionalmente, acrescenta o teu hub ao
   [kiwi-web-catalog](#kiwi-web-catalog).
4. No GitHub: *Settings → Pages → Source: GitHub Actions*, depois faz push.

```bash
npm install
npm run dev                  # o hub com recarregamento automático, http://localhost:5173
npm test
npm run build && npm run serve
npm run relay:nostr          # um relay de teste local em ws://localhost:7777
npm run new-app -- <id> "<Name>" <icon>   # cria o esqueleto de uma app nova
```

Fixa o kiwi-framework por commit ou tag, nunca por ramo. A construção verifica o
teu `distribution.js` (por exemplo, uma montagem pública precisa de relays
públicos, e vice-versa).

A stack é TypeScript, React 19 e Vite para tudo o que é visível. A camada de
dados em `shared/` é JavaScript simples com tipos JSDoc. Os testes correm no
test runner do node e, para o navegador, no Playwright.

## O contentor do hub { #the-hub-container }

O Armory é também uma imagem de contentor, `ghcr.io/derlocke-ng/armory`,
construída a partir do `container/Dockerfile` do framework (nginx). No arranque,
o seu entrypoint escreve `hub.local.json` a partir das variáveis `HUB_*`, e a
página lê-o antes de se ligar. Uma implementação pode escolher relays e política
dessa forma, mas não pode acrescentar código. Sem variáveis definidas, o hub
corre tal como foi construído.

```bash
docker run --rm -p 8080:80 \
  -e HUB_RELAYS=wss://relay.sh3.home \
  -e HUB_RELAYS_LOCKED=true -e HUB_REQUIRE_HUB=true \
  -e HUB_PUBLIC_RELAYS=wss://nos.lol -e HUB_PUBLIC_MOUNTS=uplink \
  ghcr.io/you/your-hub
```

| Variável | Significado |
|---|---|
| `HUB_RELAYS` | os relays próprios do hub |
| `HUB_PUBLIC_RELAYS` | os relays da área pública (definida e vazia: sem área pública) |
| `HUB_DIRECTORY_RELAYS` | onde as listas de relays são publicadas e consultadas |
| `HUB_RELAYS_LOCKED` | `true`: as pessoas não podem substituir os relays do hub |
| `HUB_REQUIRE_HUB` | `true`: as páginas esperam enquanto nenhum dos relays do hub responder |
| `HUB_PUBLIC_MOUNTS` | montagens na área pública, por id |
| `HUB_ACCOUNT_MOUNTS` | montagens que pedem uma conta |
| `HUB_REQUIRE_ACCOUNT` | `true`: todas as montagens pedem uma conta |
| `HUB_SPACE_RELAYS` | relays por espaço: `jobs=wss://…;gems=wss://a,wss://b` |
| `HUB_MODERATORS` | chaves que moderam todos os espaços que o hub define |
| `HUB_REGISTER_POW` | bits de prova de trabalho para uma conta nova (relays só para membros) |
| `HUB_CALDAV` | um Nextcloud; o nginx reencaminha `/remote.php/dav/` para ele, por isso o calendário não precisa de CORS |
| `HUB_ICE`, `HUB_ICE_USERNAME`, `HUB_ICE_CREDENTIAL` | servidores STUN/TURN para chamadas e transferências diretas. O acesso TURN fica visível na página, por isso dá-lhe um acesso só para este hub |

`HUB_USER_MOUNTS` é lido mas ainda não faz nada: seguir um espaço que o hub não
traz ainda está por vir.

O hub tem de ser servido por HTTPS (a WebCrypto precisa de um contexto seguro) e
os seus relays por `wss://`. Por `http://` simples (exceto localhost), a página
avisa disso e para.

### Numa Kiwi Network { #on-a-kiwi-network }

Um kiwi-master pode ter o seu próprio relay e hub: o módulo `nostr-relay` (strfry
em `relay.<host>`) e o módulo `hub` (esta imagem, o Armory por omissão, em
`hub.<host>`). São privados por omissão: acessíveis só a partir da malha, com o
certificado da fleet. Um hub semipúblico acrescenta `public_relays` e
`public_mounts`. Um público acrescenta `reverse-proxy.public`, que obtém
certificados Let's Encrypt. O relay aceita então publicações da malha e, a partir
da Internet, só de membros que provem a sua chave (NIP-42): os que estão na lista
que os administradores (`write_pubkeys`) assinam ou, com `members: registered`,
qualquer pessoa com conta no hub. Ver a [referência dos módulos](../server/modules.md#people).

## kiwi-web-catalog { #kiwi-web-catalog }

O [derlocke-ng/kiwi-web-catalog](https://github.com/derlocke-ng/kiwi-web-catalog)
lista hubs, as suas apps e o framework, com a mesma forma do catálogo do ambiente
de trabalho: um `apps.list` com um URL git por linha (`path=` para uma app dentro
do repositório de um hub, `ref=` para fixar), e um `kiwi.manifest` em cada entrada
com uma `CATEGORY` de `Framework`, `Hub` ou `App`.

Hoje lista o kiwi-framework, o Armory e as dez apps do Armory. **Não** é para
`kiwi catalog add`: estas entradas não têm instalador, e nada lê o catálogo
automaticamente ainda. Os ficheiros do catálogo são do domínio público (CC0,
segundo o seu README).

Para acrescentares o teu hub: faz um fork, acrescenta uma linha, garante que o
repositório tem um `kiwi.manifest` e abre um pull request.

## Ainda não construído { #not-built-yet }

Isto vem do próprio roadmap do framework:

- O blogue.
- Aprovações de moderação (NIP-72 kind 4550).
- Seguir espaços que um hub não traz.
- Signers NIP-07 e NIP-46.
- Um servidor TURN na stack kiwi. Está à espera no kiwi-modules; sem TURN, dois
  telemóveis com dados móveis muitas vezes não encontram um caminho direto.
