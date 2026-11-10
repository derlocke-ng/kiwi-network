# Routery: cały LAN w sieci mesh

Urządzenie w sieci mesh rozwiązuje każdą nazwę floty i dociera do każdego
node'a. LAN za routerem może robić to samo bez uruchamiania WireGuard na każdym
urządzeniu, na jeden z dwóch sposobów:

- **Router jest klientem sieci mesh.** Uruchamia WireGuard z konfiguracją
  wydaną przez wg-easy mastera
  (`kiwi-server enroll fleet.yaml router --group routers`) i trasuje podsieć
  mesh (`10.8.0.0/16`) do tunelu. To tunel *split*: przechodzi przez niego
  tylko ruch sieci mesh. Tunel *full* wysyła wszystko, więc cały LAN wychodzi
  do Internetu przez wyjście mastera.
- **Trasa statyczna do node'a gateway.** Router nie ma tunelu. Wysyła podsieć
  mesh do node'a w LAN, który uruchamia moduł `gateway`, a ten przekazuje ją
  przez swojego klienta VPN.

W obu przypadkach jedna reguła DNS zastępuje nadpisania dla poszczególnych
hostów: domena floty (`*.home`) jest przekazywana do Pi-hole mastera, który
zna każdą nazwę hosta i usługi. Poza tym nic w DNS routera się nie zmienia.

LAN nie może natomiast dotrzeć do urządzenia *za innym routerem* po jego
adresie LAN. Sieć mesh przenosi tylko adresy mesh, celowo.

## OpenWrt { #openwrt }

kiwi-server zapisuje całą konfigurację jako skrypt `uci`:

```bash
# router jako klient sieci mesh, z konfiguracją wydaną przez wg-easy mastera
kiwi-server openwrt fleet.yaml --wireguard secrets/router.conf          # split: tylko sieć mesh
kiwi-server openwrt fleet.yaml --wireguard secrets/router.conf --full   # full: wszystko

# bez tunelu na routerze: trasa statyczna do node'a gateway lychee
# (lychee potrzebuje we flocie statycznego adresu LAN: network.dhcp false + address)
kiwi-server openwrt fleet.yaml --via lychee
kiwi-server openwrt fleet.yaml --via 192.168.1.5
```

Skopiuj wynik na router i uruchom go:

```bash
kiwi-server openwrt fleet.yaml --wireguard secrets/router.conf > kiwi.sh
scp kiwi.sh root@192.168.1.1:/tmp/ && ssh root@192.168.1.1 sh /tmp/kiwi.sh
```

Skrypt instaluje pakiet WireGuard, jeśli go brakuje. Tworzy interfejs `kiwi`
(nazwę zmienisz przez `--name`) z `wg_mtu` floty jako MTU i jednym peerem dla
mastera oraz `route_allowed_ips`, strefę zapory, do której LAN może
przekazywać ruch (z maskaradą i MSS clamping), oraz przekierowanie dnsmasq dla
domeny floty (`server=/home/10.8.0.1`). Z `--full` dnsmasq wysyła każde
zapytanie do Pi-hole mastera. Każda sekcja ma nazwę, więc ponowne uruchomienie
skryptu zastępuje to, co zapisał wcześniej.

## FritzBox { #fritzbox }

Fritz!OS ma klienta WireGuard i trasy statyczne, ale nie ma przekazywania DNS
dla poszczególnych domen, więc reguła DNS przenosi się na node'a:

1. **Tunel:** Internet → Permit Access → VPN (WireGuard) → Add Connection →
   connect to another WireGuard service → zaimportuj konfigurację wydaną przez
   mastera. Jej `AllowedIPs` decyduje o trybie split albo full.
2. **Albo trasa statyczna:** Home Network → Network → Network Settings → IPv4
   Routes. Cel `10.8.0.0`, maska podsieci `255.255.0.0`, brama: adres LAN
   node'a gateway.
3. **DNS:** skieruj LAN na Pi-hole. Ustaw node'a gateway jako lokalny serwer
   DNS albo pozwól, by Pi-hole node'a był serwerem DHCP w LAN (ustawienia
   `dns.dhcp_*` plus moduł dhcp-relay). Pi-hole node'a zna nazwy floty, a
   resztę przekazuje do mastera.

Tunel i trasy statyczne mogą współistnieć. Dla sieci mesh wygrywa tunel.

## Każdy inny router { #any-other-router }

Wystarczą trzy fakty. Daj routerowi konfigurację klienta WireGuard albo dodaj
trasę statyczną dla `10.8.0.0/16` do adresu LAN node'a gateway. Następnie
skieruj DNS w LAN na Pi-hole, który zna flotę, czyli na dowolny node z modułem
`dns`. Routery z dnsmasq pod spodem (DD-WRT, Tomato, forwarder pfSense) też
przyjmą jednolinijkowe przekierowanie `server=/home/10.8.0.1`.
