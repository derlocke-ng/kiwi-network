# kiwi-cli-tools-desktop

Quatro pequenos auxiliares de linha de comandos para um ambiente de trabalho
Linux.

- Repositório: [derlocke-ng/kiwi-cli-tools-desktop](https://github.com/derlocke-ng/kiwi-cli-tools-desktop), GPL-3.0-or-later
- Versão mais recente: **v1.2.1**. Está no [catálogo Kiwi](catalogs.md), âmbito de utilizador.

```bash
kiwi install kiwi-cli-tools-desktop   # ou ./install.sh install, para ~/.local/bin
```

## `torlink`: chegar a uma máquina através do Tor { #torlink-reach-a-machine-over-tor }

Uma VPN dos pobres: chega a qualquer serviço TCP (SSH, uma interface web, uma
base de dados) noutra máquina através do Tor, sem portas abertas, sem contas e
sem servidor. O Tor e o socat correm num único contentor Podman sem root, por
isso só precisas do Podman.

Um endereço onion é a identidade. O lado que oferece cria um **código de
convite** para um par, e o outro lado aceita-o. O código leva uma chave de
autorização de cliente Tor, por isso o serviço é invisível para todos os que não
a têm: trata o código como uma palavra-passe.

```bash
# máquina A: oferece SSH e uma interface web a "bob"
torlink add-service ssh 22
torlink add-service web 8080
torlink invite bob ssh web          # imprime torlink1:…  (secreto!)

# máquina B: usa-os
torlink accept torlink1:… alice
torlink up
torlink ssh alice                   # SSH através do Tor
torlink connect alice web           # 127.0.0.1:2200 → a interface web de alice
torlink ssh-config >> ~/.ssh/config # depois `ssh alice-tor`; `select-server tor` lista-os
```

Cada convite é o seu próprio serviço onion, só com os serviços que indicaste, por
isso `torlink revoke bob` remove esse acesso de vez. `torlink ls` mostra os
serviços, os pares e os reencaminhamentos. O Tor é só TCP, e a primeira ligação
demora um pouco. A porta SOCKS do contentor (19050) só escuta no loopback. O
estado, incluindo as tuas chaves onion, vive em `~/.local/share/torlink`, e
`torlink purge` apaga-o.

## `pweb`: partilhar uma pasta por HTTPS { #pweb-share-a-folder-over-https }

Serve o **diretório atual** por HTTPS numa porta livre aleatória, para passar um
ficheiro a outra máquina na mesma rede. Na primeira execução é criado um
certificado autoassinado, que depois é reutilizado. Serve para a LAN inteira, por
isso inicia-o na pasta que queres partilhar e para-o com Ctrl+C.

```
$ cd ~/Downloads && pweb
serving /home/you/Downloads
on https://yourhost:40123  (also https://localhost:40123)
```

## `select-server`: escolher um anfitrião SSH { #select-server-pick-an-ssh-host }

Um menu numerado com todos os aliases `Host` concretos do teu `~/.ssh/config`.
Escolhe um e ele liga-se. Etiqueta anfitriões com um comentário
`# tags: work prod` dentro do bloco `Host` para filtrar:

```
$ select-server work            # só anfitriões com a etiqueta "work"
$ select-server --tags          # as etiquetas que tens
$ select-server -f other.conf   # outro ficheiro de configuração
```

## `tethering`: a correção do TTL { #tethering-the-ttl-fix }

Define TTL 64 no tráfego que chega de uma interface, para que os dispositivos
ligados por partilha de ligação através desta máquina pareçam tráfego da própria
máquina para um operador que conta saltos. Pede sudo, acrescenta uma regra
`iptables` mangle, e a regra **não** sobrevive a um reinício.

```
tethering            # escolhe a interface, define a regra
tethering --status
tethering --off
```
