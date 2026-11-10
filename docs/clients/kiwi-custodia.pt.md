# kiwi-custodia

O kiwi-custodia dá-te um ambiente Linux separado para cada rede de cliente em
que trabalhas. Cada ambiente é um contentor com a distribuição Linux que
escolheres, e todo o tráfego de rede desse contentor passa por um exit do
[kiwi-proxy](kiwi-proxy.md). Um exit é uma ligação a um upstream, guardada com
um nome, por exemplo o proxy SOCKS5 que dá acesso à rede de um cliente. Assim,
podes trabalhar para dez clientes sem ter dez ligações VPN no anfitrião, e as
ferramentas e as chaves de cada cliente ficam no ambiente desse cliente. *Se
conheces o distrobox: a ideia é a mesma, mas o contentor só consegue chegar à
rede através do seu exit.*

- Repositório: [derlocke-ng/kiwi-custodia](https://github.com/derlocke-ng/kiwi-custodia), GPL-3.0-or-later
- Última versão: **v0.2.3**. Está no [catálogo Kiwi](../desktop/catalogs.md), âmbito de utilizador.
- Tem uma ferramenta de linha de comandos (`kiwi-custodia`) e uma aplicação
  GTK4 (**Kiwi Custodia**).

Uma **box** do kiwi-custodia é uma distribuição Linux num contentor Podman
rootless, ou seja, num contentor que corre como o teu próprio utilizador, sem
permissões de root. A box tem uma pasta pessoal própria e está ligada ao
gateway de um exit. O gateway é o contentor que o kiwi-proxy arranca para um
exit, e a única rota para fora dele leva ao upstream do exit. Dentro da box
podes instalar o que quiseres com o gestor de pacotes da distribuição. As
aplicações gráficas da box abrem no teu ambiente de trabalho, e podes
acrescentá-las à grelha de aplicações. A box não tem outra rota além do exit,
e isso vale para todos os programas dentro dela: para o `dnf`, para um cliente
de jogos e para um programa com ligação estática que ignore `$ALL_PROXY`. Se o
exit parar, a box fica sem rota nenhuma.

É por isso que ter uma box para cada rede de cliente é uma boa forma de
trabalhar. As ferramentas, as chaves e o histórico da shell do cliente A ficam
numa box, os do cliente B noutra, e cada box só chega ao seu próprio cliente.

## Instalação { #install }

```bash
kiwi install kiwi-custodia   # traz o kiwi-proxy consigo; ou ./install.sh install
kiwi-custodia setup          # a imagem do túnel, mais a imagem do gateway e os dados de DNS do kiwi-proxy
```

O kiwi-custodia precisa do Podman rootless com `catatonit`, do kiwi-proxy, de
uma sessão Wayland e do Python 3.12+ com pydantic. A aplicação gráfica precisa
do GTK4 e da libadwaita. Os contentores rootless também têm de poder usar o
`/dev/net/tun`. As imagens das distribuições não são descarregadas durante a
preparação inicial. Cada imagem é descarregada quando uma box que a usa
arranca pela primeira vez. Depois de uma atualização, volta a executar
`kiwi-custodia setup`.

## Utilização { #use }

```bash
kiwi-proxy add client-a socks5://user:pass@host:1080       # um exit, definido uma vez, no kiwi-proxy
kiwi-custodia new work --exit client-a --distro fedora     # uma box nesse exit; o primeiro arranque instala uma base
kiwi-custodia enter work                                   # uma shell dentro dela: sudo dnf install …
kiwi-custodia run work -- firefox                          # um comando dentro dela
kiwi-custodia check work                                   # o que o mundo vê a partir de dentro
kiwi-custodia apps work                                    # as aplicações gráficas que tem
kiwi-custodia export work firefox                          # "Firefox (work)" na grelha de aplicações
kiwi-custodia stop work
kiwi-custodia reset work                                   # voltar à imagem base; a pasta pessoal mantém-se
kiwi-custodia-gui
```

As distribuições disponíveis são `fedora` (a predefinição), `fedora-toolbox`,
`ubuntu`, `ubuntu-toolbox`, `debian`, `debian-toolbox`, `kali`, `arch`,
`arch-toolbox`, `opensuse`, `rocky` e `alpine`. Também podes escolher `custom`
e indicar tu próprio uma imagem com `--image`.

## Como uma box é construída { #how-a-box-is-built }

Uma box em funcionamento é composta por três contentores que partilham um
namespace de rede, ou seja, as mesmas interfaces de rede, rotas e regras de
firewall. O primeiro é o **gateway** do kiwi-proxy. O segundo é um **sidecar
de túnel**, um contentor auxiliar que corre o tun2socks num dispositivo TUN.
Um dispositivo TUN é uma interface de rede virtual, e aqui passa a ser a rota
predefinida. O terceiro contentor é a própria **box**. Todo o tráfego da box
entra no dispositivo TUN e segue daí para o proxy SOCKS5 do exit. Isto
funciona através da rota predefinida e não das definições de proxy, por isso
abrange também os programas que ignoram essas definições.

- A box corre como o teu utilizador, com o mesmo uid, e o `sudo` funciona lá
  dentro sem palavra-passe. A pasta pessoal dela é
  `~/.local/share/kiwi-custodia/boxes/<id>/home`. Cada box tem a sua própria
  pasta pessoal e não usa a tua verdadeira, por isso duas boxes são duas
  identidades separadas.
- Quando uma box para, as alterações feitas dentro dela ficam guardadas num
  snapshot que pertence a essa box. O `reset` devolve a box à imagem base.
- O Wayland, o X11 (através do Xwayland), o PipeWire, o bus da sessão e o
  `/dev/dri` ficam disponíveis dentro da box, para que as aplicações gráficas
  e os jogos funcionem.
- As consultas DNS são respondidas pelo resolvedor do gateway, que também
  bloqueia domínios de publicidade. Num exit com DNS remoto, é o upstream que
  resolve os nomes.

## O que não é { #what-it-is-not }

Uma box **restringe a rede. Não é uma sandbox que proteja o teu ambiente de
trabalho dos programas que estão nela.** Tal como um contentor do distrobox, a
box tem acesso ao teu ambiente gráfico e ao bus da tua sessão. Por isso, um
programa na box pode mostrar janelas, ler a área de transferência e usar os
portais do ambiente de trabalho. O que não consegue é chegar à rede de outra
forma que não seja através do seu exit. O UDP não é reencaminhado, por isso o
QUIC e o áudio e vídeo do WebRTC não funcionam, e não há rota para IPv6.

As boxes no mesmo exit partilham-no. Boxes que têm de ficar separadas umas das
outras precisam de exits diferentes.
