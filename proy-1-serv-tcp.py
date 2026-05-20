import socket
import threading
import subprocess    


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


def atender_clientes(conn,addr):
    print(f"[NUEVA CONEXIÓN] {addr} conectado.")
    try:
        while True:
            buffer = ""
            while True:
                # Recibe datos del cliente
                chunk = conn.recv(1024).decode('utf-8')
                #si no recibi datos salgo
                if not chunk:
                    break
                #
                if '\n' in chunk:
                    buffer += chunk.replace("\n", "")
                    break
                buffer += chunk

            if not buffer or buffer.lower() == 'exit':
                print("Sesión finalizada por el cliente")
                break

            print(f"Comando recibido: {buffer}")
            lista_comandos = buffer.strip().split()

           
            if lista_comandos[0] in ['ls', 'pwd', 'cat']:

                try:
                    # Pasar la lista completa directamente
                    ejecucion = subprocess.run(lista_comandos, capture_output=True, text=True, timeout=5)
                    
                    if ejecucion.returncode != 0:
                        # Si el comando falló en el SO (ej: 'cat' de un archivo que no existe)
                        respuesta = f"Error: {ejecucion.stderr}"
                    else:
                        # Si se ejecutó correctamente 
                        respuesta = ejecucion.stdout
                        
                except Exception as e:
                    respuesta = f"Error interno al ejecutar el comando: {str(e)}\n"
                
            else:
            # Si el comando no está en la lista de permitidos 
                respuesta = f"Error: Comando '{buffer}' no permitido o inválido.\n"

            respuesta_delimitada = respuesta + "\n"
            conn.sendall(respuesta_delimitada.encode('utf-8'))           

    except Exception as e:
        print(f"[ERROR] Con {addr}: {e}")
    finally:
        conn.close()
        print(f"[DESCONECTADO] {addr} finalizó.")






def inicio():

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    #escucha hasta 5 clientes
    server.listen(5)
    print("Servidor TCP esperando conexión...")

    #crea un hilo , lo inicia, vuelve a empezar por cada solicitud de conexion, funciones del multiprocesamiento
    while True:#loop infinito
        #accept genera tupla, socjet y direccion ip
        conn, addr = server.accept()
        #paso socket del cliente y direccion del cliente, esto genera procesos concurrentes
        thread = threading.Thread(target=atender_clientes, args=(conn, addr))
        thread.start()


if __name__ == "__main__":
    inicio()
 






