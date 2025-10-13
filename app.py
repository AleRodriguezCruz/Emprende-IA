import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium

st.set_page_config(page_title="Emprende IA", page_icon="🤖", layout="wide")

st.title("🤖 Emprende IA: Tu Asistente de Negocios")
st.markdown("Hazme una pregunta como: `¿Qué negocios faltan en Maneadero?`")

@st.cache_data
def load_data():
    try:
        # El archivo ya viene limpio, solo lo cargamos
        df = pd.read_csv('datos_ensenada.csv', encoding='latin1')
        df['latitud'] = pd.to_numeric(df['latitud'], errors='coerce')
        df['longitud'] = pd.to_numeric(df['longitud'], errors='coerce')
        df.dropna(subset=['latitud', 'longitud'], inplace=True)
        return df
    except FileNotFoundError:
        st.error("Error Crítico: No se encontró 'datos_ensenada.csv'. Súbelo a tu repositorio de GitHub.")
        return None

df_completo = load_data()

ZONAS_CONOCIDAS = {
    "maneadero": (31.7167, -116.5667, 3), "centro": (31.8650, -116.6217, 2),
    "chapultepec": (31.8386, -116.6014, 2), "sauzal": (31.8833, -116.6833, 2.5),
    "valle dorado": (31.8489, -116.5858, 2)
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

def encontrar_oportunidades(df_zona):
    if df_zona.empty: return []
    conteo = df_zona['categoria_negocio'].value_counts()
    return conteo.nsmallest(5).index.tolist()

if df_completo is not None:
    query = st.text_input("¿Qué deseas analizar hoy?", "")
    if query:
        zona_identificada = encontrar_zona_en_texto(query)
        if zona_identificada:
            st.success(f"Analizando la zona de: **{zona_identificada.capitalize()}**")
            zona_info = ZONAS_CONOCIDAS[zona_identificada]
            df_zona_filtrada = filtrar_negocios_por_zona(df_completo, zona_info)
            oportunidades = encontrar_oportunidades(df_zona_filtrada)
            
            col1, col2 = st.columns([1, 1])
            with col1:
                st.subheader("Oportunidades Potenciales")
                if oportunidades:
                    st.write(f"En **{zona_identificada.capitalize()}**, he detectado baja competencia en estas áreas:")
                    for op in oportunidades: st.markdown(f"- **{op}**")
                else:
                    st.write("No se encontraron suficientes datos para analizar en esta zona.")
            with col2:
                st.subheader(f"Mapa de Negocios en {zona_identificada.capitalize()}")
                mapa = folium.Map(location=[zona_info[0], zona_info[1]], zoom_start=14)
                for _, negocio in df_zona_filtrada.iterrows():
                    folium.Marker([negocio['latitud'], negocio['longitud']], tooltip=negocio['categoria_negocio']).add_to(mapa)
                st_folium(mapa, height=400)
        else:
            st.warning("No identifiqué una zona conocida. Intenta con 'Maneadero', 'Centro', etc.")
