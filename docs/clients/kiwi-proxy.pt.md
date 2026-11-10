# kiwi-proxy

O kiwi-proxy é para quem trabalha nas redes de muitos clientes e chega a cada
uma delas por uma ligação VPN ou SOCKS própria. Guardas cada ligação como um
**exit** com nome e só a ativas quando precisas dela. Cada exit fica separado
dos outros, e um programa que usa um exit só consegue chegar à rede através
dele. Assim, dez clientes não significam dez ligações VPN a correr ao mesmo
tempo no anfitrião. Um exit pode ser usado por navegadores, ferramentas de
teste, programas do anfitrião e máquinas do kiwi-server. O kiwi-proxy funciona
com o Podman rootless, ou seja, com contentores que correm como o teu próprio
utilizador, sem permissões de root.

- Repositório: [derlocke-ng/kiwi-proxy](https://github.com/derlocke-ng/kiwi-proxy), GPL-3.0-or-later
- Última versão: **v0.7.3**. Está no [catálogo Kiwi](../desktop/catalogs.md), âmbito de utilizador.
- É composto por uma ferramenta de linha de comandos (`kiwi-proxy`), uma
  aplicação GTK4 (**Kiwi Proxy**) e unidades de utilizador do systemd. É o
  motor de proxy que antes fazia parte do kiwi-fox. Passou a ser um projeto à
  parte para que mais do que uma aplicação o possa usar.

Um **exit** é uma ligação a um upstream, guardada com um nome. O upstream é o
proxy para onde o tráfego é enviado: um proxy SOCKS5 que te deram ou um proxy
que um [módulo de fornecedor](providers.md) cria para ti através do Tor, de um
túnel VPN, do 9proxy ou da Mysterium. Um exit, por si só, é apenas uma entrada
guardada: enquanto não o ativas, não há nada a correr. Quando ativas um exit, o kiwi-proxy
arranca para ele um contentor **gateway**:

```
gateway container   owns the network namespace
                    nftables: default drop, one permitted destination
                    forwarder 127.0.0.1:1080: adds the upstream's credentials
                    dnscrypt-proxy 127.0.0.2:53: DNS through the same exit, with blocklists
```

O gateway tem um namespace de rede próprio, ou seja, um conjunto próprio de
interfaces, rotas e regras de firewall. Um navegador do kiwi-fox, uma box do
kiwi-custodia ou um contentor de ferramentas entra neste namespace e passa a
ser membro do gateway. A partir daí, a sua única rota leva ao upstream do
exit. Se o gateway parar, os seus membros ficam sem rota. É a isto que se
chama fail-closed: uma falha corta a ligação e nunca abre outro caminho.

## Instalação { #install }

```bash
kiwi install kiwi-proxy      # o kiwi-fox e o kiwi-custodia trazem-no consigo
kiwi-proxy setup             # a imagem do gateway, os dados de DNS, as imagens dos módulos de fornecedor
```

O kiwi-proxy precisa do Podman rootless e do Python 3.12+ com pydantic. A
aplicação gráfica precisa também do GTK4 e da libadwaita. As palavras-passe
são guardadas no porta-chaves do ambiente de trabalho através do
`secret-tool`. Numa máquina sem porta-chaves, ficam em ficheiros com modo
0600, que só o teu utilizador consegue ler.

## Utilização { #use }

```bash
kiwi-proxy add client-a socks5://user:pass@host:1080   # um exit; ainda nada corre
kiwi-proxy add tor-de --module tor --country de        # um exit criado por um módulo de fornecedor
kiwi-proxy list
kiwi-proxy check client-a      # o que o mundo vê através dele
kiwi-proxy up client-a         # ativar o gateway e mantê-lo ativo
kiwi-proxy down client-a       # pará-lo, juntamente com tudo o que o usa
kiwi-proxy ps                  # os gateways em execução, seja qual for a aplicação que os arrancou
kiwi-proxy reap                # parar os gateways que ninguém usa
kiwi-proxy-gui                 # "Kiwi Proxy" na grelha de aplicações
```

Um endpoint é o endereço de um upstream. Podes escrevê-lo como
`socks5://user:pass@host:port`, `http://…` ou `https://…`, ou no formato dos
fornecedores, `host:port:user:pass`. `kiwi-proxy test ENDPOINT` testa um
endpoint sem criar um exit.

### Exits para aplicações do anfitrião { #exits-for-host-applications }

Um programa do anfitrião não precisa de correr num contentor para usar um
exit. O kiwi-proxy pode publicar um exit como porta SOCKS5 no anfitrião, uma
porta por exit:

```bash
kiwi-proxy add se socks5://10.64.0.1:1080 --expose 1081
kiwi-proxy add nl socks5://10.65.0.1:1080 --expose 1082
kiwi-proxy up se && kiwi-proxy up nl
curl --proxy socks5h://127.0.0.1:1082 https://ifconfig.co/json
```

Por predefinição, a porta só escuta em `127.0.0.1`. Se a puseres a escutar
noutro endereço, tens de definir um nome de utilizador com `--expose-user` ou
permitir expressamente o acesso livre com `--expose-open`. Para teres um exit
ativo logo a partir do momento em que inicias sessão, executa
`systemctl --user enable --now kiwi-proxy@NAME`.

### DNS { #dns }

- O **modo resolvedor** é a predefinição. O dnscrypt-proxy resolve os nomes
  com DNS over HTTPS (DoH) e envia essas consultas pelo exit. O resolvedor DoH
  pode ser o da Google, da Cloudflare, da Quad9 ou da Mullvad. São aplicadas
  listas de bloqueio (OISD), atualizadas todos os dias.
- O **modo remoto** (`--dns remote`) passa os nomes ao upstream, que os
  resolve ele próprio. Este modo destina-se ao Tor e aos nomes `.onion`. As
  listas de bloqueio também se aplicam neste modo.

### Regras do gateway { #rules-of-the-gateway }

- O UDP não é reencaminhado. Isto significa que não há QUIC, nem áudio e
  vídeo do WebRTC, nem DNS em texto simples.
- Um exit só chega ao exterior por IPv4. Um nome sem endereço IPv4 é recusado.
- Um gateway arrancado por outra aplicação, como o kiwi-fox ou o
  kiwi-custodia, é removido quando sai o seu último membro. Um gateway que
  arrancaste com `kiwi-proxy up` continua a correr até executares
  `kiwi-proxy down`.
- Cada exit tem exatamente um gateway, e esse gateway pode ter qualquer número
  de membros. Membros que têm de ficar separados uns dos outros usam exits
  diferentes.

## A aplicação { #the-app }

Na aplicação **Kiwi Proxy** podes acrescentar e editar exits, a partir de um
proxy SOCKS5 que te deram ou de um módulo de fornecedor. Para um exit de um
módulo, escolhes numa lista de países com pesquisa ou numa lista de nós.
Podes ativar e parar exits, disponibilizar um exit como porta SOCKS5 neste
computador e copiar o respetivo endereço, e verificar o que o exterior vê
quando te ligas através dele. A aplicação mostra também que membros estão
ligados a um gateway e os registos de cada um, e permite instalar e
configurar os módulos de fornecedor.

## Numa máquina do kiwi-server { #on-a-kiwi-server-machine }

O repositório do kiwi-proxy contém também um módulo para o kiwi-server. Com
ele, uma máquina do kiwi-server disponibiliza exits a toda a mesh, ou seja, à
rede WireGuard privada que liga as tuas máquinas do kiwi-server. O módulo
corre um gateway por exit e publica-o no endereço da máquina na mesh. A
documentação do módulo diz que ele ainda não está na árvore de código do
kiwi-server e que ainda não foi executado numa máquina. Os módulos de
fornecedor só funcionam no ambiente de trabalho e não correm numa máquina do
kiwi-server.

Para saber mais: [arquitetura](https://github.com/derlocke-ng/kiwi-proxy/blob/main/docs/architecture.md),
[consumidores](https://github.com/derlocke-ng/kiwi-proxy/blob/main/docs/consumers.md),
[sistema de plugins](https://github.com/derlocke-ng/kiwi-proxy/blob/main/docs/plugin-system.md).
