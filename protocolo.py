def enviar_mensaje_manual(cliente, texto_mensaje):
    # convertr a bytes el mensjae para medirlo
    datos_cuerpo = texto_mensaje.encode('utf-8')
    longitud = len(datos_cuerpo)
    
    # header que indica cuantos bytes mide el msj
    # Ejemplo: Si longitud es 45, queda "0000000045"
    cabecera_texto = str(longitud).zfill(10)
    datos_cabecera = cabecera_texto.encode('utf-8')
    
    #
    cliente.sendall(datos_cabecera + datos_cuerpo)

def recibir_mensaje_manual(cliente):
    # inicializo una variable de bytes vacia
    datos_cabecera = b""
    while len(datos_cabecera) < 10:
        #si solo me trajo 4 bytes en la segunda vuelta va a pedir el restante, 10-4 = 6bytes
        chunk = cliente.recv(10 - len(datos_cabecera))
        if not chunk:
            return None  # El socket se cerró
        datos_cabecera += chunk
        
    # convierto los bytes a texto y luego a un int
    longitud_esperada = int(datos_cabecera.decode('utf-8'))
    
    # lo mismo pero para el cuerpo
    datos_cuerpo = b""
    while len(datos_cuerpo) < longitud_esperada:
        # con min si me queda menos de 1024 para recibir toma ese valor y termina
        tamaño_buffer = min(1024, longitud_esperada - len(datos_cuerpo))
        chunk = cliente.recv(tamaño_buffer)
        if not chunk:
            break
        datos_cuerpo += chunk
        
    return datos_cuerpo.decode('utf-8')