# O ficheiro fleet

O `fleet.yaml` descreve todas as máquinas que o kiwi-server constrói. Tem duas
chaves: `defaults`, que se aplica a todos os anfitriões, e `hosts`, com uma
entrada por máquina. Tudo o que um anfitrião define sobrepõe-se aos valores por
omissão. `kiwi-server init` escreve um ponto de partida comentado, e a
referência completa é
[examples/fleet.yaml](https://github.com/derlocke-ng/kiwi-server/blob/main/examples/fleet.yaml).

Um anfitrião tem um **target** (o que é instalado) e um **papel** (o que passa a
ser):

- `target`: `coreos`, `ucore` (o valor por omissão) ou `debian`. Ver [Máquinas](machines.md).
- `role`: `bare` (o valor por omissão), `master` ou `node`. Ver [Papéis](roles.md).

## Exemplo { #example }

```yaml
defaults:
  target: ucore
  role: bare
  domain: home                       # papaya passa a ser papaya.home; os serviços são cloud.papaya.home …
  timezone: Europe/Berlin
  disk: /dev/sda                     # APAGADO pela ISO sem perguntar
  admin:
    user: core
    ssh_keys: [~/.ssh/id_ed25519.pub]
  updates: { enabled: true, days: [Sun], time: "03:30", length_minutes: 90 }
  install: { on_done: poweroff }
  tls: { auto: true, ca_dir: secrets/ca, name_constraints: [home] }
  debian: { release: trixie, partitioning: lvm }

hosts:
  sorbet:                              # o master, um VPS Debian
    role: master
    target: debian
    disk: /dev/vda
    master:
      vpn-client:
        vpn_provider: mullvad
        wireguard_private_key: "<from your Mullvad WireGuard config>"
        wireguard_addresses: 10.66.1.2/32
        server_countries: Germany
      vpn-server:
        wg_host: vpn.example.org     # aquilo a que os clientes e os nodes se ligam

  lychee:                                # um node gateway
    role: node
    node:
      preset: gateway
      pub_iface: eth0                # o lado da LAN
      downloader: { download_dir: /mnt/data/downloads }

  papaya:                               # um node cloud em uCore HCI
    role: node
    ucore: { image: ghcr.io/ublue-os/ucore-hci:stable }
    node:
      preset: cloud
      vpn_ip: 10.8.0.25
      cloud: { nextcloud_datadir: /mnt/nvme_2tb/docker/knnc-data, memory_limit: 8192M }
      vault: { signups_allowed: true }   # para a primeira conta; desativa-o depois
```

Não há palavras-passe de serviços aqui. Cada palavra-passe que deixas de fora é
gerada a partir de `secrets/seed`, e `kiwi-server secrets show fleet.yaml papaya`
imprime-as. As configurações WireGuard dos nodes também não são indicadas:
`kiwi-server enroll` escreve `secrets/<hostname>.conf`, que cada node encontra
sozinho, e o endereço de malha do node é lido dele.

## Valores por omissão { #defaults }

| Chave | Por omissão |
|---|---|
| `target` / `role` / `domain` | `ucore` / `bare` / `home` |
| `timezone` / `locale` / `keyboard` | `UTC` / `en_US.UTF-8` / `us` |
| `disk` | nenhum; obrigatório para `build`, tem de começar por `/dev/` |
| `admin` | `user: core`, `ssh_keys: []`, `ssh_password_auth: false`; indica um `password_hash` para a consola |
| `network` | `dhcp: true`; estático com `address` (CIDR), `gateway`, `dns`, ou um `iprange` que distribui endereços pela ordem do ficheiro |
| `updates` | `enabled: true`, `days: [Sun]`, `time: "03:30"`, `length_minutes: 90` |
| `install` | `on_done: poweroff` (ou `reboot`) |
| `tls` | `auto: true`, `ca_dir: secrets/ca`, `name_constraints: []` |
| `debian` | `release: trixie`, `partitioning: lvm` (`regular`, `lvm`, `crypto`), `encrypt: false` |
| `ucore` | `image: ghcr.io/ublue-os/ucore:stable` |
| `unlock` | anéis Tang aos quais associar o disco (ver [Operações](operations.md#encrypted-disks-and-unlocking)) |
| `backup` | para onde se faz a cópia de segurança do diretório da fleet (`hosts: []`, `keep: 10`) |
| `vps` | `server:` o id, nome ou alcunha de um servidor netcup |

## Como as definições se combinam { #how-settings-combine }

- Os anfitriões sobrepõem-se aos valores por omissão **chave a chave**. As listas
  `admin.ssh_keys`, `debian.packages`, `debian.kernel_arguments` e as listas
  `coreos.*` *somam-se* aos valores por omissão.
- Um papel de módulos guarda as suas definições num bloco com o nome do papel
  (`master:`, `node:`): primeiro as **definições da stack**, depois **um bloco
  por módulo**.
- `modules:` nesse bloco **substitui** a lista de módulos da predefinição. Os
  módulos obrigatórios são acrescentados sozinhos.
- **As definições de ficheiro** (certificados, configurações) são caminhos
  relativos ao ficheiro fleet. O seu conteúdo é incorporado no script de papel do
  anfitrião.
- Uma definição indicada sem valor significa o valor por omissão. Uma chave mal
  escrita é um erro, com uma sugestão.

## Definições da stack { #stack-settings }

| Definição | Por omissão | Notas |
|---|---|---|
| `preset` (node) | `gateway` | `gateway`, `cloud` ou `minimal` |
| `runtime` | `podman` | quadlets podman; `docker` corre docker compose |
| `auto_update` | `registry` | `podman auto-update` semanal; `off`: as imagens mudam com um apply |
| `docker_dir` | `/home/user/docker` | a stack e os seus dados |
| `service_user` | o utilizador admin | é dono dos diretórios de dados |
| `vpn_ip` | da configuração WireGuard | o endereço de malha da máquina |
| `master_ip` | da fleet | o endereço de malha do master |
| `mesh_subnet` | `10.8.0.0/16` | |
| `wg_mtu` / `bridge_mtu` | `1376` / `1500` | mede com `kiwi-server mtu` |
| `docker_subnet` | `172.64.0.0/24` master, `172.128.0.0/24` node | |
| `pub_iface` | da rota predefinida | a interface da LAN |
| `daily_vpn_restart` | `07:00` | vazio: nunca |
| `weekly_update` | `Sun *-*-* 00:00` | vazio: nunca |

`kiwi-server roles -v` e `kiwi-server modules -v` listam todas as definições com
o respetivo valor por omissão.

## Verificar o que escreveste { #checking-what-you-wrote }

```bash
kiwi-server validate fleet.yaml          # erros e avisos
kiwi-server show fleet.yaml papaya          # a configuração efetiva de um anfitrião, com os segredos ocultos
```

O kiwi-server também verifica o domínio: `.local` é recusado, `.lan` e os
domínios de topo públicos dão um aviso (ver [DNS](../network/dns.md#names-servicehostnamehome)).

## Assumir uma máquina v1 { #taking-over-a-v1-machine }

Uma máquina que corria uma das antigas stacks v1 pode ser assumida sem perder
dados. O runtime por omissão é agora o podman, e o script de papel não para
contentores docker. Por isso, ou defines `runtime: docker`, ou paras primeiro a
stack antiga. Depois defines `docker_subnet` com o que a stack antiga usava e
mudas o nome dos diretórios de dados para os nomes dos módulos
(`kmvpn-server` → `km-vpn-server`, `knvault` → `kn-vault`, …). Os contentores
mantêm os seus endereços e o wg-easy mantém os seus peers.
