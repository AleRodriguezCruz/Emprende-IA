import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium

# --- Configuración de la Página ---
st.set_page_config(
    page_title="Emprende IA - Oportunidades en Ensenada",
    page_icon="💡",
    layout="wide"
)

# --- Título y Descripción ---
st.title("💡 Emprende IA")
st.markdown("Tu asistente inteligente para encontrar oportunidades de negocio en **Ensenada, Baja California**.")

# --- Carga de Datos ---
# Usamos @st.cache_data para que los datos se carguen una sola vez y la app sea rápida.
@st.cache_data
def load_data():
    try:
        # El nombre del archivo CSV que subiste a GitHub
        df = pd.read_csv('datos_ensenada.csv', encoding='latin1')
        df_ensenada = df[df['municipio'] == 'Ensenada'].copy()
        df_limpio = df_ensenada[['nombre_act', 'latitud', 'longitud']].copy()
        df_limpio.rename(columns={'nombre_act': 'categoria_negocio'}, inplace=True)
        df_limpio.dropna(subset=['latitud', 'longitud'], inplace=True)
        return df_limpio
    except FileNotFoundError:
        st.error("Error: No se encontró el archivo 'denue_inegi_02_.csv'. Asegúrate de que esté en tu repositorio de GitHub.")
        return pd.DataFrame() # Retorna un dataframe vacío para evitar más errores

df_limpio = load_data()

if not df_limpio.empty:
    # --- Barra Lateral de Filtros (Sidebar) ---
    st.sidebar.header("Panel de Análisis")
    
    # Crear una lista de categorías de negocio únicas para el selector
    lista_categorias = sorted(df_limpio['categoria_negocio'].unique())
    
    # Selector para el tipo de negocio
    categoria_seleccionada = st.sidebar.selectbox(
        "Selecciona un tipo de negocio:",
        options=["TODOS (Mapa de Calor)"] + lista_categorias, # Añadimos "TODOS" al principio
        index=0 # Por defecto mostrará la opción general
    )

    # --- Lógica de Filtrado ---
    if categoria_seleccionada == "TODOS (Mapa de Calor)":
        df_filtrado = df_limpio
        titulo_mapa = "Mapa de Densidad de TODOS los Negocios"
    else:
        df_filtrado = df_limpio[df_limpio['categoria_negocio'] == categoria_seleccionada]
        titulo_mapa = f"Ubicación de: {categoria_seleccionada}"

    st.header(titulo_mapa)
    st.write(f"Se encontraron **{len(df_filtrado)}** establecimientos que coinciden con tu búsqueda.")

    # --- Creación del Mapa Interactivo ---
    mapa = folium.Map(location=[31.8661, -116.6056], zoom_start=12)

    # Si se seleccionan "TODOS", mostrar un mapa de calor.
    if categoria_seleccionada == "TODOS (Mapa de Calor)":
        from folium.plugins import HeatMap
        coordenadas = df_filtrado[['latitud', 'longitud']].values.tolist()
        HeatMap(coordenadas, radius=10).add_to(mapa)
    # Si se selecciona una categoría, mostrar marcadores individuales.
    else:
        for idx, row in df_filtrado.iterrows():
            folium.Marker(
                [row['latitud'], row['longitud']],
                popup=row['categoria_negocio'],
                tooltip=row['categoria_negocio']
            ).add_to(mapa)

    # --- Mostrar el Mapa en Streamlit ---
    st_folium(mapa, width=1000, height=600)

    # --- Mostrar Top de Negocios (Opcional) ---
    if categoria_seleccionada == "TODOS (Mapa de Calor)":
        st.header("Negocios más comunes en Ensenada")
        top_negocios = df_limpio['categoria_negocio'].value_counts().head(15)

        st.bar_chart(top_negocios)
