# Contribuire

Tutto il progetto Kiwi Network è open source. Questa pagina ti dice dove va
ogni tipo di contributo. Apri issue e pull request nel repository a cui si
riferiscono. I repository sono elencati in
[Repository e stato](status.md).

- **Un’app per il catalogo.** Il catalogo è l’elenco delle app che
  kiwi-updater sa installare. Aggiungi alla tua app un `kiwi.manifest` e un
  `install.sh`, pubblica una release con un tag firmato e apri una pull
  request su [kiwi-catalog](https://github.com/derlocke-ng/kiwi-catalog). Vedi
  [Pubblicare un’app](../desktop/catalogs.md#publishing-an-app).
- **Un modulo.** I moduli si sviluppano in
  [kiwi-modules](https://github.com/derlocke-ng/kiwi-modules). Un modulo è una
  cartella con un `module.yaml` e dei template Jinja. Vedi
  [Scrivere un modulo](../server/modules.md#writing-a-module).
- **Un hub o un’app per un hub.** Fai un fork di
  [Armory](https://github.com/derlocke-ng/armory), crea lo scheletro di un’app
  con `npm run new-app` e aggiungi il tuo hub a
  [kiwi-web-catalog](https://github.com/derlocke-ng/kiwi-web-catalog). Vedi
  [Gestire il tuo hub](../people/hubs.md).
- **Un provider per kiwi-proxy.** Un provider è un plugin che fornisce a
  kiwi-proxy un tipo di connessione, come Tor o una VPN. Ogni provider offre
  SOCKS5 e nient’altro. Le regole che un provider deve rispettare sono in
  [docs/plugin-system.md](https://github.com/derlocke-ng/kiwi-proxy/blob/main/docs/plugin-system.md)
  di kiwi-proxy.
- **Questo sito e questa documentazione** si trovano nel repository
  [kiwi-network](https://github.com/derlocke-ng/kiwi-network).

## Questo repository { #this-repository }

Il repository kiwi-network contiene la homepage e questa documentazione:

```
site/          the homepage: plain HTML, CSS and JS, served at kiwi-network.eu
docs/          this documentation (MkDocs Material), served at kiwi-network.eu/docs/
docs/assets/   the logo and app icons (copied from kiwi-icons) and the docs' stylesheet
mkdocs.yml     docs configuration
```

Per vedere un’anteprima della documentazione e della homepage sul tuo
computer, esegui:

```bash
python -m pip install mkdocs-material mkdocs-static-i18n
mkdocs serve             # anteprima dal vivo su http://127.0.0.1:8000
mkdocs build --strict    # ciò che compila la CI: fallisce con link e ancore non validi
python -m http.server -d site 8080   # la homepage
```

Quando fai push su `main`, la homepage e la documentazione vengono pubblicate
tramite GitHub Pages.

Mantieni la documentazione **fedele ai repository**. Descrivi ciò che uno
strumento fa oggi, indica come previsto tutto ciò che è previsto, e per i
dettagli rimanda al codice sorgente invece di copiarli.
