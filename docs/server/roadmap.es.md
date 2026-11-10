# Hacia dónde va

!!! info "Diseñado, no construido"
    Esta página resume el
    [diseño del plano de control](https://github.com/derlocke-ng/kiwi-server/blob/main/docs/design/control-plane.md)
    de kiwi-server, acordado en octubre de 2026. Salvo que una línea diga
    *construido*, nada de esto existe todavía. La
    [hoja de ruta](https://github.com/derlocke-ng/kiwi-server/blob/main/docs/ROADMAP.md)
    sigue el orden.

Hoy kiwi-server es una herramienta de escritorio: el archivo fleet, los secretos
y la CA viven en la máquina del operador. El plan es convertirlo en un
**servicio** que pueda funcionar en un node, para que una red se pueda crear y
gestionar sin un escritorio Linux, desde un teléfono y por más de una persona.
Las máquinas siguen siendo reproducibles a partir del archivo fleet. El plano de
control es solo lo que guarda ese archivo y ejecuta el renderizador.

## Las capas { #the-layers }

1. **kiwi-modules**: los módulos y el contrato de renderizado para una máquina. *Construido.*
2. **kiwi-stack**: la parte de la máquina, a partir de `kiwi-stack apply`. *Construido.*
3. **El núcleo de kiwi-server**: la fleet, los hosts, los targets, las ISOs, la
   CA, las altas y el apply, sin interfaz gráfica como hoy. *Construido.*
4. **El módulo de control**: el núcleo como contenedor, con una API y una
   interfaz web, funcionando como módulo en un node como cualquier otro.
5. **Clientes**: primero la interfaz web. La app GTK se queda y habla con la CLI
   local o con un controlador a través de la malla, y la CLI también se queda.
   Ninguna interfaz desarrolla lógica propia.

## El node de control { #the-control-node }

El controlador funciona en un node en casa (el *node de control*), accesible
desde la malla solo para administradores, en un disco cifrado. Guarda la
semilla, la clave de la CA, el archivo fleet y todas las configuraciones.

El **master alquilado pasa a ser infraestructura de relay sustituible**. Solo
guarda lo que necesita para funcionar: sus claves y peers de WireGuard, sus
propias contraseñas y su certificado. Perderlo cuesta un nuevo apply desde el
node de control. Perder el node de control cuesta restaurar la copia de seguridad
de la fleet.

## Usuarios { #users }

Un bloque `users:` con dos roles: un **administrador de la fleet** que puede
hacerlo todo, y **administradores de node** ligados a sus propios hosts. Un
administrador de node ve el estado, los logs, las cargas de trabajo y las copias
de seguridad de esos hosts, y da de alta dispositivos en los grupos que permite
el administrador de la fleet, pero no ve nada del master, de la CA ni de los
demás nodes. El inicio de sesión es una contraseña más un certificado de cliente
de la CA de la fleet o WebAuthn, y cada cambio va a un registro de auditoría.

## Unir una máquina { #joining-a-machine }

Se mantienen ambos caminos:

- **Una ISO por host** con su rol (el `build --offline` de hoy), para
  instalaciones sin conexión.
- **Una ISO de arranque genérica** por target, construida una vez por la CI y
  sin ningún secreto. En el primer arranque obtiene su rol del controlador con un
  **token de unión** de un solo uso. Una máquina instalada a mano o un VPS se une
  con una línea: `curl https://control.<host>.<tld>/join/<token> | sudo bash`.

La idea es que cada máquina de la familia CoreOS ejecute **una imagen bootc**, y
que el rol llegue en el primer arranque.

## Federación y multi-hop { #federation-and-multi-hop }

Las redes que confían en la CA de la otra y se delegan nombres entre sí se
convierten en clientes la una de la otra. Con el tercer modo de salida, el
master de una red puede salir a Internet a través del de otra: **multi-hop**,
donde el segundo master solo ve al primero. Varios masters gestionados por un
mismo operador forman entonces un servicio VPN propio: masters de entrada en un
país, masters de salida en otros, Tor dentro.

## El huerto { #the-orchard }

El huerto (orchard) es para quienes gestionan muchos masters para otras
personas. Es una app aparte o un plugin de kiwi-server que crea VPS mediante las
API de los proveedores, entrega a cada master su instalación y un token de
registro, recoge un latido de cada master (versión, salud, disco, última
actualización) y despliega actualizaciones moviendo tags de imagen por canal.

No puede iniciar sesión en un master, leer una fleet ni tocar un node. El node de
control de cada cliente, en su casa, guarda su red. Quien aloja el master no
puede leerla, y ejecuta una VM por cliente. El soporte de netcup de kiwi-server
(`kiwi-server
vps`, *construido*) es la primera pieza de su controlador de proveedores.

## Más proveedores, y arranque por red { #more-hosters-and-network-boot }

*Previsto.* El objetivo es una instalación totalmente automatizada, esté donde
esté la máquina.

- **Proveedores como plugins.** netcup viene integrado hoy. El plan es un
  repositorio propio para las API de proveedores, para que cualquiera pueda
  añadir AWS, Hetzner y los demás tal como funciona netcup ahora: crear o borrar
  un servidor, poner la instalación en él y arrancarlo.
- **Wake-on-LAN y arranque PXE** para máquinas en casa: un node se despierta y se
  instala por la red, sin memoria USB.

## También en la lista { #also-on-the-list }

Un master de reserva, podman sin root, IPv6 de extremo a extremo, placas ARM,
rangos de puertos y un módulo de juegos, y una restauración de los datos de un
node en el primer arranque.
