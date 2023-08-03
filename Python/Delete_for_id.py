import requests
import pandas as pd

TOKEN = 'YOUR TOKEN'
def obtener_reuniones_usuario(user_id):
    url = f'https://api.zoom.us/v2/users/{user_id}/recordings'
    headers = {
        'Authorization': f'Bearer {TOKEN}',
        'Content-Type': 'application/json',
    }

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        data = response.json()
        return data.get('meetings', [])
    else:
        print(f"Error al obtener las reuniones del usuario: {response.status_code}, {response.text}")
        return []

def eliminar_grabacion(grabacion_id):
    url = f'https://api.zoom.us/v2/meetings/{grabacion_id}/recordings'
    headers = {
        'Authorization': f'Bearer {TOKEN}',
        'Content-Type': 'application/json',
    }

    response = requests.delete(url, headers=headers)

    if response.status_code == 204:
        print(f"La grabación con ID {grabacion_id} ha sido eliminada de la nube de Zoom.")
    else:
        print(f"Error al eliminar la grabación con ID {grabacion_id}: {response.status_code}, {response.text}")

# Crear un DataFrame a partir del archivo de Excel que contiene los ID de grabaciones
df = pd.read_excel('EXCEL CON SUS ID')

# Obtener los ID de grabaciones desde el DataFrame
grabaciones_a_eliminar = df['ID de Grabación'].tolist()

# Iterar sobre los ID de grabaciones y eliminarlos de la nube de Zoom
for grabacion_id in grabaciones_a_eliminar:
    eliminar_grabacion(grabacion_id)
