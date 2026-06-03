

# Shell Remoto Multihilo - Trabajo Práctico

El propósito de esta actividad es utilizar los sockets como recurso de comunicación ofrecido por el sistema operativo, a
través de las librerías estándar de Python, para desarrollar una aplicación Cliente/Servidor. El servidor actuará como un
intérprete de comandos remoto limitado, permitiendo a los clientes conectados ejecutar operaciones básicas de gestión
de archivos en el servidor.

---

## 1. Implementación de la Comunicación con Sockets

Se utilizò la API  `socket` de Python, que opera bajo el protocolo **TCP (SOCK_STREAM)** e **IPv4 (AF_INET)**.

### Flujo del Servidor (`proy-1-serv-tcp.py`)
1. **Inicialización y Enlace:** Se crea el socket  usando `socket.socket(socket.AF_INET, socket.SOCK_STREAM)`. Para evitar el error de bloqueo de puertos en reinicios rápidos del servicio, se activa la opción de reutilización de direcciones IP:
   `server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)`
   Luego, el socket se asocia a todas las interfaces locales (`0.0.0.0`) y al puerto `5000` mediante `server.bind((HOST, PORT))`.

2. **Escucha:** Se establece el modo de escucha activa con `server.listen(5)`. Este parámetro define la longitud de la cola de espera para conexiones entrantes.

3. **Aceptación Bloqueante:** El servidor entra en un bucle infinito donde la función `server.accept()` bloquea el flujo hasta que un cliente inicia el saludo. Retorna un objeto socket (`conn`) y una tupla con los datos de red del host remoto (`addr`).

4. **Limite de 5 conexiones activas** Atraves del módulo Threading se implementa el semáforo, que será el que controle que solo hayan 5 conexiones activas, antes de realizar la validación de credenciales, el hilo principal ejecuta `semaforo_clientes.acquire()`. Si el contador es mayor a cero, decrementa el valor y prosigue; si es cero, suspende el hilo actual hasta que se libere un cupo.
  * Si la autenticación falla o cuando el cliente cierra voluntariamente la sesión, se invoca `semaforo_clientes.release()`, incrementando el contador e indicando al planificador del Sistema Operativo que puede despertar a un proceso en espera.

5. **Hilos Hijos (Trabajadores):** Una vez instanciado el hilo con `threading.Thread(target=atender_clientes, args=(conn, addr))`, el método `.start()` delega la ejecución al planificador de la CPU. El hilo hijo ejecuta su propio bucle de comandos de manera aislada.


### Flujo del Cliente (`proy-1-cli-tcp.py`)
1. **Conexión Activa:** El cliente se instancia bajo la misma configuración TCP/IPv4 e inicia la conexión remota mediante `cliente.connect((HOST, PORT))`.
2. **Lectura y Escritura:** Ambos extremos utilizan  `.recv(1024)` para la captura de bytes  y `.send()` / `.sendall()` para el envio de cadenas previamente serializadas a bytes utilizando la codificación UTF-8.

---

## 2. Gestión de Hilos y Concurrencia en el Servidor

El servidor emplea un modelo de **Multiprocesamiento Basado en Hilos por Conexión** administrado atraves del modulo `threading`. Esto previene que las operaciones de entrada/salida (I/O) de un usuario bloqueen la atención de solicitudes paralelas.

---

### Agregación de nuevas funcionalidades 03/06           

* **Protocolo Manual (Prefijo de Longitud):** Para evitar que los mensajes grandes se corten o se junten en la red (fragmentación de buffers), se implementó un protocolo propio. Cada envío calcula el tamaño del mensaje y le pega adelante un header fijo de 10 bytes con ese número (usando `.zfill(10)`). El receptor lee primero los 10 bytes, sabe cuánto esperar y no corta la recepción hasta tener el cuerpo completo.
* **Seguridad SSL/TLS:** Toda la comunicación viaja cifrada envolviendo los sockets nativos con el módulo `ssl` de Python.
* **Base de Datos Segura:** Las contraseñas no se guardan en texto plano en el servidor. Se validan contra un archivo `users.json` usando **Bcrypt** para verificar los hashes encriptados.
* **Protección Anti-Path Traversal:** El comando `cd` está controlado con la librería `pathlib` para impedir que un usuario se "escape" de la carpeta raíz del servidor y acceda a archivos privados del sistema operativo.

---
## 3. Guía de Ejecución
## Preparación del Entorno (Líneas de Comando)

Antes de ejecutar el proyecto, es necesario instalar las librerías de seguridad y generar los certificados criptográficos para el canal seguro SSL/TLS.

### Paso 1: Instalar dependencias
En la terminal de Linux, instalá la librería necesaria para el manejo de contraseñas:
```bash
pip install bcrypt
```

### Paso 2: Generar el Certificado SSL y la Clave Privada
Para que el módulo ssl pueda cifrar la conexión, el servidor necesita un certificado y una clave. Generalos ejecutando el siguiente comando en tu terminal de Linux (dentro de la misma carpeta del proyecto):

```
openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout servidor.key -out servidor.crt
```


### Paso 3: Crear la base de datos de usuarios
Asegurate de tener un archivo llamado users.json en la carpeta del servidor con tus usuarios de prueba y sus contraseñas previamente hasheadas con Bcrypt. Ejemplo de estructura:

```JSON
{
  "abigail": "$2b$12$EjemploDeHashBcryptQueCoincidaConTuClave..."
}
```

## Paso 4: Iniciar el Servidor
Abrir una terminal y ejecutar:

```cmd
python3 proy-1-serv-tcp.py
```
La terminal reflejará esto: Servidor TCP esperando conexión...

## Paso 5: Iniciar el Cliente
Abri una nueva pestaña o terminal independiente y ejecutar:

```cmd
python3 proy-1-cli-tcp.py
```

### Paso 6: Interacción en Producción
Al conectar, iniciara el login de manera  sin mostrar los caracteres de la contraseña en pantalla mediante el módulo getpass:
```cmd
Usuario: aby
Contraseña: 

```
Una vez logueado, se habilitará la pantalla de inicio:
```Plaintext
Bienvenido, conexión aceptada
Comandos Disponibles (Linux / Windows):
    • ls / dir          → Listar archivos en el directorio actual o el path indicado.
    • pwd               → Mostrar la ruta absoluta del directorio de trabajo actual.
    • cd <directorio>   → Cambiar de directorio (Validación de seguridad).
    • cat / type <arch> → Mostrar el contenido de un archivo de texto en pantalla.
    • mkdir <nombre>    → Crear una nueva carpeta en la ruta actual.
    • help              → Mostrar este menú de asistencia con los comandos permitidos.
    • exit              → Finalizar la sesión actual y cerrar la conexión de forma segura.
```


Ejemplo de uso de comandos:

```Plaintext
comando: pwd
/home/usuario/tp_redes

comando: ls
users.json  servidor.py  cliente.py

comando: exit
Conexion finalizada
```
---

### Estructura del Código
servidor.py: Programa principal. Escucha conexiones, administra los hilos, valida credenciales y ejecuta los comandos mediante subprocess.run.

cliente.py: Interfaz del usuario. Captura comandos mediante consola, oculta la contraseña al tipear (getpass) y muestra los resultados.

protocolo.py: Contiene las funciones de empaquetado de datos (enviar_mensaje_manual y recibir_mensaje_manual) que manejan la cabecera de 10 bytes de forma matemática.