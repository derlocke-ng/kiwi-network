# O ambiente de trabalho

As ferramentas de ambiente de trabalho Kiwi são feitas para os **ambientes de
trabalho Fedora Atomic**: Fedora Silverblue e [Bluefin](https://projectbluefin.io/)
(em particular o Bluefin-DX). São sistemas baseados em imagens, com um `/usr`
imutável e reversão fácil. Não há nenhuma imagem Kiwi especial: instalas uma de
origem e acrescentas três camadas por cima.

1. O **[kiwi-updater](kiwi-updater.md)** instala e atualiza apps a partir de
   catálogos git: tudo na tua pasta pessoal, mais uma parte pertencente a root
   apenas para as apps que precisam dela. Também se atualiza a si próprio.
2. O **[ensconce](ensconce.md)** configura um Bluefin-DX acabado de instalar a
   partir de ficheiros de lista simples: pacotes, Flatpaks, extensões GNOME,
   sincronização Nextcloud, SSH, definições de sysctl e de energia, o ecrã de
   início de sessão e as tuas apps Kiwi. `--export` clona uma máquina.
3. **As apps**, do [catálogo Kiwi](catalogs.md):

| App | O que faz |
|---|---|
| [kiwi-killswitch](kiwi-killswitch.md) | Um kill switch de VPN fail-closed para o GNOME |
| [Redes de clientes](../clients/index.md): kiwi-proxy, kiwi-custodia, kiwi-fox | Uma saída selada por endpoint VPN ou SOCKS, e distro boxes e navegadores que vivem dentro delas |
| [kiwi-server](../server/index.md) | Construir e gerir a tua própria rede |
| [gnome-monitor](gnome-monitor.md) | Guardar e alternar disposições de ecrãs; desligar e ligar monitores individuais |
| [syncman](syncman.md) | Sincronização de pastas nos dois sentidos (gravações de jogos e mais) como serviços de utilizador |
| [kiwi-cli-tools-desktop](cli-tools.md) | `pweb`, `select-server`, `tethering`, `torlink` |

Também aqui: o [kiwi-gen](kiwi-gen.md), um gestor de chaves e certificados que
corre offline no navegador.

## A partir de uma instalação nova { #from-a-fresh-install }

```bash
# 1. kiwi-updater: âmbito de utilizador e de sistema, um só pedido de palavra-passe; o catálogo Kiwi vem com ele
curl -fsSL https://raw.githubusercontent.com/derlocke-ng/kiwi-updater/main/get-kiwi.sh | bash
kiwi list

# 2. configurar a máquina
kiwi install ensconce
ensconce --init && $EDITOR "$(ensconce --config-dir)"/settings.sh
ensconce

# 3. as apps que quiseres (ou lista-as no kiwi-apps.list do ensconce)
kiwi install kiwi-killswitch
kiwi install kiwi-custodia && kiwi-custodia setup
```

O **Kiwi Apps** (`kiwi-gui`) na grelha de aplicações faz o mesmo com um clique.

## Juntar-te à tua rede { #joining-your-network }

Um ambiente de trabalho junta-se à malha como qualquer outro dispositivo:
`kiwi-server enroll fleet.yaml
laptop --group devices` escreve uma configuração WireGuard, que importas nas
Definições do GNOME. Importa a CA da fleet (`kiwiCA.pem`) para que os seus nomes
HTTPS sejam de confiança. O ensconce instala todos os `.pem` do seu diretório
`certs/` em todo o sistema.

O [kiwi-killswitch](kiwi-killswitch.md) mantém depois a máquina fail-closed em
torno dessa ligação. A sua definição *trusted kiwi-nodes* permite que um node
gateway na tua LAN substitua o túnel em casa.
