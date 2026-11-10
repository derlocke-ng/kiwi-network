# kiwi-cli-tools-desktop

O kiwi-cli-tools-desktop é um pacote com quatro pequenas ferramentas de linha
de comandos para um computador Linux. O `torlink` dá acesso a um serviço
noutra máquina através do Tor, o `pweb` partilha uma pasta por HTTPS, o
`select-server` deixa-te escolher um anfitrião SSH num menu e o `tethering`
ajusta o TTL do tráfego dos dispositivos que usam a partilha de ligação desta
máquina.

- Repositório: [derlocke-ng/kiwi-cli-tools-desktop](https://github.com/derlocke-ng/kiwi-cli-tools-desktop), GPL-3.0-or-later
- Última versão: **v1.2.1**. Está no [catálogo Kiwi](catalogs.md), âmbito de utilizador.

```bash
kiwi install kiwi-cli-tools-desktop   # ou ./install.sh install, para ~/.local/bin
```

## `torlink`: aceder a uma máquina através do Tor { #torlink-reach-a-machine-over-tor }

O `torlink` permite-te aceder a qualquer serviço TCP noutra máquina, como o
SSH, uma interface web ou uma base de dados, através da rede Tor. É uma
alternativa simples a uma VPN: nenhuma das máquinas precisa de uma porta
aberta, não precisas de conta e não há servidor nenhum para manter. O Tor e o
socat correm juntos num contentor Podman rootless, por isso só precisas do
Podman.

Uma máquina que oferece serviços é identificada pelo seu endereço onion, um
endereço dentro da rede Tor. Nessa máquina crias um **código de convite** para
um par (peer), ou seja, para a outra parte que deve ter acesso. O par aceita o
código na máquina dele. O código contém uma chave de autorização de cliente do
Tor. Sem essa chave, ninguém consegue sequer ver que o serviço existe, por
isso trata o código como uma palavra-passe.

```bash
# máquina A: oferecer SSH e uma interface web ao "bob"
torlink add-service ssh 22
torlink add-service web 8080
torlink invite bob ssh web          # mostra torlink1:…  (secreto!)

# máquina B: usá-los
torlink accept torlink1:… alice
torlink up
torlink ssh alice                   # SSH através do Tor
torlink connect alice web           # 127.0.0.1:2200 → a interface web da alice
torlink ssh-config >> ~/.ssh/config # depois `ssh alice-tor`; `select-server tor` lista-os
```

Cada convite é um serviço onion separado, que contém apenas os serviços que
indicaste nesse convite. É por isso que `torlink revoke bob` retira esse
acesso de forma definitiva. `torlink ls` mostra os teus serviços, os teus
pares e os teus reencaminhamentos, ou seja, as portas locais que levam aos
serviços de um par. O Tor só transporta TCP, e a primeira ligação demora algum
tempo. A porta SOCKS do contentor (19050) só escuta na interface de loopback.
O estado do `torlink`, incluindo as tuas chaves onion, fica guardado em
`~/.local/share/torlink`, e `torlink purge` apaga-o.

## `pweb`: partilhar uma pasta por HTTPS { #pweb-share-a-folder-over-https }

O `pweb` serve a **pasta atual** por HTTPS, numa porta livre escolhida ao
acaso. Usa-o para passar um ficheiro a outra máquina da mesma rede. Na
primeira vez que corre, cria um certificado autoassinado, que depois
reutiliza. Enquanto o `pweb` estiver a correr, qualquer máquina da rede local
consegue aceder à pasta. Por isso, inicia-o na pasta que queres mesmo
partilhar e para-o com Ctrl+C quando acabares.

```
$ cd ~/Downloads && pweb
serving /home/you/Downloads
on https://yourhost:40123  (also https://localhost:40123)
```

## `select-server`: escolher um anfitrião SSH { #select-server-pick-an-ssh-host }

O `select-server` mostra um menu numerado com todos os aliases `Host`
concretos do teu `~/.ssh/config`, ou seja, todos os que não são padrões com
caracteres universais. Escolhes um e ele liga-se a esse anfitrião. Para
filtrar o menu, atribui etiquetas aos teus anfitriões: acrescenta um
comentário como `# tags: work prod` dentro do bloco `Host` e indica uma
etiqueta na linha de comandos:

```
$ select-server work            # só os anfitriões com a etiqueta "work"
$ select-server --tags          # as etiquetas que tens
$ select-server -f other.conf   # outro ficheiro de configuração
```

## `tethering`: ajustar o TTL para a partilha de ligação { #tethering-the-ttl-fix }

O `tethering` é para quando outros dispositivos usam a ligação à Internet
desta máquina, o que se chama tethering ou partilha de ligação. Alguns
operadores contam os saltos de rede do tráfego e conseguem assim distinguir
os dispositivos ligados por partilha da própria máquina. O `tethering` define
o TTL como 64 em todo o tráfego que chega por uma determinada interface. Para
o operador, o tráfego desses dispositivos passa então a parecer tráfego da
própria máquina. A ferramenta pede sudo e acrescenta uma regra `iptables` do
tipo mangle. A regra **não** sobrevive a um reinício.

```
tethering            # escolher a interface e definir a regra
tethering --status
tethering --off
```
