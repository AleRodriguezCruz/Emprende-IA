import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import time

# --- 1. CONFIGURACIÓN INICIAL DE LA PÁGINA ---
st.set_page_config(
    page_title="Emprende IA",
    page_icon="🤖",
    layout="wide"
)

# --- TÍTULO Y BIENVENIDA ---
st.title("🤖 Emprende IA v2.0")
st.header("Tu Asistente de Negocios Inteligente para Ensenada")
st.markdown("---")

# --- 2. BODEGA DE DATOS ---
@st.cache_data
def load_data():
    try:
        df = pd.read_csv('datos_ensenada.csv', encoding='latin1')
        df['latitud'] = pd.to_numeric(df['latitud'], errors='coerce')
        df['longitud'] = pd.to_numeric(df['longitud'], errors='coerce')
        df.dropna(subset=['latitud', 'longitud', 'categoria_negocio'], inplace=True)
        return df
    except FileNotFoundError:
        st.error("Error Crítico: No se encontró 'datos_ensenada.csv'. Súbelo a tu repositorio.")
        return None

df_completo = load_data()

# --- 3. GPS INTERNO ---
ZONAS_CONOCIDAS = {
    "maneadero": (31.7167, -116.5667, 3), "centro": (31.8650, -116.6217, 2),
    "chapultepec": (31.8386, -116.6014, 2), "sauzal": (31.8833, -116.6833, 2.5),
    "valle dorado": (31.8489, -116.5858, 2)
}

# --- 4. CEREBRO DEL ASISTENTE v2.0  ---

# Diccionario para definir las relaciones entre negocios
SINERGIAS = {
    "escuela": {
        "palabras_clave": ["escuela", "colegio", "instituto", "universidad", "escolar", "secundaria", "preparatoria", "cbtis", "conalep"],
        "oportunidad": "Papelería / Tienda de útiles",
        "busqueda_oportunidad": ["papeleria", "copias", "utiles", "cyber"]
    },
    "salud": {
        "palabras_clave": ["hospital", "clinica", "imss", "issste", "consultorio", "medico", "centro de salud"],
        "oportunidad": "Farmacia",
        "busqueda_oportunidad": ["farmacia", "drogueria", "botica"]
    },
    "gym": {
        "palabras_clave": ["gym", "gimnasio", "fitness", "crossfit", "deportivo"],
        "oportunidad": "Tienda de suplementos / Nutrición",
        "busqueda_oportunidad": ["suplementos", "nutricion", "vitaminas", "proteina"]
    }
}

def encontrar_zona_en_texto(texto):
    for zona in ZONAS_CONOCIDAS:
        if zona in texto.lower(): return zona
    return None

def filtrar_negocios_por_zona(df, zona_info):
    lat_zona, lon_zona, radio_km = zona_info
    radio_grados = radio_km / 111.0
    lat_min, lat_max = lat_zona - radio_grados, lat_zona + radio_grados
    lon_min, lon_max = lon_zona - radio_grados, lon_zona + radio_grados
    return df[(df['latitud'].between(lat_min, lat_max)) & (df['longitud'].between(lon_min, lon_max))]

def buscar_cerca(df, lat_centro, lon_centro, radio_km):
    radio_grados = radio_km / 111.0
    lat_min, lat_max = lat_centro - radio_grados, lat_centro + radio_grados
    lon_min, lon_max = lon_centro - radio_grados, lon_centro + radio_grados
    return df[(df['latitud'].between(lat_min, lat_max)) & (df['longitud'].between(lon_min, lon_max))]

def analizar_sinergias(df_zona):
    oportunidades_encontradas = []
    for tipo_ancla, reglas in SINERGIAS.items():
        regex_ancla = '|'.join(reglas['palabras_clave'])
        df_anclas = df_zona[df_zona['categoria_negocio'].str.contains(regex_ancla, case=False, na=False)]
        
        for _, ancla in df_anclas.iterrows():
            df_cercanos = buscar_cerca(df_zona, ancla['latitud'], ancla['longitud'], 0.5) # Radio de 500m
            regex_oportunidad = '|'.join(reglas['busqueda_oportunidad'])
            df_oportunidad_existente = df_cercanos[df_cercanos['categoria_negocio'].str.contains(regex_oportunidad, case=False, na=False)]
            
            if df_oportunidad_existente.empty:
                oportunidades_encontradas.append({
                    "tipo": reglas['oportunidad'],
                    "ancla_nombre": ancla['categoria_negocio'],
                    "ancla_lat": ancla['latitud'],
                    "ancla_lon": ancla['longitud']
                })
    return oportunidades_encontradas

# --- 5. INTERFAZ GRÁFICA ---
if df_completo is not None:
    st.info("👋 ¡Hola! Dime qué zona de Ensenada te gustaría analizar para encontrar oportunidades de negocio basadas en sinergias. Por ejemplo: **Analiza el centro**")
    query = st.text_input("Escribe tu consulta aquí:", "", placeholder="Oportunidades en Valle Dorado...")

    if query:
        zona_identificada = encontrar_zona_en_texto(query)
        
        if zona_identificada:
            with st.spinner('🧠 Analizando sinergias y buscando en el mapa...'):
                time.sleep(1)
                zona_info = ZONAS_CONOCIDAS[zona_identificada]
                df_zona_filtrada = filtrar_negocios_por_zona(df_completo, zona_info)
                oportunidades = analizar_sinergias(df_zona_filtrada)
            
            with st.container(border=True):
                st.success(f"✅ Análisis de Sinergias completado para: **{zona_identificada.capitalize()}**")
                
                col1, col2 = st.columns([1, 1.5])
                with col1:
                    st.subheader("🎯 Oportunidades por Sinergia")
                    st.metric("Oportunidades detectadas", len(oportunidades))
                    if oportunidades:
                        st.write("Detecté estas posibles ubicaciones:")
                        for op in oportunidades:
                            st.markdown(f"- **{op['tipo']}** cerca de *{op['ancla_nombre']}*")
                    else:
                        st.write("No se encontraron sinergias claras en esta zona con los datos actuales. ¡Podría ser un área con todo cubierto!")

                with col2:
                    st.subheader("🗺️ Mapa de Oportunidades")
                    mapa = folium.Map(location=[zona_info[0], zona_info[1]], zoom_start=14)
                    
                    # Marcar oportunidades
                    if oportunidades:
                        for op in oportunidades:
                            # Marcador AZUL para el negocio "ancla" (la escuela, el gym, etc.)
                            folium.Marker(
                                [op['ancla_lat'], op['ancla_lon']], 
                                tooltip=f"Ancla: {op['ancla_nombre']}",
                                icon=folium.Icon(color='blue', icon='info-sign')
                            ).add_to(mapa)
                            # Marcador VERDE para la OPORTUNIDAD
                            folium.Marker(
                                [op['ancla_lat'] + 0.0005, op['ancla_lon'] + 0.0005], # Un poco al lado para que no se encime
                                tooltip=f"Oportunidad: {op['tipo']}",
                                icon=folium.Icon(color='green', icon='star')
                            ).add_to(mapa)

                    st_folium(mapa, height=400, use_container_width=True)
        else:
            st.warning("⚠️ No pude identificar una zona conocida. Intenta con 'Maneadero', 'Centro', 'Chapultepec', etc.")
else:
    st.error("No se pudieron cargar los datos. La aplicación no puede continuar.")
