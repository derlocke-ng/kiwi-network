# Contribuir

Tudo é de código aberto. Os issues e os pull requests vão para o repositório a
que dizem respeito; ver [Repositórios e estado](status.md).

- **Uma app para o catálogo.** Acrescenta um `kiwi.manifest` e um `install.sh`,
  lança com uma tag assinada e abre um pull request contra o
  [kiwi-catalog](https://github.com/derlocke-ng/kiwi-catalog). Ver
  [Publicar uma app](../desktop/catalogs.md#publishing-an-app).
- **Um módulo.** Os módulos são desenvolvidos no
  [kiwi-modules](https://github.com/derlocke-ng/kiwi-modules): um diretório com um
  `module.yaml` e modelos Jinja. Ver [Escrever um módulo](../server/modules.md#writing-a-module).
- **Um hub ou uma app de hub.** Faz um fork do [Armory](https://github.com/derlocke-ng/armory),
  cria o esqueleto de uma app com `npm run new-app` e acrescenta o teu hub ao
  [kiwi-web-catalog](https://github.com/derlocke-ng/kiwi-web-catalog). Ver
  [O teu próprio hub](../people/hubs.md).
- **Um fornecedor do kiwi-proxy.** Cada fornecedor expõe SOCKS5 e mais nada. O
  contrato está no
  [docs/plugin-system.md](https://github.com/derlocke-ng/kiwi-proxy/blob/main/docs/plugin-system.md)
  do kiwi-proxy.
- **Este site e esta documentação** vivem em
  [kiwi-network](https://github.com/derlocke-ng/kiwi-network).

## Este repositório { #this-repository }

```
site/          the homepage: plain HTML, CSS and JS, served at kiwi-network.eu
site/icons/    the app icons it uses: mostly from kiwi-icons, some from the apps' own repos
docs/          this documentation (MkDocs Material), served at kiwi-network.eu/docs/
mkdocs.yml     docs configuration
```

```bash
python -m pip install mkdocs-material mkdocs-static-i18n
mkdocs serve             # pré-visualização em direto em http://127.0.0.1:8000
mkdocs build --strict    # o que a CI constrói: falha com links e âncoras partidos
python -m http.server -d site 8080   # a página inicial
```

Um push para `main` publica ambos através do GitHub Pages.

Por favor, mantém a documentação **fiel aos repositórios**. Descreve o que uma
ferramenta faz hoje, marca como planeado tudo o que estiver planeado, e põe um
link para a fonte para os detalhes em vez de os copiares.
