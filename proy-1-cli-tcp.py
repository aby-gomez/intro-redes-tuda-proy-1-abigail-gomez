import socket
import ssl
import getpass
from protocolo import enviar_mensaje_manual, recibir_mensaje_manual

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
            comando_temp= (comandos+ '\n')

            enviar_mensaje_manual(cliente,comando_temp)

            respuesta = recibir_mensaje_manual(cliente)

            if not respuesta :
                print("Conexion finalizada")
                break

            print(respuesta)
    
    except Exception as e:
        print(f"[ERROR]: {e}")

def iniciar_sesion():
    try:
        #creo objeto socket que se conecta por ipv4 y por protocolo tcp
        cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        #contexto del cliente, como uso certificado propio hay que indicar que no pida nombres de dominio reales ni certificacion real
        contexto = ssl.create_default_context()
        contexto.check_hostname = False
        contexto.verify_mode = ssl.CERT_NONE
        cliente = contexto.wrap_socket(cliente)

        cliente.connect((HOST,PORT))

        
        msg= recibir_mensaje_manual(cliente)
        print(msg)
            
        usuario = input("Usuario: ")
        contrasenia = getpass.getpass("Contraseña: ")

        enviar_mensaje_manual(cliente,(usuario+" "+contrasenia+'\n'))
        respuesta = recibir_mensaje_manual(cliente)

        if not respuesta or "denegado" in respuesta.lower():
            print(respuesta)
            return
        
        print(respuesta)
    
        enviar_comandos(cliente)

    except Exception as e:
        print(f"[ERROR]: {e}")
    

if __name__ == "__main__":
    iniciar_sesion()

