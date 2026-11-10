# Routers: uma LAN inteira na malha

Um dispositivo na malha resolve todos os nomes da fleet e alcança todos os nodes.
Uma LAN atrás de um router pode fazer o mesmo sem que cada dispositivo corra
WireGuard, de uma de duas formas:

- **O router é um cliente da malha.** Corre WireGuard com uma configuração que o
  wg-easy do master emitiu (`kiwi-server enroll fleet.yaml router --group routers`)
  e encaminha a sub-rede da malha (`10.8.0.0/16`) para o túnel.
  Esse é o túnel *split*: só o tráfego da malha passa por ele. O túnel *full*
  envia tudo, por isso a LAN inteira chega à Internet através da saída do
  master.
- **Uma rota estática para um node gateway.** O router não tem túnel. Envia a
  sub-rede da malha para um node na LAN que corre o módulo `gateway`, que a
  reencaminha através do seu cliente VPN.

Em qualquer dos casos, uma só regra de DNS substitui as exceções por anfitrião: o
domínio da fleet (`*.home`) é reencaminhado para o Pi-hole do master, que conhece
todos os nomes de anfitrião e de serviço. Nada mais muda no DNS do router.

O que a LAN não consegue fazer é alcançar um dispositivo *atrás de outro router*
pelo seu endereço de LAN. A malha só transporta endereços de malha, por desenho.

## OpenWrt { #openwrt }

O kiwi-server escreve a configuração inteira como um script `uci`:

```bash
# o router como cliente da malha, com a configuração que o wg-easy do master emitiu
kiwi-server openwrt fleet.yaml --wireguard secrets/router.conf          # split: só a malha
kiwi-server openwrt fleet.yaml --wireguard secrets/router.conf --full   # full: tudo

# sem túnel no router: uma rota estática para o node gateway lychee
# (o lychee precisa de um endereço de LAN estático na fleet: network.dhcp false + address)
kiwi-server openwrt fleet.yaml --via lychee
kiwi-server openwrt fleet.yaml --via 192.168.1.5
```

Copia o resultado para o router e corre-o:

```bash
kiwi-server openwrt fleet.yaml --wireguard secrets/router.conf > kiwi.sh
scp kiwi.sh root@192.168.1.1:/tmp/ && ssh root@192.168.1.1 sh /tmp/kiwi.sh
```

O script instala o pacote WireGuard se faltar. Cria uma interface `kiwi` (muda o
nome com `--name`), com o `wg_mtu` da fleet como MTU e um peer para o master
e `route_allowed_ips`, uma zona de firewall para a qual a LAN pode reencaminhar
(com masquerading e MSS clamping), e o reencaminhamento do dnsmasq para o domínio
da fleet (`server=/home/10.8.0.1`). Com `--full`, o dnsmasq envia todas as
consultas para o Pi-hole do master. Todas as secções têm nome, por isso correr o
script de novo substitui o que ele escreveu antes.

## FritzBox { #fritzbox }

O Fritz!OS tem um cliente WireGuard e rotas estáticas, mas não tem
reencaminhamento de DNS por domínio, por isso a regra de DNS passa para um node:

1. **Túnel:** Internet → Permit Access → VPN (WireGuard) → Add Connection →
   connect to another WireGuard service → importa a configuração que o master
   emitiu. O seu `AllowedIPs` decide entre split e full.
2. **Ou uma rota estática:** Home Network → Network → Network Settings → IPv4
   Routes. Destino `10.8.0.0`, máscara de sub-rede `255.255.0.0`, gateway o
   endereço de LAN do node gateway.
3. **DNS:** aponta a LAN para um Pi-hole. Ou defines o node gateway como servidor
   DNS local, ou deixas o Pi-hole do node ser o servidor DHCP da LAN (definições
   `dns.dhcp_*` mais o módulo dhcp-relay). O Pi-hole do node tem os nomes da fleet
   e reencaminha o resto para o master.

O túnel e as rotas estáticas podem coexistir. Para a malha, ganha o túnel.

## Qualquer outro router { #any-other-router }

Bastam três factos. Ou dás ao router uma configuração de cliente WireGuard, ou
acrescentas uma rota estática para `10.8.0.0/16` até ao endereço de LAN do node
gateway. Depois apontas o DNS da LAN para um Pi-hole que conheça a fleet, ou
seja, qualquer node que corra o módulo `dns`. Os routers com dnsmasq por baixo
(DD-WRT, Tomato, o forwarder do pfSense) também aceitam o reencaminhamento de uma
linha `server=/home/10.8.0.1`.
