# Contribuire

Tutto è open source. Issue e pull request vanno nel repository che
riguardano; vedi [Repository e stato](status.md).

- **Un'app per il catalogo.** Aggiungi un `kiwi.manifest` e un `install.sh`, rilascia
  con un tag firmato e apri una pull request verso
  [kiwi-catalog](https://github.com/derlocke-ng/kiwi-catalog). Vedi
  [Pubblicare un'app](../desktop/catalogs.md#publishing-an-app).
- **Un modulo.** I moduli vengono sviluppati in
  [kiwi-modules](https://github.com/derlocke-ng/kiwi-modules): una directory con un
  `module.yaml` e template Jinja. Vedi [Scrivere un modulo](../server/modules.md#writing-a-module).
- **Un hub o un'app per un hub.** Fai un fork di [Armory](https://github.com/derlocke-ng/armory),
  crea lo scheletro di un'app con `npm run new-app` e aggiungi il tuo hub a
  [kiwi-web-catalog](https://github.com/derlocke-ng/kiwi-web-catalog). Vedi
  [Gestire un proprio hub](../people/hubs.md).
- **Un provider per kiwi-proxy.** Ogni provider espone SOCKS5 e nient'altro. Il
  contratto è nel file
  [docs/plugin-system.md](https://github.com/derlocke-ng/kiwi-proxy/blob/main/docs/plugin-system.md) di kiwi-proxy.
- **Questo sito e questa documentazione** si trovano in
  [kiwi-network](https://github.com/derlocke-ng/kiwi-network).

## Questo repository { #this-repository }

```
site/          the homepage: plain HTML, CSS and JS, served at kiwi-network.eu
site/icons/    the app icons it uses: mostly from kiwi-icons, some from the apps' own repos
docs/          this documentation (MkDocs Material), served at kiwi-network.eu/docs/
mkdocs.yml     docs configuration
```

```bash
python -m pip install mkdocs-material mkdocs-static-i18n
mkdocs serve             # anteprima dal vivo su http://127.0.0.1:8000
mkdocs build --strict    # cosa costruisce la CI: fallisce con link e ancore rotti
python -m http.server -d site 8080   # la homepage
```

Un push su `main` pubblica entrambi tramite GitHub Pages.

Per favore mantieni la documentazione **fedele ai repository**. Descrivi cosa fa uno strumento
oggi, segna come pianificato tutto ciò che è pianificato, e rimanda al sorgente per i dettagli
invece di copiarli.
