# Jedna maszyna bez pliku fleet

kiwi-server zarządza całą siecią maszyn. Jeśli chcesz uruchomić stack tylko na
jednej maszynie, nie jest ci potrzebny. Stack to wszystkie kontenery i usługi,
które uruchamia maszyna. kiwi-server składa się z dwóch mniejszych narzędzi
i możesz używać ich osobno:

| Repozytorium | Co to jest |
|---|---|
| [**kiwi-modules**](https://github.com/derlocke-ng/kiwi-modules) | Moduły i program, który generuje z nich konfigurację. Czyta **jeden plik maszyny i zapisuje paczkę stacku**, czyli katalog z wygenerowaną konfiguracją stacku tej maszyny. v0.23.0, GPL-3.0-or-later |
| [**kiwi-stack**](https://github.com/derlocke-ng/kiwi-stack) | Część działająca na maszynie. Składa się z polecenia `kiwi-stack` i biblioteki, które umieszczają paczkę na maszynie z CoreOS, uCore albo Debianem i pilnują, żeby działała. v0.5.0, GPL-3.0-or-later |

Te dwa narzędzia przydają się, gdy chcesz mieć stack na jednej maszynie bez
reszty kiwi-server. Może to być node konfigurowany ręcznie, moduł, który
właśnie rozwijasz, albo maszyna, która sama generuje swój stack. kiwi-server
zawiera kopie obu narzędzi, każde przypięte do tagu wydania. Maszyna wygląda
dokładnie tak samo niezależnie od tego, czy skonfigurujesz ją narzędziem
kiwi-server, czy tymi dwoma narzędziami, a w obu przypadkach z tego samego
seeda powstają te same sekrety.

```
machine.yaml ──kiwi-modules render──▶ bundle/ ──copy──▶ sudo kiwi-stack apply bundle/
                                      stack.sh            → podman quadlets (or compose)
                                      docker-compose.yml  → configs, host units, timers
                                      quadlets/  configs  → kiwi-stack.target, verify
```

## Generowanie konfiguracji maszyny { #render-a-machine }

Poniższe polecenia instalują kiwi-modules, tworzą seed i generują z
przykładowego pliku maszyny paczkę stacku. Ostatnia linia kopiuje paczkę na
maszynę i tam ją stosuje.

```bash
git clone https://github.com/derlocke-ng/kiwi-modules && cd kiwi-modules
./install.sh install                       # ~/.local/bin/kiwi-modules
mkdir -p sh3/secrets && head -c 32 /dev/urandom > sh3/secrets/seed
cp examples/sh3.yaml sh3/                  # do edycji: pliki TLS, konfiguracja WireGuard
kiwi-modules render sh3/sh3.yaml -o sh3/sh3.bundle
scp -r sh3/sh3.bundle sh3:/tmp/ && ssh sh3 sudo kiwi-stack apply /tmp/sh3.bundle
```

kiwi-modules wymaga Pythona 3 z PyYAML i Jinja2. `kiwi-modules modules -v`
wypisuje wszystkie moduły i ustawienia, a `kiwi-modules profiles` role i ich
presety.

Plik maszyny opisuje jedną maszynę, tak jak w tym przykładzie:

```yaml
# node cloud
name: sh3
domain: home
target: ucore
timezone: Europe/Berlin
admin: { user: core }
role: node
node:
  preset: cloud
  cloud: { collabora: true, talk: true }
  reverse-proxy:
    tls_fullchain: secrets/sh3-fullchain.pem
    tls_privkey: secrets/sh3-privkey.pem
dns_records:                    # nazwy w sieci
  - [10.8.0.1, gate.home]
  - [10.8.0.25, cloud.sh3.home]
master_ip: 10.8.0.1
ca_cert: ca.pem                 # zaufany w kontenerach i na hoście
seed: secrets/seed              # z niego powstają generowane hasła
```

kiwi-modules nie ma własnego urzędu certyfikacji. Jeśli generujesz
konfigurację maszyny bez kiwi-server, pliki certyfikatu i klucza TLS musisz
więc dostarczyć samodzielnie. Jeśli plik maszyny nie wskazuje konfiguracji WireGuard,
kiwi-modules szuka jej w `secrets/<hostname>.conf`.

## Instalacja na maszynie { #put-it-on-the-machine }

Na maszynie zainstaluj kiwi-stack i zastosuj paczkę:

```bash
git clone https://github.com/derlocke-ng/kiwi-stack && cd kiwi-stack
sudo ./install.sh install          # /usr/local/bin/kiwi-stack i jego biblioteka
sudo kiwi-stack apply /tmp/sh3.bundle
kiwi-stack status
```

kiwi-stack wymaga basha i systemd. Potrzebuje też środowiska kontenerów, które
wskazuje `runtime` w paczce: albo podmana 4.4+ z catatonit, albo dockera
z wtyczką compose. Na Debianie kiwi-stack sam instaluje podmana.

`apply` robi ze stackiem to samo co rola kiwi-server (zobacz
[Maszyny](machines.md#apply)), tylko nie ustawia nazwy hosta ani strefy
czasowej. Można je powtarzać: ponowne zastosowanie tej samej paczki niczego
nie zmienia. Nie ma wycofywania zmian. Dane przywrócisz poleceniem
`kiwi-stack restore` z modułu backup, a starszą konfigurację, stosując starszą
paczkę.

Na maszynie nazwy nadal mówią `kiwi-server` (`/etc/kiwi-server/stack.env`,
`/var/lib/kiwi-server/`), celowo: narzędzia Kiwi
opierają się na tych nazwach, więc nie są one zmieniane.
