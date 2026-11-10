# kiwi-killswitch

Um **kill switch de VPN fail-closed** para o GNOME no Fedora Silverblue e no
Bluefin. Um único daemon root é dono da firewall. Um botão nas Definições Rápidas
do GNOME, uma app GTK4 e uma CLI controlam-no através do bus de sistema D-Bus,
sem nunca pedirem uma palavra-passe.

Protege **uma** ligação VPN de cada vez, WireGuard ou OpenVPN. Não liga a tua VPN
por ti: ativas as ligações nas Definições do GNOME, e o kill switch constrói uma
firewall à prova de fugas em torno do que estiver de facto ativo.

- Repositório: [derlocke-ng/kiwi-killswitch](https://github.com/derlocke-ng/kiwi-killswitch), GPL-3.0-or-later
- Versão mais recente: **v0.2.3**. Está no [catálogo Kiwi](catalogs.md), âmbitos de utilizador + sistema.
- GNOME Shell 45 a 50.

```
┌─ your session (unprivileged) ─────────────┐   ┌─ root ──────────────────────┐
│  GNOME Quick Settings toggle              │   │  kiwi-killswitchd           │
│  kiwi-killswitch-settings (GTK4)          │──▶│   nftables  (inet + netdev) │
│  kiwi-killswitch (CLI)                    │   │   systemd-resolved steering │
└───────────────────────────────────────────┘   │   NM + kernel event watcher │
             D-Bus system bus, group `wheel`    └─────────────────────────────┘
```

Uma extensão GNOME é um processo sem privilégios. Não pode nem deve tocar na
firewall, por isso a aplicação das regras vive no daemon e a interface só pede.

## O que faz { #what-it-does }

- **Fail-closed.** `policy drop` em output, input e forward, IPv4 e IPv6,
  trocadas de forma atómica. O tráfego só sai pelo túnel protegido. Se a VPN
  cair, se reiniciares, ou se passares do Wi-Fi para a partilha de ligação, tudo
  fica bloqueado até haver de novo um caminho permitido.
- **As interfaces novas não têm fugas.** Liga a partilha de ligação por USB ou
  ativa o Wi-Fi com o kill switch armado, e a nova interface fica bloqueada por
  omissão, não permitida por esquecimento.
- **Três níveis de aplicação.** *Standard* filtra output e input. *Strict* (o
  valor por omissão) filtra também o tráfego **reencaminhado**, porque
  contentores, VMs e o Waydroid encaminham através do anfitrião e os pacotes
  reencaminhados nunca passam pelo hook de output. *Paranoid* acrescenta uma
  cadeia **netdev egress** em cada placa de rede, a única camada que vê o tráfego
  de raw sockets.
- **O DNS não se pode extraviar.** Escolhe entre através da VPN, o da própria rede
  (só kiwi-nodes de confiança) ou um resolvedor à tua escolha. É aplicado através
  das definições por ligação do systemd-resolved, com uma rede de segurança
  nftables que descarta todas as outras consultas.
- **Os endpoints com nome de anfitrião são fixados, não confiados ao DNS.** O
  daemon resolve ele próprio o nome de anfitrião de um servidor VPN, por
  DNS-over-HTTPS para um IP fixado com um certificado verificado, e guarda em
  cache todas as respostas.
- **Escolhe uma ligação e depois carrega em Apply.** As alterações ficam preparadas, por isso
  podes mudar de "LAN de casa + kiwi-node" para "partilha de ligação + VPN"
  *quando já estás na partilha de ligação*, e depois aplicá-lo como uma única
  transação atómica, sem nenhuma janela desarmada pelo meio.
- **kiwi-nodes de confiança.** Um gateway que já faz o túnel por ti (um
  [node gateway](../server/roles.md#node)), identificado por IP **e** MAC, pode
  substituir a VPN na sua própria rede. É opcional e nunca é deduzido.
- **Uma VPN, imposta.** Só o servidor da ligação selecionada está acessível.
  Qualquer outro túnel que inicies não consegue ligar-se, e a interface diz qual.
- **Sobrevive a tudo.** Reinícios, terminar e iniciar sessão, reinícios do
  NetworkManager: as regras ficam. Uma unidade separada instala um bloqueio total
  *antes de a rede arrancar*.

## Instalar { #install }

Requer `nftables`, `NetworkManager`, `python3-gobject` e, para WireGuard,
`wireguard-tools`, todos presentes no Silverblue e no Bluefin. Nada é escrito no
`/usr` imutável. O teu utilizador tem de estar em `wheel`.

```bash
kiwi install kiwi-killswitch   # as duas metades; configura o âmbito de sistema do kiwi se for preciso
```

Ou a partir de um clone: `sudo ./install.sh install` (o daemon, a CLI, a política
do bus e as unidades systemd), depois `./install.sh install` (a extensão GNOME e a
app de definições). Termina a sessão e volta a entrar para que o GNOME carregue a
extensão. A desinstalação desarma primeiro, por isso não te pode deixar
bloqueado.

## Usar { #use }

Abre **Quick Settings → Kill Switch** para armar, desarmar e escolher que VPN é
protegida, ou o **Kiwi Kill Switch** na grelha de aplicações para tudo o resto.

```bash
kiwi-killswitch status                   # o que está imposto neste momento
kiwi-killswitch list                     # as ligações VPN que o NetworkManager conhece
kiwi-killswitch vpn <name>               # prepara qual é protegida
kiwi-killswitch set dns_mode tunnel
kiwi-killswitch apply                    # uma única transação atómica
kiwi-killswitch arm                      # ou: arm <vpn>
kiwi-killswitch disarm
kiwi-killswitch pending                  # o que está preparado; revert descarta-o
```

!!! warning "Armar por SSH"
    Armar corta uma sessão que venha de uma sub-rede que não esteja em
    `mgmt_subnets`. É o comportamento correto de um kill switch. Define-a
    primeiro:
    ```bash
    kiwi-killswitch set mgmt_subnets 192.168.0.0/16
    kiwi-killswitch set allow_in_ports 22
    kiwi-killswitch apply
    ```

**Recuperação.** A CLI não precisa de rede, por isso um TTY chega sempre:
`kiwi-killswitch disarm`. Se o próprio daemon tiver desaparecido:
`sudo nft delete table inet kiwi_ks` e `sudo nft delete table netdev kiwi_ks_egress`.

**Máquinas virtuais.** Uma VM em bridge nunca encaminha através do anfitrião, por
isso o kill switch deixa-a em paz (evita `paranoid`, que filtra na placa física).
Uma VM com NAT encaminha através do anfitrião. `strict` envia-a pelo túnel e
bloqueia-a quando o túnel está em baixo. Acrescenta a sua sub-rede a
`mgmt_subnets` para que o DHCP e o DNS dela cheguem ao anfitrião:

| Definição | Saída | Entrada | Fixada fora do túnel |
|---|---|---|---|
| `allow_lan` | sim (auto) | não | não |
| `bypass_subnets` | sim | não | não |
| `mgmt_subnets` | sim | sim | sim |

**Verificar.** Arma-o e depois desliga a VPN (`nmcli connection down …`).
`curl --max-time 5 ifconfig.me` tem de **esgotar o tempo**, não mostrar o teu IP
real. Não o avalies comparando IPs de saída: prova o uso do túnel com
`wg show <iface> transfer` ou `ip route get 1.1.1.1`.

## Coexistência e limites conhecidos { #coexistence-and-known-limits }

- **O firewalld pode ficar ativo.** As suas cadeias correm com prioridade 10 e as
  nossas com −10.
- **Não** o corras ao lado de outro kill switch que seja dono de uma tabela de
  output-drop.
- Deixa o `nftables.service` em paz se não o usas. Pará-lo esvazia todas as
  tabelas. O daemon repõe as suas regras em segundos, mas não há razão para abrir
  essa janela.
- Uma VPN com um endpoint por **nome de anfitrião** não consegue voltar a ligar-se
  enquanto o kill switch está armado, a não ser que o DNS esteja definido como
  *a resolver I choose*. O NetworkManager e o OpenVPN procuram o nome através do
  resolvedor do sistema, que está bloqueado enquanto não houver nenhum túnel
  ativo. As ligações com um IP literal não são afetadas.
- **Um resolvedor à tua escolha está acessível fora do túnel** enquanto o túnel
  estiver em baixo. Ativa o DNS-over-TLS para ele.
- **Um node de confiança guardado sem MAC** é identificado apenas pelo seu
  endereço de gateway.
- **O controlo sem palavra-passe** é a política do bus D-Bus para o grupo
  `wheel`. Isso também significa que qualquer programa que corra como tu pode
  desligar o kill switch sem perguntar.
- Impede fugas ao nível da rede. Não é o Tails nem o Whonix e não faz nada quanto
  ao fingerprinting do navegador, ao WebRTC ou a uma app que comunique para casa
  através do túnel.
- É uma ferramenta pessoal e não foi auditada de forma independente.
  `tests/run.sh` põe à prova o daemon real com nftables real, cada grupo de testes
  no seu próprio namespace, sem root.
- As suas tags de versão ainda não são assinadas, por isso, com o kiwi-updater
  2.4, a sua metade root pede a tua palavra-passe quando se atualiza.

Descende do `gnome-vpn-killswitch` (ordem de arranque), do `kiwi-vpn-monitor`
(deteção do gateway) e do `nova-killswitch` (a arquitetura do daemon), do mesmo
autor.
