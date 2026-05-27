import socket
import threading
import subprocess    
import json



"""
Requerimientos del servidor
1. Implementar un servidor TCP en Python que:
• Escuche en un puerto definido (ej. 5000).
• Acepte conexiones de hasta 5 clientes concurrentes.
• Cree un hilo por cliente para manejar la comunicación.
2. El servidor debe interpretar comandos básicos enviados por el cliente, tales como:
• ls → listar archivos en el directorio actual. y poder indicarle el path
• pwd → mostrar el directorio de trabajo.
• cat <archivo> → mostrar el contenido de un archivo.
• exit → cerrar la conexión del cliente.
.help(ver comandos disponibles)
.mkdir

3. Manejar errores (ej. archivo inexistente, comando inválido) devolviendo mensajes claros al cliente.
4. Validar usuarios, usuario y contraseña, contrastarlo con una bd en el servidor

"""

HOST = '0.0.0.0'
PORT = 5000

# semáforo global limitado a 5 pases
semaforo_clientes = threading.Semaphore(5)

comandos_disponibles= """
    • ls → listar archivos en el directorio actual o del path indicado
    • pwd → mostrar el directorio de trabajo.
    • cat <archivo> → mostrar el contenido de un archivo.
    • exit → finaliza la sesión.
    • help → ver comandos disponibles
    • mkdir → crea carpeta
"""

def atender_clientes(conn,addr):
    print(f"[NUEVA CONEXIÓN] {addr} conectado.")

    conn.sendall(("Bienvenido, conexión aceptada\n"
                 +comandos_disponibles+"\n").encode('utf-8'))  
    try:
        while True:
            while True:
                # Recibe datos del cliente
                chunk = conn.recv(1024).decode('utf-8')
                if '\n' in chunk:
                    #elimina caracteres o espacios del inicio y el final
                    chunk = chunk.strip()
                #si no recibi datos salgo
                if not chunk:
                    conn.sendall("No se registró ningun comando, intenta nuevamente\n".encode('utf-8'))            
                #
                else:
                    break
                
                
            
            if not chunk or chunk.lower() == 'exit':
                print("Sesión finalizada por el cliente")
                break

            print(f"Comando recibido: {chunk}")
            lista_comandos = chunk.split()
            print(lista_comandos)
           
            if lista_comandos[0] in ['ls', 'pwd', 'cat', 'mkdir']:

                try:
                    # subprocess le delega el trabajo al so, devuelve un objeto con  las 3 propiedades , capture ouput devuelve el texto del comnado, text true decodifica byte a string
                    ejecucion = subprocess.run(lista_comandos, capture_output=True, text=True, timeout=5)
                    
                    #cuando todo esta ok envia un 0 sino algo disntitnto
                    if ejecucion.returncode != 0:
                        # Si el comando falló en el SO (ej: 'cat' de un archivo que no existe)
                        respuesta = f"Error: {ejecucion.stderr}"
                    else:
                        # Si se ejecutó correctamente 
                        respuesta = ejecucion.stdout
                        
                except Exception as e:
                    respuesta = f"Error interno al ejecutar el comando: {str(e)}\n"

            elif lista_comandos[0].lower() == "help":
                respuesta = comandos_disponibles
            
            else:
            # Si el comando no está en la lista de permitidos 
                respuesta = f"Error: Comando '{chunk}' no permitido o inválido.\n"

            respuesta_delimitada = respuesta + "\n"
            conn.sendall(respuesta_delimitada.encode('utf-8'))           

    except Exception as e:
        print(f"[ERROR] Con {addr}: {e}")
    finally:
        conn.close()
        print(f"[DESCONECTADO] {addr} finalizó.")
        #Cuando el hilo termina, liberamos el pase para el próximo cliente
        semaforo_clientes.release()

def validar_usuario(conn) -> bool: 
    conn.sendall("Ingrese usuario y contraseña ".encode('utf-8')) 
    datos = conn.recv(1024).decode('utf-8').strip().split()
    
    #evalua que se hayan enviado datos tanto en usuario como en contraseña
    if len(datos) < 2:
        return False

    with open("users.json","r", encoding="utf-8") as archivo:
        datos_cargados = json.load(archivo)

    print(datos_cargados)
    print(datos)

    ok = datos_cargados.get(datos[0],[])
    print(ok)
    if not ok: 
        return False
    
    if ok == datos[1] : 
        return True
    
    return False

    



def inicio():

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    #evita error de Addres already in use al reiniciar 
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((HOST, PORT))
    #tamaño de la cola de espera
    server.listen(5)
    print("Servidor TCP esperando conexión...")
    try:
    #crea un hilo , lo inicia, vuelve a empezar por cada solicitud de conexion, funciones del multiprocesamiento
        while True:#loop infinito
            #accept genera tupla, socket y direccion ip
            conn, addr = server.accept()
            # antes de validar o crear el hilo veo si hay pases disponibles
            # Si ya hay 5, el flujo se frena acá hasta que uno se desconecte.
            semaforo_clientes.acquire()
            resultado_validacion = validar_usuario(conn)

            if resultado_validacion:
                #paso socket del cliente y direccion del cliente, esto genera procesos concurrentes
                thread = threading.Thread(target=atender_clientes, args=(conn, addr))
                thread.start()
            else:
                conn.close()
                # Si no pasa la validación,  cierra el socket y libera el pase inmediatamente
                semaforo_clientes.release()
    except Exception as e:
        
        print(f"[ERROR1] Con {addr}: {e}")
    
        
    


if __name__ == "__main__":
    inicio()
 






