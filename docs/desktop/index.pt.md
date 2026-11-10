# O ambiente de trabalho

A parte de ambiente de trabalho da Kiwi Network é o computador onde
trabalhas: um posto de trabalho Linux que se configura sozinho e que recebe as
aplicações de catálogos git. Um catálogo é um repositório git com uma lista
de aplicações. Não tens de configurar a máquina à mão, e podes preparar a
próxima da mesma maneira.

As ferramentas Kiwi para o ambiente de trabalho foram feitas para as
**variantes gráficas do Fedora Atomic**: o Fedora Silverblue e o
[Bluefin](https://projectbluefin.io/), em particular o Bluefin-DX. Estes
sistemas são instalados e atualizados como uma imagem completa. O diretório
`/usr` é imutável, ou seja, não pode ser alterado, e uma atualização pode ser
revertida com facilidade. Não existe nenhuma imagem Kiwi especial. Instalas
uma imagem normal do Silverblue ou do Bluefin e acrescentas-lhe três coisas.

1. O **[kiwi-updater](kiwi-updater.md)** instala aplicações a partir de
   catálogos git e mantém-nas atualizadas. Instala tudo na tua pasta pessoal.
   Só uma aplicação que precise de root recebe também uma parte que pertence
   ao root. O kiwi-updater também se atualiza a si próprio.
2. O **[ensconce](ensconce.md)** configura um Bluefin-DX acabado de instalar.
   Descreves a configuração em ficheiros de lista simples, e o ensconce
   aplica-a: pacotes, Flatpaks, extensões do GNOME, sincronização do
   Nextcloud, SSH, definições de sysctl e de energia, o ecrã de início de
   sessão e as tuas aplicações Kiwi. Com `--export`, escreve nesses ficheiros
   a configuração de uma máquina já existente, para que possas cloná-la.
3. **As aplicações**, que instalas a partir do [catálogo Kiwi](catalogs.md):

| Aplicação | O que faz |
|---|---|
| [kiwi-killswitch](kiwi-killswitch.md) | Um kill switch de VPN para o GNOME. É fail-closed: enquanto a VPN não estiver ativa, todo o tráfego fica bloqueado |
| [Redes de clientes](../clients/index.md): kiwi-proxy, kiwi-custodia, kiwi-fox | Um exit para cada endpoint VPN ou SOCKS. Um exit é um contentor isolado que só consegue chegar a esse endpoint. Boxes com distribuições Linux e navegadores podem ser ligados a um exit, para que todo o seu tráfego passe por ele |
| [kiwi-server](../server/index.md) | A ferramenta com que constróis e geres a tua própria rede |
| [gnome-monitor](gnome-monitor.md) | Guarda disposições dos ecrãs e alterna entre elas. Também desliga e volta a ligar monitores, um a um |
| [syncman](syncman.md) | Sincroniza pastas nos dois sentidos, por exemplo jogos guardados. A sincronização corre como serviços de utilizador do systemd |
| [kiwi-cli-tools-desktop](cli-tools.md) | `pweb`, `select-server`, `tethering`, `torlink` |

Esta secção descreve também o [kiwi-gen](kiwi-gen.md), um gestor de chaves e
certificados que corre no navegador e funciona sem ligação.

## A partir de uma instalação nova { #from-a-fresh-install }

Estes comandos levam-te de um sistema acabado de instalar a um ambiente de
trabalho com as aplicações Kiwi:

```bash
# 1. kiwi-updater: âmbito de utilizador e de sistema, um único pedido de palavra-passe; o catálogo Kiwi vem incluído
curl -fsSL https://raw.githubusercontent.com/derlocke-ng/kiwi-updater/main/get-kiwi.sh | bash
kiwi list

# 2. configurar a máquina
kiwi install ensconce
ensconce --init && $EDITOR "$(ensconce --config-dir)"/settings.sh
ensconce

# 3. as aplicações que quiseres (ou indica-as no kiwi-apps.list do ensconce)
kiwi install kiwi-killswitch
kiwi install kiwi-custodia && kiwi-custodia setup
```

Também podes instalar aplicações sem abrir o terminal. A aplicação **Kiwi
Apps** (`kiwi-gui`), que encontras na grelha de aplicações, instala uma
aplicação com um clique.

## Ligar à tua rede { #joining-your-network }

Um computador de trabalho é adicionado à mesh como qualquer outro dispositivo.
A mesh é a rede WireGuard privada que liga os teus servidores e dispositivos.
O comando `kiwi-server enroll fleet.yaml laptop --group devices` escreve um
ficheiro de configuração WireGuard, que depois importas nas Definições do
GNOME. Importa também a autoridade de certificação (CA) da tua rede,
`kiwiCA.pem`, para que o computador confie nos certificados HTTPS dos nomes
da tua rede. O ensconce instala para todo o sistema todos os ficheiros `.pem`
que estiverem no seu diretório `certs/`.

A partir daí, o [kiwi-killswitch](kiwi-killswitch.md) protege essa ligação e
mantém a máquina fail-closed. Isto significa que o tráfego que não passa pela
ligação é bloqueado, mesmo quando a ligação está em baixo. Em casa, pode já
haver na tua rede local um node gateway que envia o teu tráfego por um túnel.
Com a definição *trusted kiwi-nodes*, o kill switch aceita esse node gateway
em vez do túnel.
