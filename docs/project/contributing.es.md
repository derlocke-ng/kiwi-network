# Contribuir

Todo es de código abierto. Las incidencias y las pull requests van al
repositorio al que se refieren; consulta [Repositorios y estado](status.md).

- **Una app para el catálogo.** Añade un `kiwi.manifest` y un `install.sh`,
  publica con un tag firmado y abre una pull request contra
  [kiwi-catalog](https://github.com/derlocke-ng/kiwi-catalog). Consulta
  [Publicar una app](../desktop/catalogs.md#publishing-an-app).
- **Un módulo.** Los módulos se desarrollan en
  [kiwi-modules](https://github.com/derlocke-ng/kiwi-modules): un directorio con
  un `module.yaml` y plantillas Jinja. Consulta [Escribir un módulo](../server/modules.md#writing-a-module).
- **Un hub o una app de hub.** Haz un fork de
  [Armory](https://github.com/derlocke-ng/armory), genera el esqueleto de una app
  con `npm run new-app` y añade tu hub a
  [kiwi-web-catalog](https://github.com/derlocke-ng/kiwi-web-catalog). Consulta
  [Tu propio hub](../people/hubs.md).
- **Un proveedor de kiwi-proxy.** Todo proveedor expone SOCKS5 y nada más. El
  contrato está en
  [docs/plugin-system.md](https://github.com/derlocke-ng/kiwi-proxy/blob/main/docs/plugin-system.md)
  de kiwi-proxy.
- **Este sitio web y esta documentación** viven en
  [kiwi-network](https://github.com/derlocke-ng/kiwi-network).

## Este repositorio { #this-repository }

```
site/          the homepage: plain HTML, CSS and JS, served at kiwi-network.eu
site/icons/    the app icons it uses: mostly from kiwi-icons, some from the apps' own repos
docs/          this documentation (MkDocs Material), served at kiwi-network.eu/docs/
mkdocs.yml     docs configuration
```

```bash
python -m pip install mkdocs-material mkdocs-static-i18n
mkdocs serve             # vista previa en vivo en http://127.0.0.1:8000
mkdocs build --strict    # lo que construye la CI: falla con enlaces y anclas rotos
python -m http.server -d site 8080   # la página de inicio
```

Un push a `main` despliega ambos mediante GitHub Pages.

Por favor, mantén la documentación **fiel a los repositorios**. Describe lo que
hace hoy una herramienta, marca como previsto todo lo previsto y enlaza al código
fuente para los detalles en lugar de copiarlos.
