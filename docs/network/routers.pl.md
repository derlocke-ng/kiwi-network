# Routery: cała sieć lokalna w sieci mesh

Ta strona pokazuje, jak przez router podłączyć do Kiwi Network całą sieć
lokalną (LAN), na przykład domową albo biurową. Urządzenie w sieci mesh, czyli
w prywatnej sieci WireGuard twoich maszyn, rozwiązuje każdą nazwę z twojej
sieci i ma dostęp do każdego node’a. Urządzenia w sieci lokalnej za routerem
mogą to samo, a żadne z nich nie musi uruchamiać WireGuard. Można to
skonfigurować na dwa sposoby:

- **Router jest klientem w sieci mesh.** Router uruchamia WireGuard
  z konfiguracją wystawioną przez wg-easy, serwer WireGuard mastera
  (`kiwi-server enroll fleet.yaml router --group routers`). Kieruje do tunelu
  ruch do podsieci mesh (`10.8.0.0/16`). Taki tunel nazywa się *split*, bo
  przechodzi przez niego tylko ruch do sieci mesh. Tunel *full* przenosi cały
  ruch, więc cała sieć lokalna łączy się z internetem przez wyjście mastera,
  czyli jego połączenie z internetem.
- **Router ma trasę statyczną do node’a `gateway`.** Na routerze nie ma
  tunelu. Ruch do podsieci mesh router wysyła do node’a w sieci lokalnej,
  na którym działa moduł `gateway`, a ten przekazuje go dalej przez swojego
  klienta VPN.

W obu przypadkach wystarczy jedna reguła DNS i nie trzeba wpisywać
poszczególnych hostów. Reguła przekazuje zapytania o domenę twojej sieci
(`*.home`) do Pi-hole’a mastera, który zna każdą nazwę hosta i każdą nazwę
usługi. Poza tym ustawienia DNS routera się nie zmieniają.

Jednej rzeczy nie da się zrobić: urządzenie w sieci lokalnej nie połączy się
z urządzeniem *za innym routerem* po jego adresie w tamtej sieci lokalnej.
Sieć mesh przenosi tylko ruch do adresów w sieci mesh i tak ma być.

## OpenWrt { #openwrt }

Dla OpenWrt kiwi-server zapisuje całą konfigurację jako skrypt `uci`:

```bash
# router jako klient w sieci mesh, z konfiguracją wystawioną przez wg-easy mastera
kiwi-server openwrt fleet.yaml --wireguard secrets/router.conf          # split: tylko sieć mesh
kiwi-server openwrt fleet.yaml --wireguard secrets/router.conf --full   # full: cały ruch

# bez tunelu na routerze: trasa statyczna do node'a gateway lychee
# (lychee potrzebuje w pliku fleet stałego adresu w LAN: network.dhcp false + address)
kiwi-server openwrt fleet.yaml --via lychee
kiwi-server openwrt fleet.yaml --via 192.168.1.5
```

Skopiuj wynik na router i uruchom go tam:

```bash
kiwi-server openwrt fleet.yaml --wireguard secrets/router.conf > kiwi.sh
scp kiwi.sh root@192.168.1.1:/tmp/ && ssh root@192.168.1.1 sh /tmp/kiwi.sh
```

Skrypt instaluje pakiet WireGuard, jeśli go brakuje. Tworzy interfejs o nazwie
`kiwi` (nazwę zmienisz opcją `--name`). Interfejs dostaje jako MTU wartość
`wg_mtu` z pliku fleet i ma jednego peera, mastera. Peer jest tworzony
z opcją `route_allowed_ips`, więc trasy OpenWrt dodaje sam. Skrypt tworzy też
strefę zapory sieciowej, do której sieć lokalna może przekazywać ruch,
z maskaradą i MSS clamping. Na koniec dodaje regułę dnsmasq, która przekazuje
domenę twojej sieci do mastera (`server=/home/10.8.0.1`). Z opcją `--full`
dnsmasq wysyła każde zapytanie DNS do Pi-hole’a mastera. Każda sekcja, którą
zapisuje skrypt, ma nazwę, więc ponowne uruchomienie skryptu zastępuje to, co
zapisał poprzednio.

## FritzBox { #fritzbox }

Fritz!OS ma klienta WireGuard i trasy statyczne, ale nie potrafi przekazywać
zapytań DNS o jedną konkretną domenę. Regułą DNS musi się więc zająć node:

1. **Tunel:** przejdź do Internet → Permit Access → VPN (WireGuard) → Add
   Connection → connect to another WireGuard service i zaimportuj konfigurację
   wystawioną przez mastera. Linia `AllowedIPs` w tej konfiguracji decyduje
   o tym, czy tunel jest split, czy full.
2. **Albo trasa statyczna:** przejdź do Home Network → Network → Network
   Settings → IPv4 Routes. Jako cel wpisz `10.8.0.0`, jako maskę podsieci
   `255.255.0.0`, a jako bramę adres node’a `gateway` w sieci lokalnej.
3. **DNS:** ustaw w sieci lokalnej Pi-hole’a jako serwer DNS. Albo wpisz node’a
   `gateway` jako lokalny serwer DNS, albo niech Pi-hole node’a będzie serwerem
   DHCP sieci lokalnej (ustawienia `dns.dhcp_*` razem z modułem dhcp-relay).
   Pi-hole node’a zna nazwy z twojej sieci, a wszystkie inne zapytania
   przekazuje do mastera.

Tunelu i tras statycznych możesz używać jednocześnie. Ruch do sieci mesh idzie
wtedy przez tunel.

## Każdy inny router { #any-other-router }

W przypadku każdego innego routera wystarczą trzy rzeczy. Daj routerowi
konfigurację klienta WireGuard albo dodaj trasę statyczną do `10.8.0.0/16`,
która wskazuje adres node’a `gateway` w sieci lokalnej. Następnie ustaw jako
serwer DNS sieci lokalnej Pi-hole’a, który zna twoją sieć. Takim Pi-hole’em
jest każdy node z modułem `dns`. Routery oparte na dnsmasq (DD-WRT, Tomato,
forwarder w pfSense) przyjmą też jednolinijkową regułę przekazywania
`server=/home/10.8.0.1`.
