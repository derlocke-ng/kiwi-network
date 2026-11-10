# Hacia dónde va

En esta página se describe en qué está previsto que se convierta kiwi-server y
qué partes de ese plan existen ya.

!!! info "Diseñado, aún sin implementar"
    Esta página resume el
    [diseño del plano de control](https://github.com/derlocke-ng/kiwi-server/blob/main/docs/design/control-plane.md)
    de kiwi-server, que se acordó en octubre de 2026. Nada de lo que se
    describe aquí existe todavía, salvo cuando una línea dice *implementado*.
    El orden de los trabajos se sigue en la
    [hoja de ruta](https://github.com/derlocke-ng/kiwi-server/blob/main/docs/ROADMAP.md).

Hoy kiwi-server es una herramienta de escritorio. El archivo fleet, los
secretos y la CA (la autoridad de certificación de la fleet) están en tu propio
ordenador. El plan es convertirlo en un **servicio** que pueda funcionar en un
node. Así se podrá crear y administrar una red sin un escritorio Linux, desde
un teléfono y entre varias personas. Las máquinas se seguirán pudiendo
reproducir a partir del archivo fleet. El plano de control es la parte que
guarda ese archivo y ejecuta el generador, el programa que convierte el archivo
fleet en la configuración de cada máquina.

## Las capas { #the-layers }

El diseño divide el software en cinco capas.

1. **kiwi-modules** contiene los módulos y el contrato de generación, que
   define cómo se genera la configuración de una máquina. *Implementado.*
2. **kiwi-stack** es la parte que se ejecuta en la máquina. Empieza con
   `kiwi-stack apply`, que instala en la máquina una configuración generada.
   *Implementado.*
3. **El núcleo de kiwi-server** se ocupa de la fleet, los hosts, los sistemas
   de destino, las ISO, la CA, el alta de dispositivos y `apply`. No tiene
   interfaz gráfica propia, igual que hoy. *Implementado.*
4. **El módulo de control** es el núcleo empaquetado como contenedor, con una
   API y una interfaz web. Funciona en un node como un módulo más.
5. **Los clientes** son los programas con los que trabajas con el módulo de
   control. Lo primero será la interfaz web. La app GTK se mantiene y se
   comunica o bien con la CLI local, o bien con un controlador (un módulo de
   control en marcha) a través de la mesh, la red WireGuard privada. La CLI
   también se mantiene. Toda la lógica se queda en el núcleo, así que ningún
   cliente tiene lógica propia.

## El node de control { #the-control-node }

El controlador funciona en un node de casa, al que se llama *node de control*.
Solo pueden acceder a él los administradores, solo desde la mesh, y su disco
está cifrado. Guarda el seed, la clave de la CA, el archivo fleet y todas las
configuraciones.

El **master alquilado pasa a ser un simple punto de paso, fácil de sustituir**.
Se limita a reenviar
el tráfico de la red y solo guarda lo que necesita para funcionar: sus claves y
peers de WireGuard, sus propias contraseñas y su certificado. Si pierdes el
master, lo vuelves a aplicar desde el node de control. Si pierdes el node de
control, restauras la copia de seguridad de la fleet.

## Usuarios { #users }

Un bloque `users:` define usuarios con uno de dos roles. Un **administrador de
la fleet** puede hacerlo todo. Un **administrador de node** está limitado a sus
propios hosts: ve el estado, los logs, las cargas de trabajo y las copias de
seguridad de esos hosts, y puede dar de alta dispositivos en los grupos que le
permita el administrador de la fleet. Un administrador de node no ve nada del
master, de la CA ni de los demás nodes. Para iniciar sesión, un usuario
necesita una contraseña y, además, un certificado de cliente de la CA de la
fleet o WebAuthn. Cada cambio queda registrado en un log de auditoría.

## Incorporar una máquina { #joining-a-machine }

Una máquina puede entrar en la red de dos maneras, y las dos se mantienen:

- **Una ISO por host** que lleva el rol de la máquina, como el
  `build --offline` actual. Es para instalaciones sin conexión.
- **Una ISO de arranque genérica** por sistema de destino, que la CI construye
  una sola vez y que no lleva ningún secreto. En el primer arranque, la máquina
  obtiene su rol del controlador con un **token de alta** de un solo uso. Una
  máquina instalada a mano, o un VPS, entra con una sola línea:
  `curl https://control.<host>.<tld>/join/<token> | sudo bash`.

Está previsto que todas las máquinas de la familia CoreOS usen **una única
imagen bootc**, una imagen de contenedor arrancable que es la misma para todas.
La máquina recibe su rol en el primer arranque.

## Federación y multi-hop { #federation-and-multi-hop }

La federación conecta Kiwi Networks independientes. Las redes que confían en la
CA de la otra y se delegan nombres entre sí pasan a ser clientes la una de la
otra. Un master tiene tres modos de salida, que determinan cómo llega su
tráfico a Internet. Con el tercero, el master de una red envía su tráfico hacia
Internet a través del master de otra red. A esto se le llama **multi-hop**, y el
segundo master solo ve al primero. Quien gestiona varios masters de esta forma
tiene su propio servicio de VPN, con masters de entrada en un país, masters de
salida en otros y Tor dentro de la red.

## El orchard { #the-orchard }

El orchard («huerto de frutales» en inglés) es el servicio previsto para quien
gestiona muchos masters para otras personas. Será una app aparte o un plugin de
kiwi-server. Crea VPS mediante la API de los proveedores de hosting y entrega a
cada master su instalación y un token de registro. Recoge de cada master un
heartbeat, un informe de estado periódico (versión, estado, disco, última
actualización). Distribuye las actualizaciones cambiando el tag de imagen de
cada canal de actualización.

El orchard no puede iniciar sesión en un master, leer una fleet ni modificar un
node. Cada inquilino, es decir, cada persona a la que otro le gestiona el master, guarda
su red en su propio node de control, en casa. La fleet y las claves se quedan
allí, de modo que el proveedor de hosting en el que funciona la máquina virtual
del master no puede leer los datos de la red del inquilino. El master de cada
inquilino funciona en su propia máquina virtual. El orchard necesita un driver
para la API de los proveedores, y la compatibilidad de kiwi-server con netcup
(`kiwi-server vps`, *implementado*) es la primera pieza.

## Más proveedores de hosting y arranque por red { #more-hosters-and-network-boot }

*Previsto.* El objetivo es que una máquina se pueda instalar de forma
totalmente automática, esté donde esté.

- **Los proveedores de hosting como plugins.** Hoy, kiwi-server ya funciona con
  netcup de serie. El plan es tener un repositorio aparte para la API de los
  proveedores, de modo que cualquiera pueda añadir AWS, Hetzner y otros. Un
  plugin funcionaría igual que lo hace hoy la parte de netcup: crea o borra un
  servidor, pone en él la instalación y lo arranca.
- **Wake-on-LAN y arranque PXE** están previstos para las máquinas de casa.
  Wake-on-LAN enciende una máquina por la red, y PXE le permite arrancar desde
  la red. Así, un node se despierta y se instala por la red, sin necesidad de
  una memoria USB.

## Más cosas en la lista { #also-on-the-list }

La hoja de ruta incluye también un master de reserva, podman rootless, IPv6 de
extremo a extremo, placas ARM, rangos de puertos y un módulo de juegos, y la
restauración de los datos de un node en su primer arranque.
