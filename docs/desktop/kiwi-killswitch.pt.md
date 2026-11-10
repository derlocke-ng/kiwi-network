# kiwi-killswitch

O kiwi-killswitch é um **kill switch de VPN** para o GNOME no Fedora
Silverblue e no Bluefin. Um kill switch garante que o teu computador não envia
tráfego por fora da VPN, por exemplo quando a ligação VPN cai ou quando mudas
de rede. Este é **fail-closed**: a firewall bloqueia tudo o que não for
expressamente permitido, por isso, quando alguma coisa falha, o tráfego fica
bloqueado em vez de passar.

A firewall é gerida por um único daemon com permissões de root. Controlas esse
daemon com um botão no menu *Quick Settings* do GNOME, com uma aplicação GTK4
ou com uma ferramenta de linha de comandos (CLI). As três enviam os pedidos ao
daemon pelo bus de sistema do D-Bus e nunca pedem palavra-passe.

Protege **uma** ligação VPN de cada vez, WireGuard ou OpenVPN. Não liga a VPN
por ti. As ligações inicias tu nas Definições do GNOME, e o kill switch
define as regras da firewall para a ligação que está de facto ativa, para que
nenhum tráfego possa sair do computador por fora dela.

- Repositório: [derlocke-ng/kiwi-killswitch](https://github.com/derlocke-ng/kiwi-killswitch), GPL-3.0-or-later
- Última versão: **v0.2.3**. Está no [catálogo Kiwi](catalogs.md) e tem dois
  âmbitos, user + system: uma metade é instalada na tua pasta pessoal e a
  outra pertence ao root.
- Funciona com o GNOME Shell 45 a 50.

```
┌─ your session (unprivileged) ─────────────┐   ┌─ root ──────────────────────┐
│  GNOME Quick Settings toggle              │   │  kiwi-killswitchd           │
│  kiwi-killswitch-settings (GTK4)          │──▶│   nftables  (inet + netdev) │
│  kiwi-killswitch (CLI)                    │   │   systemd-resolved steering │
└───────────────────────────────────────────┘   │   NM + kernel event watcher │
             D-Bus system bus, group `wheel`    └─────────────────────────────┘
```

Uma extensão do GNOME é um processo sem permissões de root. Não pode alterar a
firewall, e não deve poder. Por isso, é o daemon que faz todo o bloqueio, e a
interface limita-se a enviar-lhe pedidos.

## O que faz { #what-it-does }

- **É fail-closed.** A firewall usa `policy drop` para o tráfego de saída, de
  entrada e reencaminhado, em IPv4 e IPv6. Isto quer dizer que todos os
  pacotes são descartados, a não ser que uma regra os permita. Um novo
  conjunto de regras substitui o anterior num único passo atómico. O tráfego
  só pode sair pelo túnel protegido. Se a VPN cair, se reiniciares ou se
  passares do Wi-Fi para a partilha de ligação do telemóvel (tethering), tudo
  continua bloqueado até haver de novo um caminho permitido.
- **As novas interfaces de rede ficam bloqueadas.** Se ligares tethering por
  USB ou ativares o Wi-Fi enquanto o kill switch está armado, ou seja, ligado,
  a nova interface fica bloqueada por predefinição. Não passa a ser permitida
  só porque nenhuma regra fala dela.
- **Há três níveis de filtragem.** *Standard* filtra o tráfego de saída e de
  entrada. *Strict* é a predefinição e filtra também o tráfego
  **reencaminhado**. Isto é necessário porque os contentores, as VMs e o
  Waydroid enviam o tráfego através do anfitrião, e os pacotes reencaminhados
  nunca passam pelo hook de saída. *Paranoid* acrescenta uma cadeia **netdev
  egress** em cada placa de rede (NIC). É a única camada que vê o tráfego de
  raw sockets.
- **As consultas DNS não podem contornar o túnel.** Escolhes que resolvedor
  DNS é usado enquanto o kill switch está armado. Podes enviar as consultas
  DNS pela VPN, usar o resolvedor da rede onde estás ou usar um resolvedor
  escolhido por ti. O resolvedor da própria rede só é usado na rede de um
  kiwi-node de confiança. O kill switch aplica a tua escolha através das
  definições por ligação (per-link) do systemd-resolved. Como segunda
  proteção, uma regra nftables descarta qualquer outra consulta DNS.
- **Para um servidor VPN indicado por nome, o daemon não confia no DNS
  normal.** Resolve ele próprio o nome do servidor VPN. Para isso usa
  DNS-over-HTTPS, liga-se a um endereço IP fixado e verifica o certificado.
  Guarda todas as respostas em cache.
- **Primeiro escolhes uma ligação, depois aplicas.** As alterações ficam
  pendentes, ou seja, vão sendo reunidas e só têm efeito quando as aplicas.
  Assim, podes mudar de «LAN de casa + kiwi-node» para «tethering + VPN»
  *quando já estás em tethering*. Ao aplicar, todas as alterações são feitas
  numa única transação atómica, e o kill switch não fica desarmado em nenhum
  momento pelo meio.
- **kiwi-nodes de confiança.** A tua rede pode ter um gateway que já envia o
  teu tráfego por um túnel. Numa Kiwi Network, esse gateway é um
  [node gateway](../server/roles.md#node). Na sua própria rede, um gateway
  destes pode substituir a VPN. O kill switch reconhece-o pelo endereço IP
  **e** pelo endereço MAC. Tens de ativar isto tu próprio. O kill switch
  nunca decide sozinho que um gateway é de confiança.
- **Só uma VPN se pode ligar.** Só o servidor da ligação selecionada está
  acessível. Qualquer outro túnel que inicies não consegue ligar-se, e a
  interface indica-te qual é esse túnel.
- **As regras mantêm-se.** Continuam ativas depois de um reinício, depois de
  terminares sessão e voltares a entrar e depois de o NetworkManager
  reiniciar. Uma unidade à parte carrega regras de bloqueio *antes de a rede
  arrancar*.

## Instalação { #install }

O kiwi-killswitch precisa do `nftables`, do `NetworkManager` e do
`python3-gobject` e, para o WireGuard, também do `wireguard-tools`. Tudo isto
já existe no Silverblue e no Bluefin. Nada é escrito no `/usr` imutável. O teu
utilizador tem de pertencer ao grupo `wheel`.

```bash
kiwi install kiwi-killswitch   # as duas metades; prepara o âmbito de sistema do kiwi se for preciso
```

Também o podes instalar a partir de um clone do repositório. Primeiro executa
`sudo ./install.sh install`, que instala o daemon, a CLI, a política D-Bus e
as unidades systemd. Depois executa `./install.sh install`, que instala a
extensão do GNOME e a aplicação de definições. Termina a sessão e volta a
entrar, para que o GNOME carregue a extensão. Ao desinstalar, o kill switch é
desarmado primeiro, por isso a desinstalação não te pode deixar sem rede.

## Utilização { #use }

Abre **Quick Settings → Kill Switch** para armar e desarmar o kill switch e
para escolher que VPN fica protegida. Para tudo o resto, abre **Kiwi Kill
Switch** na grelha de aplicações. A CLI tem estes comandos:

```bash
kiwi-killswitch status                   # o que está a ser aplicado neste momento
kiwi-killswitch list                     # as ligações VPN que o NetworkManager conhece
kiwi-killswitch vpn <name>               # escolher (pendente) qual fica protegida
kiwi-killswitch set dns_mode tunnel
kiwi-killswitch apply                    # uma única transação atómica
kiwi-killswitch arm                      # ou: arm <vpn>
kiwi-killswitch disarm
kiwi-killswitch pending                  # o que está pendente; revert descarta-o
```

!!! warning "Armar por SSH"
    Quando armas o kill switch, uma sessão SSH vinda de uma sub-rede que não
    esteja em `mgmt_subnets` é cortada. É o comportamento correto de um kill
    switch. Se trabalhas por SSH, define primeiro estes valores:
    ```bash
    kiwi-killswitch set mgmt_subnets 192.168.0.0/16
    kiwi-killswitch set allow_in_ports 22
    kiwi-killswitch apply
    ```

**Recuperação.** A CLI não precisa de rede, por isso uma consola de texto
(TTY) chega sempre para executar `kiwi-killswitch disarm`. Se o próprio daemon
tiver desaparecido, apaga as tabelas de firewall dele com
`sudo nft delete table inet kiwi_ks` e
`sudo nft delete table netdev kiwi_ks_egress`.

**Máquinas virtuais.** Uma VM em modo bridge nunca envia o tráfego através do
anfitrião, por isso o kill switch não a afeta. Nesse caso, evita o
`paranoid`, porque esse nível filtra na placa de rede física. Uma VM com NAT
envia o tráfego através do anfitrião. Com `strict`, esse tráfego sai pelo
túnel e fica bloqueado quando o túnel está em baixo. Acrescenta a sub-rede da
VM a `mgmt_subnets`, para que os pedidos de DHCP e DNS dela cheguem ao
anfitrião. A tabela mostra o que cada definição permite:

| Definição | Saída | Entrada | Fica fora do túnel |
|---|---|---|---|
| `allow_lan` | sim (automático) | não | não |
| `bypass_subnets` | sim | não | não |
| `mgmt_subnets` | sim | sim | sim |

**Verificar se funciona.** Arma o kill switch e depois desliga a VPN com
`nmcli connection down …`. Agora, `curl --max-time 5 ifconfig.me` tem de
**esgotar o tempo limite**. Não pode mostrar o teu endereço IP real. Não
avalies o resultado comparando os endereços IP públicos que vês. Para
confirmares que o tráfego passa pelo túnel, executa `wg show <iface> transfer`
ou `ip route get 1.1.1.1`.

## Outras firewalls e limites conhecidos { #coexistence-and-known-limits }

- **O firewalld pode continuar ligado.** As cadeias dele correm com
  prioridade 10, e as do kill switch com −10.
- **Não** o uses ao mesmo tempo que outro kill switch que tenha uma tabela
  própria a descartar o tráfego de saída.
- Não mexas no `nftables.service` se não o usas. Quando este serviço é
  parado, apaga todas as tabelas nftables. O daemon volta a carregar as regras
  em poucos segundos, mas durante esses segundos as regras não existem, e não
  há motivo para provocar isso.
- Uma VPN cujo servidor esteja indicado por **nome** não consegue voltar a
  ligar-se enquanto o kill switch estiver armado, a não ser que o DNS esteja
  definido como *a resolver I choose* (um resolvedor escolhido por ti). A
  razão é que o NetworkManager e o OpenVPN resolvem o nome através do
  resolvedor do sistema, e esse resolvedor está bloqueado enquanto não houver
  túnel ativo. As ligações cujo servidor está indicado por endereço IP não
  são afetadas.
- **Um resolvedor escolhido por ti fica acessível por fora do túnel**
  enquanto o túnel estiver em baixo. Ativa o DNS-over-TLS para ele.
- **Um node de confiança guardado sem endereço MAC** é reconhecido apenas pelo
  endereço do gateway.
- **O controlo sem palavra-passe** funciona através da política D-Bus para o
  grupo `wheel`. Isto significa também que qualquer programa que corra como o
  teu utilizador pode desligar o kill switch sem te perguntar.
- Impede fugas ao nível da rede, mas não é o Tails nem o Whonix. Não faz nada
  contra a impressão digital do navegador (fingerprinting), contra o WebRTC
  nem contra uma aplicação que, pelo próprio túnel, envia dados a quem a
  desenvolveu.
- É uma ferramenta pessoal e não foi auditada de forma independente. O
  `tests/run.sh` testa o daemon real com nftables reais. Cada grupo de testes
  corre no seu próprio namespace, e os testes não precisam de root.
- As tags de versão do kiwi-killswitch ainda não são assinadas. Por isso, com o kiwi-updater 2.4,
  a metade root pede a tua palavra-passe sempre que é atualizada.

O kiwi-killswitch assenta em três ferramentas anteriores do mesmo autor. A
ordem de arranque vem do `gnome-vpn-killswitch`, a deteção do gateway vem do
`kiwi-vpn-monitor` e a arquitetura do daemon vem do `nova-killswitch`.
