# DNS, nomes e certificados

Numa Kiwi Network, cada máquina e cada serviço tem um nome, como
`cloud.papaya.home`, e abre-se por HTTPS com um certificado em que os teus
dispositivos confiam. Esta página explica como os nomes são resolvidos dentro
da rede, como são formados e de onde vêm os certificados. Os servidores DNS são
Pi-holes, que também bloqueiam domínios indesejados com uma lista de bloqueio
comum.

## Uma única cadeia de servidores DNS { #one-resolver-chain }

Todas as consultas DNS da rede percorrem a mesma cadeia de servidores:

```
LAN device ──▶ gateway node's Pi-hole ──▶ master's Pi-hole ──▶ gluetun DNS-over-TLS (Quad9)
VPN client ───────────────────────────────▶ master's Pi-hole       └─ leaves through the VPN exit
```

- **Os clientes VPN** (portáteis, telemóveis) enviam as suas consultas ao
  Pi-hole do master, em `10.8.0.1`.
- **O Pi-hole de um node** pergunta primeiro ao Pi-hole do master. Desta forma,
  toda a rede usa a mesma lista de bloqueio, e todas as consultas chegam à
  Internet pela saída do master, ou seja, pela ligação do master à Internet. O
  Quad9 (`9.9.9.9`, `149.112.112.112`, definido em `fallback_dns`) vem a seguir,
  em ordem estrita, pelo que só responde enquanto o master estiver inacessível.
- **O Pi-hole do master** reencaminha as consultas para o servidor
  DNS-over-TLS do seu cliente VPN. Por predefinição, esse servidor é o Quad9
  (`dot_providers`).
- **Os nomes do domínio da tua rede** são reencaminhados para o master e nunca
  passam daí para a frente. O master marca o domínio como local.

Todas as máquinas que correm uma stack têm também os nomes da rede no seu
ficheiro `/etc/hosts`, com os seus próprios nomes a apontar para si mesmas.
Assim, os backups e as renovações de certificados conseguem resolver nomes
mesmo sem um Pi-hole. No Fedora CoreOS e no uCore, a própria máquina usa o
Pi-hole da sua stack para resolver nomes.

**Vizinhos na mesma LAN.** Se outros nodes da tua rede tiverem um endereço
estático na sub-rede de um node, o Pi-hole e o ficheiro hosts desse node
respondem com o **endereço de LAN** deles. O tráfego entre duas máquinas da
mesma LAN fica, assim, nessa LAN. O master continua a responder com os endereços
da mesh.

## Nomes: `service.hostname.home` { #names-servicehostnamehome }

Cada máquina tem o nome `<host>.<domain>`, por exemplo `papaya.home`. O nome de
cada serviço que nela corre forma-se a partir do nome da máquina:
`cloud.papaya.home`, `vault.papaya.home`, `portainer.papaya.home`,
`dl.lychee.home` e, no master, `wg.sorbet.home`, `pihole.sorbet.home`,
`hub.sorbet.home`, `relay.sorbet.home`. Todos os nomes que um módulo anuncia
entram nos registos DNS da rede com o **endereço da máquina na mesh**, e
qualquer Pi-hole da rede consegue resolver o nome de qualquer máquina e de
qualquer serviço. A definição que trata disto é `fleet_records`, e a técnica
chama-se split-horizon DNS, porque só dentro da tua rede é que há resposta para
estes nomes. Podes acrescentar os teus próprios registos com `extra_records`.

O domínio predefinido é **`.home`**. Foi escolhido porque a ICANN não o vai
delegar como domínio de topo (TLD) público. Um nome da tua rede nunca poderá,
portanto, ir parar a um registo público, e ninguém o conseguirá registar nem
obter para ele um certificado em que os navegadores confiem. Já `.kiwi` é um
TLD verdadeiro, e é por isso que a Kiwi Network deixou de o usar. O kiwi-server
verifica o domínio que escolhes. `home`, `corp`, `mail`, `internal`, `arpa` e
`test` são aceites sem qualquer aviso. `.local` é recusado, porque pertence ao
mDNS. `.lan` dá origem a um aviso, porque os routers respondem eles próprios por
esse domínio, e os TLD públicos também.

Os nomes *fora* do domínio da tua rede, de que precisas para um hub ou um relay
público, recebem certificados Let's Encrypt se o proxy inverso do master for
público.

## Proxies SOCKS5 da Mullvad pelo nome { #mullvad-socks5-proxies-by-name }

Os proxies SOCKS5 da Mullvad têm endereços num intervalo privado, e esta
funcionalidade permite usá-los pelo nome. Desde o kiwi-server 2.2.0, o Pi-hole
do master responde por todos os **proxies SOCKS5 da Mullvad**, tanto pelo nome
completo, como `de-fra-wg-socks5-001.relays.mullvad.net`, como por um nome
curto, como `de-fra-001.mullvad.home`. O gluetun recusa respostas DNS que
apontem para endereços privados: é a sua proteção contra DNS rebinding. Sem
estes registos, os nomes só seriam resolvidos pelos servidores DNS de recurso.
Um temporizador na máquina (`km-mullvad-socks.timer`, de 6 em 6 horas) atualiza
a lista a partir de
[derlocke-ng/mullvad-socks5](https://github.com/derlocke-ng/mullvad-socks5).
Dessa lista só são aceites nomes `*.relays.mullvad.net` com endereços `10.x`,
pelo que ela nunca pode desviar nenhum outro nome.

A funcionalidade vem ligada no preset do master, porque a saída desse preset é
a Mullvad. Para a desligares, define `mullvad_socks: false` no bloco `dns:` do
master.

## Uma única CA para toda a rede { #one-ca-for-the-fleet }

Uma autoridade de certificação (CA) assina os certificados que os teus serviços
usam para o HTTPS. Com `tls.auto: true`, que é a predefinição, o kiwi-server
mantém **uma única autoridade de certificação** para toda a rede, em
`secrets/ca/`. A CA é composta pelos ficheiros `kiwiCA.key` e `kiwiCA.pem`, usa
RSA-4096 e é válida durante 3650 dias. O kiwi-server cria-a da primeira vez que
uma máquina precisa de um certificado. Cada máquina que corre o proxy inverso
recebe um certificado para `<hostname>` e `*.<hostname>`. Este certificado é
válido durante 825 dias, o prazo mais longo que os navegadores ainda aceitam, e
é renovado quando faltam menos de 30 dias para expirar. Todas as máquinas
instaladas pelo kiwi-server acrescentam a CA às autoridades em que confiam.

Se definires **restrições de nomes** (name constraints), a CA só pode assinar
nomes do domínio da tua rede: `tls: { name_constraints: [home] }`. O ficheiro
fleet de exemplo define esta restrição, mas a predefinição do programa é não
haver nenhuma. Com a restrição, uma `kiwiCA.key` roubada não serve para nenhum
outro nome. Isto é importante, porque todas as máquinas confiam na CA.

```bash
kiwi-server ca fleet.yaml        # mostra a CA da rede
```

Importa o `kiwiCA.pem` nos teus próprios dispositivos (navegadores, telemóveis)
para que confiem em `https://cloud.papaya.home`. Se preferires usar certificados
teus, define `tls_fullchain` e `tls_privkey` no módulo reverse-proxy.

!!! warning "Não partilhes a pasta `secrets/`"
    A `kiwiCA.key` assina certificados em que todas as tuas máquinas confiam.
    Mantém `secrets/` e `output/` fora do git (`output/` já está no
    `.gitignore` do kiwi-server).
