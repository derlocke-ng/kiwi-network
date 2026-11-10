# Routers: uma LAN inteira na mesh

Esta página mostra como ligar uma rede local (LAN) inteira, por exemplo a tua
rede doméstica ou a do escritório, à tua Kiwi Network através do router dessa
rede. Um dispositivo que esteja na mesh, ou seja, na rede WireGuard privada das
tuas máquinas, consegue resolver todos os nomes da rede e chegar a todos os
nodes. Os dispositivos de uma LAN atrás de um router podem fazer o mesmo sem
que cada um deles tenha de correr o WireGuard. Há duas maneiras de o conseguir:

- **O router é um cliente da mesh.** O router corre o WireGuard com uma
  configuração emitida pelo wg-easy, o servidor WireGuard do master
  (`kiwi-server enroll fleet.yaml router --group routers`), e encaminha a
  sub-rede da mesh (`10.8.0.0/16`) para o túnel. A isto chama-se um túnel
  *split*, porque só o tráfego destinado à mesh passa por ele. Num túnel *full*
  passa todo o tráfego, e a LAN inteira chega à Internet pela saída do
  master, ou seja, pela ligação do master à Internet.
- **O router tem uma rota estática para um node gateway.** O router não tem
  túnel nenhum. Envia o tráfego destinado à sub-rede da mesh para um node da
  LAN que corre o módulo `gateway`, e esse node reencaminha-o através do seu
  cliente VPN.

Em ambos os casos basta uma regra de DNS, sem entradas para cada máquina. A
regra reencaminha as consultas relativas ao domínio da tua rede (`*.home`) para o
Pi-hole do master, que conhece os nomes de todas as máquinas e de todos os
serviços. No DNS do router, nada mais muda.

Há uma coisa que não funciona: um dispositivo de uma LAN não consegue chegar a
um dispositivo *atrás de outro router* pelo endereço de LAN deste último. A
mesh só transporta tráfego para endereços da mesh, e isso é intencional.

## OpenWrt { #openwrt }

Para o OpenWrt, o kiwi-server escreve a configuração completa sob a forma de um
script `uci`:

```bash
# o router como cliente da mesh, com a configuração emitida pelo wg-easy do master
kiwi-server openwrt fleet.yaml --wireguard secrets/router.conf          # split: só a mesh
kiwi-server openwrt fleet.yaml --wireguard secrets/router.conf --full   # full: tudo

# sem túnel no router: uma rota estática para o node gateway lychee
# (o lychee precisa de um endereço de LAN estático no ficheiro fleet: network.dhcp false + address)
kiwi-server openwrt fleet.yaml --via lychee
kiwi-server openwrt fleet.yaml --via 192.168.1.5
```

Copia o resultado para o router e executa-o lá:

```bash
kiwi-server openwrt fleet.yaml --wireguard secrets/router.conf > kiwi.sh
scp kiwi.sh root@192.168.1.1:/tmp/ && ssh root@192.168.1.1 sh /tmp/kiwi.sh
```

O script instala o pacote do WireGuard, se ainda não estiver instalado. Cria
uma interface chamada `kiwi`, nome que podes mudar com `--name`. A interface usa
como MTU o valor de `wg_mtu` do ficheiro fleet e tem um único peer, o master. O
peer é criado com `route_allowed_ips`, pelo que é o próprio OpenWrt a
acrescentar as rotas. O script cria também uma zona de firewall para a qual a
LAN pode encaminhar tráfego, com masquerading e MSS clamping. Por fim,
acrescenta a regra do dnsmasq que reencaminha o domínio da tua rede para o
master (`server=/home/10.8.0.1`). Com `--full`, o dnsmasq envia todas as
consultas DNS para o Pi-hole do master. Todas as secções que o script escreve
têm um nome, por isso, se o executares outra vez, ele substitui o que tinha
escrito antes.

## FritzBox { #fritzbox }

O Fritz!OS tem um cliente WireGuard e rotas estáticas, mas não consegue
reencaminhar as consultas DNS de um só domínio. A regra de DNS tem, por isso, de
ficar a cargo de um node:

1. **Túnel:** vai a Internet → Permit Access → VPN (WireGuard) → Add
   Connection → connect to another WireGuard service (ligar a outro serviço
   WireGuard) e importa a configuração que o master emitiu. É a linha
   `AllowedIPs` dessa configuração que decide se o túnel é split ou full.
2. **Ou uma rota estática:** vai a Home Network → Network → Network Settings →
   IPv4 Routes. Indica `10.8.0.0` como destino, `255.255.0.0` como máscara de
   sub-rede e o endereço de LAN do node gateway como gateway.
3. **DNS:** põe a LAN a usar um Pi-hole como servidor DNS. Podes indicar o node
   gateway como servidor DNS local, ou deixar que o Pi-hole do node seja o
   servidor DHCP da LAN (as definições `dns.dhcp_*`, em conjunto com o módulo
   dhcp-relay). O Pi-hole do node conhece os nomes da tua rede e reencaminha
   todas as outras consultas para o master.

Podes usar o túnel e as rotas estáticas ao mesmo tempo. Nesse caso, o tráfego
destinado à mesh passa pelo túnel.

## Qualquer outro router { #any-other-router }

Para qualquer outro router, bastam três coisas. Dá ao router uma configuração
de cliente WireGuard, ou então acrescenta uma rota estática para `10.8.0.0/16`
que aponte para o endereço de LAN do node gateway. Depois, põe a LAN a usar
como servidor DNS um Pi-hole que conheça a tua rede. Qualquer node que corra o
módulo `dns` é um Pi-hole desses. Os routers baseados no dnsmasq (DD-WRT,
Tomato, o forwarder do pfSense) aceitam também a regra de reencaminhamento de
uma só linha, `server=/home/10.8.0.1`.
