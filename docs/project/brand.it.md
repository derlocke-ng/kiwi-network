# Icone e colori

Questa pagina descrive le icone e i colori delle app Kiwi e spiega dove
trovarli, per esempio quando scrivi un’app per il catalogo. Tutte le app Kiwi
hanno lo stesso tipo di icona, una **sezione di kiwi**, cioè un kiwi tagliato a
metà. Al centro del frutto c’è un simbolo che rappresenta l’app, e ogni app ha
un colore tutto suo. Le icone si trovano nel repository
[derlocke-ng/kiwi-icons](https://github.com/derlocke-ng/kiwi-icons). La sua
[pagina di anteprima](https://derlocke-ng.github.io/kiwi-icons/) ti permette di
cambiare stile e tema, mostra le palette e offre URL che puoi copiare.

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

## Tre stili { #three-styles }

Ogni icona esiste in tre stili:

| Stile | Aspetto |
|---|---|
| **classic** (predefinito) | l’icona GTK rifinita, con bordo, polpa, semi e cuore |
| **flat** | senza bordo e con il cuore più grande |
| **night** | un disegno al tratto in negativo su un disco scuro |

## Struttura { #layout }

Il repository kiwi-icons contiene questi file:

| Percorso | Che cosa |
|---|---|
| `svg/<style>/<icon>.svg` | i file originali (viewBox 128×128) |
| `png/<style>/<size>/<icon>.png` | versioni PNG a 16, 32, 48, 64, 128, 256 e 512 px |
| `icons.json` | un indice leggibile dai programmi, con id, nomi, descrizioni, colori e modelli di URL |
| `palette/kiwi-palette.css`, `.json` | sei colori per ogni app: `rim`, `flesh`, `core`, `ink`, `deep`, `text` |

## In un’app { #in-an-app }

La maggior parte delle app Kiwi contiene una copia identica, byte per byte, di
un SVG classic e indica quel file con `ICON=` nel proprio `kiwi.manifest`.
gnome-monitor usa l’icona `kiwi-os` e syncman l’icona `kiwi-cloud`.
kiwi-custodia ha un’icona tutta sua. kiwi-updater, dalla versione 2.2, prende
l’icona dal proprio clone dell’app, quindi durante l’installazione non viene
scaricato nulla. Un’app che ha un launcher `.desktop` installa l’icona anche nel
tema di icone hicolor.

kiwi-icons non ha ancora una dichiarazione di licenza.
