# Ícones e cores

Todas as apps Kiwi têm a mesma marca: um **corte transversal de um kiwi** cujo
centro leva o glifo da app, numa cor própria. Os ícones vivem em
[derlocke-ng/kiwi-icons](https://github.com/derlocke-ng/kiwi-icons), com uma
[página de pré-visualização](https://derlocke-ng.github.io/kiwi-icons/) que tem um
seletor de estilo e de tema, as paletas e URLs que se podem copiar.

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

| Estilo | Aspeto |
|---|---|
| **classic** (por omissão) | o ícone GTK refinado: casca, polpa, sementes e centro |
| **flat** | sem casca, com um centro maior |
| **night** | uma marca de linhas invertida sobre um disco escuro |

## Estrutura { #layout }

| Caminho | O quê |
|---|---|
| `svg/<style>/<icon>.svg` | os originais (viewBox de 128×128) |
| `png/<style>/<size>/<icon>.png` | renderizações a 16, 32, 48, 64, 128, 256 e 512 px |
| `icons.json` | um índice legível por máquina: ids, nomes, descrições, cores, modelos de URL |
| `palette/kiwi-palette.css`, `.json` | seis cores por app: `rim`, `flesh`, `core`, `ink`, `deep`, `text` |

## Numa app { #in-an-app }

A maioria das apps Kiwi traz uma cópia idêntica byte a byte de um SVG classic e
indica-o com `ICON=` no seu `kiwi.manifest`. O gnome-monitor e o syncman usam os
ícones `kiwi-os` e `kiwi-cloud`, e o kiwi-custodia traz o seu próprio. O
kiwi-updater 2.2 e posteriores vão buscá-lo ao clone da própria app, por isso nada
é descarregado no momento da instalação. Uma app com um lançador `.desktop`
instala-o também no tema de ícones hicolor.

O kiwi-icons ainda não tem uma declaração de licença.
