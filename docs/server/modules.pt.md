# Módulos

Um módulo é um serviço de uma máquina Kiwi Network. Um [papel](roles.md) escolhe
um conjunto de módulos, e o renderizador transforma-os numa **stack** para um
anfitrião. O renderizador é o [kiwi-modules](https://github.com/derlocke-ng/kiwi-modules),
que o kiwi-server inclui no seu repositório. A stack é um ficheiro compose,
**quadlets podman** (uma unidade systemd por contentor), as configurações e as
unidades do anfitrião, e `stack.sh`, o manifesto que os nomeia a todos. O
[kiwi-stack](single.md) põe-na na máquina. Toda a geração a partir de modelos
acontece na máquina que renderiza. O target só precisa do podman 4.4 ou mais
recente (ou do docker com o plugin compose, com `runtime: docker`).

```bash
kiwi-server modules -v      # todos os módulos e todas as definições com o seu valor por omissão
```

## A rede { #the-network }

| Módulo | O que é | Corre em | Requer | No anfitrião |
|---|---|---|---|---|
| `vpn-server` | **wg-easy**: o ponto de entrada de todos os clientes e nodes; a sua rota predefinida é o cliente VPN (o salto duplo) | master | nada | `51820/udp`; a interface em `127.0.0.1:51821` |
| `vpn-client` | **gluetun**: o túnel de que todas as máquinas dependem: para o master num node, para uma VPN comercial no master | ambos | nada | nada |
| `dns` | **Pi-hole 6**: bloqueia anúncios para a malha ou para a LAN, serve os nomes da fleet e, opcionalmente, os proxies SOCKS5 da Mullvad por nome | ambos | nada | `53` num node |
| `tor` | um proxy **Tor SOCKS5** para os clientes da malha, fixado a países | ambos | nada | `127.0.0.1:9050` num node; o endereço de malha `:9050` num master |
| `reverse-proxy` | **nginx** com TLS: um bloco server por serviço; as páginas de administração só respondem à malha; nomes públicos opcionais com Let's Encrypt | ambos | nada | `80`, `443` num node ou num master público |
| `gateway` | encaminhamento por políticas no anfitrião: os clientes da LAN que usam esta máquina como gateway saem através da VPN | node | vpn-client | uma unidade do anfitrião |
| `dhcp-relay` | retransmite o DHCP da LAN para o Pi-hole, para que o Pi-hole possa ser o servidor DHCP da LAN | node | dns | `67/udp` |

## Serviços { #services }

| Módulo | O que é | Corre em | Requer |
|---|---|---|---|
| `cloud` | **Nextcloud** a partir dos contentores do projeto AIO, *sem* o contentor master do AIO (sem socket docker, corre em podman). Collabora, OnlyOffice, Talk, Imaginary, ClamAV, pesquisa de texto integral e Whiteboard são interruptores | node | vpn-client, reverse-proxy |
| `vault` | **Vaultwarden**, o gestor de palavras-passe compatível com Bitwarden | node | vpn-client, reverse-proxy |
| `downloader` | **Transmission** e **JDownloader** dentro do namespace de rede do cliente VPN: sem túnel, sem tráfego | node | vpn-client |
| `sftp` | um servidor SFTP na sua própria porta (`2224`), para ir buscar as transferências | node | nada |
| `portainer` | **Portainer CE**, uma interface web para os contentores (`127.0.0.1:9443`, e `portainer.<host>`) | ambos | nada |
| `opencloud` | **OpenCloud**: ficheiros e partilha num só binário Go (para experimentar) | node | vpn-client, reverse-proxy |
| `immich` | **Immich**: fotos e vídeos (para experimentar) | node | vpn-client, reverse-proxy |
| `paperless` | **Paperless-ngx**: documentos digitalizados com OCR e pesquisa de texto integral (para experimentar) | node | vpn-client, reverse-proxy |

Os três últimos não estão em nenhuma predefinição; acrescenta-os a `modules:`.

## Pessoas { #people }

| Módulo | O que é | Corre em | Requer |
|---|---|---|---|
| `nostr-relay` | **strfry**, o relay onde um hub guarda os seus eventos (em `relay.<host>`). A partir da Internet, os membros podem publicar depois de provarem a sua chave (NIP-42): chaves `approved` na lista assinada dos administradores, ou qualquer pessoa `registered` com conta. A malha pode sempre publicar | master | reverse-proxy |
| `hub` | um **hub kiwi-framework** como contentor (o Armory por omissão, em `hub.<host>`), privado, semipúblico ou público | master | reverse-proxy |

Ver [O teu próprio hub](../people/hubs.md).

## Cópias de segurança e discos { #backups-and-disks }

| Módulo | O que é | Corre em | Requer |
|---|---|---|---|
| `backup` | os dados desta máquina com **restic**, cifrados, para um node backup-server: todas as noites às `03:00` (nos 15 minutos seguintes) e com `kiwi-stack backup`. Cada módulo diz o que dele é guardado. Próxima versão: vários servidores e uma máquina reconstruída que se restaura sozinha ([detalhes](operations.md#coming-in-the-next-release)) | ambos | nada |
| `backup-server` | um **restic REST server**; cada máquina só alcança o seu próprio repositório, apenas em modo de acrescento | node | vpn-client, reverse-proxy |
| `tang` | servidores **Tang** para que as máquinas cifradas se desbloqueiem no arranque; um anel é um servidor com as suas próprias chaves (por omissão `infra` em `7500`) | node | nada |

Ver [Operações](operations.md).

## Definições importantes { #important-settings }

| Módulo | Definição | Por omissão | Notas |
|---|---|---|---|
| vpn-server | `wg_host` | (obrigatório) | o nome ou IP a que os clientes se ligam |
| | `server_ip` / `wg_subnet` | `10.8.0.1` / `10.8.0.0/24` | |
| | `groups` | guests, pentest, devices, routers | ver [grupos de clientes](../network/index.md#client-groups) |
| | `unlock_relay` | `{}` | portas Tang para máquinas atrás de NAT |
| vpn-client | `vpn_provider` | `custom` | `custom`: a configuração WireGuard que o master emitiu (um node); ou um fornecedor do gluetun (`mullvad`, `protonvpn`, `airvpn`, `ivpn`, `windscribe`, …) |
| | `wireguard_config` | `secrets/<hostname>.conf` | |
| | `server_countries`, `server_cities` | | onde fica uma saída comercial |
| | `dot_providers` | `quad9` | o DNS-over-TLS do gluetun |
| | `extra_dnat_rules` | `[]` | p. ex. SSH da malha para o anfitrião |
| dns | `fallback_dns` | `9.9.9.9;149.112.112.112` | só enquanto o master estiver inacessível |
| | `dhcp_enabled` | `false` | com `dhcp_start`, `dhcp_end`, `dhcp_router` |
| | `mullvad_socks` | `true` num master | [os proxies da Mullvad por nome](../network/dns.md#mullvad-socks5-proxies-by-name) |
| tor | `countries` | `de,ch,at,nl,fr` | nós de entrada e de saída, `StrictNodes` |
| reverse-proxy | `public` | `false` | só no master: 80/443 com Let's Encrypt para nomes fora do domínio da fleet |
| cloud | `nextcloud_datadir` | `<docker_dir>/knnc-data` | aponta-o para um disco grande |
| | `collabora` / `talk` | `true` / `false` | |
| | `startup_apps` | `deck twofactor_totp tasks calendar contacts notes end_to_end_encryption` | |
| vault | `signups_allowed` | `false` | ativa para a primeira conta, depois desativa |
| downloader | `download_dir` | (obrigatório) | |
| nostr-relay | `members` | `approved` | ou `registered` |
| | `write_pubkeys` | `[]` | os administradores: podem sempre publicar, e só as suas listas de membros e de banimentos contam |
| hub | `image` | `ghcr.io/derlocke-ng/armory:latest` | qualquer hub kiwi-framework |
| | `public_relays`, `public_mounts` | `[]` | um hub semipúblico |
| backup | `server` | (obrigatório) | `https://…` de um node backup-server que lista esta máquina |
| tang | `rings` | `{ infra: "7500" }` | nome e porta |

As palavras-passe e chaves que deixas de fora são geradas a partir da seed da
fleet.

## Nomes { #names }

Cada módulo anuncia os seus nomes ao proxy inverso e ao DNS da fleet, sob o nome
do anfitrião:

| Serviço | Nome |
|---|---|
| wg-easy (master) | `wg.<host>` |
| Pi-hole (qualquer anfitrião com `dns` e o proxy inverso) | `pihole.<host>` |
| Nextcloud | `cloud.<host>` |
| Vaultwarden | `vault.<host>` |
| Transmission / JDownloader | `dl.<host>` / `jd.<host>` |
| Portainer | `portainer.<host>` |
| relay / hub | `relay.<host>` / `hub.<host>` |
| servidor de cópias de segurança | `backup.<host>` |
| OpenCloud / Immich / Paperless | `opencloud.<host>` / `immich.<host>` / `paperless.<host>` |

## Contentores { #containers }

- Com podman, cada serviço é um quadlet em `/etc/containers/systemd`, arrancado
  através de `kiwi-stack.target`, com o seu registo no journal. Um contentor que
  vive no namespace de rede de outro fica ligado a ele e regressa com ele.
- Os segredos vão para ficheiros `kiwi/env/<service>.env` só acessíveis a root,
  nunca para as unidades.
- Os endereços fixos seguem o plano v1, para que uma máquina migrada os mantenha:
  vpn-client `.2`, vpn-server `.3`, dns `.4`, reverse-proxy `.5`, cloud `.6`,
  vault `.7`, tor `.8`, downloader `.9`, gateway `.10`, portainer `.250`, sftp
  `.251`. Os outros módulos contam a partir de `.100`. Os contentores sem
  endereço fixo usam o terceiro quarto da rede (`.128/26`).
- O Fedora CoreOS e o uCore correm com o SELinux ativo, por isso as montagens
  bind levam a etiqueta `:z`. As montagens do socket do contentor e de
  `/lib/modules` nunca são etiquetadas.

## Escrever um módulo { #writing-a-module }

```
modules/<name>/
├── module.yaml              what it is, what it needs, its settings
├── docker-compose.yml.j2    its services (merged into the host's compose file)
└── *.j2                     any config file it ships
```

O `module.yaml` declara os metadados do módulo e os tipos de node, as suas
dependências, as portas do anfitrião que abre, os seus modelos e para onde vai o
resultado deles, o armazenamento, o que dele é copiado em segurança, a
integração com o anfitrião (sysctls, módulos do kernel), os blocos server do
nginx que anuncia, os URLs impressos quando o papel termina, as suas regras de
validação e as suas `settings`. O esquema das definições valida o ficheiro fleet
e constrói o formulário da app. Os modelos são Jinja2 e veem o contexto do
anfitrião: o nome e o tipo do anfitrião, o endereço de cada módulo, a malha, os
nomes da fleet, todos os módulos ativos e as definições de todos os módulos.

Com podman, o ficheiro compose é traduzido em quadlets. Só um conjunto conhecido
de chaves compose é traduzido, e tudo o resto é um erro no momento da
renderização.

Os módulos são desenvolvidos e lançados no
[kiwi-modules](https://github.com/derlocke-ng/kiwi-modules). A referência
completa do formato é o
[docs/modules.md do kiwi-server](https://github.com/derlocke-ng/kiwi-server/blob/main/docs/modules.md).
