# DNS, nomes e certificados

## Uma cadeia de resolução { #one-resolver-chain }

O DNS é uma só cadeia para toda a rede:

```
LAN device ──▶ gateway node's Pi-hole ──▶ master's Pi-hole ──▶ gluetun DNS-over-TLS (Quad9)
VPN client ───────────────────────────────▶ master's Pi-hole       └─ leaves through the VPN exit
```

- **Os clientes VPN** (portáteis, telemóveis) perguntam ao Pi-hole do master em
  `10.8.0.1`.
- **O Pi-hole de um node** pergunta primeiro ao Pi-hole do master, para que a
  rede partilhe uma só lista de bloqueio e todas as consultas saiam pela saída do
  master. O Quad9 (`9.9.9.9`, `149.112.112.112`, `fallback_dns`) vem a seguir, por
  ordem estrita, e só responde enquanto o master estiver inacessível.
- **O Pi-hole do master** reencaminha para o resolvedor DNS-over-TLS do seu
  cliente VPN (Quad9 por omissão, `dot_providers`).
- **Os nomes sob o domínio da fleet** são reencaminhados para o master e nunca
  saem dele. O master marca o domínio como local.

Cada anfitrião da stack tem também os nomes da fleet em `/etc/hosts` (os seus
próprios nomes a apontar para si mesmo), para que as cópias de segurança e as
renovações de certificados resolvam sem um Pi-hole. No Fedora CoreOS e no uCore,
o próprio anfitrião resolve através do Pi-hole da sua stack.

**Vizinhos na mesma LAN.** O Pi-hole e o ficheiro hosts de um node respondem com
o **endereço de LAN** dos nodes da fleet que têm um endereço estático na sua
própria sub-rede, para que o tráfego entre duas máquinas na mesma sala fique na
sala. O master continua a responder com endereços de malha.

## Nomes: `service.hostname.home` { #names-servicehostnamehome }

Cada anfitrião é `<host>.<domain>` (`papaya.home`), e cada serviço que corre é um
nome por baixo dele: `cloud.papaya.home`, `vault.papaya.home`,
`portainer.papaya.home`, `dl.lychee.home` e, no master, `wg.sorbet.home`,
`pihole.sorbet.home`, `hub.sorbet.home`, `relay.sorbet.home`. Cada nome que um
módulo anuncia entra nos registos DNS da fleet no **endereço de malha** do
anfitrião. Todos os Pi-holes da fleet resolvem todos os nomes de anfitrião e de
serviço (split-horizon, `fleet_records`). Acrescenta os teus com
`extra_records`.

O domínio por omissão é **`.home`**, porque a ICANN não o vai delegar como domínio
de topo público. Um nome da fleet nunca pode ir parar a um registo público, e
ninguém mais o pode registar nem obter para ele um certificado em que os
navegadores confiem. `.kiwi` é um TLD real, e é por isso que a fleet deixou de o
usar. O kiwi-server verifica a tua escolha: `home`, `corp`, `mail`, `internal`,
`arpa` e `test` passam sem aviso, `.local` é recusado (pertence ao mDNS), `.lan`
dá um aviso (os routers respondem a ele por conta própria) e os TLDs públicos dão
um aviso.

Os nomes *fora* do domínio da fleet, para um hub ou relay público, recebem
certificados Let's Encrypt quando o proxy inverso do master é público.

## Proxies SOCKS5 da Mullvad por nome { #mullvad-socks5-proxies-by-name }

Desde o kiwi-server 2.2.0, o Pi-hole do master responde por todos os **proxies
SOCKS5 da Mullvad**, tanto como `de-fra-wg-socks5-001.relays.mullvad.net` como
na forma curta `de-fra-001.mullvad.home`. O gluetun recusa estas respostas em
intervalos privados (proteção contra DNS rebinding), por isso, sem os registos,
os nomes só seriam resolvidos através dos resolvedores de recurso. Um
temporizador do anfitrião (`km-mullvad-socks.timer`, a cada 6 horas) atualiza a
lista a partir de
[derlocke-ng/mullvad-socks5](https://github.com/derlocke-ng/mullvad-socks5).
Só são aceites dela nomes `*.relays.mullvad.net` em endereços `10.x`, por isso a
lista nunca pode redirecionar nenhum outro nome.

Está ativo na predefinição do master, cuja saída é a Mullvad. Desativa-o com
`mullvad_socks: false` no bloco `dns:` do master.

## Uma CA para a fleet { #one-ca-for-the-fleet }

Com `tls.auto: true` (o valor por omissão), o kiwi-server mantém **uma autoridade
de certificação** para a fleet em `secrets/ca/` (`kiwiCA.key`, `kiwiCA.pem`,
RSA-4096, válida 3650 dias), criada da primeira vez que um anfitrião precisa de um
certificado. Cada anfitrião que corre o proxy inverso recebe um certificado para
`<hostname>` e `*.<hostname>` (825 dias, a validade mais longa que os navegadores
ainda aceitam, renovado quando faltam menos de 30 dias), e cada máquina que o
kiwi-server constrói instala a CA no seu repositório de confiança.

Define **restrições de nomes** e a CA só pode assinar nomes sob o domínio da
fleet: `tls: { name_constraints: [home] }`. A fleet de exemplo faz isto; a
predefinição incorporada é não ter restrição. Uma `kiwiCA.key` roubada passa então
a não valer nada para mais nada, o que importa porque todas as máquinas confiam
nela.

```bash
kiwi-server ca fleet.yaml        # mostra a CA da fleet
```

Importa `kiwiCA.pem` nos teus próprios dispositivos (navegadores, telemóveis) para
que `https://cloud.papaya.home` seja de confiança. Para usares os teus próprios
certificados, define `tls_fullchain` e `tls_privkey` no módulo reverse-proxy.

!!! warning "Mantém `secrets/` privado"
    `kiwiCA.key` assina certificados em que todas as tuas máquinas confiam.
    Mantém `secrets/` e `output/` fora do git (`output/` já está no
    `.gitignore` do kiwi-server).
