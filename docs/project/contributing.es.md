# Cómo contribuir

Todo el proyecto Kiwi Network es de código abierto. En esta página verás adónde
va cada tipo de contribución. Abre las issues y los pull requests en el
repositorio al que se refieren. Los repositorios están enumerados en
[Repositorios y estado](status.md).

- **Una app para el catálogo.** El catálogo es la lista de apps que
  kiwi-updater puede instalar. Añade a tu app un `kiwi.manifest` y un
  `install.sh`, publícala con un tag firmado y abre un pull request en
  [kiwi-catalog](https://github.com/derlocke-ng/kiwi-catalog). Consulta
  [Publicar una app](../desktop/catalogs.md#publishing-an-app).
- **Un módulo.** Los módulos se desarrollan en
  [kiwi-modules](https://github.com/derlocke-ng/kiwi-modules). Un módulo es un
  directorio con un `module.yaml` y plantillas de Jinja. Consulta
  [Escribir un módulo](../server/modules.md#writing-a-module).
- **Un hub o una app para un hub.** Haz un fork de
  [Armory](https://github.com/derlocke-ng/armory), crea el esqueleto de una app
  con `npm run new-app` y añade tu hub a
  [kiwi-web-catalog](https://github.com/derlocke-ng/kiwi-web-catalog). Consulta
  [Tu propio hub](../people/hubs.md).
- **Un proveedor para kiwi-proxy.** Un proveedor es un plugin que aporta a
  kiwi-proxy un tipo de conexión, como Tor o una VPN. Todos los proveedores
  ofrecen SOCKS5 y nada más. Las reglas que tiene que cumplir un proveedor
  están en
  [docs/plugin-system.md](https://github.com/derlocke-ng/kiwi-proxy/blob/main/docs/plugin-system.md),
  en el repositorio de kiwi-proxy.
- **Este sitio web y esta documentación** están en el repositorio
  [kiwi-network](https://github.com/derlocke-ng/kiwi-network).

## Este repositorio { #this-repository }

El repositorio kiwi-network contiene la página principal y esta documentación:

```
site/          the homepage: plain HTML, CSS and JS, served at kiwi-network.eu
docs/          this documentation (MkDocs Material), served at kiwi-network.eu/docs/
docs/assets/   the logo and app icons (copied from kiwi-icons) and the docs' stylesheet
mkdocs.yml     docs configuration
```

Para ver la documentación y la página principal en tu propio ordenador, ejecuta:

```bash
python -m pip install mkdocs-material mkdocs-static-i18n
mkdocs serve             # vista previa en directo en http://127.0.0.1:8000
mkdocs build --strict    # lo que construye la CI: falla si hay enlaces o anclas rotos
python -m http.server -d site 8080   # la página principal
```

Cuando haces push a `main`, la página principal y la documentación se publican
a través de GitHub Pages.

Por favor, mantén la documentación **fiel a los repositorios**. Describe lo que
hace hoy cada herramienta, marca como previsto todo lo que esté previsto y, en
lugar de copiar los detalles, enlaza a la fuente.
