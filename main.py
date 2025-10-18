import pandas as pd
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

# --------------------------------------------------------------------------
# 1. CONFIGURACIÓN INICIAL Y CARGA DE DATOS
# --------------------------------------------------------------------------

# Crear la aplicación FastAPI
app = FastAPI(
    title="Emprende IA API",
    description="API para analizar oportunidades de negocio desde un archivo de Excel (CSV).",
    version="1.0.0",
)

# --- Modelo de Datos para Pydantic (para POST y PUT) ---
# Esto define cómo deben lucir los datos cuando creamos o actualizamos un negocio.
# FastAPI lo usará para validar automáticamente los datos que recibe.
class Negocio(BaseModel):
    clee: str
    nom_estab: str
    nombre_act: str
    nomb_asent: str # Colonia
    latitud: float
    longitud: float

# --- Carga y Limpieza de Datos ---
# Usamos un bloque try-except para manejar el error si el archivo no se encuentra.
try:
    # Definimos la ruta del archivo que está en la misma carpeta
    DATA_PATH = "db-ens-bc.csv.xlsx - denue_inegi_02_.csv"
    
    # Leemos el archivo CSV usando pandas
    df = pd.read_csv(DATA_PATH, encoding='latin1')

    # Limpieza básica: nos aseguramos de que las columnas clave no tengan valores nulos
    df.dropna(subset=['clee', 'nomb_asent', 'nombre_act', 'latitud', 'longitud'], inplace=True)

    # Asegurarnos que 'clee' sea un string para evitar problemas de tipo
    df['clee'] = df['clee'].astype(str)
    
    print("✅ Datos cargados y limpiados correctamente.")

except FileNotFoundError:
    print(f"❌ ERROR: No se encontró el archivo en la ruta: {DATA_PATH}")
    df = pd.DataFrame() # Creamos un DataFrame vacío para que la app no se rompa al iniciar

# --------------------------------------------------------------------------
# 2. DEFINICIÓN DE LOS ENDPOINTS DE LA API
# --------------------------------------------------------------------------

# Prefijo para todas las rutas, como lo pidió el profesor
PREFIX = "/excel/negocio"

@app.get("/")
def read_root():
    return {"mensaje": "Bienvenido a la API de Emprende IA. Ve a /docs para ver la documentación."}

# --- Endpoint para obtener la lista de todas las colonias ---
@app.get(f"{PREFIX}/colonias", tags=["Consultas"])
def get_colonias():
    """
    Obtiene una lista única y ordenada de todas las colonias.
    """
    if df.empty:
        raise HTTPException(status_code=500, detail="El archivo de datos no pudo ser cargado.")
    
    lista_colonias = sorted(df['nomb_asent'].unique())
    return {"colonias": lista_colonias}

# --- Endpoint para encontrar oportunidades en una colonia específica ---
@app.get(f"{PREFIX}/oportunidades/{{colonia}}", tags=["Análisis"])
def get_oportunidades_por_colonia(colonia: str):
    """
    Encuentra las 5 categorías de negocio con menor presencia en una colonia específica.
    """
    if df.empty:
        raise HTTPException(status_code=500, detail="El archivo de datos no pudo ser cargado.")

    # Filtramos el DataFrame por la colonia (insensible a mayúsculas/minúsculas)
    df_colonia = df[df['nomb_asent'].str.lower() == colonia.lower()]

    if df_colonia.empty:
        raise HTTPException(status_code=404, detail=f"Colonia '{colonia}' no encontrada.")

    # Contamos la frecuencia de cada categoría de negocio
    conteo = df_colonia['nombre_act'].value_counts()
    oportunidades = conteo.nsmallest(5)

    # Convertimos el resultado a un formato JSON amigable
    resultado = [{"categoria": index, "conteo": int(value)} for index, value in oportunidades.items()]
    return {"colonia": colonia, "oportunidades": resultado}

# --- Endpoint para obtener todos los negocios de una colonia ---
@app.get(f"{PREFIX}/colonia/{{colonia}}", tags=["Consultas"])
def get_negocios_por_colonia(colonia: str):
    """
    Devuelve una lista de todos los negocios ubicados en una colonia específica.
    """
    if df.empty:
        raise HTTPException(status_code=500, detail="El archivo de datos no pudo ser cargado.")

    df_colonia = df[df['nomb_asent'].str.lower() == colonia.lower()]

    if df_colonia.empty:
        raise HTTPException(status_code=404, detail=f"Colonia '{colonia}' no encontrada.")

    # Convertimos el dataframe filtrado a formato JSON (una lista de objetos)
    return df_colonia.to_dict(orient='records')

# --- Endpoint para obtener un negocio por su ID (clee) ---
@app.get(f"{PREFIX}/{{clee}}", tags=["Consultas"])
def get_negocio_por_clee(clee: str):
    """
    Obtiene la información detallada de un negocio usando su 'clee' único.
    """
    if df.empty:
        raise HTTPException(status_code=500, detail="El archivo de datos no pudo ser cargado.")
        
    negocio = df[df['clee'] == clee]
    
    if negocio.empty:
        raise HTTPException(status_code=404, detail=f"Negocio con clee '{clee}' no encontrado.")
        
    return negocio.to_dict(orient='records')[0]

# --- Endpoint para AÑADIR un nuevo negocio (simulado) ---
@app.post(f"{PREFIX}/", status_code=201, tags=["Modificaciones"])
def crear_negocio(negocio: Negocio):
    """
    Añade un nuevo negocio al archivo CSV.
    **Nota:** En un entorno real, esto se haría contra una base de datos.
    Modificar un archivo CSV en vivo puede ser riesgoso.
    """
    global df
    if df.empty:
        raise HTTPException(status_code=500, detail="El archivo de datos no pudo ser cargado.")

    # Revisar si el 'clee' ya existe
    if negocio.clee in df['clee'].values:
        raise HTTPException(status_code=400, detail=f"El negocio con clee '{negocio.clee}' ya existe.")

    # Convertimos el objeto Pydantic a un diccionario y luego a un DataFrame de una fila
    nuevo_negocio_df = pd.DataFrame([negocio.dict()])
    
    # Usamos pd.concat para añadir la nueva fila al DataFrame principal
    df = pd.concat([df, nuevo_negocio_df], ignore_index=True)
    
    # Guardar los cambios de vuelta al archivo CSV
    df.to_csv(DATA_PATH, index=False, encoding='latin1')
    
    return {"mensaje": "Negocio creado exitosamente", "data": negocio.dict()}

# --- Endpoint para ACTUALIZAR un negocio (simulado) ---
@app.put(f"{PREFIX}/{{clee}}", tags=["Modificaciones"])
def actualizar_negocio(clee: str, negocio_actualizado: Negocio):
    """
    Actualiza la información de un negocio existente.
    """
    global df
    if df.empty:
        raise HTTPException(status_code=500, detail="El archivo de datos no pudo ser cargado.")
        
    # Buscar el índice del negocio a actualizar
    indices = df.index[df['clee'] == clee].tolist()
    
    if not indices:
        raise HTTPException(status_code=404, detail=f"Negocio con clee '{clee}' no encontrado.")
    
    # Actualizamos los datos en el DataFrame
    for col, value in negocio_actualizado.dict().items():
        df.at[indices[0], col] = value
        
    # Guardar los cambios de vuelta al archivo CSV
    df.to_csv(DATA_PATH, index=False, encoding='latin1')
    
    return {"mensaje": "Negocio actualizado exitosamente", "data": negocio_actualizado.dict()}

# --- Endpoint para ELIMINAR un negocio (simulado) ---
@app.delete(f"{PREFIX}/{{clee}}", tags=["Modificaciones"])
def eliminar_negocio(clee: str):
    """
    Elimina un negocio del archivo CSV.
    """
    global df
    if df.empty:
        raise HTTPException(status_code=500, detail="El archivo de datos no pudo ser cargado.")
        
    # Verificar si el negocio existe antes de intentar borrarlo
    if clee not in df['clee'].values:
        raise HTTPException(status_code=404, detail=f"Negocio con clee '{clee}' no encontrado.")
    
    # Eliminar las filas que coincidan con el 'clee'
    df = df[df['clee'] != clee]
    
    # Guardar los cambios de vuelta al archivo CSV
    df.to_csv(DATA_PATH, index=False, encoding='latin1')
    
    return {"mensaje": f"Negocio con clee '{clee}' eliminado exitosamente."}
