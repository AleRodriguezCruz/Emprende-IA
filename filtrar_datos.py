import pandas as pd

# Archivo de entrada con todos los datos
archivo_principal = 'db-ens-bc.csv'
# Archivo de salida que crearemos
archivo_filtrado = 'datos_ensenada.csv'

print("--- Creando la Base de Datos Final (Versión Corregida) ---")

try:
    print(f"Paso 1: Cargando '{archivo_principal}'...")
    df = pd.read_csv(archivo_principal, encoding='latin1', low_memory=False)
    print("Archivo cargado.")

    # Paso 2: Filtrar por Ensenada usando la columna correcta
    print("Paso 2: Filtrando negocios de Ensenada (cve_municipio_fk == 1)...")
    df_ensenada = df[df['cve_municipio_fk'] == 1].copy()

    # Paso 3: Seleccionar las columnas correctas que sí existen
    # Usamos 'nom_estab' como el nombre/categoría del negocio
    print("Paso 3: Seleccionando las columnas finales (nom_estab, latitud, longitud)...")
    df_final = df_ensenada[['nom_estab', 'latitud', 'longitud']]

    # Renombrar 'nom_estab' para que la app lo entienda
    df_final.rename(columns={'nom_estab': 'categoria_negocio'}, inplace=True)

    # Guardar el archivo final
    df_final.to_csv(archivo_filtrado, index=False)
    
    print(f"\n¡LISTO! Se ha creado el archivo '{archivo_filtrado}'.")
    print("Este es el archivo definitivo. ¡Lo logramos!")

except FileNotFoundError:
    print(f"\nERROR: No se encontró el archivo '{archivo_principal}'.")
except KeyError as e:
    print(f"\nERROR DE COLUMNA: No se encontró la columna {e}.")
    print("Esto no debería pasar ahora, pero verifica los nombres si ocurre.")
