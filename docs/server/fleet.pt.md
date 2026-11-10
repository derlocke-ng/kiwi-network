# O ficheiro fleet

O ficheiro fleet, `fleet.yaml`, é onde descreves todas as máquinas da tua Kiwi
Network. Para cada máquina, indica que sistema operativo recebe, para que serve
e como estão configurados os seus serviços. O kiwi-server constrói todas as
máquinas a partir desta descrição: escreves uma vez o que queres e não tens de
configurar nenhuma máquina à mão.

O ficheiro tem duas chaves. `defaults` reúne as definições que valem para todas
as máquinas, e `hosts` tem uma entrada para cada máquina. Uma definição na
entrada de uma máquina sobrepõe-se à mesma definição em `defaults`. O
`kiwi-server init` escreve um ficheiro com comentários, que podes usar como
ponto de partida, e a referência completa está em
[examples/fleet.yaml](https://github.com/derlocke-ng/kiwi-server/blob/main/examples/fleet.yaml).

Cada máquina tem um **sistema de destino** (`target`), ou seja, o sistema
operativo que é instalado, e uma **função** (`role`), que é o que a máquina faz
a seguir na rede.

- `target` é `coreos`, `ucore` (o predefinido) ou `debian`. Vê [Máquinas](machines.md).
- `role` é `bare` (o predefinido), `master` ou `node`. Vê [Funções](roles.md).

## Exemplo { #example }

Este ficheiro fleet descreve três máquinas. A primeira é o master, a máquina a
que todas as outras se ligam, num VPS Debian (um servidor virtual alugado). A
segunda é um node gateway, que faz passar pela VPN o tráfego de uma rede local.
A terceira é um node cloud, que corre o Nextcloud e o Vaultwarden.

```yaml
defaults:
  target: ucore
  role: bare
  domain: home                       # papaya passa a papaya.home; os serviços são cloud.papaya.home …
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
        wg_host: vpn.example.org     # o endereço a que os clientes e os nodes se ligam

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
      vault: { signups_allowed: true }   # para a primeira conta; desliga-o depois
```

O exemplo não tem palavras-passe de serviços. O kiwi-server gera todas as que
não indicares a partir da seed em `secrets/seed`, e
`kiwi-server secrets show fleet.yaml papaya` mostra as palavras-passe dessa
máquina.

O exemplo também não indica os ficheiros de configuração WireGuard dos nodes.
O `kiwi-server enroll` guarda a configuração de um node em
`secrets/<hostname>.conf`, e o cliente VPN do node encontra-a aí sem precisar
de nenhuma entrada no ficheiro fleet. É também desse ficheiro que se tira o
endereço do node na mesh. A mesh é a rede WireGuard privada que liga todas as
tuas máquinas, e o endereço na mesh é o endereço que uma máquina tem nessa rede.

## Predefinições { #defaults }

Se uma chave não estiver definida nem no teu bloco `defaults` nem na máquina, o
kiwi-server usa o valor incorporado que aparece nesta tabela.

| Chave | Predefinição |
|---|---|
| `target` / `role` / `domain` | `ucore` / `bare` / `home` |
| `timezone` / `locale` / `keyboard` | `UTC` / `en_US.UTF-8` / `us` |
| `disk` | Não tem predefinição. O `build` precisa dela, e o valor tem de começar por `/dev/` |
| `admin` | `user: core`, `ssh_keys: []`, `ssh_password_auth: false`. Define um `password_hash` se quiseres entrar na consola |
| `network` | `dhcp: true`. Para um endereço estático, define `address` (em notação CIDR), `gateway` e `dns`. Ou então define um `iprange`, de onde as máquinas recebem os endereços pela ordem em que aparecem no ficheiro |
| `updates` | `enabled: true`, `days: [Sun]`, `time: "03:30"`, `length_minutes: 90` |
| `install` | `on_done: poweroff` (ou `reboot`) |
| `tls` | `auto: true`, `ca_dir: secrets/ca`, `name_constraints: []` |
| `debian` | `release: trixie`, `partitioning: lvm` (`regular`, `lvm`, `crypto`), `encrypt: false` |
| `ucore` | `image: ghcr.io/ublue-os/ucore:stable` |
| `unlock` | Os anéis Tang a que o disco está associado. Um anel é um servidor Tang, que permite a uma máquina cifrada desbloquear o disco no arranque (vê [Operação](operations.md#encrypted-disks-and-unlocking)) |
| `backup` | As máquinas para onde se faz backup da pasta do ficheiro fleet, e quantos backups se guardam (`hosts: []`, `keep: 10`) |
| `vps` | `server:` o id, o nome ou a alcunha de um servidor da netcup |

## Como as definições se combinam { #how-settings-combine }

- Uma máquina sobrepõe-se às predefinições **chave a chave**, por isso só tem de
  indicar as chaves que são diferentes. A exceção são as listas
  `admin.ssh_keys`, `debian.packages`, `debian.kernel_arguments` e as listas
  `coreos.*`: as entradas que uma máquina põe nestas listas são *acrescentadas*
  às predefinidas, em vez de as substituírem.
- As funções construídas a partir de módulos, `master` e `node`, guardam as suas
  definições num bloco com o nome da função (`master:` ou `node:`). Este bloco
  contém primeiro as **definições da stack** e depois **um bloco por módulo**. A
  stack é o conjunto de contentores que uma máquina corre para os seus módulos,
  e as definições da stack aplicam-se a todos eles.
- Uma lista `modules:` dentro desse bloco **substitui** a lista de módulos do
  preset. Um preset é uma lista de módulos já pronta. Os módulos de que os
  módulos indicados dependem são acrescentados automaticamente.
- **As definições de ficheiros**, como certificados e ficheiros de
  configuração, indicam-se com caminhos relativos ao ficheiro fleet. O
  kiwi-server copia o conteúdo desses ficheiros para o script da função da
  máquina, que é o script que prepara a máquina para a sua função.
- Uma definição escrita sem valor fica com o valor predefinido. Se escreveres
  mal o nome de uma chave, o kiwi-server dá um erro e sugere a chave que
  provavelmente querias.

## Definições da stack { #stack-settings }

As definições da stack aplicam-se à stack inteira de uma máquina. Escreves-as
diretamente no bloco da função.

| Definição | Predefinição | Notas |
|---|---|---|
| `preset` (node) | `gateway` | `gateway`, `cloud` ou `minimal` |
| `runtime` | `podman` | `podman` corre os contentores como quadlets do podman, que são unidades systemd para contentores. `docker` usa o docker compose |
| `auto_update` | `registry` | `registry` executa `podman auto-update` uma vez por semana. Com `off`, as imagens dos contentores só mudam quando voltares a aplicar a máquina |
| `docker_dir` | `/home/user/docker` | a pasta onde ficam a stack e os seus dados |
| `service_user` | o utilizador de administração | o utilizador a quem pertencem as pastas de dados |
| `vpn_ip` | da configuração WireGuard | o endereço da máquina na mesh |
| `master_ip` | do ficheiro fleet | o endereço do master na mesh |
| `mesh_subnet` | `10.8.0.0/16` | |
| `wg_mtu` / `bridge_mtu` | `1376` / `1500` | podes medi-los com `kiwi-server mtu` |
| `docker_subnet` | `172.64.0.0/24` master, `172.128.0.0/24` node | |
| `pub_iface` | da rota predefinida | a interface de rede do lado da LAN |
| `daily_vpn_restart` | `07:00` | um valor vazio desliga o reinício diário |
| `weekly_update` | `Sun *-*-* 00:00` | um valor vazio desliga a atualização semanal |

`kiwi-server roles -v` e `kiwi-server modules -v` listam todas as definições com
os respetivos valores predefinidos.

## Verificar o que escreveste { #checking-what-you-wrote }

O kiwi-server pode verificar o ficheiro fleet por ti e mostrar como interpreta
uma máquina.

```bash
kiwi-server validate fleet.yaml          # erros e avisos
kiwi-server show fleet.yaml papaya          # a configuração efetiva de uma máquina, com os segredos ocultos
```

O kiwi-server verifica também o domínio. Recusa `.local` e avisa quando usas
`.lan` ou um domínio de topo público (vê
[DNS](../network/dns.md#names-servicehostnamehome)).

## Integrar uma máquina v1 { #taking-over-a-v1-machine }

Podes trazer para a tua rede uma máquina que corria uma das antigas stacks v1
sem perderes os dados dela. O runtime predefinido passou a ser o podman, e o
script da função não para os contentores docker que ainda estejam a correr. Por
isso, ou defines `runtime: docker`, ou paras primeiro a stack antiga. Depois,
define `docker_subnet` com a sub-rede que a stack antiga usava e muda o nome das
pastas de dados para os nomes dos módulos novos (`kmvpn-server` →
`km-vpn-server`, `knvault` → `kn-vault`, …). Assim, os contentores mantêm os
seus endereços, e o wg-easy mantém os seus peers.
