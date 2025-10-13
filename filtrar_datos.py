import pandas as pd

# Nombre del archivo grande que descargaste
archivo_original = 'denue_inegi_02_.csv'

# Nombre que le daremos a nuestro nuevo archivo, más pequeño
archivo_filtrado = 'datos_ensenada.csv'

print(f"Cargando el archivo grande: {archivo_original}...")

# Leer el archivo CSV. Esto puede tardar un momento.
df = pd.read_csv(archivo_original, encoding='latin1')

print("Archivo cargado. Filtrando por municipio de 'Ensenada'...")

# Filtrar el DataFrame para quedarnos solo con las filas de Ensenada
df_ensenada = df[df['municipio'] == 'Ensenada']

print(f"Se encontraron {len(df_ensenada)} negocios en Ensenada.")

# Guardar el resultado en un nuevo archivo CSV, mucho más ligero
df_ensenada.to_csv(archivo_filtrado, index=False)

print(f"¡Éxito! Se ha creado el archivo '{archivo_filtrado}' con solo los datos de Ensenada.")