# Icone e colori

Ogni app Kiwi ha lo stesso segno: una **sezione di kiwi** il cui centro porta
il glifo dell'app, in un colore tutto suo. Le icone si trovano in
[derlocke-ng/kiwi-icons](https://github.com/derlocke-ng/kiwi-icons), con una
[pagina di anteprima](https://derlocke-ng.github.io/kiwi-icons/) che ha un selettore di stile e
di tema, le palette e URL copiabili.

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

| Stile | Aspetto |
|---|---|
| **classic** (default) | l'icona GTK rifinita: buccia, polpa, semi e centro |
| **flat** | niente buccia, un centro più grande |
| **night** | un segno a linee invertito su un disco scuro |

## Struttura { #layout }

| Percorso | Cosa |
|---|---|
| `svg/<style>/<icon>.svg` | gli originali (viewBox 128×128) |
| `png/<style>/<size>/<icon>.png` | render a 16, 32, 48, 64, 128, 256 e 512 px |
| `icons.json` | un indice leggibile dalle macchine: id, nomi, descrizioni, colori, template di URL |
| `palette/kiwi-palette.css`, `.json` | sei colori per app: `rim`, `flesh`, `core`, `ink`, `deep`, `text` |

## In un'app { #in-an-app }

La maggior parte delle app Kiwi include una copia identica byte per byte di un SVG classic e lo indica con
`ICON=` nel proprio `kiwi.manifest`. gnome-monitor e syncman usano le icone `kiwi-os`
e `kiwi-cloud`, e kiwi-custodia ha la sua. kiwi-updater dalla 2.2 in poi la prende dal
clone dell'app stessa, quindi al momento dell'installazione non si scarica nulla. Un'app con un
launcher `.desktop` la installa anche nel tema di icone hicolor.

kiwi-icons non ha ancora una dichiarazione di licenza.
