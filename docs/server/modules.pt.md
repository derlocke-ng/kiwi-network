# Módulos

Um módulo é um serviço que uma máquina da tua Kiwi Network pode correr, por
exemplo o servidor VPN, o servidor DNS que bloqueia a publicidade, o Nextcloud
ou o backup de todas as noites. É com os módulos que decides o que faz cada
máquina. Uma [função](roles.md) traz consigo um conjunto de módulos, e podes
alterar esse conjunto no ficheiro fleet.

Os módulos de uma máquina são transformados numa **stack**, que é tudo aquilo
de que a máquina precisa para correr esses serviços. Quem gera a stack é o
[kiwi-modules](https://github.com/derlocke-ng/kiwi-modules), de que o
kiwi-server traz uma cópia. Uma stack é composta por um ficheiro compose, pelos
**quadlets do podman** (uma unidade systemd por contentor), pelos ficheiros de
configuração, pelas unidades systemd da máquina e pelo `stack.sh`, um manifesto
que os enumera a todos. É o [kiwi-stack](single.md) que instala a stack na
máquina. Todos os modelos são preenchidos no computador onde a stack é gerada.
A máquina que corre a stack só precisa do podman 4.4 ou mais recente ou, se
definires `runtime: docker`, do docker com o plugin compose.

Este comando lista todos os módulos com as respetivas definições.

```bash
kiwi-server modules -v      # todos os módulos e todas as definições, com o valor predefinido
```

## A rede { #the-network }

Estes módulos constroem a mesh, ou seja, a rede WireGuard privada que liga
todas as tuas máquinas, e controlam o caminho pelo qual o tráfego dela chega à
Internet.

| Módulo | O que é | Corre em | Depende de | Na máquina |
|---|---|---|---|---|
| `vpn-server` | **wg-easy**, o servidor WireGuard a que se ligam todos os clientes e nodes. A sua rota predefinida é o cliente VPN, pelo que o tráfego para a Internet segue pela VPN comercial do master (o duplo salto) | master | nada | `51820/udp`, e a interface web em `127.0.0.1:51821` |
| `vpn-client` | **gluetun**, o túnel VPN por onde passa o tráfego de uma máquina. Num node, o túnel vai dar ao master; no master, vai dar a uma VPN comercial | ambos | nada | nada |
| `dns` | **Pi-hole 6**, um servidor DNS que bloqueia a publicidade, para a mesh ou para a LAN. Responde pelos nomes da tua rede e pode também resolver os nomes dos proxies SOCKS5 da Mullvad | ambos | nada | `53` num node |
| `tor` | Um proxy **SOCKS5 do Tor** para os clientes da mesh. Só usa nós do Tor nos países que definires | ambos | nada | `127.0.0.1:9050` num node, e o endereço na mesh `:9050` num master |
| `reverse-proxy` | **nginx** com TLS. Tem um bloco server por serviço, para que cada serviço esteja acessível com o seu próprio nome. As páginas de administração só estão acessíveis a partir da mesh. Os nomes públicos com certificados Let's Encrypt são opcionais | ambos | nada | `80`, `443` num node, ou num master com `public` ligado |
| `gateway` | Encaminhamento por políticas (policy routing) na máquina. Os dispositivos da LAN que usam esta máquina como gateway têm o seu tráfego para a Internet enviado pela VPN | node | vpn-client | uma unidade systemd na máquina |
| `dhcp-relay` | Passa os pedidos DHCP da LAN ao Pi-hole, para que o Pi-hole possa ser o servidor DHCP da LAN | node | dns | `67/udp` |

## Serviços { #services }

| Módulo | O que é | Corre em | Depende de |
|---|---|---|---|
| `cloud` | **Nextcloud**, montado com os contentores do projeto AIO, mas *sem* o contentor master do AIO. Por isso não precisa do socket do docker e corre no podman. O Collabora, o OnlyOffice, o Talk, o Imaginary, o ClamAV, a pesquisa de texto integral e o Whiteboard podem ser ligados ou desligados um a um | node | vpn-client, reverse-proxy |
| `vault` | **Vaultwarden**, um gestor de palavras-passe compatível com o Bitwarden | node | vpn-client, reverse-proxy |
| `downloader` | **Transmission** e **JDownloader**. Ambos correm no namespace de rede do cliente VPN, o que quer dizer que usam a ligação de rede dele e não têm nenhuma própria. Enquanto o túnel estiver em baixo, não transferem nada | node | vpn-client |
| `sftp` | Um servidor SFTP numa porta própria (`2224`), de onde podes ir buscar os downloads | node | nada |
| `portainer` | **Portainer CE**, uma interface web para os contentores. Está acessível em `127.0.0.1:9443` e em `portainer.<host>` | ambos | nada |
| `opencloud` | **OpenCloud**, para ficheiros e partilha de ficheiros, num único binário Go (para experimentar) | node | vpn-client, reverse-proxy |
| `immich` | **Immich**, para fotografias e vídeos (para experimentar) | node | vpn-client, reverse-proxy |
| `paperless` | **Paperless-ngx**, para documentos digitalizados, com OCR e pesquisa de texto integral (para experimentar) | node | vpn-client, reverse-proxy |

Os três últimos módulos não fazem parte de nenhum preset. Para usares um deles,
acrescenta-o a `modules:`.

## Pessoas { #people }

Um hub é o site próprio de uma comunidade, no navegador. Estes dois módulos
correm um hub e o relay onde o hub guarda os seus eventos.

| Módulo | O que é | Corre em | Depende de |
|---|---|---|---|
| `nostr-relay` | **strfry**, o relay onde um hub guarda os seus eventos. Está acessível em `relay.<host>`. Quem se liga a partir da Internet só pode publicar se for membro e tiver provado que a chave é sua (NIP-42). Com `approved`, os membros são as chaves de uma lista assinada pelos administradores. Com `registered`, qualquer pessoa com conta é membro. As ligações vindas da mesh podem publicar sempre | master | reverse-proxy |
| `hub` | Um **hub kiwi-framework** a correr num contentor. Por predefinição é o Armory, e está acessível em `hub.<host>`. Um hub pode ser privado, semipúblico ou público | master | reverse-proxy |

Vê [O teu próprio hub](../people/hubs.md).

## Backups e discos { #backups-and-disks }

| Módulo | O que é | Corre em | Depende de |
|---|---|---|---|
| `backup` | Faz backup dos dados desta máquina com o **restic**, cifrado, para um node que corra o módulo backup-server. O backup corre todas as noites às `03:00`, ou até 15 minutos depois, e sempre que executares `kiwi-stack backup`. Cada módulo define quais dos seus dados entram no backup. Para a próxima versão estão planeados backups para vários servidores e o restauro automático dos dados quando uma máquina é reconstruída ([pormenores](operations.md#coming-in-the-next-release)) | ambos | nada |
| `backup-server` | Um **servidor REST do restic** que guarda os backups. Cada máquina só chega ao seu próprio repositório e só pode acrescentar backups, não apagá-los (append-only) | node | vpn-client, reverse-proxy |
| `tang` | Servidores **Tang**, que permitem às máquinas com discos cifrados desbloqueá-los no arranque sem ninguém presente. Um anel é um servidor Tang com as suas próprias chaves. Por predefinição há um anel chamado `infra`, na porta `7500` | node | nada |

Vê [Operação](operations.md).

## Definições importantes { #important-settings }

| Módulo | Definição | Predefinição | Notas |
|---|---|---|---|
| vpn-server | `wg_host` | (obrigatória) | o nome ou o endereço IP a que os clientes se ligam |
| | `server_ip` / `wg_subnet` | `10.8.0.1` / `10.8.0.0/24` | |
| | `groups` | guests, pentest, devices, routers | vê [grupos de clientes](../network/index.md#client-groups) |
| | `unlock_relay` | `{}` | portas do master através das quais as máquinas atrás de NAT chegam ao seu anel Tang |
| vpn-client | `vpn_provider` | `custom` | `custom` usa a configuração WireGuard emitida pelo master, que é o que um node precisa. De resto, indica um fornecedor do gluetun (`mullvad`, `protonvpn`, `airvpn`, `ivpn`, `windscribe`, …) |
| | `wireguard_config` | `secrets/<hostname>.conf` | |
| | `server_countries`, `server_cities` | | os países e as cidades dos servidores da VPN comercial a usar |
| | `dot_providers` | `quad9` | o fornecedor de DNS-over-TLS que o gluetun usa |
| | `extra_dnat_rules` | `[]` | regras de reencaminhamento adicionais, por exemplo para SSH da mesh para a máquina |
| dns | `fallback_dns` | `9.9.9.9;149.112.112.112` | só é usado enquanto o master estiver inacessível |
| | `dhcp_enabled` | `false` | usa-se em conjunto com `dhcp_start`, `dhcp_end` e `dhcp_router` |
| | `mullvad_socks` | `true` num master | [os proxies da Mullvad pelo nome](../network/dns.md#mullvad-socks5-proxies-by-name) |
| tor | `countries` | `de,ch,at,nl,fr` | os países dos nós de entrada e de saída do Tor, impostos com `StrictNodes` |
| reverse-proxy | `public` | `false` | só no master. Abre as portas 80/443 e usa o Let's Encrypt para nomes fora do domínio da tua rede |
| cloud | `nextcloud_datadir` | `<docker_dir>/knnc-data` | aponta-a para uma pasta num disco grande |
| | `collabora` / `talk` | `true` / `false` | |
| | `startup_apps` | `deck twofactor_totp tasks calendar contacts notes end_to_end_encryption` | |
| vault | `signups_allowed` | `false` | liga-a para criares a primeira conta e depois volta a desligá-la |
| downloader | `download_dir` | (obrigatória) | |
| nostr-relay | `members` | `approved` | ou `registered` |
| | `write_pubkeys` | `[]` | as chaves dos administradores. Os administradores podem publicar sempre, e só as listas de membros e de banimentos deles é que contam |
| hub | `image` | `ghcr.io/derlocke-ng/armory:latest` | a imagem de qualquer hub feito com o kiwi-framework |
| | `public_relays`, `public_mounts` | `[]` | define-as para um hub semipúblico |
| backup | `server` | (obrigatória) | o endereço `https://…` de um node backup-server que inclua esta máquina na sua lista |
| tang | `rings` | `{ infra: "7500" }` | o nome e a porta de cada anel |

Se deixares de fora uma palavra-passe ou uma chave, ela é gerada a partir da
seed da tua rede.

## Nomes { #names }

Cada módulo regista os nomes dos seus serviços no proxy inverso e no DNS da tua
rede. Cada nome junta o nome do serviço e o nome da máquina.

| Serviço | Nome |
|---|---|
| wg-easy (master) | `wg.<host>` |
| Pi-hole (qualquer máquina com `dns` e o proxy inverso) | `pihole.<host>` |
| Nextcloud | `cloud.<host>` |
| Vaultwarden | `vault.<host>` |
| Transmission / JDownloader | `dl.<host>` / `jd.<host>` |
| Portainer | `portainer.<host>` |
| relay / hub | `relay.<host>` / `hub.<host>` |
| servidor de backups | `backup.<host>` |
| OpenCloud / Immich / Paperless | `opencloud.<host>` / `immich.<host>` / `paperless.<host>` |

## Contentores { #containers }

- Com o podman, cada serviço é um quadlet em `/etc/containers/systemd`. Os
  quadlets são arrancados através do `kiwi-stack.target`, e os seus registos vão
  para o journal do systemd. Um contentor que partilha o namespace de rede de
  outro fica ligado a esse contentor e, por isso, é reiniciado juntamente com
  ele.
- Os segredos são escritos em ficheiros `kiwi/env/<service>.env` que só o root
  pode ler. Nunca são escritos nas unidades.
- Os contentores têm endereços fixos, que seguem o plano de endereços da v1,
  para que uma máquina migrada da v1 mantenha os seus endereços: vpn-client
  `.2`, vpn-server `.3`, dns `.4`, reverse-proxy `.5`, cloud `.6`, vault `.7`,
  tor `.8`, downloader `.9`, gateway `.10`, portainer `.250` e sftp `.251`. Os
  outros módulos recebem endereços a contar a partir de `.100`. Os contentores
  sem endereço fixo recebem um do terceiro quarto da rede (`.128/26`).
- O Fedora CoreOS e o uCore correm com o SELinux ativo, por isso os bind mounts
  recebem a etiqueta `:z`. Os mounts do socket de contentores e de
  `/lib/modules` nunca são etiquetados.

## Escrever um módulo { #writing-a-module }

Um módulo é uma pasta com os ficheiros seguintes.

```
modules/<name>/
├── module.yaml              what it is, what it needs, its settings
├── docker-compose.yml.j2    its services (merged into the host's compose file)
└── *.j2                     any config file it ships
```

O `module.yaml` descreve o módulo. Declara os metadados do módulo e os tipos de
node em que corre, as suas dependências e as portas que abre na máquina. Indica
os modelos do módulo e onde é escrito o resultado de cada um, o armazenamento
e quais dos seus dados entram no backup. Declara ainda a integração com a
máquina (sysctls e módulos do kernel), os blocos server do nginx que o módulo
regista, os URL que são mostrados quando a função termina, as regras de
validação e as `settings` do módulo.

O esquema das definições serve para duas coisas: valida o ficheiro fleet, e é a
partir dele que a aplicação Kiwi Server constrói o seu formulário de
definições. Os modelos são escritos em Jinja2 e podem usar o contexto da
máquina. Este contexto contém o nome e o tipo da máquina, o endereço de cada
módulo, a mesh, os nomes da rede, os módulos ativos e as definições de cada
módulo.

Com o podman, o ficheiro compose é traduzido para quadlets. A tradução aceita
um conjunto fixo de chaves do compose, e qualquer outra chave dá um erro quando
a stack é gerada.

Os módulos são desenvolvidos e publicados no
[kiwi-modules](https://github.com/derlocke-ng/kiwi-modules). A referência
completa do formato está no
[docs/modules.md do kiwi-server](https://github.com/derlocke-ng/kiwi-server/blob/main/docs/modules.md).
