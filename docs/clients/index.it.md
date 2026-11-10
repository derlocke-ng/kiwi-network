# Lavorare con molte reti di clienti

Dieci clienti remoti spesso significano dieci VPN o endpoint SOCKS, uno per raggiungere la rete
di ciascun cliente. Eseguirli tutti sull'host è un caos: dieci tunnel insieme,
route che si scontrano e una rete che trapela nella successiva. Le app desktop di Kiwi
danno invece a ciascuno un'**uscita sigillata**: un container la cui unica route è quell'unico
upstream. I tuoi strumenti si agganciano all'uscita di cui hanno bisogno, e nient'altro sull'host
cambia.

| App | Cosa fa |
|---|---|
| [**kiwi-proxy**](kiwi-proxy.md) | Il motore. Un'**uscita** (exit) è un upstream con un nome: un SOCKS5 che ti è stato fornito, o uno creato da un modulo provider. Avviarla crea un **gateway**, un namespace di rete la cui unica route è quell'upstream. Le app dell'host possono usarlo come porta SOCKS5 locale |
| [**kiwi-custodia**](kiwi-custodia.md) | **Box di distribuzioni su un'uscita**: Fedora, Ubuntu, Debian, Kali, Arch, openSUSE, Rocky o Alpine in un container rootless con una home propria. *Tutto* ciò che è nella box esce dall'uscita: gestori di pacchetti, giochi, binari statici che non hanno mai sentito parlare di proxy |
| [**kiwi-fox**](kiwi-fox.md) | **Profili del browser su un'uscita**: Camoufox, Firefox o Tor Browser, ogni profilo con il proprio storage |
| [**Moduli dei provider**](providers.md) | Uscite da Tor, una VPN (gluetun), 9proxy o Mysterium. Tor e Mysterium sono il modo rapido per avere più IP d'uscita, comodo per i test |

```
 client A: socks5://…  ─┐                                   ┌─ box "client-a" (Fedora: ssh, ansible, dnf …)
 client B: socks5://…  ─┼─ kiwi-proxy exits ─▶ gateways ───┼─ browser profile "client-b"
 Tor / Mysterium / VPN ─┘   one per upstream   only route   └─ curl, mail, any app: socks5h://127.0.0.1:1082
                                               is the exit
```

## Come resta pulito { #how-it-stays-clean }

- **Fail closed.** Il firewall di un gateway scarta tutto tranne il suo unico
  upstream. Se il gateway muore, tutto ciò che vi era agganciato perde la sua route. Il kill
  switch è l'assenza di una route, non un software che deve accorgersene.
- **Non gira niente che non venga usato.** Un gateway avviato da una box o da un browser
  sparisce quando l'ultimo se ne va. Restano attive solo le uscite che avvii con
  `kiwi-proxy up`.
- **Ciò che è separato resta separato.** Le cose sulla stessa uscita la condividono (un IP, un
  namespace). I clienti che non devono incontrarsi ricevono uscite diverse, e ogni box ha
  la propria home, così chiavi SSH e profili del browser non si incrociano.
- **Niente root, niente route sull'host.** Tutto gira in Podman rootless, e la
  rete dell'host resta intatta.
- **Anche il DNS passa dall'uscita.** Di default i nomi si risolvono via DoH attraverso
  l'uscita, con liste di blocco della pubblicità. Per gli **hostname interni** di un cliente, passa invece
  i nomi al lato del cliente con `--dns remote` (che è anche la modalità per
  Tor e i nomi `.onion`).

## Limiti { #limits }

Questi vengono dai repository:

- **Solo TCP, solo IPv4.** L'UDP non esce da nessuna parte (niente QUIC, niente media WebRTC), e
  l'IPv6 non ha alcuna route.
- **Una configurazione VPN per macchina.** Il modulo provider VPN contiene una sola
  configurazione gluetun (un `vpn.json`, una configurazione WireGuard personalizzata), e le sue
  uscite differiscono solo per il paese del server. Per avere fianco a fianco le VPN di più clienti,
  oggi la strada è un endpoint SOCKS5 per cliente.
- **Una box è custodia della rete, non una sandbox.** Condivide il tuo display, il session
  bus e gli appunti, come distrobox. Quello che non può fare è raggiungere la rete
  se non attraverso la sua uscita.
- **Mysterium:** un'identità mantiene una sola connessione alla volta.

## Per iniziare { #get-started }

```bash
kiwi install kiwi-custodia            # porta con sé kiwi-proxy
kiwi-custodia setup                   # immagini e dati DNS

kiwi-proxy add client-a socks5://user:pass@jump.client-a.example:1080 --dns remote
kiwi-custodia new client-a --exit client-a --distro fedora
kiwi-custodia enter client-a          # a shell whose only way out is client A's SOCKS5
```
