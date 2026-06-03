

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

## 3. Guía de Ejecución


### Requisitos Previos
Contar con el archivo `users.json` inicializado en la misma carpeta del script del servidor con una base de datos de usuario ficticia:
```json
{
    "test": "1234",
    "admin": "admin"
}
```

## Paso 1: Iniciar el Servidor
Abrir una terminal y ejecutar:

```cmd
python3 proy-1-serv-tcp.py
```
La terminal reflejará esto: Servidor TCP esperando conexión...

## Paso 2: Iniciar el Cliente
Abri una nueva pestaña o terminal independiente y ejecutar:

```cmd
python3 proy-1-cli-tcp.py
```

### Paso 3: Interacción en Producción
Al conectar, iniciara el login de manera  sin mostrar los caracteres de la contraseña en pantalla mediante el módulo getpass:
```cmd
Usuario: aby
Contraseña: 

```
Una vez logueado, se habilitará la pantalla de inicio:
```Plaintext
Bienvenido, conexión aceptada
    • ls → listar archivos en el directorio actual o del path indicado
    • pwd → mostrar el directorio de trabajo.
    • cat <archivo> → mostrar el contenido de un archivo.
    • exit → finaliza la sesión.
    • help → ver comandos disponibles
    • mkdir → crea carpeta
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
