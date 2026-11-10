# kiwi-fox

Identità del browser isolate in Podman rootless.

Ogni profilo è un'identità persistente: il suo storage e, di solito, un'uscita di
[kiwi-proxy](kiwi-proxy.md) con il suo gateway sigillato e il suo resolver con blocco della
pubblicità, in uno di tre browser. Per la rete di un cliente, significa un browser
che raggiunge le console web del cliente attraverso l'uscita del cliente, e nient'altro.

- Repository: [derlocke-ng/kiwi-fox](https://github.com/derlocke-ng/kiwi-fox), GPL-3.0-or-later
- Ultima release: **v0.7.1**. È nel [catalogo Kiwi](../desktop/catalogs.md), ambito utente.
- I motori vengono scaricati, mai ridistribuiti: Camoufox (MPL-2.0) durante il setup,
  Firefox e Tor Browser su richiesta (`kiwi-fox engine fetch`), con firma verificata.

| Motore | Cosa vede una pagina |
|---|---|
| **Camoufox** (default) | una macchina Windows 11 coerente e ordinaria con una propria regione: un fingerprint congelato e falsificato |
| **Firefox** | Mozilla Firefox originale, che non falsifica nulla: i valori di questa macchina, attraverso la stessa uscita sigillata |
| **Tor Browser** | Tor Browser, non modificato, attraverso un'uscita sul modulo tor, con un circuito per sito e i nomi `.onion` |

kiwi-fox è per chi gestisce più account di sua proprietà o che è autorizzato
a gestire, e non vuole che quegli account vengano collegati tra loro dal fingerprint del browser
o dall'IP.

## Installazione { #install }

```bash
kiwi install kiwi-fox      # porta con sé kiwi-proxy; oppure ./install.sh install
kiwi-fox setup             # images, a ~630 MB browser engine, DNS data; runs kiwi-proxy's setup too
kiwi-fox engine fetch --engine firefox     # oppure torbrowser: con firma verificata
```

Richiede Podman rootless e kiwi-proxy, una sessione Wayland (X11 funziona con un
confine più debole), Python 3.12+, GTK4 + libadwaita, `secret-tool`, e
`gpg`/`gpgv` per verificare Firefox e Tor Browser. Con il driver NVIDIA
proprietario serve anche `nvidia-container-toolkit` con la sua specifica CDI.

## Uso { #use }

```bash
kiwi-proxy add client-a socks5://user:pass@host:1080   # uscita definita una volta sola, in kiwi-proxy
kiwi-fox new work --exit client-a     # un profilo su di essa: la sonda e genera una nuova identità coerente
kiwi-fox new plain --no-proxy         # this machine's own connection, nothing sealed
kiwi-fox list                         # --tag shop, --by-tag
kiwi-fox run work                     # oppure con la GUI
kiwi-fox stop work
kiwi-fox check                        # ogni profilo è ancora coerente?
kiwi-fox selfcheck work               # misura cosa vedono le pagine, poi lo verifica
kiwi-fox-gui                          # "Kiwi Fox" in the app grid
```

`--desktop-entry` mette un profilo nella griglia delle app, e i tag raggruppano i profili.

## Profili e uscite { #profiles-and-exits }

Un profilo fa riferimento a un'uscita, e le uscite sono condivise: i profili sulla stessa uscita ne condividono
il gateway (un namespace, un IP d'uscita, un insieme di circuiti Tor). Le identità
che non devono condividere un'uscita usano uscite diverse. Con `--no-proxy` non c'è
alcun gateway: il container del browser ha una rete propria sulla connessione di
questa macchina, e nulla è sigillato.

Il container del browser si aggancia al namespace del gateway con tutte le capability
rimosse tranne `SYS_CHROOT` (la sandbox di Firefox ne ha bisogno). Gira con
`no-new-privileges`, e il motore è montato in sola lettura.

## Un profilo Camoufox { #a-camoufox-profile }

È la macchina più comune che esista, perché sono i valori rari che i sistemi di rilevamento
segnalano: uno schermo 1920×1080, i font che ha ogni Windows 11 e nessun altro, e
la scheda grafica di questa macchina così come la descrive Firefox su Windows. Regione,
lingua, fuso orario e voci seguono l'uscita. Tutto si può cambiare
in seguito (`kiwi-fox set`, `kiwi-fox webgl`, `kiwi-fox fonts`), e le modifiche vengono
salvate solo se il risultato resta coerente.

## Cosa non fa { #what-it-does-not-do }

Non promette di essere "non rilevabile". I profili sono isolati per storage, IP e
ogni superficie che il motore può falsificare, ma **non** rispetto agli identificatori
cross-browser a livello hardware: i frame che la GPU disegna davvero e le tempistiche dell'hardware
vengono dalla macchina reale e sono uguali per ogni profilo su di essa. Il file
`docs/detection-notes.md` del repository documenta cosa viene misurato.

Non c'è automazione: niente bot e niente creazione di account in massa. È solo per
la navigazione interattiva.
