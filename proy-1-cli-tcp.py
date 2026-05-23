import socket
import getpass
"""
1. Implementar un cliente TCP en Python que:
• Se conecte al servidor en la IP y puerto especificados.
• Permita al usuario escribir comandos en una terminal interactiva.
• Envíe los comandos al servidor y muestre la respuesta recibida.
2. El cliente no debe validar ni interpretar los comandos: solo envía texto y muestra texto.
"""

HOST = '127.0.0.1'
PORT = 5000

def enviar_comandos(cliente):
    try:
       
    
       
        while True:
            comandos= input(f"comando:")
            comando_temp= (comandos+ '\n').encode('utf-8') 

            cliente.send(comando_temp)

            respuesta = cliente.recv(1024).decode('utf-8')

            if respuesta == "":
                print("Conexion finalizada")
                break

            print(respuesta)
    
    except Exception as e:
        print(f"[ERROR]: {e}")

def iniciar_sesion():
    try:
        #creo objeto socket que se conecta por ipv4 y por protocolo tcp
        cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        cliente.connect((HOST,PORT))

        
        msg= cliente.recv(1024).decode('utf-8')
        print(msg)
            
        usuario = input("Usuario: ")
        contrasenia = getpass.getpass("Contraseña: ")

        cliente.send((usuario+" "+contrasenia+'\n').encode('utf-8'))
        respuesta = cliente.recv(1024).decode('utf-8')

        if respuesta == "":
            print("Usuario o contraseña incorrectos")
            return
        
        print(respuesta)
        enviar_comandos(cliente)

    except Exception as e:
        print(f"[ERROR]: {e}")
    

if __name__ == "__main__":
    iniciar_sesion()

