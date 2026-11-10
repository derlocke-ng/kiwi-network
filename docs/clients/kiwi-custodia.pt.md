# kiwi-custodia

Contentores de distribuições cujo tráfego sai, até ao último byte, por uma saída
do [kiwi-proxy](kiwi-proxy.md). *Pensa no distrobox, com a rede sob custódia.*

- Repositório: [derlocke-ng/kiwi-custodia](https://github.com/derlocke-ng/kiwi-custodia), GPL-3.0-or-later
- Versão mais recente: **v0.2.3**. Está no [catálogo Kiwi](../desktop/catalogs.md), âmbito de utilizador.
- Uma CLI (`kiwi-custodia`) e uma app GTK4 (**Kiwi Custodia**)

Uma **box** é uma distribuição Linux num contentor Podman sem root, com uma pasta
pessoal própria, ligada ao gateway selado de uma saída. Instala o que quiseres
nela com o seu gestor de pacotes, corre as suas apps de ambiente de trabalho no
teu ambiente de trabalho e põe-nas na grelha de aplicações. A box não tem outra
rota senão a saída: nem para o `dnf`, nem para um cliente de jogos, nem para um
binário estático que nunca ouviu falar de `$ALL_PROXY`. Se a saída desaparecer, a
box fica sem rota nenhuma.

Isso faz de uma box por rede de cliente uma forma limpa de trabalhar: as
ferramentas, as chaves e o histórico da shell do cliente A numa box, os do
cliente B noutra, cada uma a chegar só ao seu próprio cliente.

## Instalar { #install }

```bash
kiwi install kiwi-custodia   # traz consigo o kiwi-proxy; ou ./install.sh install
kiwi-custodia setup          # a imagem do túnel, mais a imagem do gateway e os dados DNS do kiwi-proxy
```

Precisa de Podman sem root com `catatonit`, do kiwi-proxy, de uma sessão Wayland,
de Python 3.12+ com pydantic, de GTK4 + libadwaita para a app, e de
`/dev/net/tun` utilizável por contentores sem root. As imagens das distribuições
são descarregadas quando uma box arranca pela primeira vez. Corre
`kiwi-custodia setup` de novo depois de uma atualização.

## Usar { #use }

```bash
kiwi-proxy add client-a socks5://user:pass@host:1080       # uma saída, definida uma vez, no kiwi-proxy
kiwi-custodia new work --exit client-a --distro fedora     # uma box nela; o primeiro arranque instala uma base
kiwi-custodia enter work                                   # uma shell nela: sudo dnf install …
kiwi-custodia run work -- firefox                          # um comando nela
kiwi-custodia check work                                   # o que o mundo vê a partir de dentro
kiwi-custodia apps work                                    # as apps de ambiente de trabalho que tem
kiwi-custodia export work firefox                          # "Firefox (work)" na grelha de aplicações
kiwi-custodia stop work
kiwi-custodia reset work                                   # volta à imagem base; a pasta pessoal fica
kiwi-custodia-gui
```

Distribuições: `fedora` (o valor por omissão), `fedora-toolbox`, `ubuntu`,
`ubuntu-toolbox`, `debian`, `debian-toolbox`, `kali`, `arch`, `arch-toolbox`,
`opensuse`, `rocky`, `alpine`, ou `custom` com `--image`.

## Como é construída uma box { #how-a-box-is-built }

Três contentores partilham um namespace de rede: o **gateway** do kiwi-proxy, um
**sidecar de túnel** (tun2socks num dispositivo TUN que se torna a rota
predefinida) e a própria **box**. Todo o tráfego sai pelo TUN para o SOCKS5 da
saída, por isso os programas que ignoram as definições de proxy também ficam
abrangidos.

- A box corre como o teu utilizador, com o mesmo uid e `sudo` sem palavra-passe. A
  sua pasta pessoal é `~/.local/share/kiwi-custodia/boxes/<id>/home`, uma por box
  em vez da tua pasta pessoal real: duas boxes são duas identidades.
- As alterações dentro de uma box são guardadas num snapshot por box quando ela
  para, e `reset` volta à imagem base.
- O Wayland, o X11 (através do Xwayland), o PipeWire, o bus de sessão e
  `/dev/dri` são passados para dentro, por isso as apps de ambiente de trabalho e
  os jogos funcionam.
- O DNS passa pelo resolvedor do gateway (com bloqueio de anúncios), ou pelo
  upstream numa saída com DNS remoto.

## O que não é { #what-it-is-not }

Uma box é **custódia de rede, não uma sandbox em relação ao teu ambiente de
trabalho**. Tal como o distrobox, recebe o teu ecrã e o bus de sessão, por isso
um programa na box pode mostrar janelas, ler a área de transferência e usar os
portais. O que não consegue fazer é chegar à rede a não ser através da sua
saída. O UDP não tem por onde sair (sem QUIC, sem multimédia WebRTC), e o IPv6
não tem rota.

As boxes que não devem partilhar uma saída usam saídas diferentes.
