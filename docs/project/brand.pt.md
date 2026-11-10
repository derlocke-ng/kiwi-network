# Ícones e cores

Esta página descreve os ícones e as cores das aplicações Kiwi e diz onde os
podes ir buscar, por exemplo quando escreveres uma aplicação para o catálogo.
Todas as aplicações Kiwi têm o mesmo tipo de ícone: um **kiwi em corte**, ou
seja, um kiwi cortado ao meio. No centro do fruto aparece um símbolo da
aplicação, e cada aplicação tem a sua própria cor. Os ícones estão no
repositório [derlocke-ng/kiwi-icons](https://github.com/derlocke-ng/kiwi-icons).
Na [página de pré-visualização](https://derlocke-ng.github.io/kiwi-icons/)
podes mudar de estilo e de tema, ver as paletas e copiar os URL.

<div class="kiwi-icons-row" markdown>
![kiwi-updater](../assets/icons/kiwi-updater.svg){ width=56 }
![kiwi-server](../assets/icons/kiwi-server.svg){ width=56 }
![kiwi-killswitch](../assets/icons/kiwi-killswitch.svg){ width=56 }
![kiwi-proxy](../assets/icons/kiwi-proxy.svg){ width=56 }
![kiwi-fox](../assets/icons/kiwi-fox.svg){ width=56 }
![ensconce](../assets/icons/ensconce.svg){ width=56 }
![kiwi-cli-tools-desktop](../assets/icons/kiwi-cli-tools-desktop.svg){ width=56 }
![kiwi-network](../assets/icons/kiwi-network.svg){ width=56 }
</div>

## Três estilos { #three-styles }

Cada ícone existe em três estilos:

| Estilo | Aspeto |
|---|---|
| **classic** (predefinido) | o ícone GTK mais trabalhado, com casca, polpa, sementes e centro |
| **flat** | sem casca e com o centro maior |
| **night** | um desenho a traço, em negativo, sobre um disco escuro |

## Estrutura do repositório { #layout }

O repositório kiwi-icons contém estes ficheiros:

| Caminho | O que é |
|---|---|
| `svg/<style>/<icon>.svg` | os ficheiros originais (viewBox de 128×128) |
| `png/<style>/<size>/<icon>.png` | versões em PNG com 16, 32, 48, 64, 128, 256 e 512 px |
| `icons.json` | um índice para ser lido por programas, com ids, nomes, descrições, cores e modelos de URL |
| `palette/kiwi-palette.css`, `.json` | seis cores por aplicação: `rim`, `flesh`, `core`, `ink`, `deep`, `text` |

## Numa aplicação { #in-an-app }

A maior parte das aplicações Kiwi traz uma cópia exata, byte a byte, de um SVG
do estilo classic e indica esse ficheiro com `ICON=` no seu `kiwi.manifest`. O
gnome-monitor usa o ícone `kiwi-os` e o syncman usa o ícone `kiwi-cloud`. O
kiwi-custodia tem um ícone próprio. A partir da versão 2.2, o kiwi-updater vai
buscar o ícone ao clone da aplicação que já tem, pelo que nada é descarregado durante
a instalação. Uma aplicação que tenha um lançador `.desktop` instala também o
ícone no tema de ícones hicolor.

O kiwi-icons ainda não indica nenhuma licença.
