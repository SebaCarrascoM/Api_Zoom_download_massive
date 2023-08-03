import requests
import os
from urllib3.exceptions import IncompleteRead

fecha_inicio = '2022-01-01'
fecha_fin = '2022-12-31'
TOKEN = 'YOU TOKEN'

def obtener_lista_usuarios(token, pagina=1, limite=500000):
    url = 'https://api.zoom.us/v2/users'

    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json',
    }

    params = {
        'page_size': limite,
        'page_number': pagina
    }

    response = requests.get(url, headers=headers, params=params)

    if response.status_code == 200:
        data = response.json()
        return data.get('users', [])
    else:
        print(f"Error al obtener la lista de usuarios: {response.status_code}, {response.text}")
        return []

def obtener_reuniones_usuario(email, fecha_inicio, fecha_fin,user_email):
    url = f'https://api.zoom.us/v2/users/{email}/recordings'
    headers = {
        'Authorization': f'Bearer {TOKEN}',
        'Content-Type': 'application/json',
    }

    params = {
        'from': fecha_inicio,
        'to': fecha_fin,
        'page_size': 500000,
    }

    response = requests.get(url, headers=headers, params=params)

    if response.status_code == 200:
        data = response.json()

        return data.get('meetings', [])
    else:
        print(f"Error al obtener las reuniones del usuario: {response.status_code}, {response.text}")
        return []

def identificar_usuarios_en_misma_reunion(lista_usuarios, fecha_inicio, fecha_fin):
    reuniones_usuarios = {}

    for usuario in lista_usuarios:
        
        user_email = usuario.get('email')
        reuniones_usuario = obtener_reuniones_usuario(fecha_inicio, fecha_fin,user_email)

        for reunion in reuniones_usuario:
            reunion_id = reunion.get('id')

            if reunion_id in reuniones_usuarios:
                reuniones_usuarios[reunion_id].append(user_email)
            else:
                reuniones_usuarios[reunion_id] = [user_email]

    return reuniones_usuarios

def limpiar_nombre_archivo(nombre):
    caracteres_no_validos = r'<>:"/\|?*'
    for caracter in caracteres_no_validos:
        nombre = nombre.replace(caracter, '')
    nombre = nombre.strip()
    return nombre

def descargar_grabaciones(grabaciones_descargables, reuniones_usuarios):
    usuarios_descargados = set()

    for grabacion in grabaciones_descargables:
        grab_id = grabacion.get('id')
        grabado = grabacion.get('topic', '').replace('"', '')

        # Obtener la lista de usuarios que participaron en esta reunión
        usuarios_en_reunion = reuniones_usuarios.get(grab_id, [])

        for archivo in grabacion.get('recording_files', []):

            if archivo.get('file_type') == 'MP4':
                url_grabacion = archivo.get('download_url')
                nombre_archivo = f"{grab_id}_{grabado}_{archivo.get('file_size')}.mp4"
                nombre_archivo = limpiar_nombre_archivo(nombre_archivo)

                ruta_completa = os.path.join('Directorio', nombre_archivo)

                if not os.path.exists(ruta_completa):
                    try:
                        response = requests.get(url_grabacion)
                        with open(ruta_completa, 'wb') as archivo:
                            archivo.write(response.content)
                        print(f"Descargado: {ruta_completa}")

                        # Agregar los usuarios de esta reunión a la lista de usuarios descargados
                        usuarios_descargados.update(usuarios_en_reunion)

                    except IncompleteRead as e:
                        print(f"Error de descarga: {e}")
                    except Exception as e:
                        print(f"Error de descarga: {e}")
                else:
                    print(f"El archivo ya existe: {ruta_completa}")

def descargar_grabacion(url_grabacion, nombre_archivo):
    if not os.path.exists(nombre_archivo):
        try:
            response = requests.get(url_grabacion)
            with open(nombre_archivo, 'wb') as archivo:
                archivo.write(response.content)
            print(f"Descargado: {nombre_archivo}")
        except IncompleteRead as e:
            print(f"Error de descarga: {e}")
    else:
        print(f"El archivo ya existe: {nombre_archivo}")

# Obtener la lista de usuarios
lista_usuarios = obtener_lista_usuarios(TOKEN)

# Identificar los usuarios que estuvieron en las mismas reuniones
reuniones_usuarios = identificar_usuarios_en_misma_reunion(lista_usuarios, fecha_inicio, fecha_fin)

for usuario in lista_usuarios:
    
    user_email= usuario.get('email')
    grabaciones = obtener_reuniones_usuario(user_email, fecha_inicio, fecha_fin)
    if grabaciones:
        print({user_email})
        print(f"Se encontraron grabaciones para el usuario con ID: {user_email}")
        descargar_grabaciones(grabaciones, reuniones_usuarios)
    else:
        print({user_email})
        print(f"No se encontraron grabaciones para el usuario con ID: {user_email}")
