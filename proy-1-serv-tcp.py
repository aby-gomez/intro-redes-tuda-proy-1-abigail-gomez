import socket
import threading
import subprocess    
import json
import sys
import ssl
import bcrypt
import os
from pathlib import Path
from protocolo import enviar_mensaje_manual, recibir_mensaje_manual
      

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
DIRECTORIO_RAIZ = Path(os.getcwd()).resolve()

comandos_disponibles= """
   Comandos Disponibles (Linux / Windows):
    • ls / dir          → Listar archivos en el directorio actual o el path indicado.
    • pwd               → Mostrar la ruta absoluta del directorio de trabajo actual.
    • cd <directorio>   → Cambiar de directorio (Validación de seguridad).
    • cat / type <arch> → Mostrar el contenido de un archivo de texto en pantalla.
    • mkdir <nombre>    → Crear una nueva carpeta en la ruta actual.
    • help              → Mostrar este menú de asistencia con los comandos permitidos.
    • exit              → Finalizar la sesión actual y cerrar la conexión de forma segura.
"""




def atender_clientes(conn,addr):
    
    #para que sea multihilo la validacion del cliente se encuentra dentro del hilo
    if not validar_usuario(conn):
        print(f"[ACCESO DENEGADO] {addr} falló la autenticación.")
        enviar_mensaje_manual(conn,"Acceso denegado: Credenciales invalidas.\n")
        conn.close()
        semaforo_clientes.release() 
        return
    
    print(f"[NUEVA CONEXIÓN] {addr} conectado.")
    enviar_mensaje_manual(conn,("Bienvenido, conexion aceptada\n"
                  +comandos_disponibles+"\n"))                
    try:
        while True:
                # Recibe datos del cliente
            chunk = recibir_mensaje_manual(conn)
                
            chunk = chunk.strip()
                #si no recibi datos salgo
            if not chunk:
                enviar_mensaje_manual(conn,"No se registro ningun comando, intenta nuevamente\n")         
                continue   
                
            if chunk.lower() == 'exit':
                print("Sesión finalizada por el cliente")
                break

            print(f"Comando recibido: {chunk}")
            lista_comandos = chunk.split()

           
            # subprocess al crear un proceso hijo (otra terminal) no maneja bien el comando cd
            if lista_comandos[0].lower() == "cd":
                if len(lista_comandos) < 2:
                    if sys.platform == "win32":
                        # En Windows, 'cd' solo devuelve la ruta actual
                        respuesta = os.getcwd()
                    else:
                      
                        respuesta = f"Directorio actual: {os.getcwd()}"
                else:
                    try:
                        
                        # DIRECTORIO_RAIZ definido arriba, os.getcwd() directorio donde esta el servidor, path de linux une por si sola la ruta , no importa si esta en win o linux
                        ruta_destino = (Path(os.getcwd()) / lista_comandos[1]).resolve()
                        
                        # Validación Anti-Path Traversal, se fija si el directorio al que quiere ir es hijo de mi directorio raiz o esta dentro del mismo
                        if DIRECTORIO_RAIZ in ruta_destino.parents or ruta_destino == DIRECTORIO_RAIZ:
                            os.chdir(ruta_destino)  # Cambia el directorio de trabajo del proceso padre(el servidor)
                            respuesta = f"Directorio cambiado a: {os.getcwd()}"
                        else:
                            respuesta = "Error de Seguridad: No tenés permisos para salir de la raíz."
                    except Exception as e:
                        respuesta = f"Error al cambiar de directorio: {str(e)}"


            elif sys.platform == "linux" and lista_comandos[0] in ['ls', 'pwd', 'cat', 'mkdir'] or (sys.platform == "win32" and lista_comandos[0] in ['dir', 'pwd', 'type', 'mkdir']):

                try:
                    
                    # subprocess le delega el trabajo al so, devuelve un objeto con  las 3 propiedades , capture ouput devuelve el texto del comnado, text true decodifica byte a string
                    ejecucion = subprocess.run(lista_comandos, shell=(sys.platform == "win32"),capture_output=True, text=True, timeout=5)
                    
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
            enviar_mensaje_manual(conn,respuesta_delimitada)           

    except Exception as e:
        print(f"[ERROR] Con {addr}: {e}")
    finally:
        conn.close()
        print(f"[DESCONECTADO] {addr} finalizó.")
        #Cuando el hilo termina, liberamos el pase para el próximo cliente
        semaforo_clientes.release()


def validar_usuario(conn) -> bool: 
    enviar_mensaje_manual(conn,("Ingrese usuario y contraseña ")) 
    datos = recibir_mensaje_manual(conn).strip().split()
    
    #evalua que se hayan enviado datos tanto en usuario como en contraseña
    if len(datos) < 2:
        return False

    with open("users.json","r", encoding="utf-8") as archivo:
        datos_cargados = json.load(archivo)
    

    pass_hash = datos_cargados.get(datos[0],[])
    
    if not pass_hash: 
        return False
    
    #convierto los strings a bytes
    password_cliente_bytes = datos[1].encode('utf-8')
    pass_hash_bytes = pass_hash.encode('utf-8')

    #bcrypt checquea si coinciden las contrseñas
    if bcrypt.checkpw(password_cliente_bytes, pass_hash_bytes): 
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

            #creo contexto de servidor
            contexto = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
            #cargo certficiados
            contexto.load_cert_chain(certfile="servidor.crt", keyfile="servidor.key")
            #enuvelvo el socket de la conexion con el contexto
            conn = contexto.wrap_socket(conn, server_side=True)
            
            #paso socket del cliente y direccion del cliente, esto genera procesos concurrentes
            thread = threading.Thread(target=atender_clientes, args=(conn, addr))
            thread.start()
            
    except Exception as e:
        
        print(f"[ERROR1] Con {addr}: {e}")
    
        
    


if __name__ == "__main__":
    inicio()
 






